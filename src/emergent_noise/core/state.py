"""
core/state.py – Zustandsdefinition und Konfiguration.

Ein ``GridState`` repräsentiert den vollständigen Momentanzustand eines
2-D-Gitters. Jedes der acht Felder ist ein float32-Array der Form (height, width).
Alle Werte liegen per Konvention im Intervall [0, 1].

Seit v0.4.0 (Epic 3) enthält GridState zwei zusätzliche Meta-Regel-Felder:
- ``genome_strength``   – lokale Reaktionsstärke (evolviert durch Meta-Regeln)
- ``genome_threshold``  – lokaler Energie-Schwellwert (evolviert durch Meta-Regeln)
Diese bilden das dezentrale Regelgenom des Systems (Arbeitsmappe Kap. 9).

``SimConfig`` ist das zentrale Konfigurationsobjekt. Alle Parameter der
Simulation werden hier definiert – keine magischen Zahlen in anderen Modulen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional

import numpy as np
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from emergent_noise.core.initial_conditions import InitialCondition


FIELD_NAMES: tuple[str, ...] = (
    "energy",
    "matter",
    "information",
    "coupling",
    "reactivity",
    "memory",
    "coherence",
    "flow_x",
    "flow_y",
)


class SimConfig(BaseModel):
    """Vollständige Konfiguration einer Simulation.

    Alle Untermodule empfangen dieses Objekt, statt eigene Konstanten zu
    definieren. Dadurch bleibt die Simulation vollständig reproduzierbar, wenn
    Config + Seed gespeichert werden.
    """

    height: int = Field(64, ge=4, description="Gitterhöhe in Zellen")
    width: int = Field(64, ge=4, description="Gitterbreite in Zellen")
    seed: int = Field(42, description="Zufalls-Seed für vollständige Reproduzierbarkeit")

    # --- Diffusion ---
    diffusion_energy: float = Field(0.2, ge=0.0, le=1.0, description="Diffusionsrate für Energie")
    diffusion_information: float = Field(
        0.05, ge=0.0, le=1.0, description="Diffusionsrate für Information"
    )

    # --- Reaktion ---
    reaction_energy_threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Energie-Schwellwert, ab dem eine Reaktion ausgelöst wird"
    )
    reaction_strength: float = Field(
        0.1, ge=0.0, le=1.0, description="Stärke der Zustandsänderung pro Reaktionsereignis"
    )

    # --- Gedächtnis ---
    memory_decay: float = Field(
        0.97, ge=0.0, le=1.0, description="Multiplikativer Zerfallsfaktor des Gedächtnisses pro Tick"
    )
    memory_imprint_strength: float = Field(
        0.3, ge=0.0, le=1.0, description="Gewicht des aktuellen Zustands beim Einschreiben ins Gedächtnis"
    )

    # --- Rauschen ---
    noise_amplitude: float = Field(
        0.02, ge=0.0, le=1.0, description="Maximale Amplitude des strukturierten Rauschens"
    )
    noise_scale: float = Field(
        8.0, gt=0.0, description="Räumliche Skalierung des Perlin-ähnlichen Rauschens (Zellen)"
    )

    # --- Reaktivität ---
    reactivity_recovery: float = Field(
        0.98, ge=0.0, le=1.0,
        description="EMA-Rate für Reaktivitätserholung zum Ruhezustand (1=keine Erholung)"
    )
    reactivity_rest: float = Field(
        0.5, ge=0.0, le=1.0,
        description="Gleichgewichts-Ruhezustand der Reaktivität"
    )

    # --- Materie ---
    matter_erosion_rate: float = Field(
        0.02, ge=0.0, le=1.0,
        description="Rate, mit der Fluss Materie erodiert"
    )
    matter_deposition_rate: float = Field(
        0.005, ge=0.0, le=1.0,
        description="Rate, mit der Materie in ruhigen gekoppelten Regionen abgelagert wird"
    )

    # --- Kopplung ---
    coupling_gain: float = Field(
        0.005, ge=0.0, le=1.0, description="Wachstumsrate der Kopplung bei ähnlicher Kohärenz"
    )
    coupling_loss: float = Field(
        0.08, ge=0.0, le=1.0, description="Zerfallsrate der Kopplung bei lokaler Energievarianz"
    )
    coupling_sync_rate: float = Field(
        0.05, ge=0.0, le=1.0, description="Rate, mit der Kohärenz durch Kopplung synchronisiert wird"
    )

    # --- Fluss ---
    flow_gradient_strength: float = Field(
        0.1, ge=0.0, le=1.0, description="Stärke des energiegetriebenen Flusses"
    )
    flow_damping: float = Field(
        0.95, ge=0.0, le=1.0, description="Dämpfungsfaktor des Flusses pro Tick (Reibung)"
    )
    flow_advection_rate: float = Field(
        0.05, ge=0.0, le=1.0, description="Rate des advektiven Energietransports entlang des Flusses"
    )
    flow_curl_strength: float = Field(
        0.03, ge=0.0, le=1.0, description="Stärke des kopplungsgetriebenen Wirbelantriebs"
    )

    # --- Meta-Regeln (Epic 3) ---
    meta_mutation_rate: float = Field(
        0.01, ge=0.0, le=1.0,
        description="Wahrscheinlichkeit pro Zelle+Tick einer Regelgenome-Mutation"
    )
    meta_mutation_strength: float = Field(
        0.05, ge=0.0, le=0.5,
        description="Maximale Änderung eines Regelparameters durch eine Mutation (uniform ±)"
    )
    meta_selection_rate: float = Field(
        0.1, ge=0.0, le=1.0,
        description="Anteil der Zellen, die pro Tick durch Selektion aktualisiert werden"
    )
    meta_retention_threshold: float = Field(
        0.7, ge=0.0, le=1.0,
        description="Fitness-Schwelle, ab der ein Regelprofil ins Gedächtnis geschrieben wird"
    )
    meta_enabled: bool = Field(
        True,
        description="Schalter: Meta-Regel-Evolution aktiv oder deaktiviert"
    )

    # --- Initialisierung ---
    init_energy_mean: float = Field(0.4, ge=0.0, le=1.0)
    init_energy_std: float = Field(0.15, ge=0.0)
    init_matter_mean: float = Field(0.3, ge=0.0, le=1.0)
    init_matter_std: float = Field(0.1, ge=0.0)
    init_information_mean: float = Field(0.2, ge=0.0, le=1.0)
    init_information_std: float = Field(0.1, ge=0.0)

    @model_validator(mode="after")
    def _check_std_plausible(self) -> "SimConfig":
        for attr in ("init_energy_std", "init_matter_std", "init_information_std"):
            if getattr(self, attr) > 0.5:
                raise ValueError(f"{attr} > 0.5 würde viele Werte außerhalb [0,1] erzeugen.")
        return self


@dataclass
class GridState:
    """Vollständiger Zustand eines 2-D-Gitters zu einem Zeitpunkt.

    Alle Felder sind float32-Arrays der Form (height, width) mit Werten in
    [0, 1]. ``tick`` zählt die Anzahl ausgeführter Simulationsschritte.

    Die Felder:
    - ``energy``     – Aktivierungspotenzial / Reaktionsfähigkeit
    - ``matter``     – lokale Dichte / Trägheit / Substrat
    - ``information``– komprimierbare Ordnung / lokaler Mustergehalt
    - ``coupling``   – Stärke der Nachbarschaftsverbindungen
    - ``reactivity`` – Wahrscheinlichkeit lokaler Transformationen
    - ``memory``     – sedimentierte Vergangenheit / lokale Hysterese
    - ``coherence``  – lokale Synchronität / Musterstabilität
    - ``flow_x``     – gerichtete Flussvektorkomponente (x)
    - ``flow_y``     – gerichtete Flussvektorkomponente (y)
    """

    energy: np.ndarray
    matter: np.ndarray
    information: np.ndarray
    coupling: np.ndarray
    reactivity: np.ndarray
    memory: np.ndarray
    coherence: np.ndarray
    flow_x: np.ndarray
    flow_y: np.ndarray
    # Meta-Regel-Felder (Epic 3): lokales Regelgenom
    genome_strength: np.ndarray   # lokale reaction_strength pro Zelle
    genome_threshold: np.ndarray  # lokaler reaction_energy_threshold pro Zelle
    tick: int = 0

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def initialize(
        cls,
        config: SimConfig,
        initial_condition: Optional["InitialCondition"] = None,
    ) -> "GridState":
        """Erzeuge einen neuen Anfangszustand aus ``config``.

        Zufallswerte werden mit ``config.seed`` initialisiert, damit Läufe
        vollständig reproduzierbar sind. Alle Werte werden auf [0, 1] geclippt.

        Parameters
        ----------
        config:
            Simulation configuration.
        initial_condition:
            Optional InitialCondition applied after random initialisation.
            Allows presets to inject structured seeds (gradients, spots, lines)
            without changing SimConfig. If None, the random baseline is used.
        """
        rng = np.random.default_rng(config.seed)
        H, W = config.height, config.width

        def _rand_field(mean: float, std: float) -> np.ndarray:
            arr = rng.normal(mean, std, (H, W)).astype(np.float32)
            return np.clip(arr, 0.0, 1.0)

        def _uniform_field() -> np.ndarray:
            return rng.uniform(0.0, 1.0, (H, W)).astype(np.float32)

        state = cls(
            energy=_rand_field(config.init_energy_mean, config.init_energy_std),
            matter=_rand_field(config.init_matter_mean, config.init_matter_std),
            information=_rand_field(config.init_information_mean, config.init_information_std),
            coupling=_uniform_field() * 0.5,
            reactivity=_uniform_field() * 0.6,
            memory=np.zeros((H, W), dtype=np.float32),
            coherence=_uniform_field() * 0.3,
            flow_x=np.zeros((H, W), dtype=np.float32),
            flow_y=np.zeros((H, W), dtype=np.float32),
            # Genome initialisieren: leichte Variation um den globalen Startwert
            genome_strength=np.clip(
                rng.normal(config.reaction_strength, 0.02, (H, W)).astype(np.float32),
                0.0, 1.0,
            ),
            genome_threshold=np.clip(
                rng.normal(config.reaction_energy_threshold, 0.05, (H, W)).astype(np.float32),
                0.0, 1.0,
            ),
            tick=0,
        )
        if initial_condition is not None:
            initial_condition.apply(state)
            for _f in (
                state.energy, state.matter, state.information, state.coupling,
                state.reactivity, state.memory, state.coherence,
            ):
                np.clip(_f, 0.0, 1.0, out=_f)
        return state

    # ------------------------------------------------------------------
    # Hilfsmethoden
    # ------------------------------------------------------------------

    def as_dict(self) -> Dict[str, np.ndarray]:
        """Gibt alle Zustandsfelder als Dictionary zurück (ohne tick, ohne Genome).

        Die Genome-Felder werden bewusst ausgelassen, da sie keine Primärfelder
        der Simulation sind und z.B. für Entropie-/Persistenz-Analysen nicht
        direkt verglichen werden sollen.
        """
        return {
            "energy": self.energy,
            "matter": self.matter,
            "information": self.information,
            "coupling": self.coupling,
            "reactivity": self.reactivity,
            "memory": self.memory,
            "coherence": self.coherence,
            "flow_x": self.flow_x,
            "flow_y": self.flow_y,
        }

    def genome_dict(self) -> Dict[str, np.ndarray]:
        """Gibt die Regelgenom-Felder als Dictionary zurück."""
        return {
            "genome_strength": self.genome_strength,
            "genome_threshold": self.genome_threshold,
        }

    def shape(self) -> tuple[int, int]:
        """Gibt (height, width) zurück."""
        return self.energy.shape  # type: ignore[return-value]

    def clip_all(self) -> None:
        """Clippt alle Felder in-place auf [0, 1].

        Wird am Ende jedes Ticks aufgerufen, damit kein Feld seinen Wertebereich
        verlässt. Verhindert kumulative Drift durch wiederholte Additionen.
        Genome werden ebenfalls geclippt, da ihre Werte dieselben Grenzen haben.
        """
        for arr in self.as_dict().values():
            np.clip(arr, 0.0, 1.0, out=arr)
        np.clip(self.genome_strength,  0.0, 1.0, out=self.genome_strength)
        np.clip(self.genome_threshold, 0.0, 1.0, out=self.genome_threshold)
