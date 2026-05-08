"""
rules/coupling.py – Nachbarschaftskopplung und lokale Netzwerkbildung.

Kopplung (``coupling``) modelliert die Stärke der Verbindung zwischen Zellen.
Hohe Kopplung bedeutet, dass Zellen ihren Zustand stärker aneinander angleichen.

Implementierte Regeln:

1. Kopplungswachstum (Binding):
   Wenn zwei benachbarte Zellen ähnliche Kohärenz haben, wächst ihre Kopplung.
   Ähnlichkeit wird als negierter absoluter Unterschied gemessen.
   Formel: coupling += gain * (1 - |coherence - mean_neighbor_coherence|)

2. Kopplungszerfall (Unbinding):
   In chaotischen Regionen (hohe lokale Energievarianz) nimmt Kopplung ab.
   Formel: coupling -= loss * local_energy_variance

3. Kopplungsgetriebene Kohärenz-Synchronisation:
   Zellen mit hoher Kopplung synchronisieren ihre Kohärenz mit Nachbarn.
   Formel: coherence += sync_rate * coupling * (mean_neighbor_coherence - coherence)

Wissenschaftliche Motivation:
    Kopplung ist das relationale Feld des Systems. Aus ihr können Cluster,
    Membranen und Netzwerke entstehen. Hohe Kopplung stabilisiert Muster;
    niedrige Kopplung lässt Regionen unabhängig werden — ein Vorläufer von
    Kompartimentierung (proto-zelluläre Grenzbildung).
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


def _mean_neighbors(field: np.ndarray) -> np.ndarray:
    """Mittlerer Wert der vier Von-Neumann-Nachbarn (periodisch)."""
    return 0.25 * (
        np.roll(field, 1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, 1, axis=1)
        + np.roll(field, -1, axis=1)
    )


def _local_variance(field: np.ndarray) -> np.ndarray:
    """Lokale Varianz: (f - mean_neighbors)^2, Maß für lokale Unordnung."""
    diff = field - _mean_neighbors(field)
    return diff * diff


def apply_coupling(state: GridState, config: SimConfig) -> None:
    """Aktualisiere Kopplung und Kohärenz in-place.

    Kopplung wächst wo Kohärenz ähnlich ist (Bindungsregel), sinkt wo
    Energie chaotisch ist (Zerfallsregel). Hohe Kopplung synchronisiert
    Kohärenz mit Nachbarn (Synchronisationsregel).
    """
    gain = config.coupling_gain
    loss = config.coupling_loss
    sync = config.coupling_sync_rate

    mean_coh = _mean_neighbors(state.coherence)
    coh_similarity = 1.0 - np.abs(state.coherence - mean_coh)

    # Regel 1: Bindung – ähnliche Kohärenz stärkt Kopplung
    state.coupling += gain * coh_similarity

    # Regel 2: Zerfall – lokale Energievarianz + globaler Basalzerfall
    # Der Basalzerfall (gain * 0.5) verhindert Sättigung bei homogenen Feldern.
    energy_var = _local_variance(state.energy)
    state.coupling -= loss * energy_var + gain * 2.0 * state.coupling

    # Regel 3: Synchronisation – hohe Kopplung gleicht Kohärenz an
    state.coherence += sync * state.coupling * (mean_coh - state.coherence)
