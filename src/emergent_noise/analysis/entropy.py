"""
analysis/entropy.py – Shannon-Entropie und abgeleitete Metriken.

Entropie misst die mittlere Unvorhersagbarkeit eines Feldes. Ein Feld mit
gleichmäßig verteilten Werten hat hohe Entropie; ein Feld mit einem scharfen
Peak hat niedrige Entropie.

Wissenschaftliche Vorsicht:
    Entropie ist hier eine diskrete Näherung (Histogramm-Schätzung), keine
    exakte differentielle Entropie. Sie dient als erster Komplexitätsindikator,
    nicht als Information im streng physikalischen Sinne.
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState


def field_entropy(field: np.ndarray, n_bins: int = 32) -> float:
    """Berechne die normalisierte Shannon-Entropie eines 2-D-Feldes.

    Die Entropie wird über ein Histogramm mit ``n_bins`` Bins im Bereich [0, 1]
    geschätzt. Das Ergebnis wird auf [0, 1] normalisiert (log2(n_bins) als Maximum).

    Parameters
    ----------
    field:
        2-D float-Array mit Werten in [0, 1].
    n_bins:
        Anzahl der Histogramm-Bins.

    Returns
    -------
    float
        Normalisierte Shannon-Entropie in [0, 1]. Wert nahe 1 → sehr ungeordnet;
        Wert nahe 0 → sehr geordnet oder konstant.
    """
    counts, _ = np.histogram(field, bins=n_bins, range=(0.0, 1.0))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    raw_entropy = -np.sum(probs * np.log2(probs))
    max_entropy = np.log2(n_bins)
    return float(raw_entropy / max_entropy) if max_entropy > 0 else 0.0


def state_entropy_summary(state: GridState, n_bins: int = 32) -> dict[str, float]:
    """Berechne die normalisierte Shannon-Entropie für alle Felder des GridState.

    Returns
    -------
    dict[str, float]
        Feldname → normalisierte Entropie in [0, 1].
    """
    return {name: field_entropy(arr, n_bins) for name, arr in state.as_dict().items()}
