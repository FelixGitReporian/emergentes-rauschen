"""
experiments/configs.py – Vordefinierte Experiment-Konfigurationen (Epic 7).

Jedes Experiment testet einen anderen Aspekt des Systems und ist
mit einer wissenschaftlichen Frage verknüpft (Arbeitsmappe Kap. 4).

Experiment-Familien:
    STABILITY_SWEEP    – Wie stabil ist das System unter variierender Rauschstärke?
    REACTION_SWEEP     – Wie verändert der Reaktions-Schwellwert das Regime?
    META_EVOLUTION     – Wie entwickeln sich Regelgenome über Zeit?
    MEMORY_EFFECT      – Welchen Einfluss hat Gedächtnis-Zerfall?
    COUPLING_STUDY     – Wann entstehen Synchronisationsphänomene?
    PROTO_LIFE_SEARCH  – Unter welchen Parametern entstehen Proto-Kompartimente?
    CONSCIOUSNESS_SCAN – Wann sind Bewusstseins-Marker am höchsten?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from emergent_noise.core.state import SimConfig


@dataclass
class ExperimentConfig:
    """Vollständige Experiment-Definition.

    Attribute
    ----------
    name:
        Eindeutiger Name des Experiments.
    description:
        Kurze Beschreibung (Zweck + erwartetes Ergebnis).
    scientific_question:
        Die zugrundeliegende wissenschaftliche Frage.
    base_config:
        Basis SimConfig.
    param_sweeps:
        Dict von Parametername → Liste von Testwerten.
        Jede Kombination wird als eigener Lauf ausgeführt.
    n_ticks:
        Anzahl Ticks pro Lauf.
    repeat:
        Anzahl Wiederholungen (verschiedene Seeds).
    tags:
        Kategorisierungstags.
    """

    name: str
    description: str
    scientific_question: str
    base_config: SimConfig
    param_sweeps: Dict[str, List[Any]] = field(default_factory=dict)
    n_ticks: int = 200
    repeat: int = 3
    tags: List[str] = field(default_factory=list)


def _base() -> SimConfig:
    """Minimale Basis-Config für Experimente (kleines Grid, schnell)."""
    return SimConfig(height=32, width=32, seed=42)


# ──────────────────────────────────────────────────────────────────
# Vordefinierte Experimente
# ──────────────────────────────────────────────────────────────────

STABILITY_SWEEP = ExperimentConfig(
    name="stability_sweep",
    description=(
        "Variiert Rausch-Amplitude von 0 bis 0.2 und misst Persistenz, "
        "Entropie und Regime-Stabilität."
    ),
    scientific_question=(
        "Welche minimale Rauschstärke zerstört stabile Muster? "
        "Gibt es eine kritische Rausch-Schwelle (Bifurkation)?"
    ),
    base_config=_base(),
    param_sweeps={"noise_amplitude": [0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]},
    n_ticks=300,
    tags=["noise", "stability", "bifurcation"],
)

REACTION_SWEEP = ExperimentConfig(
    name="reaction_threshold_sweep",
    description=(
        "Variiert reaction_energy_threshold von 0.3 bis 0.95 und "
        "beobachtet Regime-Übergänge."
    ),
    scientific_question=(
        "Wie verändert der Reaktions-Schwellwert die emergenten Regime? "
        "Wann entsteht kritisches Verhalten (CRITICAL-Regime)?"
    ),
    base_config=_base(),
    param_sweeps={
        "reaction_energy_threshold": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    },
    n_ticks=250,
    tags=["reaction", "regime", "critical_transition"],
)

META_EVOLUTION = ExperimentConfig(
    name="meta_evolution_study",
    description=(
        "Aktiviert Meta-Regeln und misst Genome-Diversität, Novelty "
        "und Proto-Leben-Score über Zeit."
    ),
    scientific_question=(
        "Entstehen durch Regel-Evolution räumlich differenzierte Profile? "
        "Korreliert Genome-Diversität mit Proto-Leben-Score?"
    ),
    base_config=SimConfig(
        height=32, width=32, seed=42,
        meta_enabled=True, meta_mutation_rate=0.05, meta_mutation_strength=0.05,
    ),
    param_sweeps={"meta_mutation_rate": [0.01, 0.05, 0.1, 0.2]},
    n_ticks=500,
    tags=["meta_rules", "evolution", "genome", "novelty"],
)

MEMORY_EFFECT = ExperimentConfig(
    name="memory_decay_study",
    description=(
        "Variiert memory_decay von 0.9 bis 0.999 und misst "
        "Systemgedächtnis und Hysterese."
    ),
    scientific_question=(
        "Welche Rolle spielt Gedächtnis-Zerfall für die Entstehung "
        "persistenter Strukturen? Schwächeres Gedächtnis → mehr Vergessen?"
    ),
    base_config=_base(),
    param_sweeps={"memory_decay": [0.9, 0.95, 0.97, 0.99, 0.999]},
    n_ticks=400,
    tags=["memory", "persistence", "hysteresis"],
)

COUPLING_STUDY = ExperimentConfig(
    name="coupling_synchronization",
    description=(
        "Variiert coupling_gain und misst Kohärenz-Synchronisation, "
        "MI zwischen Feldern und Phasenübergänge."
    ),
    scientific_question=(
        "Wann entsteht globale Synchronisation? "
        "Gibt es einen Coupling-Schwellwert für Ordnungs-Unordnungs-Übergang?"
    ),
    base_config=_base(),
    param_sweeps={"coupling_gain": [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]},
    n_ticks=300,
    tags=["coupling", "synchronization", "coherence", "phase_transition"],
)

PROTO_LIFE_SEARCH = ExperimentConfig(
    name="proto_life_parameter_search",
    description=(
        "Grid-Search über reaction_strength × matter_deposition_rate "
        "nach maximalen Proto-Kompartiment-Scores."
    ),
    scientific_question=(
        "Unter welchen Parameterkombinationen entstehen stabile, "
        "abgegrenzte proto-zelluläre Strukturen?"
    ),
    base_config=_base(),
    param_sweeps={
        "reaction_strength": [0.05, 0.1, 0.15, 0.2],
        "matter_deposition_rate": [0.001, 0.005, 0.01, 0.02],
    },
    n_ticks=300,
    tags=["proto_life", "compartments", "emergence"],
)

CONSCIOUSNESS_SCAN = ExperimentConfig(
    name="consciousness_marker_scan",
    description=(
        "Variiert mehrere Parameter und misst Φ-Proxy, Active-Inference, "
        "Global-Workspace und Proto-Leben-Score."
    ),
    scientific_question=(
        "Welche Parameter maximieren Bewusstseins-Proxies? "
        "Korrelieren Φ-Proxy und Proto-Leben-Score miteinander?"
    ),
    base_config=SimConfig(
        height=32, width=32, seed=42, meta_enabled=True,
    ),
    param_sweeps={
        "coupling_gain": [0.005, 0.02, 0.05],
        "noise_amplitude": [0.01, 0.05, 0.1],
    },
    n_ticks=400,
    tags=["consciousness", "phi", "active_inference", "proto_life"],
)

# Alle vordefinierten Experimente als Dict
ALL_EXPERIMENTS: Dict[str, ExperimentConfig] = {
    exp.name: exp
    for exp in [
        STABILITY_SWEEP, REACTION_SWEEP, META_EVOLUTION,
        MEMORY_EFFECT, COUPLING_STUDY, PROTO_LIFE_SEARCH,
        CONSCIOUSNESS_SCAN,
    ]
}
