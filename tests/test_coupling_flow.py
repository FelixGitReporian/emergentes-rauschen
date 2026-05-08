"""
tests/test_coupling_flow.py – Tests für Kopplung und Fluss.
"""

import numpy as np
import pytest

from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.rules.coupling import apply_coupling
from emergent_noise.rules.flow import apply_flow, _gradient_x, _gradient_y, _divergence


@pytest.fixture
def cfg() -> SimConfig:
    return SimConfig(height=16, width=16, seed=0)


# ------------------------------------------------------------------
# Kopplung
# ------------------------------------------------------------------

def test_coupling_changes_coherence(cfg: SimConfig) -> None:
    """Kopplung muss Kohärenz verändern wenn Gradienten vorhanden sind."""
    state = GridState.initialize(cfg)
    state.coupling[:] = 0.8
    # Inhomogene Kohärenz erzeugt Gradienten → Synchronisation greift
    state.coherence[:, :8] = 0.1
    state.coherence[:, 8:] = 0.9
    coherence_before = state.coherence.copy()
    apply_coupling(state, cfg)
    assert not np.array_equal(state.coherence, coherence_before)


def test_coupling_gain_increases_coupling(cfg: SimConfig) -> None:
    """Bei homogener Kohärenz (maximale Ähnlichkeit) soll Kopplung steigen."""
    state = GridState.initialize(cfg)
    state.coherence[:] = 0.5   # alle gleich → coh_similarity ≈ 1
    state.energy[:] = 0.0      # keine Varianz → kein Verlust
    state.coupling[:] = 0.2
    coupling_before = state.coupling.copy()
    apply_coupling(state, cfg)
    assert state.coupling.mean() >= coupling_before.mean()


def test_coupling_does_not_explode(cfg: SimConfig) -> None:
    """Kopplung darf nach clip nicht > 1 werden."""
    state = GridState.initialize(cfg)
    state.coupling[:] = 0.99
    state.coherence[:] = 0.5
    apply_coupling(state, cfg)
    state.clip_all()
    assert state.coupling.max() <= 1.0


# ------------------------------------------------------------------
# Fluss
# ------------------------------------------------------------------

def test_flow_activates_from_gradient(cfg: SimConfig) -> None:
    """Energie-Gradient muss Fluss erzeugen."""
    state = GridState.initialize(cfg)
    state.flow_x[:] = 0.0
    state.flow_y[:] = 0.0
    state.energy[:] = 0.0
    state.energy[:, :8] = 1.0   # Gradient in x-Richtung
    apply_flow(state, cfg)
    assert state.flow_x.std() > 0.0


def test_flow_damping_reduces_magnitude(cfg: SimConfig) -> None:
    """Dämpfung muss den Fluss abschwächen."""
    cfg_damp = SimConfig(height=16, width=16, seed=0,
                         flow_gradient_strength=0.0,
                         flow_curl_strength=0.0,
                         flow_damping=0.8)
    state = GridState.initialize(cfg_damp)
    state.flow_x[:] = 0.5
    state.flow_y[:] = 0.5
    state.energy[:] = 0.5  # kein Gradient
    state.coupling[:] = 0.5
    apply_flow(state, cfg_damp)
    assert state.flow_x.mean() < 0.5


def test_gradient_x_antisymmetric() -> None:
    """Gradient in x für konstantes Feld muss 0 sein."""
    field = np.ones((8, 8), dtype=np.float32) * 0.5
    grad = _gradient_x(field)
    np.testing.assert_allclose(grad, 0.0, atol=1e-6)


def test_divergence_zero_for_constant_vector() -> None:
    """Divergenz eines konstanten Vektorfeldes muss 0 sein."""
    fx = np.ones((8, 8), dtype=np.float32) * 0.3
    fy = np.ones((8, 8), dtype=np.float32) * 0.3
    div = _divergence(fx, fy)
    np.testing.assert_allclose(div, 0.0, atol=1e-6)
