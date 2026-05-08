"""
core/tick.py – Deterministischer Tick-Loop.

Der ``TickLoop`` koordiniert die Ausführung aller Regeln in einer fixen,
dokumentierten Reihenfolge pro Simulationsschritt. Die Reihenfolge ist
bewusst gewählt und dokumentiert:

    1. Strukturiertes Rauschen addieren        (Symmetriebrechung)
    2. Diffusion                                (Transport)
    3. Reaktion (nutzt lokale Genome)           (lokale Transformation)
    4. Kopplung + Kohärenz-Synchronisation      (Netzwerkbildung)
    5. Fluss + advektiver Transport             (Vektordynamik, Wirbel)
    6. Gedächtnis aktualisieren                 (Hysterese / Spur)
    7. Meta-Regeln (Mutation/Selektion/Retention)(Regelgenom-Evolution)
    8. Alle Felder auf [0, 1] clippen           (Wertebereichserhalt)
    9. tick-Zähler erhöhen

Warum diese Reihenfolge?
    Rauschen zuerst stellt sicher, dass kleine Störungen in jeden
    Transformationsschritt eingehen. Diffusion nach Rauschen glättet extremes
    Rauschen sofort ab. Reaktion sieht bereits den diffundierten Zustand.
    Gedächtnis schreibt den Post-Reaktions-Zustand als Spur.

Deterministik:
    Für seed S und Startzustand Z liefert jeder Lauf mit identischer Config
    identische Zustände. Der Noise-Generator kombiniert seed + tick, sodass
    jeder Tick seinen eigenen deterministischen Rauschterm hat.
"""

from __future__ import annotations

from typing import Callable, List

from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.noise.structured_noise import make_structured_noise
from emergent_noise.rules.coupling import apply_coupling
from emergent_noise.rules.diffusion import apply_diffusion
from emergent_noise.rules.flow import apply_flow
from emergent_noise.rules.memory import apply_memory
from emergent_noise.rules.meta_rules import apply_meta_rules
from emergent_noise.rules.reaction import apply_reaction


StepCallback = Callable[[GridState], None]


class TickLoop:
    """Führt den deterministischen Simulations-Tick-Loop aus.

    Parameters
    ----------
    config:
        Konfigurationsobjekt. Wird unveränderlich behandelt.
    callbacks:
        Optionale Liste von Callables, die nach jedem Tick mit dem aktuellen
        ``GridState`` aufgerufen werden (z. B. für Logging oder Visualisierung).

    Usage
    -----
    >>> config = SimConfig(height=64, width=64, seed=42)
    >>> state = GridState.initialize(config)
    >>> loop = TickLoop(config)
    >>> for _ in range(100):
    ...     loop.step(state)
    """

    def __init__(
        self,
        config: SimConfig,
        callbacks: List[StepCallback] | None = None,
    ) -> None:
        self.config = config
        self.callbacks: List[StepCallback] = callbacks or []

    def step(self, state: GridState) -> None:
        """Führe einen einzelnen deterministischen Tick aus.

        Alle Regeln werden sequenziell in der dokumentierten Reihenfolge
        in-place auf ``state`` angewendet.
        """
        cfg = self.config

        # 1. Strukturiertes Rauschen auf energy und information addieren
        noise = make_structured_noise(
            height=cfg.height,
            width=cfg.width,
            amplitude=cfg.noise_amplitude,
            scale=cfg.noise_scale,
            seed=cfg.seed,
            tick=state.tick,
        )
        state.energy += noise
        state.information += noise * 0.5  # Information reagiert weniger stark auf Rauschen

        # 2. Diffusion
        apply_diffusion(state, cfg)

        # 3. Reaktion
        apply_reaction(state, cfg)

        # 4. Kopplung + Kohärenz-Synchronisation
        apply_coupling(state, cfg)

        # 5. Fluss + advektiver Transport
        apply_flow(state, cfg)

        # 6. Gedächtnis
        apply_memory(state, cfg)

        # 7. Meta-Regeln: Regelgenom-Evolution (Mutation, Selektion, Retention)
        apply_meta_rules(state, cfg)

        # 8. Wertebereiche sichern
        state.clip_all()

        # 9. Tick erhöhen
        state.tick += 1

        # Callbacks (z. B. Visualisierung, Logging)
        for cb in self.callbacks:
            cb(state)

    def run(self, state: GridState, n_ticks: int) -> GridState:
        """Führe ``n_ticks`` Schritte aus und gib den finalen Zustand zurück.

        Parameters
        ----------
        state:
            Anfangszustand (wird in-place verändert).
        n_ticks:
            Anzahl auszuführender Schritte.

        Returns
        -------
        GridState
            Identisch mit dem übergebenen ``state`` nach ``n_ticks`` Schritten.
        """
        for _ in range(n_ticks):
            self.step(state)
        return state
