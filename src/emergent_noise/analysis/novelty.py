"""
analysis/novelty.py – Neuheitsmetrik und Verhaltens-Diversität.

Neuheit misst, wie verschieden der aktuelle Zustand von einem Referenz-
Ensemble früherer Zustände ist. Hohe Neuheit deutet auf neue, ungesehene
Regime hin. Niedrige Neuheit bedeutet, das System wiederholt bekannte Muster.

Implementierte Metriken:

1. BehaviorVector   – Komprimierter Zustandsvektor für Vergleiche.
2. NoveltyTracker   – Verfolgt Novelty über ein Archiv vergangener Zustände.
3. genome_diversity – Räumliche Diversität der Regelgenom-Verteilung.
4. genome_entropy   – Shannon-Entropie der Genome-Wert-Verteilung.

Orientierung an Arbeitsmappe Kap. 9.3 (Selektionskriterien) und
Kap. 7.2 (Parameter-Kandidaten-Tracking).

Wissenschaftliche Vorsicht:
    Novelty-Metriken messen statistische Abweichung, keine semantische
    Neuheit. Ein hoher Novelty-Score bedeutet «statistisch ungewohnt»,
    nicht «biologisch interessant» oder «bewusst erlebt».
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List

import numpy as np

from emergent_noise.core.state import GridState


@dataclass
class BehaviorVector:
    """Komprimierter Verhaltensvektor eines GridState.

    Fasst den Zustand als niedrig-dimensionalen Vektor zusammen:
    Für jedes Feld werden mean, std, aktive_fraktion berechnet.
    Dadurch werden ~27 Werte statt H×W Werte verglichen.

    Attribute
    ----------
    tick:
        Tick des erfassten Zustands.
    values:
        1-D float-Array mit den komprimierten Kennzahlen.
    field_names:
        Namen der Felder in der Reihenfolge wie in ``values``.
    """

    tick: int
    values: np.ndarray
    field_names: List[str]

    @classmethod
    def from_state(cls, state: GridState) -> "BehaviorVector":
        """Erzeuge BehaviorVector aus GridState.

        Für jedes Feld werden berechnet:
        - mean (globaler Mittelwert)
        - std  (globale Standardabweichung)
        - active_fraction (Anteil Zellen > 0.5)

        Zusätzlich: genome_strength.mean(), genome_threshold.mean()
        """
        fields = state.as_dict()
        vals: List[float] = []
        names: List[str] = []
        for fname, arr in fields.items():
            vals.extend([float(arr.mean()), float(arr.std()), float((arr > 0.5).mean())])
            names.extend([f"{fname}.mean", f"{fname}.std", f"{fname}.active"])
        # Genome-Zusammenfassung
        vals.extend([
            float(state.genome_strength.mean()),
            float(state.genome_strength.std()),
            float(state.genome_threshold.mean()),
            float(state.genome_threshold.std()),
        ])
        names.extend([
            "genome_strength.mean", "genome_strength.std",
            "genome_threshold.mean", "genome_threshold.std",
        ])
        return cls(tick=state.tick, values=np.array(vals, dtype=np.float32), field_names=names)


def _vector_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euklidische Distanz zwischen zwei Verhaltensvektoren (normalisiert)."""
    return float(np.sqrt(np.sum((a - b) ** 2)) / max(len(a), 1))


