"""
rules/diffusion.py – Diffusionsregeln für Energie und Information.

Diffusion transportiert skalare Größen von Zellen hoher Konzentration zu
Zellen niedriger Konzentration. Wir nutzen einen diskreten Laplace-Operator
(5-Punkt-Stern) auf dem periodischen Gitter.

Wissenschaftliche Motivation:
    Diffusion ist der einfachste Transportmechanismus in Feldsimulationen und
    Grundlage von Turing-Musterbildung (Reaktions-Diffusions-Systemen).
    Unterschiedliche Raten für verschiedene Felder sind entscheidend –
    langsam diffundierende Information gegenüber schnell diffundierender Energie
    kann Gradienten und Muster erzeugen.

Randbedingung: periodisch (toroidale Topologie).

Performance:
    Wenn Numba installiert ist, wird der Laplace-Kern JIT-kompiliert
    (erster Aufruf kompiliert, danach deutlich schneller für große Grids).
    Ohne Numba wird transparent auf NumPy zurückgefallen.
"""

from __future__ import annotations

import numpy as np

from emergent_noise.core.state import GridState, SimConfig

try:
    from numba import njit as _njit  # type: ignore[import-untyped]
    _NUMBA = True
except ImportError:
    _NUMBA = False


def _laplacian_numpy(field: np.ndarray) -> np.ndarray:
    """5-Punkt-Laplace-Operator (NumPy, periodisch)."""
    return (
        np.roll(field, 1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, 1, axis=1)
        + np.roll(field, -1, axis=1)
        - 4.0 * field
    )


if _NUMBA:
    @_njit(cache=True, fastmath=True)
    def _laplacian_numba(field: np.ndarray) -> np.ndarray:  # type: ignore[misc]
        """Numba-JIT-kompilierter 5-Punkt-Laplace mit explizitem periodischem Index."""
        H, W = field.shape
        out = np.empty_like(field)
        for i in range(H):
            ip = (i + 1) % H
            im = (i - 1) % H
            for j in range(W):
                jp = (j + 1) % W
                jm = (j - 1) % W
                out[i, j] = (
                    field[ip, j] + field[im, j] + field[i, jp] + field[i, jm]
                    - 4.0 * field[i, j]
                )
        return out

    def _laplacian(field: np.ndarray) -> np.ndarray:
        """Laplace-Operator: Numba wenn verfügbar, sonst NumPy."""
        return _laplacian_numba(field)
else:
    def _laplacian(field: np.ndarray) -> np.ndarray:  # type: ignore[misc]
        """Laplace-Operator: NumPy-Fallback (Numba nicht installiert)."""
        return _laplacian_numpy(field)


def apply_diffusion(state: GridState, config: SimConfig) -> None:
    """Diffundiere Energie und Information in-place.

    Energie diffundiert schnell (``config.diffusion_energy``), Information
    langsam (``config.diffusion_information``). Die unterschiedlichen Raten
    erzeugen Gradienten, die als Triebkraft für Reaktionen wirken können.

    Formel: f_new = f + rate * ∇²f
    """
    state.energy += config.diffusion_energy * _laplacian(state.energy)
    state.information += config.diffusion_information * _laplacian(state.information)
