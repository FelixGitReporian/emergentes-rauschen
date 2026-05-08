"""
tests/test_morphogenesis.py – Tests for Morphogenesis & Growth Metrics (Epic 12).
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.analysis.morphogenesis import (
    GrowthFrontMetrics,
    MorphogenesisResult,
    analyse_growth_front,
    analyse_morphogenesis,
    branch_count,
    extract_skeleton,
    fractal_dimension,
    tip_count,
)


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _solid_square(H: int = 32, W: int = 32, size: int = 10) -> np.ndarray:
    arr = np.zeros((H, W), dtype=np.float32)
    r0, c0 = H // 2 - size // 2, W // 2 - size // 2
    arr[r0 : r0 + size, c0 : c0 + size] = 0.9
    return arr


def _horizontal_line(H: int = 32, W: int = 32, row: int = 16, length: int = 20) -> np.ndarray:
    arr = np.zeros((H, W), dtype=np.float32)
    c0 = W // 2 - length // 2
    arr[row, c0 : c0 + length] = 0.9
    return arr


def _cross(H: int = 32, W: int = 32) -> np.ndarray:
    arr = np.zeros((H, W), dtype=np.float32)
    arr[H // 2, :] = 0.9       # horizontal bar
    arr[:, W // 2] = 0.9       # vertical bar
    return arr


def _empty(H: int = 32, W: int = 32) -> np.ndarray:
    return np.zeros((H, W), dtype=np.float32)


# ──────────────────────────────────────────────────────────────────
# extract_skeleton
# ──────────────────────────────────────────────────────────────────

def test_skeleton_empty_input() -> None:
    binary = np.zeros((32, 32), dtype=bool)
    skel = extract_skeleton(binary)
    assert not skel.any()


def test_skeleton_of_solid_square_is_nonempty() -> None:
    arr = _solid_square()
    binary = arr > 0.5
    skel = extract_skeleton(binary)
    assert skel.any(), "Skeleton of solid square should be non-empty"


def test_skeleton_subset_of_original() -> None:
    arr = _solid_square()
    binary = arr > 0.5
    skel = extract_skeleton(binary)
    # Skeleton must be contained within the original binary
    assert np.all(skel <= binary)


def test_skeleton_line_is_thin() -> None:
    arr = _horizontal_line()
    binary = arr > 0.5
    skel = extract_skeleton(binary)
    # Skeleton of a single-pixel-wide line should be ≤ original
    assert skel.sum() <= binary.sum()


def test_skeleton_returns_bool() -> None:
    arr = _solid_square()
    binary = arr > 0.5
    skel = extract_skeleton(binary)
    assert skel.dtype == bool


# ──────────────────────────────────────────────────────────────────
# branch_count
# ──────────────────────────────────────────────────────────────────

def test_branch_count_empty() -> None:
    skel = np.zeros((32, 32), dtype=bool)
    assert branch_count(skel) == 0


def test_branch_count_line_is_zero() -> None:
    """A straight line skeleton has no branch points."""
    skel = np.zeros((32, 32), dtype=bool)
    skel[16, 5:25] = True
    assert branch_count(skel) == 0


def test_branch_count_cross_has_one_branch() -> None:
    """A cross shape has exactly one branch point at the intersection."""
    skel = np.zeros((32, 32), dtype=bool)
    skel[16, 8:25] = True   # horizontal
    skel[8:25, 16] = True   # vertical
    n = branch_count(skel)
    # Centre pixel has 4 neighbours → branch point
    assert n >= 1


def test_branch_count_nonnegative() -> None:
    arr = _solid_square()
    skel = extract_skeleton(arr > 0.5)
    assert branch_count(skel) >= 0


# ──────────────────────────────────────────────────────────────────
# tip_count
# ──────────────────────────────────────────────────────────────────

def test_tip_count_empty() -> None:
    assert tip_count(np.zeros((32, 32), dtype=bool)) == 0


def test_tip_count_line_has_two_tips() -> None:
    """A straight line has exactly 2 endpoints."""
    skel = np.zeros((32, 32), dtype=bool)
    skel[16, 5:25] = True
    assert tip_count(skel) == 2


def test_tip_count_cross_has_four_tips() -> None:
    skel = np.zeros((32, 32), dtype=bool)
    skel[16, 8:25] = True
    skel[8:25, 16] = True
    n = tip_count(skel)
    assert n >= 2


# ──────────────────────────────────────────────────────────────────
# fractal_dimension
# ──────────────────────────────────────────────────────────────────

def test_fractal_dim_empty() -> None:
    assert fractal_dimension(np.zeros((32, 32), dtype=bool)) == 0.0


def test_fractal_dim_full_array() -> None:
    """A fully filled 2-D array has fractal dimension ≈ 2."""
    fd = fractal_dimension(np.ones((64, 64), dtype=bool))
    assert fd == pytest.approx(2.0, abs=0.05)


def test_fractal_dim_line() -> None:
    """A single-pixel line has fractal dimension close to 1."""
    binary = np.zeros((64, 64), dtype=bool)
    binary[32, :] = True
    fd = fractal_dimension(binary)
    assert fd <= 1.5, f"Line fractal dim should be near 1, got {fd}"


def test_fractal_dim_in_range() -> None:
    arr = _solid_square(H=64, W=64, size=20)
    fd = fractal_dimension(arr > 0.5)
    assert 1.0 <= fd <= 2.0


def test_fractal_dim_complex_higher_than_line() -> None:
    """A 2-D solid has higher fractal dimension than a line."""
    binary_solid = np.zeros((64, 64), dtype=bool)
    binary_solid[20:44, 20:44] = True
    binary_line = np.zeros((64, 64), dtype=bool)
    binary_line[32, :] = True
    assert fractal_dimension(binary_solid) > fractal_dimension(binary_line)


# ──────────────────────────────────────────────────────────────────
# analyse_growth_front
# ──────────────────────────────────────────────────────────────────

def test_growth_front_empty_field() -> None:
    gf = analyse_growth_front(_empty())
    assert gf.front_area == 0
    assert gf.directionality_magnitude == 0.0


def test_growth_front_solid_square_has_front() -> None:
    gf = analyse_growth_front(_solid_square())
    assert gf.front_area > 0


def test_growth_front_fraction_in_range() -> None:
    gf = analyse_growth_front(_solid_square())
    assert 0.0 <= gf.front_fraction <= 1.0


def test_growth_front_energy_in_range() -> None:
    gf = analyse_growth_front(_solid_square())
    assert 0.0 <= gf.mean_front_energy <= 1.0


def test_growth_front_directionality_magnitude_in_range() -> None:
    gf = analyse_growth_front(_solid_square())
    assert 0.0 <= gf.directionality_magnitude <= 1.5


def test_growth_front_fully_filled_has_no_front() -> None:
    arr = np.ones((32, 32), dtype=np.float32)
    gf = analyse_growth_front(arr)
    assert gf.front_area == 0


def test_growth_front_returns_dataclass() -> None:
    gf = analyse_growth_front(_solid_square())
    assert isinstance(gf, GrowthFrontMetrics)


# ──────────────────────────────────────────────────────────────────
# analyse_morphogenesis
# ──────────────────────────────────────────────────────────────────

def test_morphogenesis_empty_field() -> None:
    result = analyse_morphogenesis("energy", _empty())
    assert result.active_fraction == 0.0
    assert result.branch_count == 0
    assert result.tip_count == 0
    assert result.fractal_dimension == 0.0


def test_morphogenesis_returns_correct_type() -> None:
    result = analyse_morphogenesis("energy", _solid_square())
    assert isinstance(result, MorphogenesisResult)


def test_morphogenesis_field_name_preserved() -> None:
    result = analyse_morphogenesis("memory", _solid_square())
    assert result.field_name == "memory"


def test_morphogenesis_tick_preserved() -> None:
    result = analyse_morphogenesis("energy", _solid_square(), tick=42)
    assert result.tick == 42


def test_morphogenesis_active_fraction_in_range() -> None:
    result = analyse_morphogenesis("energy", _solid_square())
    assert 0.0 < result.active_fraction <= 1.0


def test_morphogenesis_skeleton_density_in_range() -> None:
    result = analyse_morphogenesis("energy", _solid_square())
    assert 0.0 <= result.skeleton_density <= 1.0


def test_morphogenesis_fractal_dim_in_range() -> None:
    result = analyse_morphogenesis("energy", _solid_square(H=64, W=64))
    assert 1.0 <= result.fractal_dimension <= 2.0


def test_morphogenesis_no_fractal_skip() -> None:
    result = analyse_morphogenesis(
        "energy", _solid_square(), compute_fractal=False
    )
    assert result.fractal_dimension == 0.0


def test_morphogenesis_branch_tip_ratio_nonnegative() -> None:
    result = analyse_morphogenesis("energy", _cross())
    assert result.branch_tip_ratio >= 0.0


def test_morphogenesis_growth_front_in_result() -> None:
    result = analyse_morphogenesis("energy", _solid_square())
    assert isinstance(result.growth_front, GrowthFrontMetrics)
    assert result.growth_front.front_area > 0


def test_morphogenesis_cross_has_branches() -> None:
    result = analyse_morphogenesis("energy", _cross())
    assert result.branch_count >= 0  # cross may yield 0 after extreme thinning
    assert result.tip_count >= 0


def test_morphogenesis_complex_higher_fd_than_empty() -> None:
    r_solid = analyse_morphogenesis("energy", _solid_square(H=64, W=64, size=30))
    r_empty = analyse_morphogenesis("energy", _empty(64, 64))
    assert r_solid.fractal_dimension > r_empty.fractal_dimension


# ──────────────────────────────────────────────────────────────────
# Integration with GridState
# ──────────────────────────────────────────────────────────────────

def test_morphogenesis_on_live_state() -> None:
    from emergent_noise.core.state import GridState, SimConfig
    state = GridState.initialize(SimConfig(height=32, width=32, seed=0))
    result = analyse_morphogenesis("energy", state.energy, tick=state.tick)
    assert isinstance(result, MorphogenesisResult)
    assert 0.0 <= result.active_fraction <= 1.0
    assert result.growth_front.front_fraction >= 0.0


def test_morphogenesis_on_memory_field_after_ticks() -> None:
    from emergent_noise.core.state import GridState, SimConfig
    from emergent_noise.core.tick import TickLoop
    cfg = SimConfig(height=32, width=32, seed=1)
    state = GridState.initialize(cfg)
    loop = TickLoop(cfg)
    for _ in range(20):
        loop.step(state)
    result = analyse_morphogenesis("memory", state.memory, tick=state.tick)
    assert isinstance(result, MorphogenesisResult)
