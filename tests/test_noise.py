"""
tests/test_noise.py – Tests für strukturiertes Rauschen.

Geprüft wird:
- Deterministik: gleiche Parameter → gleicher Output
- Verschiedene Ticks → verschiedener Output
- Amplitude wird eingehalten
- Korrekte Form
"""

import numpy as np
import pytest

from emergent_noise.noise.structured_noise import make_structured_noise


def test_noise_shape() -> None:
    noise = make_structured_noise(16, 24, amplitude=0.1, scale=4.0, seed=1)
    assert noise.shape == (16, 24)


def test_noise_dtype() -> None:
    noise = make_structured_noise(8, 8, amplitude=0.05, scale=4.0, seed=1)
    assert noise.dtype == np.float32


def test_noise_amplitude_bound() -> None:
    """Rauschfeld-Werte müssen innerhalb [-amplitude, amplitude] liegen."""
    amp = 0.05
    noise = make_structured_noise(32, 32, amplitude=amp, scale=6.0, seed=99)
    assert noise.min() >= -amp - 1e-6
    assert noise.max() <= amp + 1e-6


def test_noise_deterministic() -> None:
    """Gleicher Seed + Tick → identisches Rauschfeld."""
    n1 = make_structured_noise(16, 16, amplitude=0.1, scale=4.0, seed=5, tick=10)
    n2 = make_structured_noise(16, 16, amplitude=0.1, scale=4.0, seed=5, tick=10)
    np.testing.assert_array_equal(n1, n2)


def test_noise_different_ticks_differ() -> None:
    """Verschiedene Ticks müssen verschiedene Rauschfelder erzeugen."""
    n1 = make_structured_noise(16, 16, amplitude=0.1, scale=4.0, seed=5, tick=0)
    n2 = make_structured_noise(16, 16, amplitude=0.1, scale=4.0, seed=5, tick=1)
    assert not np.array_equal(n1, n2)


def test_noise_not_all_zero() -> None:
    """Rauschfeld darf nicht vollständig null sein."""
    noise = make_structured_noise(16, 16, amplitude=0.1, scale=4.0, seed=42)
    assert not np.all(noise == 0.0)
