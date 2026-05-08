"""
rules/memory.py – Gedächtnisregeln: Zerfall und Einprägung (Imprint).

Gedächtnis modelliert die lokale Hysterese des Feldes: Zellen „erinnern"
vergangene Aktivierungszustände. Das Gedächtnisfeld wird pro Tick zweistufig
aktualisiert:

1. Zerfall (Decay): memory *= decay_factor
   Das Gedächtnis verblasst langsam, wenn keine neue Aktivität eintrifft.

2. Einprägung (Imprint): Exponential Moving Average (EMA) zur aktuellen Energie.
   memory = decay * memory + (1 - decay) * imprint_strength * energy

   Diese Formulierung garantiert, dass der Gleichgewichtswert von memory
   immer in [0, 1] liegt, solange energy ∈ [0, 1]. Der Parameter
   ``memory_imprint_strength`` skaliert, wie stark Energie eingeschrieben wird.

Wissenschaftliche Motivation:
    Gedächtnisfelder erzeugen Hysterese – Pfadabhängigkeit, Narben vergangener
    Ereignisse, sedimentierte Geschichte. Sie sind zentral für Proto-Lern-Dynamiken
    und für die Spurenlese-Analyse (was war wahrscheinlich vorher?).
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


def apply_memory(state: GridState, config: SimConfig) -> None:
    """Aktualisiere das Gedächtnisfeld in-place.

    Schritt 1 – Zerfall:
        Das Gedächtnis wird mit ``memory_decay`` multipliziert (< 1.0).
        Ohne neue Einprägung konvergiert es exponentiell gegen 0.

    Schritt 2 – Imprint:
        Die aktuelle Energie wird anteilig (``memory_imprint_strength``)
        ins Gedächtnis eingeschrieben. Hochenergetische Ereignisse hinterlassen
        stärkere Spuren.
    """
    imprint_rate = (1.0 - config.memory_decay) * config.memory_imprint_strength
    state.memory = config.memory_decay * state.memory + imprint_rate * state.energy