class NoveltyTracker:
    """Verfolgt die Novelty eines Systems über ein Archiv vergangener Zustände.

    Novelty = mittlere Distanz zum k-nächsten-Nachbar im Archiv.
    Große Abstände → das System ist in unbekannten Regionen des Zustandsraums.

    Parameters
    ----------
    archive_size:
        Maximale Anzahl gespeicherter BehaviorVectors.
    k_neighbors:
        Anzahl nächster Nachbarn für Novelty-Berechnung.
    """

    def __init__(self, archive_size: int = 50, k_neighbors: int = 5) -> None:
        self.archive_size = archive_size
        self.k_neighbors = k_neighbors
        self._archive: Deque[BehaviorVector] = deque(maxlen=archive_size)
        self.novelty_history: List[dict] = []

    def update(self, state: GridState) -> float:
        """Berechne Novelty des aktuellen Zustands und füge ihn ins Archiv ein.

        Parameters
        ----------
        state:
            Aktueller GridState.

        Returns
        -------
        Novelty-Score (float ≥ 0). 0 = identisch mit bekannten Zuständen.
        """
        current = BehaviorVector.from_state(state)
        novelty = self._compute_novelty(current)
        self._archive.append(current)
        self.novelty_history.append({"tick": state.tick, "novelty": novelty})
        return novelty

    def _compute_novelty(self, vec: BehaviorVector) -> float:
        """Mittlere Distanz zu den k nächsten Archiv-Nachbarn."""
        if len(self._archive) == 0:
            return 0.0
        distances = sorted(
            [_vector_distance(vec.values, a.values) for a in self._archive]
        )
        k = min(self.k_neighbors, len(distances))
        return float(np.mean(distances[:k]))

    @property
    def current_novelty(self) -> float:
        """Letzter berechneter Novelty-Score."""
        if not self.novelty_history:
            return 0.0
        return self.novelty_history[-1]["novelty"]


def genome_diversity(state: GridState) -> Dict[str, float]:
    """Berechne räumliche Diversität der Regelgenom-Felder.

    Misst, wie verschieden die Regelprofile über den Grid verteilt sind:
    - ``strength_std``   – Standardabweichung von genome_strength
    - ``threshold_std``  – Standardabweichung von genome_threshold
    - ``strength_range`` – max - min von genome_strength
    - ``threshold_range``– max - min von genome_threshold
    - ``joint_entropy``  – kombinierte Entropie beider Genome-Felder
      (normalisiert auf [0, 1])

    Hohe Diversität deutet auf räumlich differenziertes Regelprofil hin —
    möglicher Indikator für emergente Spezialisierung.

    Parameters
    ----------
    state:
        GridState mit Genome-Feldern.

    Returns
    -------
    Dictionary mit Diversitäts-Metriken.
    """
    gs = state.genome_strength
    gt = state.genome_threshold

    # Kombinierte 2-D-Histogramm-Entropie
    joint, _, _ = np.histogram2d(
        gs.ravel(), gt.ravel(), bins=16, range=[[0, 1], [0, 1]]
    )
    joint = joint / joint.sum()
    mask = joint > 0
    h_joint = float(-np.sum(joint[mask] * np.log2(joint[mask])))
    h_max = np.log2(16 * 16)  # maximale Entropie bei 16×16 Bins
    joint_entropy_norm = float(h_joint / h_max) if h_max > 0 else 0.0

    return {
        "strength_mean":    round(float(gs.mean()), 5),
        "strength_std":     round(float(gs.std()), 5),
        "strength_range":   round(float(gs.max() - gs.min()), 5),
        "threshold_mean":   round(float(gt.mean()), 5),
        "threshold_std":    round(float(gt.std()), 5),
        "threshold_range":  round(float(gt.max() - gt.min()), 5),
        "joint_entropy":    round(joint_entropy_norm, 5),
    }


def genome_entropy(state: GridState, n_bins: int = 16) -> float:
    """Normalisierte Shannon-Entropie der genome_strength-Verteilung.

    Misst, wie gleichmäßig die Reaktionsstärken über alle Zellen verteilt sind.
    Hohe Entropie → diverse Stärkeverteilung. Niedrig → homogenes Profil.

    Parameters
    ----------
    state:
        GridState mit Genome-Feldern.
    n_bins:
        Histogramm-Auflösung.

    Returns
    -------
    Normalisierte Entropie in [0, 1].
    """
    hist, _ = np.histogram(state.genome_strength, bins=n_bins, range=(0.0, 1.0))
    hist = hist / hist.sum()
    mask = hist > 0
    h = float(-np.sum(hist[mask] * np.log2(hist[mask])))
    h_max = np.log2(n_bins)
    return float(h / h_max) if h_max > 0 else 0.0
