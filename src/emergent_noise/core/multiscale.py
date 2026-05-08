"""
core/multiscale.py – Mehrskalenmodell: Mikro/Meso/Makro (Epic 6).

Das Mehrskalenmodell koppelt drei Beschreibungsebenen:

    Mikro  – Einzelne Gitterzellen (GridState, bereits implementiert)
    Meso   – Cluster als eigenständige Entitäten (MesoLayer)
    Makro  – Attraktor-Landschaft, Regime-Übergänge (MacroLayer)

Orientierung an Arbeitsmappe Kap. 10.5:
    Mikro: Zellen/Partikel
    Meso:  Cluster/Membranen/Wellen
    Makro: Attraktoren/Regime/Landschaften

Wissenschaftliche Vorsicht:
    Mehrskalige Beschreibungen sind Modellierungsentscheidungen, keine
    ontologischen Behauptungen. Die Grenzen zwischen Mikro, Meso und
    Makro sind fließend und analysezweckabhängig.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import label, uniform_filter

from emergent_noise.core.state import GridState


# ──────────────────────────────────────────────────────────────────
# MESO-LAYER: Cluster als Entitäten
# ──────────────────────────────────────────────────────────────────

@dataclass
class MesoEntity:
    """Ein Meso-Level-Cluster: eine kohärente räumliche Einheit.

    Attribute
    ----------
    id:
        Eindeutige Cluster-ID.
    centroid:
        (y, x)-Schwerpunkt.
    area:
        Fläche in Gitterzellen.
    mean_energy:
        Mittlere Energie.
    mean_coherence:
        Mittlere Kohärenz (Maß für interne Synchronität).
    velocity:
        Geschätzter Bewegungsvektor (dy, dx) gegenüber Vorschritt.
    age:
        Anzahl Ticks, die diese Entität überlebt hat.
    lineage_id:
        ID des Vorläufer-Clusters (für Tracking, -1 = neu entstanden).
    """

    id: int
    centroid: Tuple[float, float]
    area: int
    mean_energy: float
    mean_coherence: float
    velocity: Tuple[float, float] = (0.0, 0.0)
    age: int = 0
    lineage_id: int = -1


class MesoLayer:
    """Verwaltet Meso-Level-Cluster aus GridState-Feldern.

    Erkennt Cluster (verbundene aktive Regionen), verfolgt sie über
    Zeit und schätzt ihre Bewegung (Tracker).

    Parameters
    ----------
    energy_threshold:
        Schwellwert für aktive Energie-Region.
    min_area:
        Minimalfläche für einen Meso-Cluster.
    """

    def __init__(
        self,
        energy_threshold: float = 0.5,
        min_area: int = 9,
    ) -> None:
        self.energy_threshold = energy_threshold
        self.min_area = min_area
        self._prev_entities: List[MesoEntity] = []
        self.entities: List[MesoEntity] = []
        self.history: List[dict] = []

    def update(self, state: GridState) -> List[MesoEntity]:
        """Aktualisiere Meso-Entitäten aus aktuellem GridState.

        Schritte:
        1. Finde verbundene aktive Regionen (label).
        2. Filtere nach Mindestgröße.
        3. Schätze Geschwindigkeit durch Matching mit Vorschritt (nächster Schwerpunkt).
        4. Speichere in history.

        Parameters
        ----------
        state:
            Aktueller GridState.

        Returns
        -------
        Liste aktueller MesoEntity-Objekte.
        """
        energy_mask = state.energy > self.energy_threshold
        labeled, n_comp = label(energy_mask)
        new_entities: List[MesoEntity] = []

        for cid in range(1, n_comp + 1):
            mask = labeled == cid
            area = int(mask.sum())
            if area < self.min_area:
                continue

            ys, xs = np.where(mask)
            centroid = (float(ys.mean()), float(xs.mean()))
            mean_energy = float(state.energy[mask].mean())
            mean_coherence = float(state.coherence[mask].mean())

            # Geschwindigkeit schätzen: nächster Vorläufer
            vel = (0.0, 0.0)
            lineage = -1
            if self._prev_entities:
                dists = [
                    np.sqrt((centroid[0] - pe.centroid[0])**2 +
                            (centroid[1] - pe.centroid[1])**2)
                    for pe in self._prev_entities
                ]
                best_idx = int(np.argmin(dists))
                if dists[best_idx] < 10.0:  # Max-Tracking-Radius
                    pe = self._prev_entities[best_idx]
                    vel = (centroid[0] - pe.centroid[0], centroid[1] - pe.centroid[1])
                    lineage = pe.id

            new_entities.append(MesoEntity(
                id=cid,
                centroid=centroid,
                area=area,
                mean_energy=round(mean_energy, 4),
                mean_coherence=round(mean_coherence, 4),
                velocity=vel,
                age=0,
                lineage_id=lineage,
            ))

        self._prev_entities = self.entities
        self.entities = new_entities

        summary = {
            "tick": state.tick,
            "n_meso_entities": len(new_entities),
            "total_area": sum(e.area for e in new_entities),
            "mean_entity_energy": round(
                float(np.mean([e.mean_energy for e in new_entities]))
                if new_entities else 0.0, 4
            ),
        }
        self.history.append(summary)
        return new_entities


# ──────────────────────────────────────────────────────────────────
# MAKRO-LAYER: Attraktor-Landschaft
# ──────────────────────────────────────────────────────────────────

@dataclass
class AttractorLandscape:
    """Makro-Level Attraktor-Landschaft.

    Verfolgt die Systemdynamik in einem niedrig-dimensionalen
    Zustandsraum (PCA-ähnliche Projektion auf Energie+Kohärenz-Ebene).

    Attribute
    ----------
    trajectory:
        Liste von (energy_mean, coherence_mean, tick)-Tuples.
    basins:
        Erkannte Attraktor-Becken (grob durch Dichte-Schätzung).
    """

    trajectory: List[Tuple[float, float, int]] = field(default_factory=list)
    transition_events: List[dict] = field(default_factory=list)

    def update(self, state: GridState) -> dict:
        """Aktualisiere Attraktor-Landschaft aus aktuellem Zustand.

        Nutzt (energy_mean, coherence_mean) als 2D-Projektion des
        hochdimensionalen Zustandsraums. Erkennt mögliche Übergänge
        durch sprunghafte Änderungen.

        Returns
        -------
        Dictionary mit Zustandspunkt + Transition-Flag.
        """
        em = float(state.energy.mean())
        cm = float(state.coherence.mean())
        tick = state.tick

        point = (round(em, 4), round(cm, 4), tick)
        self.trajectory.append(point)

        # Transition erkennen: Sprung in der Trajektorie
        transition = False
        if len(self.trajectory) >= 3:
            prev = self.trajectory[-2]
            delta = np.sqrt((em - prev[0])**2 + (cm - prev[1])**2)
            if delta > 0.05:  # Schwellwert für Phasenübergang
                event = {
                    "tick": tick,
                    "delta": round(float(delta), 5),
                    "from": (prev[0], prev[1]),
                    "to": (em, cm),
                }
                self.transition_events.append(event)
                transition = True

        return {
            "energy_mean": em,
            "coherence_mean": cm,
            "tick": tick,
            "transition_detected": transition,
            "n_transitions": len(self.transition_events),
        }

    def trajectory_array(self) -> np.ndarray:
        """Gibt Trajektorie als (N, 2) Array zurück (energy, coherence)."""
        if not self.trajectory:
            return np.empty((0, 2))
        return np.array([[p[0], p[1]] for p in self.trajectory])


# ──────────────────────────────────────────────────────────────────
# MULTISCALE-CONTROLLER: verbindet alle Ebenen
# ──────────────────────────────────────────────────────────────────

class MultiscaleController:
    """Verbindet Mikro, Meso und Makro in einem einheitlichen Update.

    Parameters
    ----------
    energy_threshold:
        Schwellwert für Meso-Cluster-Erkennung.
    min_meso_area:
        Mindestgröße für Meso-Entitäten.
    """

    def __init__(
        self,
        energy_threshold: float = 0.5,
        min_meso_area: int = 9,
    ) -> None:
        self.meso = MesoLayer(energy_threshold, min_meso_area)
        self.macro = AttractorLandscape()

    def update(self, state: GridState) -> dict:
        """Vollständiges Multiscale-Update.

        Returns
        -------
        Dictionary mit Meso- und Makro-Zusammenfassung.
        """
        meso_entities = self.meso.update(state)
        macro_state   = self.macro.update(state)

        return {
            "meso": {
                "n_entities":    len(meso_entities),
                "total_area":    sum(e.area for e in meso_entities),
                "mean_velocity": round(float(np.mean([
                    np.sqrt(e.velocity[0]**2 + e.velocity[1]**2)
                    for e in meso_entities
                ])) if meso_entities else 0.0, 5),
            },
            "macro": macro_state,
        }
