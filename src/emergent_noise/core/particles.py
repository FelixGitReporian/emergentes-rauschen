"""
core/particles.py – Partikel-Feld-Hybrid (Epic 4).

Dieses Modul implementiert ein Partikel-System, das in das bestehende
Gitter-Feld-System integriert ist. Partikel sind diskrete, bewegliche
Einheiten, die durch Felder beeinflusst werden und Felder verändern.

Architektur (Arbeitsmappe Kap. 10.3):
    Partikel bewegen sich durch den kontinuierlichen Raum [0, H) × [0, W).
    Alle Arrays sind vektorisiert (NumPy), keine Python-Objekte pro Partikel.

    Partikel-Zustandsfelder (alle Form (N,) oder (N,2)):
    - ``positions``   – kontinuierliche (y, x)-Koordinaten
    - ``velocities``  – (vy, vx)-Geschwindigkeitsvektor
    - ``energy``      – lokale Energie des Partikels (skaliert Feldwirkung)
    - ``mass``        – Trägheit (skaliert Beschleunigung und Feldeinfluss)
    - ``active``      – bool-Maske: aktive/inaktive Partikel
    - ``age``         – Anzahl Ticks seit Entstehung

Kopplung (bidirektional):
    Feld → Partikel (field_to_particle):
        Felder beschleunigen Partikel entlang ihrer Gradienten.
        Hohe Energie zieht Partikel an, hoher Fluss trägt sie mit.

    Partikel → Feld (particle_to_field):
        Partikel deponieren Energie und Information in ihre Umgebung.
        Aggregierte Partikel erhöhen lokale Materie und Kopplung.

Kollision + Aggregation:
    Partikel innerhalb eines Radius r fusionieren zu einem schwereren Partikel.
    Dies modelliert Verdichtung, Clusterbildung, proto-zelluläre Aggregation.

Proto-Kompartiment-Erkennung:
    Aggregationen von >= n Partikeln in einer Region gelten als
    Proto-Kompartiment (Vorläufer von Zell-artigen Strukturen).

Wissenschaftliche Vorsicht:
    Dieses Partikel-System ist eine stark vereinfachte Abstraktion.
    Die Physik ist nicht korrekt (keine Energieerhaltung, keine Impulse).
    Das Ziel ist Emergenz-Exploration, nicht physikalische Simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from emergent_noise.core.state import GridState, SimConfig


# ──────────────────────────────────────────────────────────────────
# Konfiguration
# ──────────────────────────────────────────────────────────────────

@dataclass
class ParticleConfig:
    """Konfiguration des Partikel-Systems.

    Alle Partikel-spezifischen Parameter sind hier gesammelt.
    Kann separat von SimConfig erzeugt oder als Erweiterung verwendet werden.

    Attribute
    ----------
    n_particles:
        Anfangszahl aktiver Partikel.
    max_particles:
        Maximale Gesamtzahl (aktiv + inaktiv) — Array-Größe ist fest.
    field_attraction:
        Stärke, mit der Energie-Gradient Partikel beschleunigt.
    flow_drag:
        Anteil des Flussvektors, der zur Partikelgeschwindigkeit addiert wird.
    velocity_damping:
        Multiplikativer Dämpfungsfaktor pro Tick (Reibung, < 1).
    energy_deposit:
        Menge Energie, die ein Partikel pro Tick an seine Gitterzelle abgibt.
    matter_deposit:
        Menge Materie, die ein Partikel pro Tick an seine Gitterzelle abgibt.
    collision_radius:
        Abstand (in Gitterzellen), unterhalb dem zwei Partikel aggregieren.
    min_mass_for_compartment:
        Mindestmasse eines Partikels, um als Proto-Kompartiment zu gelten.
    seed:
        Zufalls-Seed für reproduzierbare Initialisierung.
    """

    n_particles: int = 50
    max_particles: int = 200
    field_attraction: float = 0.05
    flow_drag: float = 0.3
    velocity_damping: float = 0.92
    energy_deposit: float = 0.01
    matter_deposit: float = 0.005
    collision_radius: float = 1.5
    min_mass_for_compartment: float = 3.0
    seed: int = 42


# ──────────────────────────────────────────────────────────────────
# ParticleSystem
# ──────────────────────────────────────────────────────────────────

class ParticleSystem:
    """Verwaltet alle Partikel und ihre Dynamik.

    Alle Partikel-Daten sind als NumPy-Arrays der Länge ``max_particles``
    gespeichert. Inaktive Partikel haben ``active[i] == False`` und werden
    bei Berechnungen ignoriert.

    Parameters
    ----------
    config:
        ParticleConfig mit allen Partikel-Parametern.
    height, width:
        Grid-Dimensionen (aus SimConfig).
    """

    def __init__(
        self,
        config: ParticleConfig,
        height: int,
        width: int,
    ) -> None:
        self.config = config
        self.height = height
        self.width = width

        N = config.max_particles
        rng = np.random.default_rng(config.seed)

        n = min(config.n_particles, N)

        # Positionen: gleichmäßig zufällig im Grid
        self.positions = np.zeros((N, 2), dtype=np.float32)
        self.positions[:n, 0] = rng.uniform(0, height, n).astype(np.float32)  # y
        self.positions[:n, 1] = rng.uniform(0, width,  n).astype(np.float32)  # x

        # Geschwindigkeiten: klein, zufällig
        self.velocities = np.zeros((N, 2), dtype=np.float32)
        self.velocities[:n] = rng.uniform(-0.3, 0.3, (n, 2)).astype(np.float32)

        # Partikel-Energie: zufällig in [0.3, 0.8]
        self.energy = np.zeros(N, dtype=np.float32)
        self.energy[:n] = rng.uniform(0.3, 0.8, n).astype(np.float32)

        # Masse: alle starten bei 1.0
        self.mass = np.zeros(N, dtype=np.float32)
        self.mass[:n] = 1.0

        # Alter (in Ticks)
        self.age = np.zeros(N, dtype=np.int32)

        # Aktiv-Maske
        self.active = np.zeros(N, dtype=bool)
        self.active[:n] = True

    # ──────────────────────────────────────────────────────────────
    # Hilfsfunktionen
    # ──────────────────────────────────────────────────────────────

    def _active_indices(self) -> np.ndarray:
        """Gibt Indizes aktiver Partikel zurück."""
        return np.where(self.active)[0]

    def _grid_coords(self, idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Runde Positionen zu ganzzahligen Grid-Koordinaten (periodisch).

        Returns
        -------
        (row_idx, col_idx) – ganzzahlige Arrays der Grid-Position.
        """
        rows = (self.positions[idx, 0] % self.height).astype(np.int32)
        cols = (self.positions[idx, 1] % self.width).astype(np.int32)
        return rows, cols

    def _bilinear_sample(
        self, field: np.ndarray, idx: np.ndarray
    ) -> np.ndarray:
        """Bilinear-Interpolation: lese Feldwert an kontinuierlicher Position.

        Ermöglicht glatte Feldwerte zwischen Gitterpunkten für genauere
        Partikel-Dynamik. Periodische Randbedingungen.

        Parameters
        ----------
        field:
            2-D float-Array (height × width).
        idx:
            Partikel-Indizes für die Sample durchgeführt werden soll.

        Returns
        -------
        1-D float-Array mit interpolierten Feldwerten.
        """
        H, W = self.height, self.width
        y = self.positions[idx, 0] % H
        x = self.positions[idx, 1] % W

        y0 = np.floor(y).astype(np.int32) % H
        y1 = (y0 + 1) % H
        x0 = np.floor(x).astype(np.int32) % W
        x1 = (x0 + 1) % W

        fy = (y - np.floor(y)).astype(np.float32)
        fx = (x - np.floor(x)).astype(np.float32)

        val = (
            (1 - fy) * (1 - fx) * field[y0, x0]
            + (1 - fy) * fx      * field[y0, x1]
            +      fy  * (1 - fx) * field[y1, x0]
            +      fy  * fx       * field[y1, x1]
        )
        return val.astype(np.float32)

    # ──────────────────────────────────────────────────────────────
    # Feld → Partikel Kopplung
    # ──────────────────────────────────────────────────────────────

    def apply_field_to_particles(self, state: GridState) -> None:
        """Felder beschleunigen und beeinflussen Partikel.

        Mechanismen:
        1. Energie-Gradient-Attraktion:
           Partikel werden in Richtung zunehmender Energie beschleunigt
           (Gradient-Abstieg im negativen Sinne → Attraktion zu Hochpunkten).

        2. Fluss-Transport (Drag):
           Das Flussfeld (flow_x, flow_y) trägt Partikel mit sich.

        3. Energie-Absorption:
           Partikel absorbieren Energie vom Feld (Partikel-Energie steigt,
           Feld-Energie sinkt leicht am Ort des Partikels).

        4. Reaktivitäts-Aktivierung:
           Hohe Reaktivität am Partikelort erhöht Partikel-Geschwindigkeit
           (Partikel werden «aktiviert»).

        Parameters
        ----------
        state:
            Aktueller GridState (wird in-place verändert).
        """
        cfg = self.config
        idx = self._active_indices()
        if len(idx) == 0:
            return

        H, W = self.height, self.width

        # 1. Energie-Gradient-Attraktion
        # Numerischer Gradient des Energiefelds (zentrale Differenzen, periodisch)
        grad_y = np.roll(state.energy, -1, axis=0) - np.roll(state.energy, 1, axis=0)
        grad_x = np.roll(state.energy, -1, axis=1) - np.roll(state.energy, 1, axis=1)
        # Gradient/2 ≈ lokale Steigung
        grad_y *= 0.5
        grad_x *= 0.5

        gy = self._bilinear_sample(grad_y, idx)
        gx = self._bilinear_sample(grad_x, idx)

        self.velocities[idx, 0] += cfg.field_attraction * gy / np.maximum(self.mass[idx], 0.5)
        self.velocities[idx, 1] += cfg.field_attraction * gx / np.maximum(self.mass[idx], 0.5)

        # 2. Fluss-Transport (Drag)
        fy = self._bilinear_sample(state.flow_y, idx)
        fx = self._bilinear_sample(state.flow_x, idx)
        self.velocities[idx, 0] += cfg.flow_drag * fy
        self.velocities[idx, 1] += cfg.flow_drag * fx

        # 3. Energie-Absorption
        rows, cols = self._grid_coords(idx)
        absorbed = cfg.energy_deposit * self.energy[idx]
        self.energy[idx] = np.clip(self.energy[idx] + absorbed * 0.1, 0.0, 1.0)
        state.energy[rows, cols] = np.clip(
            state.energy[rows, cols] - absorbed, 0.0, 1.0
        )

        # 4. Reaktivitäts-Aktivierung: hohe Reaktivität erhöht Geschwindigkeit
        reactivity = self._bilinear_sample(state.reactivity, idx)
        speed_boost = 0.02 * (reactivity - 0.5)  # nur wenn über Mittelwert
        speed_boost = np.maximum(speed_boost, 0.0)
        speed_norms = np.sqrt(
            self.velocities[idx, 0] ** 2 + self.velocities[idx, 1] ** 2
        )
        nz = speed_norms > 1e-6
        if nz.any():
            self.velocities[idx[nz], 0] += (
                speed_boost[nz] * self.velocities[idx[nz], 0] / speed_norms[nz]
            )
            self.velocities[idx[nz], 1] += (
                speed_boost[nz] * self.velocities[idx[nz], 1] / speed_norms[nz]
            )

    # ──────────────────────────────────────────────────────────────
    # Partikel → Feld Kopplung
    # ──────────────────────────────────────────────────────────────

    def apply_particles_to_field(self, state: GridState) -> None:
        """Partikel verändern Felder an ihrem Aufenthaltsort.

        Mechanismen:
        1. Energie-Deposition:
           Jeder Partikel gibt proportional zu seiner Energie
           einen kleinen Betrag ans Energiefeld ab.

        2. Materie-Deposition:
           Partikel erhöhen die lokale Materie (Sedimentationsanalogon,
           Substratbildung, proto-zelluläre Verdichtung).

        3. Kopplungs-Verstärkung:
           Mehrere Partikel am selben Ort verstärken das Kopplungsfeld.
           Modelliert Aggregation als Bindungsmechanismus.

        4. Informations-Injektion:
           Partikel injizieren Information (lokale Musterentropie erhöht sich).

        Parameters
        ----------
        state:
            Aktueller GridState (wird in-place verändert).
        """
        cfg = self.config
        idx = self._active_indices()
        if len(idx) == 0:
            return

        rows, cols = self._grid_coords(idx)

        # Anzahl Partikel pro Zelle (für Kopplungsverstärkung)
        density = np.zeros((self.height, self.width), dtype=np.float32)
        np.add.at(density, (rows, cols), 1.0)
        density = np.clip(density / max(len(idx), 1), 0.0, 1.0)

        # 1. Energie-Deposition
        np.add.at(
            state.energy, (rows, cols),
            cfg.energy_deposit * self.energy[idx]
        )

        # 2. Materie-Deposition
        np.add.at(
            state.matter, (rows, cols),
            cfg.matter_deposit * self.mass[idx]
        )

        # 3. Kopplungs-Verstärkung durch Dichte
        state.coupling += 0.01 * density

        # 4. Information-Injektion (Entropie-Erhöhung)
        np.add.at(
            state.information, (rows, cols),
            0.005 * self.energy[idx]
        )

    # ──────────────────────────────────────────────────────────────
    # Bewegung
    # ──────────────────────────────────────────────────────────────

    def move(self) -> None:
        """Aktualisiere Positionen und dämpfe Geschwindigkeiten.

        Positionen werden periodisch gehalten (torusförmiges Grid).
        Geschwindigkeiten werden pro Tick mit ``velocity_damping`` gedämpft.
        Maximale Geschwindigkeit ist 2.0 Zellen/Tick (Stabilitätsgrenze).
        """
        idx = self._active_indices()
        if len(idx) == 0:
            return

        cfg = self.config
        # Geschwindigkeit begrenzen (numerische Stabilität)
        speeds = np.sqrt(
            self.velocities[idx, 0] ** 2 + self.velocities[idx, 1] ** 2
        )
        max_speed = 2.0
        fast = speeds > max_speed
        if fast.any():
            scale = max_speed / speeds[fast]
            self.velocities[idx[fast], 0] *= scale
            self.velocities[idx[fast], 1] *= scale

        # Position aktualisieren
        self.positions[idx] += self.velocities[idx]

        # Periodische Randbedingungen
        self.positions[idx, 0] %= self.height
        self.positions[idx, 1] %= self.width

        # Geschwindigkeit dämpfen (Reibung)
        self.velocities[idx] *= cfg.velocity_damping

        # Alter erhöhen
        self.age[idx] += 1

    # ──────────────────────────────────────────────────────────────
    # Kollision + Aggregation
    # ──────────────────────────────────────────────────────────────

    def apply_collisions(self) -> None:
        """Fusioniere Partikel innerhalb des Kollisionsradius.

        Mechanismus:
        - Für alle Paare aktiver Partikel: wenn Abstand < collision_radius,
          fusionieren sie zu einem schwereren Partikel.
        - Das überlebende Partikel erbt die Masse-gewichtete Position,
          Impuls und Energie beider Partikel.
        - Das zweite Partikel wird deaktiviert.

        Implementierung: O(N²) über aktive Partikel, daher für N < 500
        akzeptabel. Für größere Systeme → spatial hashing (Epic 5+).

        Wissenschaftliche Vorsicht:
            Dies ist keine korrekte physikalische Kollision (kein Impuls-
            Erhalt). Es ist ein vereinfachter Aggregationsmechanismus.
        """
        idx = self._active_indices()
        n = len(idx)
        if n < 2:
            return

        cfg = self.config
        r2 = cfg.collision_radius ** 2
        deactivated = set()

        pos = self.positions[idx]  # (n, 2)

        for i in range(n):
            if idx[i] in deactivated:
                continue
            pi = pos[i]
            for j in range(i + 1, n):
                if idx[j] in deactivated:
                    continue
                pj = pos[j]
                dy = (pi[0] - pj[0]) % self.height
                dy = min(dy, self.height - dy)
                dx = (pi[1] - pj[1]) % self.width
                dx = min(dx, self.width - dx)
                dist2 = dy * dy + dx * dx
                if dist2 < r2:
                    # Fusion: i absorbiert j
                    ii, jj = idx[i], idx[j]
                    mi, mj = self.mass[ii], self.mass[jj]
                    mt = mi + mj
                    # Masse-gewichtete Position
                    self.positions[ii] = (
                        (mi * self.positions[ii] + mj * self.positions[jj]) / mt
                    )
                    # Masse-gewichteter Impuls
                    self.velocities[ii] = (
                        (mi * self.velocities[ii] + mj * self.velocities[jj]) / mt
                    )
                    # Energie addieren (Energie ist extensiv)
                    self.energy[ii] = np.clip(
                        (mi * self.energy[ii] + mj * self.energy[jj]) / mt, 0.0, 1.0
                    )
                    self.mass[ii] = mt
                    self.active[jj] = False
                    deactivated.add(jj)
                    # Aktualisiere pos für i (in-place)
                    pos[i] = self.positions[ii]

    # ──────────────────────────────────────────────────────────────
    # Partikel-Zustand
    # ──────────────────────────────────────────────────────────────

    @property
    def n_active(self) -> int:
        """Anzahl aktiver Partikel."""
        return int(self.active.sum())

    def active_positions(self) -> np.ndarray:
        """Gibt (n_active, 2) Array mit (y, x)-Positionen aktiver Partikel."""
        return self.positions[self.active]

    def active_masses(self) -> np.ndarray:
        """Gibt 1-D Array mit Massen aktiver Partikel."""
        return self.mass[self.active]

    def active_energies(self) -> np.ndarray:
        """Gibt 1-D Array mit Energien aktiver Partikel."""
        return self.energy[self.active]

    def summary(self) -> dict:
        """Gibt kompakte Statistik über das Partikel-System zurück.

        Returns
        -------
        Dictionary mit:
        - ``n_active``       – aktive Partikel
        - ``mean_mass``      – mittlere Masse
        - ``max_mass``       – schwerster Partikel (mögliche Aggregate)
        - ``mean_speed``     – mittlere Geschwindigkeit
        - ``mean_energy``    – mittlere Partikel-Energie
        - ``n_compartments`` – Proto-Kompartimente (mass >= min_mass_for_compartment)
        """
        idx = self._active_indices()
        if len(idx) == 0:
            return {
                "n_active": 0, "mean_mass": 0.0, "max_mass": 0.0,
                "mean_speed": 0.0, "mean_energy": 0.0, "n_compartments": 0,
            }
        speeds = np.sqrt(
            self.velocities[idx, 0] ** 2 + self.velocities[idx, 1] ** 2
        )
        n_comp = int((self.mass[idx] >= self.config.min_mass_for_compartment).sum())
        return {
            "n_active":      int(len(idx)),
            "mean_mass":     round(float(self.mass[idx].mean()), 3),
            "max_mass":      round(float(self.mass[idx].max()), 3),
            "mean_speed":    round(float(speeds.mean()), 5),
            "mean_energy":   round(float(self.energy[idx].mean()), 4),
            "n_compartments": n_comp,
        }


# ──────────────────────────────────────────────────────────────────
# Tick-Integration
# ──────────────────────────────────────────────────────────────────

def step_particles(
    particles: ParticleSystem,
    state: GridState,
    do_collisions: bool = True,
) -> None:
    """Führe einen vollständigen Partikel-Tick aus.

    Reihenfolge:
        1. Feld → Partikel (Felder beschleunigen Partikel)
        2. Partikel → Feld (Partikel verändern Felder)
        3. Bewegung (Positionen + Dämpfung)
        4. Kollisionen + Aggregation (optional)

    Parameters
    ----------
    particles:
        ParticleSystem (wird in-place verändert).
    state:
        GridState (wird in-place durch Partikel-zu-Feld-Kopplung verändert).
    do_collisions:
        Ob Kollisionserkennung aktiv sein soll.
    """
    particles.apply_field_to_particles(state)
    particles.apply_particles_to_field(state)
    particles.move()
    if do_collisions:
        particles.apply_collisions()
