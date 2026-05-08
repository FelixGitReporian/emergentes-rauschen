"""
analysis/morphology.py – Morphologische Metriken für 2-D-Felder.

Morphologie beschreibt die *Form* aktiver Regionen: Wie komplex sind ihre
Ränder? Gibt es Löcher? Entstehen Filamente oder kompakte Klumpen?

Implementierte Metriken:

1. boundary_complexity  – Verhältnis Rand/Fläche aktiver Regionen.
   Hohe Randkomplexität deutet auf filamentöse oder fraktale Strukturen hin.

2. euler_number         – Topologische Invariante (Komponenten − Löcher).
   Negativ = mehr Löcher als Zusammenhangskomponenten.

3. elongation           – Verhältnis von Bounding-Box-Seiten des größten Clusters.
   > 2 deutet auf Filamente / elongierte Strukturen hin.

4. compactness          – 4π·Fläche / Umfang². 1 = Kreis, < 1 = irregular.

5. MorphologyResult     – Dataclass mit allen Metriken für ein Feld.

Wissenschaftliche Vorsicht:
    Diese Metriken sind geometrische Beschreibungen, keine Kausalaussagen.
    Hohe Randkomplexität *deutet auf* filamentöse Dynamiken hin; sie *beweist*
    keine spezifische physikalische Ursache.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_erosion, label, find_objects


@dataclass
class MorphologyResult:
    """Morphologische Metriken eines einzelnen Feldes zu einem Tick."""

    field_name: str
    tick: int
    threshold: float
    active_fraction: float       # Anteil aktiver Zellen
    n_components: int            # Anzahl zusammenhängender Komponenten
    n_holes: int                 # Löcher (Euler-Topologie, näherungsweise)
    euler_number: int            # n_components - n_holes
    boundary_complexity: float   # Rand/Fläche-Verhältnis
    elongation: float            # Größter Cluster: Breite/Höhe (≥1)
    compactness: float           # 4π·A/P² für größten Cluster (≤1)


def compute_morphology(
    name: str,
    arr: np.ndarray,
    tick: int = 0,
    threshold: float = 0.5,
) -> MorphologyResult:
    """Berechne morphologische Metriken für ein 2-D-Feld.

    Parameters
    ----------
    name:
        Feldname.
    arr:
        2-D float-Array [0, 1].
    tick:
        Aktueller Simulationsschritt (für Zeitreihen).
    threshold:
        Schwellwert: Zellen > threshold gelten als 'aktiv'.
    """
    binary = (arr > threshold).astype(bool)
    active_fraction = float(binary.mean())

    if active_fraction == 0.0:
        return MorphologyResult(
            field_name=name, tick=tick, threshold=threshold,
            active_fraction=0.0, n_components=0, n_holes=0,
            euler_number=0, boundary_complexity=0.0,
            elongation=1.0, compactness=0.0,
        )

    # Zusammenhangskomponenten
    labeled, n_components = label(binary)

    # Rand: Zellen die aktiv sind, aber einen inaktiven Nachbar haben
    eroded = binary_erosion(binary)
    boundary = binary & ~eroded
    boundary_size = int(boundary.sum())
    active_size = int(binary.sum())
    boundary_complexity = boundary_size / max(active_size, 1)

    # Euler-Zahl approximieren: n_components − n_holes
    # Löcher = zusammenhängende inaktive Regionen die vollständig von aktiven umschlossen sind
    inverted_labeled, n_inv = label(~binary)
    # Grenzregion (Rand des Arrays) ist keine Loch-Komponente
    border_labels: set[int] = set()
    border_labels.update(inverted_labeled[0, :].tolist())
    border_labels.update(inverted_labeled[-1, :].tolist())
    border_labels.update(inverted_labeled[:, 0].tolist())
    border_labels.update(inverted_labeled[:, -1].tolist())
    border_labels.discard(0)
    n_holes = n_inv - len(border_labels)
    euler_number = n_components - n_holes

    # Elongation + Compactness des größten Clusters
    sizes = [(labeled == i).sum() for i in range(1, n_components + 1)]
    largest_label = int(np.argmax(sizes)) + 1
    largest_mask = labeled == largest_label
    objs = find_objects(largest_mask.astype(int))
    if objs and objs[0] is not None:
        s = objs[0]
        h = s[0].stop - s[0].start
        w = s[1].stop - s[1].start
        elongation = float(max(h, w) / max(min(h, w), 1))
        area = int(largest_mask.sum())
        perimeter = int((largest_mask & ~binary_erosion(largest_mask)).sum())
        compactness = (4 * np.pi * area / max(perimeter ** 2, 1)) if perimeter > 0 else 0.0
    else:
        elongation = 1.0
        compactness = 0.0

    return MorphologyResult(
        field_name=name,
        tick=tick,
        threshold=threshold,
        active_fraction=active_fraction,
        n_components=n_components,
        n_holes=max(n_holes, 0),
        euler_number=euler_number,
        boundary_complexity=boundary_complexity,
        elongation=elongation,
        compactness=float(compactness),
    )
