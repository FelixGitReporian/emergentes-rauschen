"""
analysis/attractors.py – Persistenz, Cluster und Phasenübergangs-Indikatoren.

Dieses Modul implementiert Analysewerkzeuge für emergente Strukturen:

1. PersistenceTracker: Verfolgt, wie stabil Felder über Zeit sind.
2. find_clusters: Erkennt zusammenhängende Regionen über einem Schwellwert.
3. phase_transition_indicator: Misst Nähe zu Phasenübergängen via Varianz-Peak.
4. field_summary: Schnelle Statistikzusammenfassung eines Feldes.

Wissenschaftliche Vorsicht:
    Diese Metriken sind erste Indikatoren, keine bewiesenen Attraktornachweise.
    Ein hoher Persistenzwert deutet auf stabile Strukturen hin, beweist aber
    keine Attraktor-Eigenschaft im dynamischen-Systeme-Sinne.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from scipy.ndimage import label


# ------------------------------------------------------------------
# Statistik-Summary
# ------------------------------------------------------------------


@dataclass
class FieldSummary:
    """Deskriptive Statistik eines einzelnen Feldes."""

    name: str
    mean: float
    std: float
    min: float
    max: float
    active_fraction: float  # Anteil Zellen > 0.5


def field_summary(name: str, arr: np.ndarray, threshold: float = 0.5) -> FieldSummary:
    """Berechne deskriptive Statistik für ein 2-D-Feld.

    Parameters
    ----------
    name:
        Feldname (für Ausgabe).
    arr:
        2-D float-Array.
    threshold:
        Schwellwert für ``active_fraction``.
    """
    return FieldSummary(
        name=name,
        mean=float(arr.mean()),
        std=float(arr.std()),
        min=float(arr.min()),
        max=float(arr.max()),
        active_fraction=float((arr > threshold).mean()),
    )


# ------------------------------------------------------------------
# Cluster-Erkennung
# ------------------------------------------------------------------


@dataclass
class ClusterResult:
    """Ergebnis einer Cluster-Analyse für ein Feld."""

    field_name: str
    threshold: float
    n_clusters: int
    mean_cluster_size: float
    largest_cluster_size: int
    cluster_fraction: float  # Anteil Zellen in Clustern


def find_clusters(
    name: str, arr: np.ndarray, threshold: float = 0.6
) -> ClusterResult:
    """Erkenne zusammenhängende Regionen über ``threshold`` (4-Connectivity).

    Nutzt ``scipy.ndimage.label`` für 2-D-Connected-Components.

    Parameters
    ----------
    name:
        Feldname.
    arr:
        2-D float-Array mit Werten in [0, 1].
    threshold:
        Zellen mit Wert > threshold gelten als 'aktiv'.

    Returns
    -------
    ClusterResult mit Anzahl, mittlerer Größe und größtem Cluster.
    """
    binary = arr > threshold
    labeled, n_clusters = label(binary)

    if n_clusters == 0:
        return ClusterResult(
            field_name=name,
            threshold=threshold,
            n_clusters=0,
            mean_cluster_size=0.0,
            largest_cluster_size=0,
            cluster_fraction=0.0,
        )

    sizes = [int((labeled == i).sum()) for i in range(1, n_clusters + 1)]
    return ClusterResult(
        field_name=name,
        threshold=threshold,
        n_clusters=n_clusters,
        mean_cluster_size=float(np.mean(sizes)),
        largest_cluster_size=int(max(sizes)),
        cluster_fraction=float(binary.mean()),
    )


# ------------------------------------------------------------------
# Persistenz-Tracker
# ------------------------------------------------------------------


class PersistenceTracker:
    """Verfolgt die zeitliche Stabilität von Feldern über mehrere Ticks.

    Persistenz = mittlere zeitliche Korrelation zwischen aufeinanderfolgenden
    Zuständen. Hohe Persistenz → stabile Struktur (Attraktor-Kandidat).
    Niedrige Persistenz → turbulente / chaotische Phase.

    Parameters
    ----------
    window:
        Anzahl der Ticks, über die der gleitende Mittelwert berechnet wird.
    """

    def __init__(self, window: int = 10) -> None:
        self.window = window
        self._history: Dict[str, List[np.ndarray]] = {}
        self.persistence: Dict[str, float] = {}

    def update(self, fields: Dict[str, np.ndarray]) -> None:
        """Füge aktuellen Zustand hinzu und berechne Persistenz.

        Persistenz wird als mittlere pixelweise Korrelation zwischen
        aktuellem und vorherigem Snapshot definiert:
        corr = 1 - mean(|f_t - f_{t-1}|) / max_possible_change

        Parameters
        ----------
        fields:
            Dictionary {feldname: array}, z.B. aus GridState.as_dict().
        """
        for name, arr in fields.items():
            if name not in self._history:
                self._history[name] = []

            hist = self._history[name]
            hist.append(arr.copy())
            if len(hist) > self.window:
                hist.pop(0)

            if len(hist) >= 2:
                diffs = [np.mean(np.abs(hist[i] - hist[i - 1])) for i in range(1, len(hist))]
                self.persistence[name] = float(1.0 - np.mean(diffs))
            else:
                self.persistence[name] = 1.0

    def most_stable(self) -> str | None:
        """Gibt den Namen des stabilsten Feldes zurück."""
        if not self.persistence:
            return None
        return max(self.persistence, key=lambda k: self.persistence[k])

    def least_stable(self) -> str | None:
        """Gibt den Namen des instabilsten Feldes zurück."""
        if not self.persistence:
            return None
        return min(self.persistence, key=lambda k: self.persistence[k])


# ------------------------------------------------------------------
# Phasenübergangs-Indikator
# ------------------------------------------------------------------


@dataclass
class PhaseIndicator:
    """Indikatoren für die Nähe zu einem Phasenübergang.

    Wissenschaftliche Vorsicht:
        Diese Metriken sind heuristische Annäherungen, keine exakten
        Phasenübergangsnachweise. Erhöhte Varianz und Suszeptibilität
        nahe kritischer Punkte sind bekannte Phänomene (kritisches
        Verlangsamen, Critical Slowing Down).
    """

    tick: int
    energy_variance: float
    information_variance: float
    susceptibility: float  # Varianz der Varianzen über Felder
    near_transition: bool  # Heuristisch: True wenn susceptibility > threshold


def compute_phase_indicator(
    tick: int,
    fields: Dict[str, np.ndarray],
    transition_threshold: float = 0.05,
) -> PhaseIndicator:
    """Berechne heuristische Phasenübergangs-Indikatoren.

    Erhöhte Varianz (besonders ihrer Fluktuation über Zeit) ist ein
    bekannter Vorläufer von Phasenübergängen in komplexen Systemen
    (Critical Slowing Down). Dieser Indikator ist ein erster Schritt,
    kein bewiesener Nachweis.

    Parameters
    ----------
    tick:
        Aktueller Simulationsschritt.
    fields:
        Dictionary {feldname: array}.
    transition_threshold:
        Suszeptibilitätsschwelle für ``near_transition``-Flag.
    """
    variances = {name: float(arr.var()) for name, arr in fields.items()}
    e_var = variances.get("energy", 0.0)
    i_var = variances.get("information", 0.0)
    susceptibility = float(np.std(list(variances.values())))

    return PhaseIndicator(
        tick=tick,
        energy_variance=e_var,
        information_variance=i_var,
        susceptibility=susceptibility,
        near_transition=susceptibility > transition_threshold,
    )
