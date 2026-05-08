"""
analysis/mutual_information.py – Mutual Information zwischen Feldern und Regionen.

Mutual Information (MI) misst, wie viel Information über ein Feld durch ein
anderes gewonnen werden kann. MI = 0 bedeutet statistische Unabhängigkeit;
hohe MI bedeutet starke Kopplung.

Implementierte Funktionen:

1. field_mi(a, b)       – MI zwischen zwei Feldern (ganzer Grid).
2. mi_matrix(fields)    – Paarweise MI-Matrix aller Felder.
3. local_mi(a, b, r)    – Räumlich aufgelöste lokale MI (Fenstergröße r).

Wissenschaftliche Vorsicht:
    MI misst statistische Abhängigkeit, keine Kausalität. Hohe MI zwischen
    energy und coherence bedeutet *Korrelation*, nicht dass energy coherence
    *verursacht*. Kausale Schlüsse erfordern weitere Analyse (z.B. Transfer Entropy).
"""

from __future__ import annotations

import numpy as np


def _histogram_mi(
    a: np.ndarray,
    b: np.ndarray,
    n_bins: int = 16,
) -> float:
    """Berechne MI via 2-D-Histogramm (diskrete Näherung).

    MI(A;B) = H(A) + H(B) − H(A,B)
    Normalisiert auf [0, 1] durch Division durch min(H(A), H(B)).
    """
    a_flat = a.ravel().astype(np.float64)
    b_flat = b.ravel().astype(np.float64)

    # Wertebereich auf [0,1] begrenzen
    a_flat = np.clip(a_flat, 0.0, 1.0)
    b_flat = np.clip(b_flat, 0.0, 1.0)

    # Gemeinsames 2-D-Histogramm
    joint, _, _ = np.histogram2d(a_flat, b_flat, bins=n_bins, range=[[0, 1], [0, 1]])
    joint = joint / joint.sum()

    # Marginal-Verteilungen
    p_a = joint.sum(axis=1)
    p_b = joint.sum(axis=0)

    # Entropien
    def _entropy(p: np.ndarray) -> float:
        mask = p > 0
        return float(-np.sum(p[mask] * np.log2(p[mask])))

    h_a = _entropy(p_a)
    h_b = _entropy(p_b)
    h_ab = _entropy(joint.ravel())

    mi = h_a + h_b - h_ab
    mi = max(0.0, mi)  # numerische Bereinigung

    normalizer = min(h_a, h_b)
    return float(mi / normalizer) if normalizer > 1e-10 else 0.0


def field_mi(
    a: np.ndarray,
    b: np.ndarray,
    n_bins: int = 16,
) -> float:
    """Berechne normalisierte Mutual Information zwischen zwei 2-D-Feldern.

    Parameters
    ----------
    a, b:
        2-D float-Arrays (müssen gleiche Shape haben).
    n_bins:
        Bins für die Histogramm-Näherung.

    Returns
    -------
    Normalisierte MI in [0, 1]. 0 = unabhängig, 1 = funktional abhängig.
    """
    assert a.shape == b.shape, "Felder müssen gleiche Shape haben."
    return _histogram_mi(a, b, n_bins)


def mi_matrix(
    fields: dict[str, np.ndarray],
    n_bins: int = 16,
) -> dict[tuple[str, str], float]:
    """Berechne paarweise MI-Matrix für alle Feldkombinationen.

    Parameters
    ----------
    fields:
        Dictionary {feldname: 2-D-array}.
    n_bins:
        Bins für Histogramm-Näherung.

    Returns
    -------
    Dictionary {(name_a, name_b): mi_value} für alle Paare (a ≠ b).
    MI ist symmetrisch: MI(A,B) = MI(B,A).
    """
    names = list(fields.keys())
    result: dict[tuple[str, str], float] = {}
    for i, na in enumerate(names):
        for nb in names[i + 1 :]:
            mi = _histogram_mi(fields[na], fields[nb], n_bins)
            result[(na, nb)] = mi
            result[(nb, na)] = mi
    return result


def local_mi(
    a: np.ndarray,
    b: np.ndarray,
    radius: int = 4,
    n_bins: int = 8,
) -> np.ndarray:
    """Räumlich aufgelöste lokale MI (gleitendes Fenster).

    Für jede Zelle (i, j) wird MI in einem (2r+1)×(2r+1)-Fenster berechnet.
    Rand: periodisch.

    Parameters
    ----------
    a, b:
        2-D float-Arrays gleicher Shape.
    radius:
        Halb-Fenstergröße in Zellen.
    n_bins:
        Bins pro Histogramm-Achse (klein halten wegen Performance).

    Returns
    -------
    2-D float-Array mit lokaler MI, gleiche Shape wie Eingabe.
    """
    H, W = a.shape
    out = np.zeros((H, W), dtype=np.float32)
    w = radius
    for i in range(H):
        for j in range(W):
            rows = [(i + di) % H for di in range(-w, w + 1)]
            cols = [(j + dj) % W for dj in range(-w, w + 1)]
            patch_a = a[np.ix_(rows, cols)]
            patch_b = b[np.ix_(rows, cols)]
            out[i, j] = _histogram_mi(patch_a, patch_b, n_bins)
    return out
