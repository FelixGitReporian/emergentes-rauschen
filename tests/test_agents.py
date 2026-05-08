"""
tests/test_agents.py – Tests for the Real Agent Layer (Epic 11).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from emergent_noise.core.agents import AgentConfig, AgentSystem, step_agents
from emergent_noise.core.state import GridState, SimConfig


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _state(H: int = 32, W: int = 32, seed: int = 0) -> GridState:
    return GridState.initialize(SimConfig(height=H, width=W, seed=seed))


def _boids(n: int = 20, H: int = 32, W: int = 32, seed: int = 0) -> AgentSystem:
    cfg = AgentConfig(n_agents=n, max_agents=n * 2, policy="boids", seed=seed)
    return AgentSystem(cfg, H, W)


def _ants(n: int = 20, H: int = 32, W: int = 32, seed: int = 0) -> AgentSystem:
    cfg = AgentConfig(n_agents=n, max_agents=n * 2, policy="ant", seed=seed)
    return AgentSystem(cfg, H, W)


# ──────────────────────────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────────────────────────

def test_init_active_count() -> None:
    agents = _boids(n=30)
    assert agents.active.sum() == 30


def test_init_positions_in_bounds() -> None:
    agents = _boids(n=50, H=64, W=64)
    idx = agents._idx()
    assert agents.positions[idx, 0].min() >= 0.0
    assert agents.positions[idx, 0].max() < 64.0
    assert agents.positions[idx, 1].min() >= 0.0
    assert agents.positions[idx, 1].max() < 64.0


def test_init_headings_in_range() -> None:
    agents = _boids(n=50)
    idx = agents._idx()
    assert agents.heading[idx].min() >= -math.pi - 0.01
    assert agents.heading[idx].max() <= math.pi + 0.01


def test_init_speeds_in_range() -> None:
    agents = _boids(n=50)
    idx = agents._idx()
    speeds = np.sqrt(agents.velocities[idx, 0] ** 2 + agents.velocities[idx, 1] ** 2)
    assert speeds.min() >= agents.config.min_speed - 0.01
    assert speeds.max() <= agents.config.max_speed + 0.01


def test_init_deterministic() -> None:
    a1 = _boids(n=20, seed=7)
    a2 = _boids(n=20, seed=7)
    np.testing.assert_array_equal(a1.positions, a2.positions)
    np.testing.assert_array_equal(a1.heading, a2.heading)


def test_inactive_slots_zero() -> None:
    agents = _boids(n=10)
    N = agents.config.max_agents
    # Inactive slots should be exactly zeroed
    inactive = np.where(~agents.active)[0]
    assert np.all(agents.positions[inactive] == 0.0)


# ──────────────────────────────────────────────────────────────────
# Single step — sanity
# ──────────────────────────────────────────────────────────────────

def test_step_changes_positions() -> None:
    agents = _boids(n=20)
    state = _state()
    before = agents.positions[agents._idx()].copy()
    agents.step(state)
    after = agents.positions[agents._idx()]
    assert not np.allclose(before, after), "Positions unchanged after step"


def test_step_positions_stay_in_bounds() -> None:
    agents = _boids(n=50, H=64, W=64)
    state = _state(H=64, W=64)
    for _ in range(20):
        agents.step(state)
    idx = agents._idx()
    assert agents.positions[idx, 0].min() >= 0.0
    assert agents.positions[idx, 0].max() < 64.0
    assert agents.positions[idx, 1].min() >= 0.0
    assert agents.positions[idx, 1].max() < 64.0


def test_step_speed_clamped() -> None:
    agents = _boids(n=30)
    state = _state()
    for _ in range(10):
        agents.step(state)
    idx = agents._idx()
    speeds = np.sqrt(agents.velocities[idx, 0] ** 2 + agents.velocities[idx, 1] ** 2)
    assert speeds.max() <= agents.config.max_speed + 0.05


def test_step_heading_synced_with_velocity() -> None:
    agents = _boids(n=20)
    state = _state()
    agents.step(state)
    idx = agents._idx()
    expected = np.arctan2(agents.velocities[idx, 0], agents.velocities[idx, 1])
    np.testing.assert_allclose(agents.heading[idx], expected, atol=1e-5)


def test_age_increments() -> None:
    agents = _boids(n=10)
    state = _state()
    agents.step(state)
    assert agents.age[agents._idx()].min() == 1
    agents.step(state)
    assert agents.age[agents._idx()].min() == 2


# ──────────────────────────────────────────────────────────────────
# step_agents public API
# ──────────────────────────────────────────────────────────────────

def test_step_agents_function() -> None:
    agents = _boids(n=15)
    state = _state()
    before = agents.positions[agents._idx()].copy()
    step_agents(agents, state)
    after = agents.positions[agents._idx()]
    assert not np.allclose(before, after)


# ──────────────────────────────────────────────────────────────────
# Boids policy
# ──────────────────────────────────────────────────────────────────

def test_boids_many_steps_stable() -> None:
    """100 Boids steps should not produce NaN or inf."""
    agents = _boids(n=40, H=64, W=64, seed=3)
    state = _state(H=64, W=64, seed=3)
    for _ in range(100):
        step_agents(agents, state)
    idx = agents._idx()
    assert np.isfinite(agents.positions[idx]).all()
    assert np.isfinite(agents.velocities[idx]).all()
    assert np.isfinite(agents.heading[idx]).all()


def test_boids_velocity_coherence_increases_with_many_agents() -> None:
    """With many agents close together, coherence should be > 0."""
    # Pack 80 agents in a small 16x16 area — they will interact
    cfg = AgentConfig(
        n_agents=80, max_agents=160, policy="boids",
        perception_radius=5.0, seed=42,
    )
    agents = AgentSystem(cfg, 16, 16)
    state = _state(H=16, W=16)
    for _ in range(50):
        step_agents(agents, state)
    s = agents.stats()
    assert s["velocity_coherence"] > 0.0


def test_boids_single_agent_no_crash() -> None:
    """A single Boids agent has no neighbours and should step without error."""
    agents = _boids(n=1, H=32, W=32)
    state = _state()
    for _ in range(10):
        step_agents(agents, state)
    assert agents.active.sum() == 1


# ──────────────────────────────────────────────────────────────────
# Ant policy
# ──────────────────────────────────────────────────────────────────

def test_ant_deposits_to_memory_field() -> None:
    agents = _ants(n=30, H=64, W=64)
    state = _state(H=64, W=64)
    memory_before = state.memory.copy()
    for _ in range(10):
        step_agents(agents, state)
    # Memory should have increased somewhere
    assert state.memory.max() > memory_before.max() or state.memory.sum() > memory_before.sum()


def test_ant_memory_stays_in_bounds() -> None:
    agents = _ants(n=50, H=64, W=64)
    state = _state(H=64, W=64)
    for _ in range(50):
        step_agents(agents, state)
    assert state.memory.min() >= 0.0
    assert state.memory.max() <= 1.0


def test_ant_many_steps_stable() -> None:
    """50 ant steps should not produce NaN."""
    agents = _ants(n=40, H=64, W=64, seed=5)
    state = _state(H=64, W=64, seed=5)
    for _ in range(50):
        step_agents(agents, state)
    idx = agents._idx()
    assert np.isfinite(agents.positions[idx]).all()
    assert np.isfinite(agents.velocities[idx]).all()


# ──────────────────────────────────────────────────────────────────
# Field sampling
# ──────────────────────────────────────────────────────────────────

def test_sample_field_shape() -> None:
    agents = _boids(n=20)
    state = _state()
    vals = agents.sample_field(state.energy)
    assert vals.shape == (20,)


def test_sample_field_in_bounds() -> None:
    agents = _boids(n=20)
    state = _state()
    vals = agents.sample_field(state.energy)
    assert vals.min() >= 0.0
    assert vals.max() <= 1.0 + 1e-5


def test_sample_gradient_shape() -> None:
    agents = _boids(n=20)
    state = _state()
    idx = agents._idx()
    gy, gx = agents.sample_gradient(state.energy, idx)
    assert gy.shape == (20,)
    assert gx.shape == (20,)


# ──────────────────────────────────────────────────────────────────
# Field deposition
# ──────────────────────────────────────────────────────────────────

def test_deposit_increases_field() -> None:
    agents = _boids(n=20)
    state = _state()
    before = state.memory.sum()
    idx = agents._idx()
    agents.deposit_to_field(state.memory, idx, 0.1)
    assert state.memory.sum() > before


def test_deposit_stays_in_bounds() -> None:
    agents = _boids(n=50, H=64, W=64)
    state = _state(H=64, W=64)
    idx = agents._idx()
    for _ in range(50):
        agents.deposit_to_field(state.memory, idx, 0.5)
    assert state.memory.max() <= 1.0


# ──────────────────────────────────────────────────────────────────
# Stats
# ──────────────────────────────────────────────────────────────────

def test_stats_keys() -> None:
    agents = _boids(n=20)
    s = agents.stats()
    for k in ("n_active", "mean_speed", "mean_heading", "heading_std",
              "velocity_coherence", "mean_age"):
        assert k in s


def test_stats_n_active_correct() -> None:
    agents = _boids(n=25)
    assert agents.stats()["n_active"] == 25


def test_stats_empty_agents() -> None:
    cfg = AgentConfig(n_agents=0, max_agents=10, policy="boids")
    agents = AgentSystem(cfg, 32, 32)
    s = agents.stats()
    assert s["n_active"] == 0
    assert s["velocity_coherence"] == 0.0


def test_stats_coherence_in_range() -> None:
    agents = _boids(n=40, H=64, W=64)
    state = _state(H=64, W=64)
    for _ in range(30):
        step_agents(agents, state)
    s = agents.stats()
    assert 0.0 <= s["velocity_coherence"] <= 1.0


# ──────────────────────────────────────────────────────────────────
# Neighbour search
# ──────────────────────────────────────────────────────────────────

def test_neighbour_search_self_excluded() -> None:
    agents = _boids(n=20)
    idx = agents._idx()
    neighbours = agents._find_neighbours(idx, radius=10.0)
    for li, nb in enumerate(neighbours):
        assert idx[li] not in nb, f"Agent {idx[li]} found itself in neighbours"


def test_neighbour_search_within_radius() -> None:
    """All returned neighbours should be within the perception radius."""
    agents = _boids(n=30, H=64, W=64, seed=0)
    idx = agents._idx()
    radius = 8.0
    H, W = 64, 64
    neighbours = agents._find_neighbours(idx, radius=radius)
    for li, nb in enumerate(neighbours):
        if len(nb) == 0:
            continue
        dy = agents.positions[nb, 0] - agents.positions[idx[li], 0]
        dx = agents.positions[nb, 1] - agents.positions[idx[li], 1]
        dy -= H * np.round(dy / H)
        dx -= W * np.round(dx / W)
        dist = np.sqrt(dy ** 2 + dx ** 2)
        assert dist.max() < radius + 0.01, "Neighbour outside radius returned"


# ──────────────────────────────────────────────────────────────────
# AgentConfig defaults
# ──────────────────────────────────────────────────────────────────

def test_agent_config_defaults() -> None:
    cfg = AgentConfig()
    assert cfg.policy == "boids"
    assert cfg.max_speed > cfg.min_speed
    assert cfg.separation_radius < cfg.perception_radius
