"""
tests/test_state.py – Tests für core/state.py.

Geprüft wird:
- Korrekte Dimensionen nach Initialisierung
- Wertebereiche aller Felder in [0, 1]
- Reproduzierbarkeit: gleicher Seed → identischer Zustand
- Unterschiedlichkeit: verschiedene Seeds → verschiedene Zustände
- clip_all() stellt [0, 1] sicher
"""

import numpy as np
import pytest

from emergent_noise.core.state import GridState, SimConfig


@pytest.fixture
def default_config() -> SimConfig:
    return SimConfig(height=16, width=16, seed=42)


def test_initialize_shape(default_config: SimConfig) -> None:
    """Alle Felder müssen die konfigurierte Form (H, W) haben."""
    state = GridState.initialize(default_config)
    for name, arr in state.as_dict().items():
        assert arr.shape == (16, 16), f"Feld '{name}': erwartet (16,16), got {arr.shape}"


def test_initialize_value_range(default_config: SimConfig) -> None:
    """Alle Felder müssen nach Initialisierung in [0, 1] liegen."""
    state = GridState.initialize(default_config)
    for name, arr in state.as_dict().items():
        assert arr.min() >= 0.0, f"Feld '{name}' hat Werte < 0"
        assert arr.max() <= 1.0, f"Feld '{name}' hat Werte > 1"


def test_initialize_dtype(default_config: SimConfig) -> None:
    """Alle Felder sollen float32 sein."""
    state = GridState.initialize(default_config)
    for name, arr in state.as_dict().items():
        assert arr.dtype == np.float32, f"Feld '{name}': erwartet float32, got {arr.dtype}"


def test_initialize_tick_zero(default_config: SimConfig) -> None:
    """tick muss nach Initialisierung 0 sein."""
    state = GridState.initialize(default_config)
    assert state.tick == 0


def test_reproducibility_same_seed(default_config: SimConfig) -> None:
    """Zwei Initialisierungen mit gleichem Seed müssen identische Zustände liefern."""
    state_a = GridState.initialize(default_config)
    state_b = GridState.initialize(default_config)
    for name in state_a.as_dict():
        arr_a = state_a.as_dict()[name]
        arr_b = state_b.as_dict()[name]
        np.testing.assert_array_equal(arr_a, arr_b, err_msg=f"Feld '{name}' ist nicht reproduzierbar")


def test_different_seeds_differ() -> None:
    """Verschiedene Seeds müssen verschiedene energy-Felder erzeugen."""
    cfg_a = SimConfig(height=16, width=16, seed=1)
    cfg_b = SimConfig(height=16, width=16, seed=2)
    state_a = GridState.initialize(cfg_a)
    state_b = GridState.initialize(cfg_b)
    assert not np.array_equal(state_a.energy, state_b.energy)


def test_clip_all_restores_range() -> None:
    """clip_all() muss Out-of-Range-Werte auf [0, 1] zurückbringen."""
    config = SimConfig(height=8, width=8, seed=0)
    state = GridState.initialize(config)
    state.energy[:] = 5.0
    state.information[:] = -3.0
    state.clip_all()
    assert state.energy.max() <= 1.0
    assert state.information.min() >= 0.0


def test_shape_method(default_config: SimConfig) -> None:
    state = GridState.initialize(default_config)
    assert state.shape() == (16, 16)


def test_memory_initialized_to_zero(default_config: SimConfig) -> None:
    """Gedächtnis muss bei 0 starten (keine Vergangenheit)."""
    state = GridState.initialize(default_config)
    np.testing.assert_array_equal(state.memory, np.zeros((16, 16), dtype=np.float32))
