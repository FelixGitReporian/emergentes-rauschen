"""
tests/test_rules.py – Tests für Diffusions-, Reaktions- und Gedächtnisregeln.

Geprüft wird:
- Diffusion glättet Gradienten (Energie diffundiert)
- Reaktion verändert Kohärenz bei hoher Energie + hoher Reaktivität
- Gedächtnis-Zerfall: Wert sinkt ohne Imprint
- Gedächtnis-Imprint: Wert steigt mit Energie
"""

import numpy as np
import pytest

from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.rules.diffusion import apply_diffusion, _laplacian
from emergent_noise.rules.memory import apply_memory
from emergent_noise.rules.reaction import apply_reaction


@pytest.fixture
def flat_config() -> SimConfig:
    return SimConfig(height=8, width=8, seed=0)


# ------------------------------------------------------------------
# Diffusion
# ------------------------------------------------------------------


def test_laplacian_constant_field() -> None:
    """Laplace-Operator auf konstantem Feld muss 0 ergeben."""
    field = np.ones((8, 8), dtype=np.float32) * 0.5
    lap = _laplacian(field)
    np.testing.assert_allclose(lap, 0.0, atol=1e-6)


def test_diffusion_smoothes_gradient(flat_config: SimConfig) -> None:
    """Diffusion muss einen starken Gradienten abschwächen."""
    state = GridState.initialize(flat_config)
    state.energy[:] = 0.0
    state.energy[:, :4] = 1.0  # Scharfe Grenze in der Mitte
    std_before = state.energy.std()
    apply_diffusion(state, flat_config)
    state.clip_all()
    std_after = state.energy.std()
    assert std_after < std_before, "Diffusion sollte den Gradienten glätten"


def test_diffusion_constant_field_unchanged(flat_config: SimConfig) -> None:
    """Konstantes Feld darf durch Diffusion nicht verändert werden."""
    state = GridState.initialize(flat_config)
    state.energy[:] = 0.5
    apply_diffusion(state, flat_config)
    np.testing.assert_allclose(state.energy, 0.5, atol=1e-6)


# ------------------------------------------------------------------
# Reaktion
# ------------------------------------------------------------------


def test_reaction_increases_coherence_where_energy_high(flat_config: SimConfig) -> None:
    """Hohe Energie + hohe Reaktivität soll Kohärenz erhöhen."""
    state = GridState.initialize(flat_config)
    state.energy[:] = 0.9
    state.reactivity[:] = 0.8
    state.coherence[:] = 0.1
    coherence_before = state.coherence.copy()
    apply_reaction(state, flat_config)
    assert state.coherence.mean() > coherence_before.mean()


def test_reaction_reduces_energy_where_high(flat_config: SimConfig) -> None:
    """Reaktion bei hoher Energie soll Energie reduzieren."""
    state = GridState.initialize(flat_config)
    state.energy[:] = 0.9
    state.reactivity[:] = 0.8
    energy_before = state.energy.copy()
    apply_reaction(state, flat_config)
    assert state.energy.mean() < energy_before.mean()


# ------------------------------------------------------------------
# Gedächtnis
# ------------------------------------------------------------------


def test_memory_decays(flat_config: SimConfig) -> None:
    """Ohne Energie-Imprint muss Gedächtnis pro Tick abnehmen."""
    state = GridState.initialize(flat_config)
    state.memory[:] = 0.8
    state.energy[:] = 0.0  # Kein Imprint
    apply_memory(state, flat_config)
    assert state.memory.mean() < 0.8


def test_memory_imprint_with_energy(flat_config: SimConfig) -> None:
    """Mit Energie-Imprint muss Gedächtnis wachsen (von 0 aus)."""
    state = GridState.initialize(flat_config)
    state.memory[:] = 0.0
    state.energy[:] = 1.0  # Maximaler Imprint
    apply_memory(state, flat_config)
    assert state.memory.mean() > 0.0


def test_reactivity_recovers_toward_rest() -> None:
    """Reaktivität soll sich zum Ruhezustand hin erholen."""
    config = SimConfig(height=16, width=16, seed=0, reactivity_recovery=0.9, reactivity_rest=0.5)
    state = GridState.initialize(config)
    state.reactivity[:] = 0.0  # weit unter Ruhezustand
    state.energy[:] = 0.0      # keine Aktivierungsreaktion
    apply_reaction(state, config)
    assert state.reactivity.mean() > 0.0


def test_reactivity_consumed_by_activation() -> None:
    """Reaktivität wird bei Aktivierungsreaktionen verbraucht."""
    config = SimConfig(height=16, width=16, seed=0, reaction_strength=0.2,
                       reactivity_recovery=0.0, reactivity_rest=0.5)
    state = GridState.initialize(config)
    state.energy[:] = 0.9       # über Schwellwert
    state.reactivity[:] = 0.8   # über 0.5 → Aktivierung
    before = state.reactivity.copy()
    apply_reaction(state, config)
    # Aktivierungsmaske greift → reactivity sinkt (vor Erholung) in consumed region
    # Nach EMA-Erholung (rate=0): reactivity = 0 * before + (1-0) * 0.5 = 0.5 ≠ before
    assert not np.array_equal(state.reactivity, before)


def test_matter_erodes_with_flow() -> None:
    """Materie soll durch hohe Flussgeschwindigkeit erodiert werden."""
    config = SimConfig(height=16, width=16, seed=0, matter_erosion_rate=0.5)
    state = GridState.initialize(config)
    state.matter[:] = 0.8
    state.flow_x[:] = 1.0   # hohe Flussgeschwindigkeit
    state.flow_y[:] = 0.0
    state.energy[:] = 0.0   # keine Aktivierungsreaktion
    state.reactivity[:] = 0.0
    matter_before = state.matter.mean()
    apply_reaction(state, config)
    assert state.matter.mean() < matter_before


def test_matter_deposits_in_calm_regions() -> None:
    """Materie soll in ruhigen, gekoppelten Regionen abgelagert werden."""
    config = SimConfig(height=16, width=16, seed=0,
                       matter_deposition_rate=0.5, matter_erosion_rate=0.0)
    state = GridState.initialize(config)
    state.matter[:] = 0.2
    state.flow_x[:] = 0.0   # kein Fluss → Ablagerung
    state.flow_y[:] = 0.0
    state.coupling[:] = 0.9
    state.energy[:] = 0.0
    state.reactivity[:] = 0.0
    matter_before = state.matter.mean()
    apply_reaction(state, config)
    assert state.matter.mean() > matter_before


def test_memory_decay_factor(flat_config: SimConfig) -> None:
    """Gedächtnis muss nach einem Tick mit decay-Faktor multipliziert worden sein."""
    cfg = SimConfig(height=8, width=8, seed=0, memory_decay=0.9, memory_imprint_strength=0.0)
    state = GridState.initialize(cfg)
    state.memory[:] = 1.0
    state.energy[:] = 0.0
    apply_memory(state, cfg)
    np.testing.assert_allclose(state.memory, 0.9, atol=1e-6)
