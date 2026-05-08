"""
analysis/compartments.py – Proto-Kompartiment-Erkennung.

Kompartimente sind räumlich abgegrenzte Bereiche mit innerer Kohärenz und
äußerer Grenze. In biologischen Systemen sind Membranen die archetypische
Kompartiment-Grenze. Hier suchen wir nach feldbasierten Kompartimenten:
Regionen, in denen Energie hoch, Kopplung stark und Randkomplexität gering
ist — potenzielle Proto-Zell-Analoga.

Implementierte Funktionen:

1. detect_compartments      – Feldbasierte Kompartiment-Suche.
2. particle_compartments    – Partikelbasierte Kompartiment-Suche.
3. CompartmentResult        – Ergebnis-Dataclass mit allen Metriken.

Orientierung an Arbeitsmappe Kap. 13.1 (Proto-Leben):
    Ein Muster ist proto-lebensähnlich, wenn es eine Grenze oder
    Kompartimentierung bildet, Energie-/Informationsflüsse reguliert,
    und sich selbst teilweise erhält.

Wissenschaftliche Vorsicht:
    Diese Metriken sind strukturelle Proxies, kein Nachweis von Leben
    oder bewussten Prozessen. Hohe Kompartiment-Werte bedeuten «abgegrenztes
    aktives Feldgebiet», nicht «Zelle» oder «Organismus».
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from scipy.ndimage import label, uniform_filter

from emergent_noise.core.state import GridState


@dataclass
class Compartment:
    """Beschreibung eines einzelnen Proto-Kompartiments.

    Attribute
    ----------
    id:
        Eindeutige ID innerhalb des aktuellen Ticks.
    centroid:
        (y, x)-Schwerpunkt des Kompartiments.
    area:
        Fläche in Gitterzellen.
    mean_energy:
        Mittlere Energie innerhalb des Kompartiments.
    mean_coupling:
        Mittlere Kopplung innerhalb des Kompartiments.
    boundary_length:
        Länge der Außengrenze (in Zellen).
    compactness:
        4π × Fläche / Umfang² (1 = Kreis, < 1 = unregelmäßig).
    proto_life_score:
        Heuristischer Score für Proto-Lebens-Ähnlichkeit [0, 1].
    """

    id: int
    centroid: tuple[float, float]
    area: int
    mean_energy: float
    mean_coupling: float
    boundary_length: int
    compactness: float
    proto_life_score: float


@dataclass
class CompartmentResult:
    """Ergebnis der Kompartiment-Analyse für einen Tick.

    Attribute
    ----------
    tick:
        Simulationsschritt.
    n_compartments:
        Anzahl erkannter Proto-Kompartimente.
    compartments:
        Liste aller gefundenen Kompartimente.
    mean_proto_life_score:
        Mittlerer Proto-Leben-Score über alle Kompartimente.
    max_proto_life_score:
        Höchster Proto-Leben-Score.
    """

    tick: int
    n_compartments: int
    compartments: List[Compartment]
    mean_proto_life_score: float
    max_proto_life_score: float


def _boundary_length(mask: np.ndarray) -> int:
    """Berechne die Randlänge eines binären Masken-Arrays.

    Zählt Randzellen: Zellen, die True sind und mindestens einen
    False-Nachbarn haben (4-Konnektivität).
    """
    if not mask.any():
        return 0
    # Nachbarn: oben, unten, links, rechts
    up    = np.roll(mask, -1, axis=0)
    down  = np.roll(mask,  1, axis=0)
    left  = np.roll(mask, -1, axis=1)
    right = np.roll(mask,  1, axis=1)
    # Randzellen: in Maske, aber nicht alle Nachbarn auch in Maske
    border = mask & ~(up & down & left & right)
    return int(border.sum())


def _proto_life_score(
    area: int,
    mean_energy: float,
    mean_coupling: float,
    compactness: float,
    min_area: int = 4,
) -> float:
    """Heuristischer Proto-Leben-Score für ein Kompartiment.

    Scoring-Kriterien (je 0.25 Punkte, gesamt 0–1):
    - Energie    > 0.4  (ausreichende Aktivität)
    - Kopplung   > 0.3  (innere Vernetzung)
    - Fläche     > min_area (nicht zu klein)
    - Compactness > 0.3 (nicht zu fragmentiert)

    Wissenschaftliche Vorsicht: Dieser Score ist ein sehr grober Proxy.
    """
    score = 0.0
    if mean_energy > 0.4:
        score += 0.25
    if mean_coupling > 0.3:
        score += 0.25
    if area >= min_area:
        score += 0.25
    if compactness > 0.3:
        score += 0.25
    return round(score, 3)


def detect_compartments(
    state: GridState,
    energy_threshold: float = 0.5,
    coupling_threshold: float = 0.3,
    min_area: int = 4,
) -> CompartmentResult:
    """Erkenne Proto-Kompartimente aus Felddaten.

    Ein Proto-Kompartiment ist ein zusammenhängender Bereich, in dem:
    - Energie > energy_threshold  (aktive Region)
    - Mittlere Kopplung > coupling_threshold (innere Vernetzung)
    - Fläche >= min_area Zellen

    Parameters
    ----------
    state:
        Aktueller GridState.
    energy_threshold:
        Schwellwert für aktive Energie-Region.
    coupling_threshold:
        Mindestkopplung für innere Vernetzung.
    min_area:
        Mindestgröße eines Kompartiments in Zellen.

    Returns
    -------
    CompartmentResult mit allen gefundenen Kompartimenten.
    """
    # Binäre Energie-Maske
    energy_mask = state.energy > energy_threshold

    # Verbundene Komponenten (8-Konnektivität)
    labeled, n_components = label(energy_mask)

    compartments: List[Compartment] = []

    for comp_id in range(1, n_components + 1):
        mask = labeled == comp_id
        area = int(mask.sum())
        if area < min_area:
            continue

        mean_energy   = float(state.energy[mask].mean())
        mean_coupling = float(state.coupling[mask].mean())

        if mean_coupling < coupling_threshold:
            continue

        # Schwerpunkt
        ys, xs = np.where(mask)
        centroid = (float(ys.mean()), float(xs.mean()))

        # Randlänge und Compactness
        bl = _boundary_length(mask)
        if bl > 0:
            compactness = float(4 * np.pi * area / (bl ** 2))
            compactness = min(compactness, 1.0)
        else:
            compactness = 1.0

        pls = _proto_life_score(area, mean_energy, mean_coupling, compactness, min_area)

        compartments.append(Compartment(
            id=comp_id,
            centroid=centroid,
            area=area,
            mean_energy=round(mean_energy, 4),
            mean_coupling=round(mean_coupling, 4),
            boundary_length=bl,
            compactness=round(compactness, 4),
            proto_life_score=pls,
        ))

    scores = [c.proto_life_score for c in compartments]
    return CompartmentResult(
        tick=state.tick,
        n_compartments=len(compartments),
        compartments=compartments,
        mean_proto_life_score=round(float(np.mean(scores)) if scores else 0.0, 4),
        max_proto_life_score=round(float(max(scores)) if scores else 0.0, 4),
    )


def particle_compartments(
    positions: np.ndarray,
    masses: np.ndarray,
    height: int,
    width: int,
    min_mass: float = 3.0,
    density_radius: int = 3,
) -> dict:
    """Erkenne Kompartimente aus Partikel-Aggregationen.

    Berechnet eine Partikel-Dichtekarte und sucht Bereiche hoher Dichte
    mit schweren Partikeln (Aggregate).

    Parameters
    ----------
    positions:
        (N, 2) Array aktiver Partikel-Positionen (y, x).
    masses:
        (N,) Array der Partikel-Massen.
    height, width:
        Grid-Dimensionen.
    min_mass:
        Mindestmasse für ein Aggregat-Kompartiment.
    density_radius:
        Glättungsradius für Dichte-Karte.

    Returns
    -------
    Dictionary mit:
    - ``density_map``        – (H, W) Partikel-Dichtekarte
    - ``n_heavy_particles``  – Anzahl Partikel mit Masse >= min_mass
    - ``mean_aggregate_mass``– mittlere Masse der schweren Partikel
    - ``compartment_positions``– Positionen schwerer Partikel
    """
    if len(positions) == 0:
        return {
            "density_map": np.zeros((height, width), dtype=np.float32),
            "n_heavy_particles": 0,
            "mean_aggregate_mass": 0.0,
            "compartment_positions": np.empty((0, 2)),
        }

    density = np.zeros((height, width), dtype=np.float32)
    rows = np.clip(positions[:, 0].astype(np.int32), 0, height - 1)
    cols = np.clip(positions[:, 1].astype(np.int32), 0, width - 1)
    np.add.at(density, (rows, cols), masses)

    # Glätten für Dichtekarte
    smoothed = uniform_filter(density, size=density_radius * 2 + 1).astype(np.float32)

    heavy = masses >= min_mass
    n_heavy = int(heavy.sum())

    return {
        "density_map": smoothed,
        "n_heavy_particles": n_heavy,
        "mean_aggregate_mass": round(float(masses[heavy].mean()) if n_heavy > 0 else 0.0, 3),
        "compartment_positions": positions[heavy],
    }
