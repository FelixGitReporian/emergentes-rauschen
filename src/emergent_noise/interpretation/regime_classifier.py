"""
interpretation/regime_classifier.py – Heuristische Regime-Erkennung.

Ein Regime ist ein kohärenter, wiederkehrender Zustandstyp im Phasenraum der
Simulation. Dieser Classifier erkennt Regime aus Feldmetriken — ohne Machine
Learning, rein regelbasiert und transparent.

Erkannte Regime-Typen:

- QUIESCENT      : Niedriges Energieniveau, geringe Aktivität, kaum Muster.
- DIFFUSE        : Hohe Entropie, viel Rauschen, keine stabilen Cluster.
- CLUSTERED      : Mehrere separate aktive Regionen, mittlere Kohärenz.
- VORTEX         : Aktiver Fluss, Rotation sichtbar (flow-Magnitude > Schwelle).
- COHERENT       : Hohe Kohärenz, wenige Cluster (eine dominante Struktur).
- FILAMENTARY    : Hohe Randkomplexität, elongierte Strukturen.
- CRITICAL       : Nahe Phasenübergang (erhöhte Suszeptibilität, kritisches Verlangsamen).
- COMPLEX        : Mehrere Eigenschaften gleichzeitig (Sammelbegriff).

Wissenschaftliche Vorsicht:
    Diese Klassifikation ist heuristisch und regelbasiert. Die Schwellwerte
    sind Startpunkte, keine universellen Konstanten. Regime-Labels sind
    Lesarten, keine ontologischen Fakten.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

import numpy as np


class RegimeType(str, Enum):
    """Bekannte Regime-Typen."""
    QUIESCENT   = "quiescent"
    DIFFUSE     = "diffuse"
    CLUSTERED   = "clustered"
    VORTEX      = "vortex"
    COHERENT    = "coherent"
    FILAMENTARY = "filamentary"
    CRITICAL    = "critical"
    COMPLEX     = "complex"
    UNKNOWN     = "unknown"


@dataclass
class RegimeResult:
    """Ergebnis der Regime-Klassifikation für einen Tick."""

    tick: int
    primary_regime: RegimeType
    secondary_regimes: List[RegimeType]
    confidence: float             # [0, 1] – heuristischer Konfidenz-Score
    evidence: Dict[str, float]    # Gemessene Indikatoren
    description: str              # Kurzbeschreibung in natürlicher Sprache


@dataclass
class RegimeSignals:
    """Komprimierte Signale aus Feldmetriken für die Regime-Erkennung.

    Wird von ``classify_regime`` aus rohen Feldern berechnet.
    """
    energy_mean: float
    energy_std: float
    coherence_mean: float
    flow_magnitude: float         # Mittlere |flow| über Grid
    n_clusters: int               # Cluster im energy-Feld (threshold=0.5)
    boundary_complexity: float    # Randkomplexität des energy-Feldes
    elongation: float             # Elongation des größten Clusters
    entropy_energy: float         # Normalisierte Entropie des energy-Feldes
    susceptibility: float         # Phasenübergangs-Suszeptibilität
    persistence_energy: float     # Persistenz des energy-Feldes


def _signals_from_fields(
    fields: Dict[str, np.ndarray],
    clusters_energy: int = 0,
    boundary_complexity: float = 0.0,
    elongation: float = 1.0,
    entropy_energy: float = 0.5,
    susceptibility: float = 0.0,
    persistence_energy: float = 1.0,
) -> RegimeSignals:
    """Extrahiere komprimierte Signale aus Feld-Dictionary."""
    energy = fields.get("energy", np.zeros((1, 1)))
    coherence = fields.get("coherence", np.zeros((1, 1)))
    fx = fields.get("flow_x", np.zeros((1, 1)))
    fy = fields.get("flow_y", np.zeros((1, 1)))
    flow_mag = float(np.sqrt(fx ** 2 + fy ** 2).mean())

    return RegimeSignals(
        energy_mean=float(energy.mean()),
        energy_std=float(energy.std()),
        coherence_mean=float(coherence.mean()),
        flow_magnitude=flow_mag,
        n_clusters=clusters_energy,
        boundary_complexity=boundary_complexity,
        elongation=elongation,
        entropy_energy=entropy_energy,
        susceptibility=susceptibility,
        persistence_energy=persistence_energy,
    )


def classify_regime(
    tick: int,
    fields: Dict[str, np.ndarray],
    clusters_energy: int = 0,
    boundary_complexity: float = 0.0,
    elongation: float = 1.0,
    entropy_energy: float = 0.5,
    susceptibility: float = 0.0,
    persistence_energy: float = 1.0,
) -> RegimeResult:
    """Klassifiziere das aktuelle Regime aus Feldmetriken.

    Parameters
    ----------
    tick:
        Aktueller Simulationsschritt.
    fields:
        Dictionary {feldname: array} aus ``GridState.as_dict()``.
    clusters_energy:
        Anzahl Cluster im energy-Feld (aus ``find_clusters``).
    boundary_complexity:
        Rand/Fläche-Verhältnis (aus ``compute_morphology``).
    elongation:
        Elongation des größten Clusters (aus ``compute_morphology``).
    entropy_energy:
        Normalisierte Entropie des energy-Feldes (aus ``field_entropy``).
    susceptibility:
        Phasenübergangs-Suszeptibilität (aus ``compute_phase_indicator``).
    persistence_energy:
        Persistenz des energy-Feldes (aus ``PersistenceTracker``).

    Returns
    -------
    RegimeResult mit primary_regime, secondary_regimes, confidence, evidence.
    """
    sig = _signals_from_fields(
        fields, clusters_energy, boundary_complexity,
        elongation, entropy_energy, susceptibility, persistence_energy,
    )

    scores: Dict[RegimeType, float] = {r: 0.0 for r in RegimeType}

    # --- QUIESCENT: niedrige Energie, geringe Varianz, keine Cluster ---
    if sig.energy_mean < 0.25:
        scores[RegimeType.QUIESCENT] += 0.6
    if sig.energy_std < 0.03:
        scores[RegimeType.QUIESCENT] += 0.3
    if sig.n_clusters == 0:
        scores[RegimeType.QUIESCENT] += 0.2

    # --- DIFFUSE: hohe Entropie, viele kleine Cluster ---
    if sig.entropy_energy > 0.7:
        scores[RegimeType.DIFFUSE] += 0.5
    if sig.n_clusters > 10:
        scores[RegimeType.DIFFUSE] += 0.3
    if sig.energy_std > 0.08 and sig.coherence_mean < 0.2:
        scores[RegimeType.DIFFUSE] += 0.3

    # --- CLUSTERED: moderate Energie, mehrere Cluster, mittlere Kohärenz ---
    if 2 <= sig.n_clusters <= 10:
        scores[RegimeType.CLUSTERED] += 0.5
    if 0.2 < sig.energy_mean < 0.7:
        scores[RegimeType.CLUSTERED] += 0.2
    if sig.coherence_mean > 0.2:
        scores[RegimeType.CLUSTERED] += 0.2

    # --- VORTEX: aktiver Fluss ---
    if sig.flow_magnitude > 0.01:
        scores[RegimeType.VORTEX] += 0.4
    if sig.flow_magnitude > 0.03:
        scores[RegimeType.VORTEX] += 0.4

    # --- COHERENT: hohe Kohärenz, 1-2 dominante Cluster ---
    if sig.coherence_mean > 0.3:
        scores[RegimeType.COHERENT] += 0.5
    if 1 <= sig.n_clusters <= 3:
        scores[RegimeType.COHERENT] += 0.3
    if sig.persistence_energy > 0.998:
        scores[RegimeType.COHERENT] += 0.2

    # --- FILAMENTARY: hohe Randkomplexität, hohe Elongation ---
    if sig.boundary_complexity > 0.4:
        scores[RegimeType.FILAMENTARY] += 0.5
    if sig.elongation > 2.5:
        scores[RegimeType.FILAMENTARY] += 0.4

    # --- CRITICAL: hohe Suszeptibilität (nahe Phasenübergang) ---
    if sig.susceptibility > 0.04:
        scores[RegimeType.CRITICAL] += 0.5
    if sig.susceptibility > 0.07:
        scores[RegimeType.CRITICAL] += 0.4
    if sig.persistence_energy < 0.99:
        scores[RegimeType.CRITICAL] += 0.2

    # --- COMPLEX: viele gleichzeitig hohe Scores ---
    active_scores = [s for r, s in scores.items() if r not in (RegimeType.COMPLEX, RegimeType.UNKNOWN) and s > 0.3]
    if len(active_scores) >= 3:
        scores[RegimeType.COMPLEX] += 0.4 * len(active_scores)

    # Primär + Sekundär bestimmen
    scores.pop(RegimeType.UNKNOWN)
    sorted_regimes = sorted(scores.items(), key=lambda x: -x[1])
    primary = sorted_regimes[0][0] if sorted_regimes[0][1] > 0.0 else RegimeType.UNKNOWN
    secondary = [r for r, s in sorted_regimes[1:4] if s > 0.25]

    # Konfidenz = normalisierter Lead des primären Scores
    top_score = sorted_regimes[0][1]
    second_score = sorted_regimes[1][1] if len(sorted_regimes) > 1 else 0.0
    max_possible = 1.5
    confidence = float(np.clip(top_score / max_possible, 0.0, 1.0))
    if top_score > 0 and second_score / max(top_score, 1e-9) > 0.7:
        confidence *= 0.7  # Unsicherheit wenn zwei Regime ähnlich stark

    evidence = {
        "energy_mean": round(sig.energy_mean, 4),
        "energy_std": round(sig.energy_std, 4),
        "coherence_mean": round(sig.coherence_mean, 4),
        "flow_magnitude": round(sig.flow_magnitude, 5),
        "n_clusters": sig.n_clusters,
        "boundary_complexity": round(sig.boundary_complexity, 4),
        "elongation": round(sig.elongation, 3),
        "entropy_energy": round(sig.entropy_energy, 4),
        "susceptibility": round(sig.susceptibility, 5),
        "persistence_energy": round(sig.persistence_energy, 5),
    }

    return RegimeResult(
        tick=tick,
        primary_regime=primary,
        secondary_regimes=secondary,
        confidence=round(confidence, 3),
        evidence=evidence,
        description=_describe(primary, sig),
    )


def _describe(regime: RegimeType, sig: RegimeSignals) -> str:
    """Erzeuge eine kurze natürlichsprachliche Beschreibung des Regimes."""
    descriptions = {
        RegimeType.QUIESCENT: (
            f"Ruhezustand: niedrige Energie ({sig.energy_mean:.2f}), kaum Aktivität. "
            "Das System befindet sich nahe seinem energetischen Minimum."
        ),
        RegimeType.DIFFUSE: (
            f"Diffuses Regime: hohe Entropie ({sig.entropy_energy:.2f}), "
            "viele kleine Aktivitätsbereiche ohne stabile Struktur. "
            "Rauschen dominiert gegenüber Ordnung."
        ),
        RegimeType.CLUSTERED: (
            f"Cluster-Regime: {sig.n_clusters} separate aktive Regionen erkennbar. "
            "Lokale Ordnung bei globaler Fragmentierung — mögliche Vorläufer "
            "von Kompartimentierung."
        ),
        RegimeType.VORTEX: (
            f"Wirbelregime: aktives Flussfeld (|flow|≈{sig.flow_magnitude:.4f}). "
            "Gerichtete Zirkulation — deutet auf Energietransport "
            "und Rotation hin."
        ),
        RegimeType.COHERENT: (
            f"Kohärentes Regime: hohe Kohärenz ({sig.coherence_mean:.2f}), "
            f"{sig.n_clusters} dominante Struktur(en). "
            "Das System hat einen stabilen, geordneten Attraktor erreicht."
        ),
        RegimeType.FILAMENTARY: (
            f"Filamentäres Regime: Randkomplexität={sig.boundary_complexity:.2f}, "
            f"Elongation={sig.elongation:.1f}. "
            "Netzwerk- oder fadenförmige Strukturen — "
            "könnte auf reaktions-diffusions-artige Musterbildung hindeuten."
        ),
        RegimeType.CRITICAL: (
            f"Kritisches Regime: Suszeptibilität={sig.susceptibility:.4f}. "
            "Das System befindet sich nahe einem Phasenübergang. "
            "Hohe Fluktuation und potentielle Instabilität."
        ),
        RegimeType.COMPLEX: (
            "Komplexes Regime: mehrere Regime-Eigenschaften gleichzeitig aktiv. "
            "Mögliche Koexistenz verschiedener Dynamiken oder Übergangsphase."
        ),
        RegimeType.UNKNOWN: (
            "Unbekanntes Regime: keine dominante Charakteristik erkannt."
        ),
    }
    return descriptions.get(regime, "Unbekanntes Regime.")
