"""
noise/structured_noise.py – Strukturiertes, deterministisches Rauschen.

Statt weißem Rauschen verwenden wir eine Überlagerung von Sinus-Wellen mit
zufälligen Phasen und Frequenzen. Das erzeugt räumlich kohärentes Rauschen,
das einem Perlin-Noise-ähnlichen Charakter hat, aber ohne externe Abhängigkeiten
auskommt.

Wissenschaftliche Motivation:
    Strukturiertes Rauschen bricht Symmetrien auf vorhersagbar-reproduzierbare
    Weise und fördert Musterbildung (Turing-Instabilität, spontane Symmetriebrechung).
    Echtes weißes Rauschen würde kaum geordnete Muster erzeugen.
"""

from __future__ import annotations

import numpy as np


def make_structured_noise(
    height: int,
    width: int,
    amplitude: float,
    scale: float,
    seed: int,
    tick: int = 0,
) -> np.ndarray:
    """Erzeuge ein räumlich strukturiertes Rauschfeld.

    Das Feld entsteht durch Überlagerung von ``n_harmonics`` Sinus-Wellen mit
    zufälligen Richtungen, Phasen und Frequenzen nahe ``1/scale``. Das Ergebnis
    ist deterministisch für gegebene (seed, tick)-Kombination.

    Parameters
    ----------
    height, width:
        Gitterdimensionen.
    amplitude:
        Maximale Amplitude (Werte in [-amplitude, +amplitude]).
    scale:
        Charakteristische räumliche Länge in Zellen. Größere Werte →
        großräumigere Strukturen.
    seed:
        Basis-Seed; wird mit tick kombiniert für zeitliche Variation.
    tick:
        Aktueller Simulationsschritt; sorgt für Tick-zu-Tick-Variation.

    Returns
    -------
    np.ndarray, shape (height, width), dtype float32
        Rauschfeld mit Werten in [−amplitude, +amplitude].
    """
    rng = np.random.default_rng(seed + tick * 1_000_003)
    n_harmonics = 8

    ys = np.arange(height, dtype=np.float32)
    xs = np.arange(width, dtype=np.float32)
    grid_y, grid_x = np.meshgrid(ys, xs, indexing="ij")

    field = np.zeros((height, width), dtype=np.float32)

    base_freq = 1.0 / max(scale, 1.0)
    for _ in range(n_harmonics):
        freq = base_freq * rng.uniform(0.5, 2.0)
        angle = rng.uniform(0, 2 * np.pi)
        phase = rng.uniform(0, 2 * np.pi)
        kx = freq * np.cos(angle)
        ky = freq * np.sin(angle)
        field += np.sin(2 * np.pi * (kx * grid_x + ky * grid_y) + phase).astype(np.float32)

    # Normalisieren auf [-1, 1] dann skalieren
    max_abs = np.max(np.abs(field))
    if max_abs > 0:
        field /= max_abs
    field *= amplitude
    return field
