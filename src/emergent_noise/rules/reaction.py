"""
rules/reaction.py – Lokale Reaktionsregeln.

Reaktionsregeln transformieren lokale Zustände, wenn Schwellwertbedingungen
erfüllt sind. Sie sind das Pendant zu chemischen Reaktionen: Wenn bestimmte
„Zutaten" (Feld-Werte) lokal vorhanden sind, finden Umwandlungen statt.

Implementierte Regeln:
1. Energie-Reaktion: hohe Energie + hohe Reaktivität → Kohärenzgewinn,
   Energieverlust, Informationsgewinn.
2. Kohärenz-Zerfall: niedrige Energie + niedrige Kohärenz → Kohärenzverlust,
   leichte Energiefreisetzung.
3. Reaktivitäts-Dynamik: Reaktivität erholt sich langsam (Ruhezustand) und
   wird durch Aktivierungsreaktionen verbraucht. Modelliert Ermüdung/Erholung.
4. Materie-Erosion: Hohe Flussgeschwindigkeit erodiert Materie (Transport).
5. Materie-Ablagerung: Niedrige Energie + hohe Kopplung lagert Materie ab
   (Sedimentationsanalogon, Substratbildung).

Seit v0.4.0 (Epic 3):
    Regel 1 nutzt die lokalen Regelgenom-Felder ``genome_strength`` und
    ``genome_threshold`` aus dem GridState statt globaler Config-Konstanten.
    Dadurch reagiert jede Zelle nach ihrer eigenen evolvierten Reaktionsstärke
    und ihrem eigenen Schwellwert — das Verhalten ist räumlich heterogen.

Wissenschaftliche Vorsicht:
    Diese Regeln sind heuristische Abstraktionen, keine exakten chemischen
    Gleichungen. Sie illustrieren, wie Reaktivität als lokaler Katalysator
    wirken und Materie als persistentes Substrat fungieren kann.
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


def apply_reaction(state: GridState, config: SimConfig) -> None:
    """Wende lokale Reaktionsregeln in-place an.

    Regel 1 – Aktivierungsreaktion:
        Wenn energy > threshold UND reactivity > 0.5:
            energy      −= strength
            coherence   += strength * 0.8
            information += strength * 0.5
            reactivity  −= strength * 0.6   (Reaktivität wird verbraucht)

    Regel 2 – Zerfall:
        Wenn energy < 0.2 UND coherence < 0.2:
            coherence −= strength * 0.5
            energy    += strength * 0.3

    Regel 3 – Reaktivitätserholung (Exponential Moving Average zum Ruhezustand):
        reactivity = recovery * reactivity + (1 - recovery) * reactivity_rest
        Erholung überall, unabhängig von Schwellwerten.

    Regel 4 – Materie-Erosion:
        Wo Flussgeschwindigkeit (|flow|) hoch ist, wird Materie erodiert.
        matter −= erosion_rate * |flow|

    Regel 5 – Materie-Ablagerung:
        Wo Fluss niedrig UND Kopplung hoch, lagert sich Materie ab.
        matter += deposition_rate * coupling * (1 - |flow|)
    """
    s = config.reaction_strength  # globaler Fallback (Zerfall + Erosion)

    # Regel 1: Aktivierungsreaktion – nutzt lokales Regelgenom (Epic 3)
    # Jede Zelle hat ihren eigenen Schwellwert (genome_threshold) und
    # ihre eigene Reaktionsstärke (genome_strength) aus dem evolvierten Genome.
    mask_activate = (state.energy > state.genome_threshold) & (state.reactivity > 0.5)
    local_s = state.genome_strength  # Array: Stärke pro Zelle
    state.energy[mask_activate] -= local_s[mask_activate]
    state.coherence[mask_activate] += local_s[mask_activate] * 0.8
    state.information[mask_activate] += local_s[mask_activate] * 0.5
    state.reactivity[mask_activate] -= local_s[mask_activate] * 0.6

    # Regel 2: Zerfall
    mask_decay = (state.energy < 0.2) & (state.coherence < 0.2)
    state.coherence[mask_decay] -= s * 0.5
    state.energy[mask_decay] += s * 0.3

    # Regel 3: Reaktivitätserholung (EMA zum Ruhezustand)
    rec = config.reactivity_recovery
    state.reactivity = rec * state.reactivity + (1.0 - rec) * config.reactivity_rest

    # Regel 4: Materie-Erosion durch Fluss
    flow_magnitude = np.sqrt(state.flow_x ** 2 + state.flow_y ** 2)
    state.matter -= config.matter_erosion_rate * flow_magnitude

    # Regel 5: Materie-Ablagerung in ruhigen, gekoppelten Regionen
    # Ablagerungsrate wird durch (1 - matter) skaliert → Gleichgewicht < 1.0
    mask_deposit = flow_magnitude < 0.1
    state.matter[mask_deposit] += (
        config.matter_deposition_rate
        * state.coupling[mask_deposit]
        * (1.0 - state.matter[mask_deposit])
    )
