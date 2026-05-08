"""
tests/test_presets.py – Tests for the Experiment Preset Registry (Epic 9).
"""

from __future__ import annotations

import re

import pytest

from emergent_noise.core.state import SimConfig
from emergent_noise.experiments.presets import (
    PRESETS,
    ExperimentPreset,
    ParticleSettings,
    get_preset,
    list_categories,
    list_presets,
    list_presets_by_category,
)

_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")

# ──────────────────────────────────────────────────────────────────
# Registry integrity
# ──────────────────────────────────────────────────────────────────

def test_presets_not_empty() -> None:
    assert len(PRESETS) >= 8, "Expected at least 8 presets"


def test_all_ids_unique() -> None:
    ids = [p.id for p in PRESETS.values()]
    assert len(ids) == len(set(ids)), "Duplicate preset IDs found"


def test_all_ids_are_snake_case() -> None:
    for pid in PRESETS:
        assert _SNAKE_CASE.match(pid), f"ID '{pid}' is not valid snake_case"


def test_all_titles_non_empty() -> None:
    for p in PRESETS.values():
        assert p.title.strip(), f"Preset '{p.id}' has empty title"


def test_all_descriptions_non_empty() -> None:
    for p in PRESETS.values():
        assert p.description.strip(), f"Preset '{p.id}' has empty description"


def test_all_inspirations_non_empty() -> None:
    for p in PRESETS.values():
        assert p.inspiration.strip(), f"Preset '{p.id}' has empty inspiration"


def test_all_categories_non_empty() -> None:
    for p in PRESETS.values():
        assert p.category.strip(), f"Preset '{p.id}' has empty category"


# ──────────────────────────────────────────────────────────────────
# Config validity
# ──────────────────────────────────────────────────────────────────

def test_all_configs_are_simconfig() -> None:
    for p in PRESETS.values():
        assert isinstance(p.config, SimConfig), (
            f"Preset '{p.id}' config is not a SimConfig"
        )


def test_all_configs_have_valid_seed() -> None:
    for p in PRESETS.values():
        assert isinstance(p.config.seed, int), f"Preset '{p.id}' seed is not int"


def test_all_configs_have_valid_grid() -> None:
    for p in PRESETS.values():
        assert p.config.height >= 4, f"Preset '{p.id}' height < 4"
        assert p.config.width >= 4, f"Preset '{p.id}' width < 4"


def test_key_parameters_exist_on_simconfig() -> None:
    """All key_parameters must be valid SimConfig field names."""
    config_fields = set(SimConfig.model_fields.keys())
    for p in PRESETS.values():
        for param in p.key_parameters:
            assert param in config_fields, (
                f"Preset '{p.id}' key_parameter '{param}' not found on SimConfig"
            )


# ──────────────────────────────────────────────────────────────────
# Particle settings
# ──────────────────────────────────────────────────────────────────

def test_particle_settings_type() -> None:
    for p in PRESETS.values():
        assert isinstance(p.particle_settings, ParticleSettings), (
            f"Preset '{p.id}' particle_settings is not ParticleSettings"
        )


def test_particle_settings_count_positive() -> None:
    for p in PRESETS.values():
        if p.particle_settings.enabled:
            assert p.particle_settings.count > 0, (
                f"Preset '{p.id}' has enabled particles but count=0"
            )


# ──────────────────────────────────────────────────────────────────
# Registry helpers
# ──────────────────────────────────────────────────────────────────

def test_get_preset_known() -> None:
    p = get_preset("stigmergy_ant_trails")
    assert isinstance(p, ExperimentPreset)
    assert p.id == "stigmergy_ant_trails"


def test_get_preset_unknown_raises() -> None:
    with pytest.raises(KeyError, match="Unknown preset"):
        get_preset("does_not_exist_xyz")


def test_list_presets_returns_all() -> None:
    all_presets = list_presets()
    assert len(all_presets) == len(PRESETS)
    for p in all_presets:
        assert isinstance(p, ExperimentPreset)


def test_list_categories_sorted() -> None:
    cats = list_categories()
    assert cats == sorted(cats), "list_categories() should return sorted list"
    assert len(cats) > 0


def test_list_categories_unique() -> None:
    cats = list_categories()
    assert len(cats) == len(set(cats)), "list_categories() contains duplicates"


def test_list_presets_by_category_filters() -> None:
    cat = list_categories()[0]
    filtered = list_presets_by_category(cat)
    assert len(filtered) > 0
    for p in filtered:
        assert p.category == cat


def test_list_presets_by_category_unknown_returns_empty() -> None:
    result = list_presets_by_category("__nonexistent_category__")
    assert result == []


# ──────────────────────────────────────────────────────────────────
# Experimental flag
# ──────────────────────────────────────────────────────────────────

def test_experimental_presets_are_marked() -> None:
    boids = get_preset("boids_field_approx")
    assert boids.experimental is True, "boids_field_approx should be marked experimental"


def test_not_all_presets_experimental() -> None:
    non_exp = [p for p in PRESETS.values() if not p.experimental]
    assert len(non_exp) > 0, "At least some presets should not be experimental"


# ──────────────────────────────────────────────────────────────────
# Content quality checks
# ──────────────────────────────────────────────────────────────────

def test_all_presets_have_expected_patterns() -> None:
    for p in PRESETS.values():
        assert len(p.expected_patterns) > 0, (
            f"Preset '{p.id}' has no expected_patterns"
        )


def test_all_presets_have_limitations() -> None:
    for p in PRESETS.values():
        assert len(p.limitations) > 0, f"Preset '{p.id}' has no limitations"


def test_all_presets_have_suggested_metrics() -> None:
    for p in PRESETS.values():
        assert len(p.suggested_metrics) > 0, (
            f"Preset '{p.id}' has no suggested_metrics"
        )


def test_all_presets_have_tags() -> None:
    for p in PRESETS.values():
        assert len(p.tags) > 0, f"Preset '{p.id}' has no tags"


# ──────────────────────────────────────────────────────────────────
# Determinism
# ──────────────────────────────────────────────────────────────────

def test_presets_are_reproducible() -> None:
    """Same preset loaded twice should produce identical configs."""
    from emergent_noise.core.state import GridState
    p = get_preset("stigmergy_ant_trails")
    s1 = GridState.initialize(p.config)
    s2 = GridState.initialize(p.config)
    import numpy as np
    np.testing.assert_array_equal(s1.energy, s2.energy)
