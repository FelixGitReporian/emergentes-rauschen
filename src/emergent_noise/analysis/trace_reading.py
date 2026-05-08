"""
analysis/trace_reading.py – Spurenlese-Engine.

Die Spurenlese-Engine integriert alle Analyse-Module zu einem einzigen,
strukturierten Lese-Akt: Sie nimmt den aktuellen GridState entgegen und
erzeugt einen vollständigen ``TraceReport`` — ein JSON-fähiges Objekt mit
Feldmetriken, Morphologie, MI, Regime-Klassifikation und Narrativ.

Architektur:
    1. Feldstatistiken    (attractors.field_summary)
    2. Morphologie        (morphology.compute_morphology) für energy
    3. Mutual Information (mutual_information.mi_matrix) für key-Felder
    4. Regime-Erkennung   (regime_classifier.classify_regime)
    5. Narrativ           (narratives.build_narrative)
    → TraceReport (JSON-fähig via .to_dict())

Orientierung an Arbeitsmappe Kap. 11.3 (Spurenlesen als Erkenntnisform):
    «Muster erkennen → Historische Signatur suchen → Interpretation anbieten»

Wissenschaftliche Vorsicht:
    Ein TraceReport ist ein strukturiertes Analyseergebnis, kein Beweis.
    Die Konfidenz-Werte sind heuristische Schätzungen.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

import numpy as np

from emergent_noise.analysis.attractors import (
    ClusterResult,
    FieldSummary,
    PersistenceTracker,
    compute_phase_indicator,
    field_summary,
    find_clusters,
)
from emergent_noise.analysis.morphology import MorphologyResult, compute_morphology
from emergent_noise.analysis.mutual_information import mi_matrix
from emergent_noise.analysis.trace_metrics import (
    TraceMetricsSnapshot,
    compute_trace_metrics,
    MemoryEntropyTracker,
    ClusterLifetimeTracker,
)
from emergent_noise.interpretation.narratives import Narrative, build_narrative
from emergent_noise.interpretation.regime_classifier import RegimeResult, classify_regime


_MI_FIELDS = ("energy", "information", "coherence", "coupling", "memory")


@dataclass
class TraceReport:
    """Vollständiger Spurenbericht für einen Simulationszeitpunkt.

    Alle Felder sind JSON-serialisierbar (via .to_dict()).
    """

    tick: int
    field_summaries: Dict[str, Dict[str, float]]
    morphology: Dict[str, Any]           # MorphologyResult für energy
    mi_matrix: Dict[str, float]          # Paarweise MI (key="a|b")
    clusters: Dict[str, Any]             # ClusterResult für energy
    phase: Dict[str, Any]                # PhaseIndicator
    regime: Dict[str, Any]               # RegimeResult
    narrative: Dict[str, Any]            # Narrative
    trace_metrics: Dict[str, Any] = field(default_factory=dict)  # Epic 13

    def to_dict(self) -> dict:
        """Exportiere als vollständig JSON-fähiges Dictionary."""
        return {
            "tick": self.tick,
            "field_summaries": self.field_summaries,
            "morphology": self.morphology,
            "mi_matrix": self.mi_matrix,
            "clusters": self.clusters,
            "phase": self.phase,
            "regime": {
                **self.regime,
                "primary_regime": self.regime.get("primary_regime", ""),
                "secondary_regimes": [
                    r if isinstance(r, str) else r.value
                    for r in self.regime.get("secondary_regimes", [])
                ],
            },
            "narrative": self.narrative,
            "trace_metrics": self.trace_metrics,
        }

    def to_json(self, indent: int = 2) -> str:
        """Exportiere als JSON-String."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def read_traces(
    tick: int,
    fields: Dict[str, np.ndarray],
    persistence_tracker: PersistenceTracker | None = None,
    prev_memory: np.ndarray | None = None,
    prev_energy: np.ndarray | None = None,
    entropy_tracker: MemoryEntropyTracker | None = None,
    lifetime_tracker: ClusterLifetimeTracker | None = None,
) -> TraceReport:
    """Führe vollständige Spurenanalyse für den aktuellen Zustand durch.

    Parameters
    ----------
    tick:
        Aktueller Simulationsschritt.
    fields:
        Dictionary {feldname: array} aus ``GridState.as_dict()``.
    persistence_tracker:
        Optionaler PersistenceTracker — wenn None, werden Persistenzwerte
        auf 1.0 gesetzt.

    Returns
    -------
    TraceReport mit allen Analyseergebnissen.
    """
    # 1. Feldstatistiken
    summaries = {
        name: {
            "mean": round(float(arr.mean()), 5),
            "std": round(float(arr.std()), 5),
            "min": round(float(arr.min()), 5),
            "max": round(float(arr.max()), 5),
            "active_fraction": round(float((arr > 0.5).mean()), 4),
        }
        for name, arr in fields.items()
    }

    # 2. Morphologie (energy)
    energy = fields.get("energy", np.zeros((8, 8)))
    morph: MorphologyResult = compute_morphology("energy", energy, tick=tick)
    morph_dict = {
        "field_name": morph.field_name,
        "tick": morph.tick,
        "active_fraction": round(morph.active_fraction, 4),
        "n_components": morph.n_components,
        "n_holes": morph.n_holes,
        "euler_number": morph.euler_number,
        "boundary_complexity": round(morph.boundary_complexity, 4),
        "elongation": round(morph.elongation, 3),
        "compactness": round(morph.compactness, 4),
    }

    # 3. Mutual Information (key-Felder)
    mi_fields = {k: fields[k] for k in _MI_FIELDS if k in fields}
    mi_raw = mi_matrix(mi_fields, n_bins=12)
    mi_dict = {f"{a}|{b}": round(v, 4) for (a, b), v in mi_raw.items() if a < b}

    # 4. Cluster (energy)
    clusters: ClusterResult = find_clusters("energy", energy, threshold=0.5)
    cluster_dict = {
        "field_name": clusters.field_name,
        "threshold": clusters.threshold,
        "n_clusters": clusters.n_clusters,
        "mean_cluster_size": round(clusters.mean_cluster_size, 2),
        "largest_cluster_size": clusters.largest_cluster_size,
        "cluster_fraction": round(clusters.cluster_fraction, 4),
    }

    # 5. Phase-Indikator
    phase = compute_phase_indicator(tick, fields)
    phase_dict = {
        "tick": phase.tick,
        "energy_variance": round(phase.energy_variance, 6),
        "information_variance": round(phase.information_variance, 6),
        "susceptibility": round(phase.susceptibility, 6),
        "near_transition": bool(phase.near_transition),
    }

    # 6. Persistenz
    persistence = persistence_tracker.persistence if persistence_tracker else {}
    persistence_energy = persistence.get("energy", 1.0)

    # 7. Regime-Klassifikation
    from emergent_noise.analysis.entropy import field_entropy
    entropy_energy = field_entropy(energy)

    regime: RegimeResult = classify_regime(
        tick=tick,
        fields=fields,
        clusters_energy=clusters.n_clusters,
        boundary_complexity=morph.boundary_complexity,
        elongation=morph.elongation,
        entropy_energy=entropy_energy,
        susceptibility=phase.susceptibility,
        persistence_energy=persistence_energy,
    )
    regime_dict = {
        "tick": regime.tick,
        "primary_regime": regime.primary_regime.value,
        "secondary_regimes": [r.value for r in regime.secondary_regimes],
        "confidence": regime.confidence,
        "evidence": regime.evidence,
        "description": regime.description,
    }

    # 8. Narrativ
    narrative: Narrative = build_narrative(regime)
    narrative_dict = {
        "tick": narrative.tick,
        "observed_regime": narrative.observed_regime,
        "interpretations": narrative.interpretations,
        "likely_past": narrative.likely_past,
        "likely_future": narrative.likely_future,
        "confidence": narrative.confidence,
        "scientific_caveat": narrative.scientific_caveat,
    }

    # 9. Epic 13 trace metrics
    tm_snap = compute_trace_metrics(
        tick=tick,
        fields=fields,
        prev_memory=prev_memory,
        prev_energy=prev_energy,
        entropy_tracker=entropy_tracker,
        lifetime_tracker=lifetime_tracker,
    )
    tm_dict = tm_snap.to_dict()

    return TraceReport(
        tick=tick,
        field_summaries=summaries,
        morphology=morph_dict,
        mi_matrix=mi_dict,
        clusters=cluster_dict,
        phase=phase_dict,
        regime=regime_dict,
        narrative=narrative_dict,
        trace_metrics=tm_dict,
    )
