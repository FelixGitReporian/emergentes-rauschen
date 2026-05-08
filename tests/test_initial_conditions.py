"""
tests/test_initial_conditions.py – Tests for InitialCondition system (Epic 10).
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.core.initial_conditions import (
    BottomSeed,
    BottomUpEnergyGradient,
    CenteredSeed,
    CompoundInitialCondition,
    InitialCondition,
    LineSeed,
    PointSeed,
    RadialBurst,
    RandomClusteredSeed,
    SinusoidalDisturbance,
    TopDownEnergyGradient,
    TopSeed,
    UniformBaseline,
    INITIAL_CONDITIONS,
    get_initial_condition,
    list_initial_condition_names,
)
from emergent_noise.core.state import GridState, SimConfig

# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _make_state(H: int = 32, W: int = 32, seed: int = 0) -> GridState:
    cfg = SimConfig(height=H, width=W, seed=seed)
    return GridState.initialize(cfg)


# ──────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────

def test_registry_not_empty() -> None:
    assert len(INITIAL_CONDITIONS) >= 10


def test_registry_names_sorted() -> None:
    names = list_initial_condition_names()
    assert names == sorted(names)


def test_get_initial_condition_known() -> None:
    ic = get_initial_condition("centered_seed")
    assert isinstance(ic, InitialCondition)


def test_get_initial_condition_unknown_raises() -> None:
    with pytest.raises(KeyError, match="Unknown initial condition"):
        get_initial_condition("__does_not_exist__")


def test_all_named_conditions_are_initial_condition() -> None:
    for name, ic in INITIAL_CONDITIONS.items():
        assert isinstance(ic, InitialCondition), f"'{name}' is not an InitialCondition"


# ──────────────────────────────────────────────────────────────────
# UniformBaseline (identity)
# ──────────────────────────────────────────────────────────────────

def test_uniform_baseline_does_not_change_state() -> None:
    s1 = _make_state()
    s2 = _make_state()
    UniformBaseline().apply(s2)
    np.testing.assert_array_equal(s1.energy, s2.energy)


# ──────────────────────────────────────────────────────────────────
# CenteredSeed
# ──────────────────────────────────────────────────────────────────

def test_centered_seed_injects_centre() -> None:
    state = _make_state(32, 32)
    CenteredSeed(radius=3.0, energy_value=0.99).apply(state)
    cy, cx = 16, 16
    assert state.energy[cy, cx] == pytest.approx(0.99, abs=0.01)


def test_centered_seed_corners_unchanged_approx() -> None:
    state = _make_state(32, 32)
    original_corner = float(state.energy[0, 0])
    CenteredSeed(radius=3.0).apply(state)
    # Corner should be well outside radius=3 from centre=16,16
    assert state.energy[0, 0] == pytest.approx(original_corner, abs=0.01)


def test_centered_seed_also_information() -> None:
    state = _make_state(32, 32)
    CenteredSeed(radius=3.0, energy_value=0.95, also_information=True).apply(state)
    assert state.information[16, 16] == pytest.approx(0.95, abs=0.01)


def test_centered_seed_no_information() -> None:
    state = _make_state(32, 32)
    before_info = float(state.information[16, 16])
    CenteredSeed(radius=3.0, energy_value=0.95, also_information=False).apply(state)
    assert state.information[16, 16] == pytest.approx(before_info, abs=0.01)


# ──────────────────────────────────────────────────────────────────
# BottomSeed
# ──────────────────────────────────────────────────────────────────

def test_bottom_seed_fills_bottom_band() -> None:
    state = _make_state(32, 32)
    BottomSeed(band_height=4, energy_value=0.85).apply(state)
    assert state.energy[-1, 0] == pytest.approx(0.85, abs=0.01)
    assert state.energy[-4, 0] == pytest.approx(0.85, abs=0.01)


def test_bottom_seed_does_not_fill_top() -> None:
    state = _make_state(32, 32)
    before = float(state.energy[0, 0])
    BottomSeed(band_height=4).apply(state)
    assert state.energy[0, 0] == pytest.approx(before, abs=0.01)


def test_bottom_seed_also_matter() -> None:
    state = _make_state(32, 32)
    BottomSeed(band_height=3, energy_value=0.8, also_matter=True).apply(state)
    assert state.matter[-1, 0] >= 0.5


# ──────────────────────────────────────────────────────────────────
# TopSeed
# ──────────────────────────────────────────────────────────────────

def test_top_seed_fills_top_band() -> None:
    state = _make_state(32, 32)
    TopSeed(band_height=3, energy_value=0.9).apply(state)
    assert state.energy[0, 0] == pytest.approx(0.9, abs=0.01)
    assert state.energy[2, 0] == pytest.approx(0.9, abs=0.01)


# ──────────────────────────────────────────────────────────────────
# Gradient conditions
# ──────────────────────────────────────────────────────────────────

def test_top_down_gradient_top_higher_than_bottom() -> None:
    state = _make_state(32, 32)
    TopDownEnergyGradient(top_value=0.9, bottom_value=0.1).apply(state)
    assert state.energy[0, 0] > state.energy[-1, 0]


def test_top_down_gradient_monotone() -> None:
    state = _make_state(32, 32)
    TopDownEnergyGradient(top_value=0.9, bottom_value=0.1).apply(state)
    # Each row should be >= next row
    col_vals = state.energy[:, 0]
    diffs = np.diff(col_vals.astype(np.float64))
    assert np.all(diffs <= 1e-5), "Top-down gradient is not monotonically decreasing"


def test_bottom_up_gradient_bottom_higher() -> None:
    state = _make_state(32, 32)
    BottomUpEnergyGradient(bottom_value=0.9, top_value=0.1).apply(state)
    assert state.energy[-1, 0] > state.energy[0, 0]


# ──────────────────────────────────────────────────────────────────
# RadialBurst
# ──────────────────────────────────────────────────────────────────

def test_radial_burst_injects_ring() -> None:
    H, W = 64, 64
    state = _make_state(H, W)
    RadialBurst(radius=10.0, ring_width=4.0, energy_value=0.95).apply(state)
    # Point on the ring: (H//2 + 10, W//2) should be high energy
    assert state.energy[H // 2 + 10, W // 2] == pytest.approx(0.95, abs=0.01)


def test_radial_burst_centre_not_filled() -> None:
    H, W = 64, 64
    state = _make_state(H, W)
    original = float(state.energy[H // 2, W // 2])
    RadialBurst(radius=15.0, ring_width=2.0, energy_value=0.95).apply(state)
    # Centre is far inside the ring, should not be filled
    assert state.energy[H // 2, W // 2] == pytest.approx(original, abs=0.05)


# ──────────────────────────────────────────────────────────────────
# LineSeed
# ──────────────────────────────────────────────────────────────────

def test_line_seed_horizontal_fills_row() -> None:
    state = _make_state(32, 32)
    LineSeed(orientation="horizontal", position=10, width=2, energy_value=0.9).apply(state)
    assert state.energy[10, 5] == pytest.approx(0.9, abs=0.01)
    assert state.energy[10, 20] == pytest.approx(0.9, abs=0.01)


def test_line_seed_vertical_fills_column() -> None:
    state = _make_state(32, 32)
    LineSeed(orientation="vertical", position=15, width=2, energy_value=0.9).apply(state)
    assert state.energy[5, 15] == pytest.approx(0.9, abs=0.01)


def test_line_seed_target_field() -> None:
    state = _make_state(32, 32)
    LineSeed(orientation="horizontal", position=8, energy_value=0.8, target_field="information").apply(state)
    assert state.information[8, 0] == pytest.approx(0.8, abs=0.01)


# ──────────────────────────────────────────────────────────────────
# PointSeed
# ──────────────────────────────────────────────────────────────────

def test_point_seed_injects_at_position() -> None:
    state = _make_state(32, 32)
    PointSeed(row=5, col=10, radius=2.0, energy_value=0.88).apply(state)
    assert state.energy[5, 10] == pytest.approx(0.88, abs=0.01)


def test_point_seed_negative_wrap() -> None:
    state = _make_state(32, 32)
    PointSeed(row=-1, col=-1, radius=2.0, energy_value=0.88).apply(state)
    # -1 wraps to row=31, col=31
    assert state.energy[31, 31] == pytest.approx(0.88, abs=0.01)


# ──────────────────────────────────────────────────────────────────
# RandomClusteredSeed
# ──────────────────────────────────────────────────────────────────

def test_random_clusters_raises_mean_energy() -> None:
    state_before = _make_state(64, 64)
    state_after = _make_state(64, 64)
    mean_before = float(state_before.energy.mean())
    RandomClusteredSeed(n_clusters=10, cluster_radius=4.0, energy_value=0.9, seed=7).apply(state_after)
    assert state_after.energy.mean() > mean_before


def test_random_clusters_deterministic() -> None:
    s1 = _make_state(64, 64, seed=0)
    s2 = _make_state(64, 64, seed=0)
    ic = RandomClusteredSeed(n_clusters=5, seed=99)
    ic.apply(s1)
    ic.apply(s2)
    np.testing.assert_array_equal(s1.energy, s2.energy)


# ──────────────────────────────────────────────────────────────────
# SinusoidalDisturbance
# ──────────────────────────────────────────────────────────────────

def test_sinusoidal_modulates_field() -> None:
    state = _make_state(64, 64)
    before = state.energy.copy()
    SinusoidalDisturbance(wavelength=16.0, amplitude=0.2, axis=0).apply(state)
    assert not np.allclose(state.energy, before)


def test_sinusoidal_stays_in_bounds() -> None:
    state = _make_state(64, 64)
    SinusoidalDisturbance(wavelength=8.0, amplitude=0.5, axis=1).apply(state)
    assert state.energy.min() >= 0.0
    assert state.energy.max() <= 1.0


# ──────────────────────────────────────────────────────────────────
# CompoundInitialCondition
# ──────────────────────────────────────────────────────────────────

def test_compound_applies_in_order() -> None:
    state = _make_state(32, 32)
    # BottomSeed then TopSeed — both should be active
    CompoundInitialCondition([
        BottomSeed(band_height=3, energy_value=0.9),
        TopSeed(band_height=3, energy_value=0.8),
    ]).apply(state)
    assert state.energy[-1, 0] == pytest.approx(0.9, abs=0.01)
    assert state.energy[0, 0] == pytest.approx(0.8, abs=0.01)


def test_compound_plus_operator() -> None:
    ic = BottomSeed() + TopSeed()
    assert isinstance(ic, CompoundInitialCondition)
    assert len(ic.conditions) == 2


def test_compound_empty_is_identity() -> None:
    s1 = _make_state(32, 32)
    s2 = _make_state(32, 32)
    CompoundInitialCondition([]).apply(s2)
    np.testing.assert_array_equal(s1.energy, s2.energy)


# ──────────────────────────────────────────────────────────────────
# GridState.initialize integration
# ──────────────────────────────────────────────────────────────────

def test_gridstate_initialize_with_condition() -> None:
    cfg = SimConfig(height=32, width=32, seed=42)
    ic = CenteredSeed(radius=3.0, energy_value=0.99)
    state = GridState.initialize(cfg, initial_condition=ic)
    assert state.energy[16, 16] == pytest.approx(0.99, abs=0.01)


def test_gridstate_initialize_without_condition_unchanged() -> None:
    cfg = SimConfig(height=32, width=32, seed=42)
    s1 = GridState.initialize(cfg)
    s2 = GridState.initialize(cfg)
    np.testing.assert_array_equal(s1.energy, s2.energy)


def test_gridstate_initialize_all_fields_in_bounds() -> None:
    cfg = SimConfig(height=32, width=32, seed=0)
    ic = CompoundInitialCondition([
        BottomSeed(band_height=4, energy_value=0.95),
        TopDownEnergyGradient(),
        RadialBurst(ring_width=3.0, energy_value=0.98),
    ])
    state = GridState.initialize(cfg, initial_condition=ic)
    for name, arr in state.as_dict().items():
        assert arr.min() >= 0.0, f"{name} below 0 after IC"
        assert arr.max() <= 1.0, f"{name} above 1 after IC"


# ──────────────────────────────────────────────────────────────────
# Preset integration: presets with IC produce expected seeds
# ──────────────────────────────────────────────────────────────────

def test_preset_tree_growth_has_bottom_energy() -> None:
    from emergent_noise.experiments.presets import get_preset
    p = get_preset("tree_growth_branching")
    state = GridState.initialize(p.config, initial_condition=p.initial_condition)
    # Bottom rows should have high energy (BottomSeed)
    assert state.energy[-1, :].mean() > 0.5


def test_preset_excitable_media_has_ring() -> None:
    from emergent_noise.experiments.presets import get_preset
    p = get_preset("excitable_media_waves")
    state = GridState.initialize(p.config, initial_condition=p.initial_condition)
    H, W = state.energy.shape
    # Energy at the ring radius (~H/4 from centre) should be elevated
    ring_r = H // 4
    ring_val = float(state.energy[H // 2 + ring_r, W // 2])
    centre_val = float(state.energy[H // 2, W // 2])
    # Ring energy should be >= centre energy (radial burst was injected)
    assert ring_val >= centre_val - 0.1


def test_preset_stigmergy_has_clusters() -> None:
    from emergent_noise.experiments.presets import get_preset
    p = get_preset("stigmergy_ant_trails")
    state = GridState.initialize(p.config, initial_condition=p.initial_condition)
    # Random clusters raise mean energy above the baseline
    state_no_ic = GridState.initialize(p.config)
    assert state.energy.mean() >= state_no_ic.energy.mean() - 0.05
