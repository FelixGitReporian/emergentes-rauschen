"""
core/agents.py – Real Agent Layer (Epic 11).

Implements a fully vectorized agent system with explicit heading, velocity,
and policy-based behaviour rules. Two agent policies are provided:

1. BoidsPolicy  – separation + alignment + cohesion (Reynolds 1987).
2. AntPolicy    – pheromone-following with random exploration and deposition.

Architecture:
    All agent arrays are shape (max_agents,), float32.
    Active agents are tracked via a boolean ``active`` mask.
    Spatial hashing bins agents into a grid for O(N) neighbour search.

    Bidirectional coupling:
    - Field → Agent:  agents sample field values (energy, memory, flow) at
                      their continuous position via bilinear interpolation.
    - Agent → Field:  agents deposit pheromone/energy/matter into the field
                      at their grid cell (add with clip).

Scientific caution:
    Boids implement the classical three-rule model (Reynolds 1987).
    This is a faithful, not merely approximate, implementation of those rules.
    The AntPolicy is inspired by Deneubourg's ant model but uses the abstract
    memory field as pheromone — no nest/food chemistry is simulated.
    Both policies operate in a continuous toroidal space.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

from emergent_noise.core.state import GridState


# ──────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────

@dataclass
class AgentConfig:
    """Configuration for the agent system.

    Parameters
    ----------
    n_agents:
        Number of initially active agents.
    max_agents:
        Fixed array capacity (active + reserve).
    policy:
        "boids" or "ant". Determines which behavioural rules run.
    max_speed:
        Maximum speed in grid-cells per tick.
    min_speed:
        Minimum speed (agents don't stop).
    perception_radius:
        Radius within which an agent perceives neighbours (boids)
        or samples field gradients (ant). In grid cells.
    separation_weight:
        Boids: strength of separation steering.
    alignment_weight:
        Boids: strength of velocity alignment.
    cohesion_weight:
        Boids: strength of cohesion toward local centre.
    separation_radius:
        Boids: radius below which separation kicks in (< perception_radius).
    pheromone_weight:
        Ant: weight of pheromone gradient in steering.
    noise_weight:
        Ant: weight of random heading perturbation.
    deposit_rate:
        Ant: amount of pheromone deposited per tick into memory field.
    energy_deposit:
        Amount of energy deposited into the field per tick.
    field_flow_drag:
        Fraction of flow field added to agent velocity each tick.
    velocity_damping:
        Multiplicative damping per tick (< 1 = friction).
    seed:
        Random seed for reproducible initialization.
    """

    n_agents: int = 100
    max_agents: int = 400
    policy: str = "boids"
    max_speed: float = 0.8
    min_speed: float = 0.15
    perception_radius: float = 6.0
    separation_weight: float = 1.8
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.8
    separation_radius: float = 2.5
    pheromone_weight: float = 2.0
    noise_weight: float = 0.3
    deposit_rate: float = 0.04
    energy_deposit: float = 0.005
    field_flow_drag: float = 0.08
    velocity_damping: float = 0.96
    seed: int = 42


# ──────────────────────────────────────────────────────────────────
# Agent System
# ──────────────────────────────────────────────────────────────────

class AgentSystem:
    """Vectorized agent system with heading and policy-based behaviour.

    All arrays are of shape (max_agents,) or (max_agents, 2) and kept
    as float32 for performance. Only agents where ``active[i] == True``
    participate in any computation.

    Parameters
    ----------
    config:
        AgentConfig with all parameters.
    height, width:
        Grid dimensions (from SimConfig).
    """

    def __init__(self, config: AgentConfig, height: int, width: int) -> None:
        self.config = config
        self.height = height
        self.width = width

        N = config.max_agents
        rng = np.random.default_rng(config.seed)
        n = min(config.n_agents, N)

        # Positions: continuous (y, x) in [0, H) × [0, W)
        self.positions = np.zeros((N, 2), dtype=np.float32)
        self.positions[:n, 0] = rng.uniform(0, height, n).astype(np.float32)
        self.positions[:n, 1] = rng.uniform(0, width,  n).astype(np.float32)

        # Heading: angle in radians [-π, π]
        self.heading = np.zeros(N, dtype=np.float32)
        self.heading[:n] = rng.uniform(-math.pi, math.pi, n).astype(np.float32)

        # Velocity: (vy, vx) derived from heading × speed
        self.velocities = np.zeros((N, 2), dtype=np.float32)
        speeds = rng.uniform(config.min_speed, config.max_speed, n).astype(np.float32)
        self.velocities[:n, 0] = speeds * np.sin(self.heading[:n])
        self.velocities[:n, 1] = speeds * np.cos(self.heading[:n])

        # Per-agent energy
        self.energy = np.zeros(N, dtype=np.float32)
        self.energy[:n] = rng.uniform(0.4, 0.9, n).astype(np.float32)

        # Age in ticks
        self.age = np.zeros(N, dtype=np.int32)

        # Active mask
        self.active = np.zeros(N, dtype=bool)
        self.active[:n] = True

        # Internal RNG for stochastic behaviour
        self._rng = np.random.default_rng(config.seed + 1)

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    def _idx(self) -> np.ndarray:
        return np.where(self.active)[0]

    def _grid_coords(self, idx: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rows = (self.positions[idx, 0] % self.height).astype(np.int32)
        cols = (self.positions[idx, 1] % self.width).astype(np.int32)
        return rows, cols

    def _bilinear_sample(self, field: np.ndarray, idx: np.ndarray) -> np.ndarray:
        """Sample a 2-D field at continuous agent positions (bilinear, toroidal)."""
        H, W = self.height, self.width
        y = self.positions[idx, 0] % H
        x = self.positions[idx, 1] % W
        y0 = np.floor(y).astype(np.int32) % H
        y1 = (y0 + 1) % H
        x0 = np.floor(x).astype(np.int32) % W
        x1 = (x0 + 1) % W
        fy = (y - np.floor(y)).astype(np.float32)
        fx = (x - np.floor(x)).astype(np.float32)
        return (
            (1 - fy) * (1 - fx) * field[y0, x0]
            + (1 - fy) * fx      * field[y0, x1]
            +      fy  * (1 - fx) * field[y1, x0]
            +      fy  * fx       * field[y1, x1]
        ).astype(np.float32)

    def _spatial_hash(self, idx: np.ndarray, cell_size: float) -> np.ndarray:
        """Return (n_active, 2) integer bin coords for spatial hashing."""
        rows = np.floor(self.positions[idx, 0] / cell_size).astype(np.int32)
        cols = np.floor(self.positions[idx, 1] / cell_size).astype(np.int32)
        return np.stack([rows, cols], axis=1)

    # ──────────────────────────────────────────────────────────────
    # Field sampling
    # ──────────────────────────────────────────────────────────────

    def sample_field(self, field: np.ndarray, idx: Optional[np.ndarray] = None) -> np.ndarray:
        """Bilinear-interpolated field values at agent positions."""
        if idx is None:
            idx = self._idx()
        return self._bilinear_sample(field, idx)

    def sample_gradient(
        self, field: np.ndarray, idx: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Approximate gradient of *field* at agent positions (central differences)."""
        H, W = self.height, self.width
        grad_y = np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)
        grad_x = np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)
        gy = self._bilinear_sample(grad_y * 0.5, idx)
        gx = self._bilinear_sample(grad_x * 0.5, idx)
        return gy, gx

    # ──────────────────────────────────────────────────────────────
    # Field deposition
    # ──────────────────────────────────────────────────────────────

    def deposit_to_field(
        self,
        field: np.ndarray,
        idx: np.ndarray,
        amount: float,
    ) -> None:
        """Add *amount* to *field* at each agent's grid cell (in-place, clipped)."""
        rows, cols = self._grid_coords(idx)
        np.add.at(field, (rows, cols), amount)
        np.clip(field, 0.0, 1.0, out=field)

    # ──────────────────────────────────────────────────────────────
    # Neighbour search (spatial hashing)
    # ──────────────────────────────────────────────────────────────

    def _find_neighbours(
        self, idx: np.ndarray, radius: float
    ) -> list[np.ndarray]:
        """For each agent in *idx* return array of neighbour indices within *radius*.

        Uses a grid-bin approach: agents are binned into cells of size ~radius,
        then only the 3×3 neighbourhood of bins is checked.
        This is O(N · k) where k is the expected count in a 3×3 bin window.
        """
        H, W = self.height, self.width
        cell = max(radius, 1.0)
        n_bins_y = max(1, int(math.ceil(H / cell)))
        n_bins_x = max(1, int(math.ceil(W / cell)))

        bins_y = np.floor(self.positions[idx, 0] / cell).astype(np.int32) % n_bins_y
        bins_x = np.floor(self.positions[idx, 1] / cell).astype(np.int32) % n_bins_x

        # Build bin → list of local indices (into idx)
        bin_map: dict[tuple, list] = {}
        for li, (by, bx) in enumerate(zip(bins_y, bins_x)):
            key = (int(by), int(bx))
            bin_map.setdefault(key, []).append(li)

        neighbours: list[np.ndarray] = []
        positions_active = self.positions[idx]  # shape (n, 2)

        for li, (by, bx) in enumerate(zip(bins_y, bins_x)):
            cands: list[int] = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    key = ((int(by) + dy) % n_bins_y, (int(bx) + dx) % n_bins_x)
                    cands.extend(bin_map.get(key, []))

            if len(cands) == 0:
                neighbours.append(np.empty(0, dtype=np.int64))
                continue

            cands_arr = np.array(cands, dtype=np.int64)
            # Remove self
            cands_arr = cands_arr[cands_arr != li]
            if len(cands_arr) == 0:
                neighbours.append(np.empty(0, dtype=np.int64))
                continue

            # Toroidal distance
            dy_vec = positions_active[cands_arr, 0] - positions_active[li, 0]
            dx_vec = positions_active[cands_arr, 1] - positions_active[li, 1]
            dy_vec = dy_vec - H * np.round(dy_vec / H)
            dx_vec = dx_vec - W * np.round(dx_vec / W)
            dist = np.sqrt(dy_vec ** 2 + dx_vec ** 2)

            within = cands_arr[dist < radius]
            # Convert local indices back to global agent indices
            neighbours.append(idx[within] if len(within) > 0 else np.empty(0, dtype=np.int64))

        return neighbours

    # ──────────────────────────────────────────────────────────────
    # Boids policy
    # ──────────────────────────────────────────────────────────────

    def _apply_boids(self, idx: np.ndarray) -> None:
        """Reynolds (1987) Boids: separation + alignment + cohesion.

        Each rule produces a steering vector that is summed and used to
        update the agent's heading and velocity.
        """
        cfg = self.config
        H, W = self.height, self.width
        n = len(idx)
        if n < 2:
            return

        neighbours_all = self._find_neighbours(idx, cfg.perception_radius)
        pos = self.positions[idx]     # (n, 2)
        vel = self.velocities[idx]    # (n, 2)

        steer = np.zeros((n, 2), dtype=np.float32)

        for li in range(n):
            nb_global = neighbours_all[li]
            if len(nb_global) == 0:
                continue

            # Map global→local for vectorized access
            nb_pos = self.positions[nb_global]  # (k, 2)
            nb_vel = self.velocities[nb_global]  # (k, 2)

            # Toroidal displacement vectors
            dy = nb_pos[:, 0] - pos[li, 0]
            dx = nb_pos[:, 1] - pos[li, 1]
            dy -= H * np.round(dy / H)
            dx -= W * np.round(dx / W)
            dist = np.sqrt(dy ** 2 + dx ** 2) + 1e-6  # avoid div0

            # ── Separation ──────────────────────────────────────
            sep_mask = dist < cfg.separation_radius
            if sep_mask.any():
                sep_dy = dy[sep_mask] / dist[sep_mask]
                sep_dx = dx[sep_mask] / dist[sep_mask]
                steer[li, 0] -= cfg.separation_weight * sep_dy.mean()
                steer[li, 1] -= cfg.separation_weight * sep_dx.mean()

            # ── Alignment ───────────────────────────────────────
            mean_vel = nb_vel.mean(axis=0)
            speed = math.sqrt(float(mean_vel[0] ** 2 + mean_vel[1] ** 2)) + 1e-6
            steer[li, 0] += cfg.alignment_weight * (mean_vel[0] / speed)
            steer[li, 1] += cfg.alignment_weight * (mean_vel[1] / speed)

            # ── Cohesion ────────────────────────────────────────
            centre_dy = nb_pos[:, 0].mean() - pos[li, 0]
            centre_dx = nb_pos[:, 1].mean() - pos[li, 1]
            centre_dy -= H * round(float(centre_dy) / H)
            centre_dx -= W * round(float(centre_dx) / W)
            coh_dist = math.sqrt(float(centre_dy ** 2 + centre_dx ** 2)) + 1e-6
            steer[li, 0] += cfg.cohesion_weight * (centre_dy / coh_dist)
            steer[li, 1] += cfg.cohesion_weight * (centre_dx / coh_dist)

        # Apply steering to velocity
        self.velocities[idx] += steer * 0.1

    # ──────────────────────────────────────────────────────────────
    # Ant policy
    # ──────────────────────────────────────────────────────────────

    def _apply_ant(self, idx: np.ndarray, state: GridState) -> None:
        """Pheromone gradient following + random exploration.

        Agents steer toward memory field gradients (abstract pheromone)
        and deposit into memory + energy fields.
        """
        cfg = self.config
        if len(idx) == 0:
            return

        # Sample memory gradient (pheromone)
        gy, gx = self.sample_gradient(state.memory, idx)

        # Random heading noise
        noise = self._rng.uniform(-math.pi, math.pi, len(idx)).astype(np.float32)

        # Steering: weighted sum of pheromone gradient + noise
        steer_y = cfg.pheromone_weight * gy + cfg.noise_weight * np.sin(noise)
        steer_x = cfg.pheromone_weight * gx + cfg.noise_weight * np.cos(noise)

        self.velocities[idx, 0] += steer_y * 0.15
        self.velocities[idx, 1] += steer_x * 0.15

        # Deposit pheromone into memory field
        self.deposit_to_field(state.memory, idx, cfg.deposit_rate * 0.1)

        # Deposit energy trace
        if cfg.energy_deposit > 0:
            self.deposit_to_field(state.energy, idx, cfg.energy_deposit * 0.05)

    # ──────────────────────────────────────────────────────────────
    # Field influence on agents
    # ──────────────────────────────────────────────────────────────

    def _apply_field_forces(self, idx: np.ndarray, state: GridState) -> None:
        """Flow drag + energy gradient attraction from the field."""
        cfg = self.config
        if len(idx) == 0:
            return

        # Flow drag: field flow vector carries agents along
        flow_y = self._bilinear_sample(state.flow_y, idx)
        flow_x = self._bilinear_sample(state.flow_x, idx)
        self.velocities[idx, 0] += cfg.field_flow_drag * flow_y
        self.velocities[idx, 1] += cfg.field_flow_drag * flow_x

    # ──────────────────────────────────────────────────────────────
    # Speed clamping + heading sync
    # ──────────────────────────────────────────────────────────────

    def _clamp_speed(self, idx: np.ndarray) -> None:
        cfg = self.config
        speeds = np.sqrt(
            self.velocities[idx, 0] ** 2 + self.velocities[idx, 1] ** 2
        ) + 1e-8
        # Clamp to [min_speed, max_speed]
        factor = np.clip(speeds, cfg.min_speed, cfg.max_speed) / speeds
        self.velocities[idx, 0] *= factor
        self.velocities[idx, 1] *= factor
        # Sync heading with velocity direction
        self.heading[idx] = np.arctan2(
            self.velocities[idx, 0], self.velocities[idx, 1]
        ).astype(np.float32)

    # ──────────────────────────────────────────────────────────────
    # Integration
    # ──────────────────────────────────────────────────────────────

    def _integrate(self, idx: np.ndarray) -> None:
        """Euler integration: position += velocity; wrap toroidally."""
        self.positions[idx] += self.velocities[idx]
        self.positions[idx, 0] %= self.height
        self.positions[idx, 1] %= self.width
        self.age[idx] += 1

    # ──────────────────────────────────────────────────────────────
    # Agent → Field deposition (general)
    # ──────────────────────────────────────────────────────────────

    def _deposit_general(self, idx: np.ndarray, state: GridState) -> None:
        """All agents deposit energy into the field."""
        cfg = self.config
        if cfg.energy_deposit > 0:
            self.deposit_to_field(state.energy, idx, cfg.energy_deposit)

    # ──────────────────────────────────────────────────────────────
    # Main step function
    # ──────────────────────────────────────────────────────────────

    def step(self, state: GridState) -> None:
        """Advance all active agents by one tick.

        Order:
            1. Field forces (flow drag)
            2. Policy (boids / ant)
            3. Velocity damping
            4. Speed clamping + heading sync
            5. Euler integration
            6. Agent → field deposition
        """
        idx = self._idx()
        if len(idx) == 0:
            return

        # 1. Field forces
        self._apply_field_forces(idx, state)

        # 2. Policy
        if self.config.policy == "boids":
            self._apply_boids(idx)
        elif self.config.policy == "ant":
            self._apply_ant(idx, state)

        # 3. Damping
        self.velocities[idx] *= self.config.velocity_damping

        # 4. Speed clamp + heading sync
        self._clamp_speed(idx)

        # 5. Integrate
        self._integrate(idx)

        # 6. Deposit
        self._deposit_general(idx, state)

    # ──────────────────────────────────────────────────────────────
    # Statistics
    # ──────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return a dict of summary statistics for the active agents."""
        idx = self._idx()
        n = len(idx)
        if n == 0:
            return {
                "n_active": 0,
                "mean_speed": 0.0,
                "mean_heading": 0.0,
                "heading_std": 0.0,
                "velocity_coherence": 0.0,
                "mean_age": 0.0,
            }
        speeds = np.sqrt(
            self.velocities[idx, 0] ** 2 + self.velocities[idx, 1] ** 2
        )
        # Velocity coherence: length of mean unit velocity vector ∈ [0, 1]
        unit_vy = self.velocities[idx, 0] / (speeds + 1e-8)
        unit_vx = self.velocities[idx, 1] / (speeds + 1e-8)
        coherence = float(np.sqrt(unit_vy.mean() ** 2 + unit_vx.mean() ** 2))
        return {
            "n_active": n,
            "mean_speed": float(speeds.mean()),
            "mean_heading": float(self.heading[idx].mean()),
            "heading_std": float(self.heading[idx].std()),
            "velocity_coherence": round(coherence, 4),
            "mean_age": float(self.age[idx].mean()),
        }


# ──────────────────────────────────────────────────────────────────
# Module-level step function (mirrors step_particles pattern)
# ──────────────────────────────────────────────────────────────────

def step_agents(agents: AgentSystem, state: GridState) -> None:
    """Advance *agents* by one tick given current *state*.

    This is the public entry point, matching the ``step_particles`` API.
    """
    agents.step(state)
