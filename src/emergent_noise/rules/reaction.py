"""
rules/reaction.py – Lokale Reaktionsregeln.

Reaktionsregeln transformieren lokale Zustände, wenn Schwellwertbedingungen
erfüllt sind. Sie sind das Pendant zu chemischen Reaktionen: Wenn bestimmte
„Zutaten" (Feld-Werte) lokal vorhanden sind, finden Umwandlungen statt.

Implementierte Regeln (Phase 1):
1. Energie-Reaktion: hohe Energie + hohe Reaktivität → Kohärenzgewinn,
   Energieverlust, Informationsgewinn.
2. Kohärenz-Zerfall: niedrige Energie + niedrige Kohärenz → Kohärenzverlust,
   leichte Energiefreisetzung.

Wissenschaftliche Vorsicht:
    Diese Regeln sind heuristische Abstraktionen, keine exakten chemischen
    Gleichungen. Sie illustrieren, wie Reaktivität als lokaler Katalysator
    wirken kann.
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


def apply_reaction(state: GridState, config: SimConfig) -> None:
    """Wende lokale Reaktionsregeln in-place an.

    Regel 1 – Aktivierungsreaktion:
        Wenn energy > threshold UND reactivity > 0.5:
            energy    −= strength          (Energie wird „verbraucht")
            coherence += strength * 0.8    (Ordnung entsteht)
            information += strength * 0.5  (Information wächst)

    Regel 2 – Zerfall:
        Wenn energy < 0.2 UND coherence < 0.2:
            coherence −= strength * 0.5    (Ordnung zerfällt)
            energy    += strength * 0.3    (geringe Energiefreisetzung)
    """
    thr = config.reaction_energy_threshold
    s = config.reaction_strength

    # Regel 1: Aktivierungsreaktion
    mask_activate = (state.energy > thr) & (state.reactivity > 0.5)
    state.energy[mask_activate] -= s
    state.coherence[mask_activate] += s * 0.8
    state.information[mask_activate] += s * 0.5

    # Regel 2: Zerfall
    mask_decay = (state.energy < 0.2) & (state.coherence < 0.2)
    state.coherence[mask_decay] -= s * 0.5
    state.energy[mask_decay] += s * 0.3
