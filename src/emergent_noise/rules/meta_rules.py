"""
rules/meta_rules.py – Meta-Regel-Evolution (Regel-Genom).

Dieses Modul implementiert die Selbstmodifikation des Regelsystems:
Lokale Regelprofile (Genome) können mutieren, selektiert und gesichert werden.

Architektur (Arbeitsmappe Kap. 9):
    Jede Zelle besitzt ein lokales Regelprofil (Regelgenom):
    - ``genome_strength``   – lokale Reaktionsstärke (beeinflusst Aktivierungsreaktion)
    - ``genome_threshold``  – lokaler Energie-Schwellwert (beeinflusst Aktivierungsschwelle)

    Diese Genome sind float32-Arrays der Form (height, width) in GridState.
    ``apply_meta_rules`` führt pro Tick drei Schritte aus:

    1. MUTATION (Zufällige Variation, Kap. 9.3):
       Zufällig ausgewählte Zellen erhalten eine kleine Zufallsänderung
       ihrer Genome-Parameter. Rate und Stärke sind konfigurierbar.
       → Erzeugt genetische Diversität.

    2. SELEKTION (Fitness-basierter Kopier-Schritt, Kap. 9.4):
       Fitness = lokale_kohärenz * (1 - lokale_energievarianz).
       Zellen mit hoher Fitness propagieren ihr Profil auf schwächere Nachbarn.
       → Erfolgreiche Profile breiten sich aus.

    3. RETENTION (Gedächtnisschreiben, Kap. 9.5):
       Zellen mit Fitness > retention_threshold schreiben ihr Profil
       ins Gedächtnisfeld (memory) als schwaches Signal.
       → Persistente Muster hinterlassen strukturelle Spuren.

Fitness-Definition (heuristisch):
    fitness(i,j) = coherence(i,j) * (1 - local_energy_variance(i,j))
    Hohe Kohärenz + niedrige lokale Energievarianz = stabiles, geordnetes Profil.
    Dies ist ein Proxy, kein Beweis für biologische Fitness.

Wissenschaftliche Vorsicht:
    Meta-Regel-Evolution ist eine Abstraktion, kein Modell realer Genetik.
    Die verwendeten Fitness-Proxies (Kohärenz, Energievarianz) sind heuristisch.
    Das Ziel ist die Exploration emergenter Selbstmodifikation, nicht die
    Reproduktion spezifischer biologischer oder physikalischer Mechanismen.
    Regime-Änderungen durch Evolution sind Hypothesen, keine Belege.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter

from emergent_noise.core.state import GridState, SimConfig


def _compute_fitness(state: GridState) -> np.ndarray:
    """Berechne die lokale Fitness jeder Zelle.

    Fitness = coherence * (1 - lokale_energievarianz)

    Hohe Kohärenz (stabile Synchronität) und niedrige lokale Energievarianz
    (ruhiges, vorhersagbares Verhalten) gelten als Proxy für ein erfolgreiches
    lokales Regelprofil.

    Parameters
    ----------
    state:
        Aktueller GridState.

    Returns
    -------
    2-D float32-Array mit Fitness-Werten in [0, 1].
    """
    # Lokale Energievarianz: Abweichung vom lokalen Mittel (Fenster 3×3)
    local_mean = uniform_filter(state.energy.astype(np.float64), size=3).astype(np.float32)
    local_var = uniform_filter(
        (state.energy - local_mean) ** 2, size=3
    ).astype(np.float32)
    # Normalisiere Varianz auf [0,1] (max theoretisch 0.25 für binäres Feld)
    local_var_norm = np.clip(local_var / 0.25, 0.0, 1.0)

    fitness = state.coherence * (1.0 - local_var_norm)
    return np.clip(fitness, 0.0, 1.0).astype(np.float32)


def _apply_mutation(
    state: GridState,
    config: SimConfig,
    rng: np.random.Generator,
) -> None:
    """Führe zufällige Genome-Mutationen in-place durch.

    Wähle zufällig ``rate * H * W`` Zellen aus und verändere deren
    ``genome_strength`` oder ``genome_threshold`` um einen kleinen
    Zufallsbetrag in [-strength, +strength].

    Parameters
    ----------
    state:
        GridState (wird in-place verändert).
    config:
        SimConfig mit ``meta_mutation_rate`` und ``meta_mutation_strength``.
    rng:
        Zufallsgenerator (deterministisch aus tick+seed).
    """
    H, W = state.energy.shape
    n_cells = H * W
    n_mutate = max(1, int(config.meta_mutation_rate * n_cells))

    # Zufällig ausgewählte Zell-Indizes (flach)
    idx = rng.choice(n_cells, size=n_mutate, replace=False)
    rows, cols = np.unravel_index(idx, (H, W))

    s = config.meta_mutation_strength
    delta_s = rng.uniform(-s, s, n_mutate).astype(np.float32)
    delta_t = rng.uniform(-s, s, n_mutate).astype(np.float32)

    state.genome_strength[rows, cols] += delta_s
    state.genome_threshold[rows, cols] += delta_t


def _apply_selection(
    state: GridState,
    config: SimConfig,
    fitness: np.ndarray,
    rng: np.random.Generator,
) -> None:
    """Propagiere erfolgreiche Genome auf schwächere Nachbarzellen.

    Wähle ``selection_rate * H * W`` Zellen aus. Für jede ausgewählte Zelle:
    - Finde den besten Nachbarn (höchste Fitness im 3×3-Fenster).
    - Wenn der Nachbar fitter ist, kopiere dessen Genome-Werte.

    Dies entspricht einem einfachen lokalen Selektions-Schritt ohne
    Rekombination. Erfolgreiche Profile wandern durch den Raum.

    Parameters
    ----------
    state:
        GridState (wird in-place verändert).
    config:
        SimConfig mit ``meta_selection_rate``.
    fitness:
        Vorberechnetes Fitness-Array (H×W).
    rng:
        Zufallsgenerator.
    """
    H, W = state.energy.shape
    n_cells = H * W
    n_select = max(1, int(config.meta_selection_rate * n_cells))
    idx = rng.choice(n_cells, size=n_select, replace=False)
    rows, cols = np.unravel_index(idx, (H, W))

    for r, c in zip(rows, cols):
        best_fit = fitness[r, c]
        best_r, best_c = r, c
        # 3×3-Nachbarschaft (periodische Randbedingungen)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (r + dr) % H, (c + dc) % W
                if fitness[nr, nc] > best_fit:
                    best_fit = fitness[nr, nc]
                    best_r, best_c = nr, nc
        if best_r != r or best_c != c:
            state.genome_strength[r, c] = state.genome_strength[best_r, best_c]
            state.genome_threshold[r, c] = state.genome_threshold[best_r, best_c]


def _apply_retention(
    state: GridState,
    config: SimConfig,
    fitness: np.ndarray,
) -> None:
    """Schreibe erfolgreiche Regelprofile als schwaches Signal ins Gedächtnisfeld.

    Zellen mit Fitness > retention_threshold verstärken das memory-Feld.
    Das Gedächtnisfeld fungiert als Sediment: Bereiche, in denen dauerhaft
    erfolgreiche Regelprofile aktiv sind, hinterlassen eine Spur.

    Der Effekt ist absichtlich schwach (Faktor 0.01), damit er das Gedächtnis
    nicht dominiert und mit der normalen Gedächtnisdynamik koexistiert.

    Parameters
    ----------
    state:
        GridState (wird in-place verändert).
    config:
        SimConfig mit ``meta_retention_threshold``.
    fitness:
        Vorberechnetes Fitness-Array (H×W).
    """
    mask = fitness > config.meta_retention_threshold
    # Schwache Verstärkung des Gedächtnisses durch erfolgreiche Profile
    state.memory[mask] += 0.01 * fitness[mask]


def apply_meta_rules(state: GridState, config: SimConfig) -> None:
    """Führe alle Meta-Regel-Schritte in-place aus.

    Reihenfolge pro Tick:
        1. Fitness berechnen
        2. Mutation (zufällige Variationen)
        3. Selektion (lokale Ausbreitung fitter Profile)
        4. Retention (Gedächtnis-Spur)
        5. Genome clippen auf [0, 1]

    Wenn ``config.meta_enabled`` False ist, wird nichts ausgeführt.

    Parameters
    ----------
    state:
        GridState (wird in-place verändert).
    config:
        SimConfig mit allen ``meta_*``-Parametern.
    """
    if not config.meta_enabled:
        return

    # Deterministischer RNG: kombiniert globalen Seed + aktuellen Tick
    rng = np.random.default_rng(config.seed + state.tick * 997)

    fitness = _compute_fitness(state)
    _apply_mutation(state, config, rng)
    _apply_selection(state, config, fitness, rng)
    _apply_retention(state, config, fitness)

    # Genome-Werte auf [0,1] begrenzen (erfolgt auch in clip_all, hier explizit)
    np.clip(state.genome_strength,  0.0, 1.0, out=state.genome_strength)
    np.clip(state.genome_threshold, 0.0, 1.0, out=state.genome_threshold)
