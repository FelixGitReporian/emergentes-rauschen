"""
core/initial_conditions.py – Initial Condition abstraction (Epic 10).

An InitialCondition post-processes a freshly created GridState by injecting
structured patterns into one or more fields *before* the first tick runs.
This allows presets to reliably trigger specific phenomena (branching growth,
excitation waves, spiral seeds, …) without needing custom SimConfig hacks.

Design principles:
- Minimal invasion: InitialCondition.apply() mutates a GridState in-place.
- Composable: CompoundInitialCondition chains multiple conditions.
- Deterministic: conditions that use randomness accept an rng argument derived
  from config.seed so results are fully reproducible.
- All injected values are clipped to [0, 1].

Available conditions:
    UniformBaseline         – no structural override (default / identity)
    CenteredSeed            – high-energy spot in the centre
    BottomSeed              – horizontal band of energy at the bottom edge
    TopDownEnergyGradient   – smooth energy gradient from top (high) to bottom
    BottomUpEnergyGradient  – smooth energy gradient from bottom (high) to top
    RadialBurst             – ring of high energy at a given radius
    LineSeed                – horizontal or vertical line of energy
    RandomClusteredSeed     – N random high-energy circular blobs
    MovingDisturbance       – stationary snapshot of a sinusoidal disturbance wave
    CompoundInitialCondition– ordered composition of multiple conditions

Scientific caution:
    Initial conditions shape which attractors the system falls into.
    They do not guarantee a specific emergent pattern — they only make
    certain patterns more likely by breaking spatial symmetry in a targeted way.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from emergent_noise.core.state import GridState


# ──────────────────────────────────────────────────────────────────
# Base class
# ──────────────────────────────────────────────────────────────────

class InitialCondition(ABC):
    """Abstract base for all initial conditions.

    Subclasses implement ``apply(state)`` which mutates the state in-place
    and returns it for chaining.
    """

    @abstractmethod
    def apply(self, state: GridState) -> GridState:
        """Apply this condition to *state* and return it."""

    def __add__(self, other: "InitialCondition") -> "CompoundInitialCondition":
        """Compose two conditions with ``+`` operator."""
        return CompoundInitialCondition([self, other])

    @property
    def name(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        return f"{self.name}()"


# ──────────────────────────────────────────────────────────────────
# Identity
# ──────────────────────────────────────────────────────────────────

class UniformBaseline(InitialCondition):
    """No structural override — leaves the randomly initialised state as-is.

    Useful as a default / explicit no-op when a preset does not need a
    special starting condition.
    """

    def apply(self, state: GridState) -> GridState:
        return state


# ──────────────────────────────────────────────────────────────────
# Point / spot seeds
# ──────────────────────────────────────────────────────────────────

@dataclass
class CenteredSeed(InitialCondition):
    """Inject a high-energy circular spot at the centre of the grid.

    Useful for: radial growth experiments, autopoiesis, excitable media
    where a single nucleation point is needed.

    Parameters
    ----------
    radius:
        Radius of the seed spot in grid cells (default 3).
    energy_value:
        Energy injected inside the spot (default 0.9).
    also_information:
        If True, also set information field to ``energy_value`` inside the spot.
    """

    radius: float = 3.0
    energy_value: float = 0.9
    also_information: bool = True

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        cy, cx = H // 2, W // 2
        ys, xs = np.ogrid[:H, :W]
        mask = (ys - cy) ** 2 + (xs - cx) ** 2 <= self.radius ** 2
        state.energy[mask] = np.clip(self.energy_value, 0.0, 1.0)
        if self.also_information:
            state.information[mask] = np.clip(self.energy_value, 0.0, 1.0)
        return state


@dataclass
class PointSeed(InitialCondition):
    """Inject a high-energy spot at a given (row, col) position.

    Parameters
    ----------
    row, col:
        Centre of the seed. Negative values wrap (like Python indexing).
    radius:
        Radius in grid cells.
    energy_value:
        Energy value injected.
    field:
        Which GridState field to inject into (default "energy").
    """

    row: int = 0
    col: int = 0
    radius: float = 3.0
    energy_value: float = 0.9
    target_field: str = "energy"

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        r = self.row % H
        c = self.col % W
        ys, xs = np.ogrid[:H, :W]
        mask = (ys - r) ** 2 + (xs - c) ** 2 <= self.radius ** 2
        arr = getattr(state, self.target_field)
        arr[mask] = np.clip(self.energy_value, 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Edge / band seeds
# ──────────────────────────────────────────────────────────────────

@dataclass
class BottomSeed(InitialCondition):
    """Inject a band of high energy at the bottom edge.

    Simulates a root zone, nutrient source or seeding line.
    Useful for: tree growth (growth starts from bottom), river networks.

    Parameters
    ----------
    band_height:
        Number of rows from the bottom to fill (default 4).
    energy_value:
        Energy value for the seed band.
    also_matter:
        If True, also set matter (substrate / biomass) in the band.
    """

    band_height: int = 4
    energy_value: float = 0.85
    also_matter: bool = True

    def apply(self, state: GridState) -> GridState:
        H = state.energy.shape[0]
        h = min(self.band_height, H)
        state.energy[-h:, :] = np.clip(self.energy_value, 0.0, 1.0)
        if self.also_matter:
            state.matter[-h:, :] = np.clip(self.energy_value * 0.8, 0.0, 1.0)
        return state


@dataclass
class TopSeed(InitialCondition):
    """Inject a band of high energy at the top edge.

    Simulates a light source or atmospheric input from above.

    Parameters
    ----------
    band_height:
        Number of rows from the top to fill (default 4).
    energy_value:
        Energy value for the seed band.
    """

    band_height: int = 4
    energy_value: float = 0.85

    def apply(self, state: GridState) -> GridState:
        H = state.energy.shape[0]
        h = min(self.band_height, H)
        state.energy[:h, :] = np.clip(self.energy_value, 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Gradient seeds
# ──────────────────────────────────────────────────────────────────

@dataclass
class TopDownEnergyGradient(InitialCondition):
    """Smooth linear energy gradient from top (high) to bottom (low).

    Simulates a light or temperature gradient — energy decreases with depth.
    Useful for: top-down morphogenesis, light-driven growth.

    Parameters
    ----------
    top_value:
        Energy at the top row (default 0.8).
    bottom_value:
        Energy at the bottom row (default 0.1).
    """

    top_value: float = 0.8
    bottom_value: float = 0.1

    def apply(self, state: GridState) -> GridState:
        H = state.energy.shape[0]
        gradient = np.linspace(self.top_value, self.bottom_value, H, dtype=np.float32)
        state.energy[:] = np.clip(gradient[:, np.newaxis], 0.0, 1.0)
        return state


@dataclass
class BottomUpEnergyGradient(InitialCondition):
    """Smooth linear energy gradient from bottom (high) to top (low).

    Simulates a nutrient or heat source from below.
    Useful for: upward growth, convection-like dynamics.

    Parameters
    ----------
    bottom_value:
        Energy at the bottom row (default 0.8).
    top_value:
        Energy at the top row (default 0.05).
    """

    bottom_value: float = 0.8
    top_value: float = 0.05

    def apply(self, state: GridState) -> GridState:
        H = state.energy.shape[0]
        gradient = np.linspace(self.top_value, self.bottom_value, H, dtype=np.float32)
        state.energy[:] = np.clip(gradient[:, np.newaxis], 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Radial / ring seeds
# ──────────────────────────────────────────────────────────────────

@dataclass
class RadialBurst(InitialCondition):
    """Inject a ring of high energy at a given radius from the centre.

    Useful for: reliably triggering spiral waves in excitable media,
    ring-like wavefronts in reaction-diffusion systems.

    Parameters
    ----------
    radius:
        Radius of the ring in grid cells (default H/4).
    ring_width:
        Thickness of the ring (default 2).
    energy_value:
        Peak energy in the ring.
    center:
        (row, col) centre; if None, uses grid centre.
    """

    radius: Optional[float] = None
    ring_width: float = 2.0
    energy_value: float = 0.95
    center: Optional[Tuple[int, int]] = None

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        cy, cx = self.center if self.center is not None else (H // 2, W // 2)
        r = self.radius if self.radius is not None else H / 4.0
        ys, xs = np.ogrid[:H, :W]
        dist = np.sqrt((ys - cy) ** 2 + (xs - cx) ** 2).astype(np.float32)
        mask = np.abs(dist - r) <= self.ring_width / 2.0
        state.energy[mask] = np.clip(self.energy_value, 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Line seeds
# ──────────────────────────────────────────────────────────────────

@dataclass
class LineSeed(InitialCondition):
    """Inject a horizontal or vertical line of high energy.

    Useful for: stripe pattern seeding, reaction-diffusion stripe selection,
    directional trace experiments.

    Parameters
    ----------
    orientation:
        "horizontal" or "vertical".
    position:
        Row (horizontal) or column (vertical) index. Negative values wrap.
    width:
        Thickness of the line in cells (default 2).
    energy_value:
        Energy value in the line.
    target_field:
        Which field to inject into (default "energy").
    """

    orientation: str = "horizontal"
    position: int = 0
    width: int = 2
    energy_value: float = 0.9
    target_field: str = "energy"

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        arr = getattr(state, self.target_field)
        half = self.width // 2
        if self.orientation == "horizontal":
            pos = self.position % H
            r0, r1 = max(0, pos - half), min(H, pos + half + 1)
            arr[r0:r1, :] = np.clip(self.energy_value, 0.0, 1.0)
        else:
            pos = self.position % W
            c0, c1 = max(0, pos - half), min(W, pos + half + 1)
            arr[:, c0:c1] = np.clip(self.energy_value, 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Random clustered seed
# ──────────────────────────────────────────────────────────────────

@dataclass
class RandomClusteredSeed(InitialCondition):
    """Scatter N random high-energy circular blobs across the grid.

    Useful for: patch dynamics (multiple resource patches), multi-centre
    growth experiments, heterogeneous landscape seeding.

    Parameters
    ----------
    n_clusters:
        Number of blobs to scatter.
    cluster_radius:
        Radius of each blob in grid cells.
    energy_value:
        Peak energy in each blob.
    seed:
        Random seed for blob positions (independent of SimConfig seed).
    target_field:
        Which field to inject into.
    """

    n_clusters: int = 8
    cluster_radius: float = 4.0
    energy_value: float = 0.85
    seed: int = 0
    target_field: str = "energy"

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        rng = np.random.default_rng(self.seed)
        arr = getattr(state, self.target_field)
        ys, xs = np.ogrid[:H, :W]
        for _ in range(self.n_clusters):
            cy = int(rng.integers(0, H))
            cx = int(rng.integers(0, W))
            mask = (ys - cy) ** 2 + (xs - cx) ** 2 <= self.cluster_radius ** 2
            arr[mask] = np.clip(self.energy_value, 0.0, 1.0)
        return state


# ──────────────────────────────────────────────────────────────────
# Sinusoidal disturbance
# ──────────────────────────────────────────────────────────────────

@dataclass
class SinusoidalDisturbance(InitialCondition):
    """Overlay a sinusoidal wave pattern onto a field.

    Useful for: seeding stripe-like initial conditions in reaction-diffusion
    experiments, breaking symmetry with a known wavelength.

    Parameters
    ----------
    wavelength:
        Wavelength in grid cells.
    amplitude:
        Peak amplitude added to the existing field.
    axis:
        0 = horizontal stripes (varies with row), 1 = vertical (varies with col).
    target_field:
        Which field to modulate.
    """

    wavelength: float = 16.0
    amplitude: float = 0.2
    axis: int = 0
    target_field: str = "energy"

    def apply(self, state: GridState) -> GridState:
        H, W = state.energy.shape
        arr = getattr(state, self.target_field)
        if self.axis == 0:
            coords = np.arange(H, dtype=np.float32)[:, np.newaxis]
        else:
            coords = np.arange(W, dtype=np.float32)[np.newaxis, :]
        wave = (self.amplitude * np.sin(2.0 * math.pi * coords / self.wavelength)).astype(np.float32)
        np.clip(arr + wave, 0.0, 1.0, out=arr)
        return state


# ──────────────────────────────────────────────────────────────────
# Composition
# ──────────────────────────────────────────────────────────────────

@dataclass
class CompoundInitialCondition(InitialCondition):
    """Apply a sequence of InitialConditions in order.

    Can be built manually or via the ``+`` operator::

        cond = BottomUpEnergyGradient() + BottomSeed(band_height=3)
    """

    conditions: List[InitialCondition] = field(default_factory=list)

    def apply(self, state: GridState) -> GridState:
        for cond in self.conditions:
            cond.apply(state)
        return state

    def __repr__(self) -> str:
        parts = " + ".join(repr(c) for c in self.conditions)
        return f"CompoundInitialCondition([{parts}])"


# ──────────────────────────────────────────────────────────────────
# Convenience registry
# ──────────────────────────────────────────────────────────────────

#: Named prebuilt conditions for use in presets and the dashboard selector.
INITIAL_CONDITIONS: dict[str, InitialCondition] = {
    "none":                   UniformBaseline(),
    "centered_seed":          CenteredSeed(),
    "bottom_seed":            BottomSeed(),
    "top_seed":               TopSeed(),
    "top_down_gradient":      TopDownEnergyGradient(),
    "bottom_up_gradient":     BottomUpEnergyGradient(),
    "radial_burst":           RadialBurst(),
    "horizontal_line":        LineSeed(orientation="horizontal", position=0),
    "vertical_line":          LineSeed(orientation="vertical", position=0),
    "random_clusters":        RandomClusteredSeed(),
    "sinusoidal_horizontal":  SinusoidalDisturbance(axis=0),
    "sinusoidal_vertical":    SinusoidalDisturbance(axis=1),
}


def get_initial_condition(name: str) -> InitialCondition:
    """Return a named initial condition. Raises KeyError with helpful message."""
    if name not in INITIAL_CONDITIONS:
        available = ", ".join(sorted(INITIAL_CONDITIONS))
        raise KeyError(f"Unknown initial condition '{name}'. Available: {available}")
    return INITIAL_CONDITIONS[name]


def list_initial_condition_names() -> list[str]:
    """Return sorted list of available named initial condition keys."""
    return sorted(INITIAL_CONDITIONS)
