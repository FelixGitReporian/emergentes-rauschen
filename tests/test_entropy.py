"""
tests/test_entropy.py – Tests für die Entropie-Analyse.
"""

import numpy as np
import pytest

from emergent_noise.analysis.entropy import field_entropy, state_entropy_summary
from emergent_noise.core.state import GridState, SimConfig


def test_entropy_uniform_field_is_high() -> None:
    """Ein gleichmäßig verteiltes Feld soll hohe normalisierte Entropie haben."""
    rng = np.random.default_rng(0)
    field = rng.uniform(0.0, 1.0, (64, 64)).astype(np.float32)
    entropy = field_entropy(field)
    assert entropy > 0.85, f"Gleichmäßiges Feld: Entropie sollte > 0.85 sein, ist {entropy:.3f}"


def test_entropy_constant_field_is_zero() -> None:
    """Ein konstantes Feld soll Entropie 0 haben."""
    field = np.full((32, 32), 0.5, dtype=np.float32)
    entropy = field_entropy(field)
    assert entropy == pytest.approx(0.0, abs=1e-6)


def test_entropy_range() -> None:
    """Normalisierte Entropie muss in [0, 1] liegen."""
    rng = np.random.default_rng(7)
    field = rng.random((32, 32)).astype(np.float32)
    entropy = field_entropy(field)
    assert 0.0 <= entropy <= 1.0


def test_state_entropy_summary_keys() -> None:
    """state_entropy_summary muss für jedes Feld einen Eintrag liefern."""
    config = SimConfig(height=16, width=16, seed=0)
    state = GridState.initialize(config)
    summary = state_entropy_summary(state)
    expected_keys = set(state.as_dict().keys())
    assert set(summary.keys()) == expected_keys
