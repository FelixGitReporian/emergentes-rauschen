"""
rules/flow.py – Gerichteter Fluss, Gradienten-Transport und Wirbel.

Das Flussfeld (``flow_x``, ``flow_y``) modelliert gerichtete Bewegungstendenzen
im Grid. Werte in [-1, 1] repräsentieren die Flussrichtung und -stärke.

Implementierte Mechanismen:

1. Gradient-Antrieb:
   Energie-Gradienten erzeugen Fluss: Energie fließt von hohen zu niedrigen
   Bereichen (analog zu Druck/Temperaturgradienten).
   flow_x += -gradient_strength * dE/dx
   flow_y += -gradient_strength * dE/dy

2. Fluss-Dämpfung:
   Fluss zerfällt ohne kontinuierlichen Antrieb (Reibung).
   flow *= flow_damping

3. Advektiver Transport:
   Energie wird anteilig entlang des Flussvektors verschoben.
   energy_new(i,j) += advection_rate * flow_divergence

4. Wirbelbildung (Curl-Forcing):
   Lokale Kopplung erzeugt Rotationstendenzen — Grundlage für Wirbelmuster.
   (Rotationsbeitrag via Curl des Kopplungsfeldes)

Wissenschaftliche Motivation:
    Flussfelder sind entscheidend für Wellen, Strömungen, Wirbel und aktive
    Materialdynamiken. Sie verbinden lokale Gradienten mit globalem Transport
    und sind ein Vorläufer für hydrodynamische und quantenfeldähnliche Muster.

Wertebereich: flow_x, flow_y ∈ [-1, 1]; wird per clip_all() gesichert.
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


def _gradient_x(field: np.ndarray) -> np.ndarray:
    """Zentraldifferenz in x-Richtung (periodisch). Approximiert dF/dx."""
    return 0.5 * (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1))


def _gradient_y(field: np.ndarray) -> np.ndarray:
    """Zentraldifferenz in y-Richtung (periodisch). Approximiert dF/dy."""
    return 0.5 * (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0))


def _divergence(fx: np.ndarray, fy: np.ndarray) -> np.ndarray:
    """Diskrete Divergenz des Vektorfeldes (fx, fy). Approximiert ∇·F."""
    return _gradient_x(fx) + _gradient_y(fy)


def apply_flow(state: GridState, config: SimConfig) -> None:
    """Aktualisiere Flussfeld und advektiven Energietransport in-place.

    Schritt 1: Energie-Gradient treibt Fluss an (abwärts den Gradienten).
    Schritt 2: Kopplung erzeugt schwache Rotationstendenz (Wirbelantrieb).
    Schritt 3: Fluss-Dämpfung (Reibung).
    Schritt 4: Advektiver Energietransport entlang des Flusses.
    """
    gs = config.flow_gradient_strength
    damp = config.flow_damping
    adv = config.flow_advection_rate
    curl_s = config.flow_curl_strength

    # Schritt 1: Gradient-Antrieb (Energie fließt bergab)
    state.flow_x -= gs * _gradient_x(state.energy)
    state.flow_y -= gs * _gradient_y(state.energy)

    # Schritt 2: Kopplungs-Wirbel (Curl-Forcing)
    # Curl des Kopplungsfeldes erzeugt Rotationskomponenten
    state.flow_x += curl_s * _gradient_y(state.coupling)
    state.flow_y -= curl_s * _gradient_x(state.coupling)

    # Schritt 3: Dämpfung
    state.flow_x *= damp
    state.flow_y *= damp

    # Schritt 4: Advektiver Transport – Energie folgt dem Fluss
    div = _divergence(state.flow_x, state.flow_y)
    state.energy -= adv * div  # Divergenz = Quellen/Senken des Energieflusses
