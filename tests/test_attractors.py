"""
tests/test_attractors.py – Tests für analysis/attractors.py.
"""

import numpy as np
import pytest

from emergent_noise.analysis.attractors import (
    ClusterResult,
    FieldSummary,
    PersistenceTracker,
    PhaseIndicator,
    compute_phase_indicator,
    field_summary,
    find_clusters,
)
from emergent_noise.core.state import GridState, SimConfig


# ------------------------------------------------------------------
# FieldSummary
# ------------------------------------------------------------------

def test_field_summary_values() -> None:
    arr = np.array([[0.0, 0.5], [1.0, 0.25]], dtype=np.float32)
    s = field_summary("test", arr, threshold=0.5)
    assert s.name == "test"
    assert s.mean == pytest.approx(0.4375, abs=1e-4)
    assert 0.0 <= s.active_fraction <= 1.0


# ------------------------------------------------------------------
# Cluster
# ------------------------------------------------------------------

def test_find_clusters_empty() -> None:
    arr = np.zeros((16, 16), dtype=np.float32)
    result = find_clusters("energy", arr, threshold=0.5)
    assert result.n_clusters == 0
    assert result.largest_cluster_size == 0


def test_find_clusters_single_blob() -> None:
    arr = np.zeros((16, 16), dtype=np.float32)
    arr[4:8, 4:8] = 0.9   # ein quadratisches Cluster
    result = find_clusters("energy", arr, threshold=0.5)
    assert result.n_clusters >= 1
    assert result.largest_cluster_size >= 1


def test_find_clusters_two_blobs() -> None:
    arr = np.zeros((16, 16), dtype=np.float32)
    arr[1:3, 1:3] = 0.9
    arr[10:13, 10:13] = 0.9
    result = find_clusters("energy", arr, threshold=0.5)
    assert result.n_clusters == 2


# ------------------------------------------------------------------
# PersistenceTracker
# ------------------------------------------------------------------

def test_persistence_constant_field_high() -> None:
    """Konstantes Feld → Persistenz nahe 1."""
    tracker = PersistenceTracker(window=5)
    field = np.ones((16, 16), dtype=np.float32) * 0.5
    for _ in range(5):
        tracker.update({"energy": field})
    assert tracker.persistence["energy"] > 0.99


def test_persistence_random_field_low() -> None:
    """Zufällig wechselndes Feld → Persistenz < 1."""
    rng = np.random.default_rng(0)
    tracker = PersistenceTracker(window=5)
    for _ in range(6):
        tracker.update({"energy": rng.uniform(0, 1, (16, 16)).astype(np.float32)})
    assert tracker.persistence["energy"] < 0.9


def test_persistence_most_stable_returns_key() -> None:
    tracker = PersistenceTracker(window=3)
    rng = np.random.default_rng(1)
    for _ in range(4):
        tracker.update({
            "energy": np.ones((8, 8), dtype=np.float32) * 0.5,
            "noise": rng.uniform(0, 1, (8, 8)).astype(np.float32),
        })
    assert tracker.most_stable() == "energy"
    assert tracker.least_stable() == "noise"


# ------------------------------------------------------------------
# PhaseIndicator
# ------------------------------------------------------------------

def test_phase_indicator_returns_dataclass() -> None:
    config = SimConfig(height=16, width=16, seed=0)
    state = GridState.initialize(config)
    ind = compute_phase_indicator(state.tick, state.as_dict())
    assert isinstance(ind, PhaseIndicator)
    assert ind.energy_variance >= 0.0
    assert isinstance(ind.near_transition, bool)
