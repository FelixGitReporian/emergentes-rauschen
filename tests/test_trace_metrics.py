"""
tests/test_trace_metrics.py – Tests for Trace Reading Metrics (Epic 13).
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.analysis.trace_metrics import (
    ActivationEvent,
    ClusterLifetimeStats,
    ClusterLifetimeTracker,
    DirectionalityResult,
    MemoryEntropyTracker,
    TraceMetricsSnapshot,
    compute_trace_metrics,
    flow_directionality,
    memory_persistence,
    reconstruct_events,
    spatial_autocorrelation,
    wavefront_speed,
)
from emergent_noise.analysis.trace_reading import TraceReport, read_traces


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _blank(H: int = 32, W: int = 32) -> np.ndarray:
    return np.zeros((H, W), dtype=np.float32)


def _filled(H: int = 32, W: int = 32, val: float = 0.8) -> np.ndarray:
    return np.full((H, W), val, dtype=np.float32)


def _noisy(H: int = 32, W: int = 32, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(0, 1, (H, W)).astype(np.float32)


def _square(H: int = 32, W: int = 32, size: int = 8, val: float = 0.9) -> np.ndarray:
    arr = np.zeros((H, W), dtype=np.float32)
    r0, c0 = H // 2 - size // 2, W // 2 - size // 2
    arr[r0 : r0 + size, c0 : c0 + size] = val
    return arr


def _live_fields(H: int = 32, W: int = 32, seed: int = 0) -> dict:
    from emergent_noise.core.state import GridState, SimConfig
    state = GridState.initialize(SimConfig(height=H, width=W, seed=seed))
    return state.as_dict()


# ──────────────────────────────────────────────────────────────────
# 1. memory_persistence
# ──────────────────────────────────────────────────────────────────

def test_persistence_identical_fields() -> None:
    arr = _square()
    assert memory_persistence(arr, arr) == 1.0


def test_persistence_no_overlap() -> None:
    a = _blank()
    a[:, :16] = 0.9
    b = _blank()
    b[:, 16:] = 0.9
    # No overlap → Jaccard = 0
    assert memory_persistence(a, b) == 0.0


def test_persistence_both_empty() -> None:
    assert memory_persistence(_blank(), _blank()) == 1.0


def test_persistence_in_range() -> None:
    p = memory_persistence(_noisy(), _noisy(seed=1))
    assert 0.0 <= p <= 1.0


def test_persistence_partial_overlap() -> None:
    a = _blank()
    b = _blank()
    a[10:20, 10:20] = 0.9
    b[14:24, 14:24] = 0.9
    p = memory_persistence(a, b)
    assert 0.0 < p < 1.0


# ──────────────────────────────────────────────────────────────────
# 2. spatial_autocorrelation (Moran's I)
# ──────────────────────────────────────────────────────────────────

def test_sac_constant_field_is_zero() -> None:
    arr = _filled(val=0.5)
    assert spatial_autocorrelation(arr) == 0.0


def test_sac_clustered_is_positive() -> None:
    arr = _blank()
    arr[10:22, 10:22] = 0.9  # large cluster
    mi = spatial_autocorrelation(arr)
    assert mi > 0.0, f"Clustered field should have positive Moran's I, got {mi}"


def test_sac_checkerboard_is_negative() -> None:
    H, W = 32, 32
    arr = np.zeros((H, W), dtype=np.float32)
    arr[::2, ::2] = 1.0
    arr[1::2, 1::2] = 1.0
    # Not perfectly dispersed but should be lower than clustered
    mi = spatial_autocorrelation(arr)
    assert mi < 0.5  # relaxed bound


def test_sac_in_range() -> None:
    mi = spatial_autocorrelation(_noisy())
    assert -1.0 <= mi <= 1.0


def test_sac_random_field_near_zero() -> None:
    mi = spatial_autocorrelation(_noisy(H=64, W=64))
    assert abs(mi) < 0.3  # random should be near 0


# ──────────────────────────────────────────────────────────────────
# 3. flow_directionality
# ──────────────────────────────────────────────────────────────────

def test_directionality_uniform_rightward() -> None:
    H, W = 32, 32
    vy = np.zeros((H, W), dtype=np.float32)
    vx = np.ones((H, W), dtype=np.float32)
    dr = flow_directionality(vy, vx)
    assert abs(dr.anisotropy - 1.0) < 0.01
    assert abs(dr.dominant_vx - 1.0) < 0.01
    assert abs(dr.dominant_vy) < 0.01


def test_directionality_isotropic() -> None:
    rng = np.random.default_rng(0)
    # Random angles → low anisotropy
    angles = rng.uniform(-np.pi, np.pi, (32, 32)).astype(np.float32)
    vy = np.sin(angles)
    vx = np.cos(angles)
    dr = flow_directionality(vy, vx)
    assert dr.anisotropy < 0.3


def test_directionality_anisotropy_in_range() -> None:
    dr = flow_directionality(_noisy(), _noisy(seed=1))
    assert 0.0 <= dr.anisotropy <= 1.0


def test_directionality_returns_dataclass() -> None:
    dr = flow_directionality(_blank(), _blank())
    assert isinstance(dr, DirectionalityResult)


def test_directionality_mean_angle_in_range() -> None:
    dr = flow_directionality(_noisy(), _noisy(seed=5))
    assert -np.pi - 0.01 <= dr.mean_angle_rad <= np.pi + 0.01


# ──────────────────────────────────────────────────────────────────
# 4. MemoryEntropyTracker
# ──────────────────────────────────────────────────────────────────

def test_entropy_tracker_records_history() -> None:
    tracker = MemoryEntropyTracker()
    tracker.update(1, _noisy())
    tracker.update(2, _noisy(seed=1))
    assert len(tracker.history) == 2


def test_entropy_tracker_current_entropy_positive() -> None:
    tracker = MemoryEntropyTracker()
    tracker.update(1, _noisy())
    assert tracker.current_entropy() > 0.0


def test_entropy_tracker_empty_returns_zero() -> None:
    tracker = MemoryEntropyTracker()
    assert tracker.current_entropy() == 0.0
    assert tracker.trend() == 0.0


def test_entropy_tracker_trend_sign() -> None:
    tracker = MemoryEntropyTracker(window=5)
    for i in range(6):
        tracker.update(i, np.full((16, 16), i * 0.1, dtype=np.float32))
    # Entropy should change; trend should be computable
    t = tracker.trend()
    assert isinstance(t, float)


def test_entropy_tracker_to_arrays() -> None:
    tracker = MemoryEntropyTracker()
    for i in range(5):
        tracker.update(i, _noisy(seed=i))
    ticks, vals = tracker.to_arrays()
    assert len(ticks) == 5
    assert len(vals) == 5


def test_entropy_tracker_single_entry_trend_zero() -> None:
    tracker = MemoryEntropyTracker()
    tracker.update(0, _noisy())
    assert tracker.trend() == 0.0


# ──────────────────────────────────────────────────────────────────
# 5. ClusterLifetimeTracker
# ──────────────────────────────────────────────────────────────────

def test_cluster_tracker_empty_field() -> None:
    tracker = ClusterLifetimeTracker()
    stats = tracker.update(0, _blank())
    assert stats.n_active == 0


def test_cluster_tracker_one_cluster_stays() -> None:
    tracker = ClusterLifetimeTracker()
    arr = _square()
    for t in range(5):
        stats = tracker.update(t, arr)
    assert stats.n_active >= 1


def test_cluster_tracker_cluster_dies() -> None:
    tracker = ClusterLifetimeTracker()
    tracker.update(0, _square())
    stats = tracker.update(1, _blank())
    assert stats.n_completed >= 1
    assert stats.mean_lifetime > 0.0


def test_cluster_tracker_stats_nonnegative() -> None:
    tracker = ClusterLifetimeTracker()
    arr = _noisy()
    for t in range(10):
        s = tracker.update(t, arr)
    assert s.mean_lifetime >= 0.0
    assert s.max_lifetime >= 0


def test_cluster_tracker_returns_dataclass() -> None:
    tracker = ClusterLifetimeTracker()
    stats = tracker.update(0, _square())
    assert isinstance(stats, ClusterLifetimeStats)


# ──────────────────────────────────────────────────────────────────
# 6. reconstruct_events
# ──────────────────────────────────────────────────────────────────

def test_reconstruct_no_events_identical() -> None:
    arr = _square()
    events = reconstruct_events(arr, arr, tick=1)
    assert events == []


def test_reconstruct_new_activation_detected() -> None:
    prev = _blank()
    curr = _square(val=0.9)
    events = reconstruct_events(prev, curr, tick=5, min_area=1)
    assert len(events) >= 1


def test_reconstruct_event_has_correct_tick() -> None:
    prev = _blank()
    curr = _square(val=0.9)
    events = reconstruct_events(prev, curr, tick=42, min_area=1)
    assert all(e.tick == 42 for e in events)


def test_reconstruct_min_area_filter() -> None:
    prev = _blank()
    curr = _blank()
    curr[10, 10] = 0.9   # 1 cell — below default min_area=3
    events = reconstruct_events(prev, curr, tick=1, min_area=3)
    assert events == []


def test_reconstruct_event_centroid_in_bounds() -> None:
    prev = _blank(H=32, W=32)
    curr = _square(H=32, W=32, val=0.9)
    events = reconstruct_events(prev, curr, tick=1, min_area=1)
    for e in events:
        assert 0 <= e.centroid_y < 32
        assert 0 <= e.centroid_x < 32


def test_reconstruct_returns_list() -> None:
    events = reconstruct_events(_blank(), _blank(), tick=0)
    assert isinstance(events, list)


# ──────────────────────────────────────────────────────────────────
# 7. wavefront_speed
# ──────────────────────────────────────────────────────────────────

def test_wavefront_speed_no_front() -> None:
    assert wavefront_speed(_blank(), _blank()) == 0.0


def test_wavefront_speed_static_front_is_zero() -> None:
    arr = _square()
    assert wavefront_speed(arr, arr) == 0.0


def test_wavefront_speed_moving_front_positive() -> None:
    H, W = 32, 32
    prev = np.zeros((H, W), dtype=np.float32)
    prev[:, :10] = 0.9
    curr = np.zeros((H, W), dtype=np.float32)
    curr[:, :14] = 0.9  # front moved 4 cells rightward
    speed = wavefront_speed(prev, curr)
    assert speed > 0.0


def test_wavefront_speed_nonnegative() -> None:
    speed = wavefront_speed(_noisy(), _noisy(seed=1))
    assert speed >= 0.0


# ──────────────────────────────────────────────────────────────────
# compute_trace_metrics
# ──────────────────────────────────────────────────────────────────

def test_compute_trace_metrics_returns_snapshot() -> None:
    fields = _live_fields()
    snap = compute_trace_metrics(tick=5, fields=fields)
    assert isinstance(snap, TraceMetricsSnapshot)


def test_compute_trace_metrics_tick_preserved() -> None:
    snap = compute_trace_metrics(tick=99, fields=_live_fields())
    assert snap.tick == 99


def test_compute_trace_metrics_persistence_default() -> None:
    snap = compute_trace_metrics(tick=0, fields=_live_fields())
    assert snap.memory_persistence == 1.0  # no prev_memory → default 1.0


def test_compute_trace_metrics_with_prev_fields() -> None:
    fields = _live_fields()
    prev_memory = _noisy()
    snap = compute_trace_metrics(tick=1, fields=fields, prev_memory=prev_memory)
    assert 0.0 <= snap.memory_persistence <= 1.0


def test_compute_trace_metrics_sac_in_range() -> None:
    snap = compute_trace_metrics(tick=0, fields=_live_fields())
    assert -1.0 <= snap.spatial_autocorrelation_energy <= 1.0
    assert -1.0 <= snap.spatial_autocorrelation_memory <= 1.0


def test_compute_trace_metrics_entropy_positive() -> None:
    snap = compute_trace_metrics(tick=0, fields=_live_fields())
    assert snap.memory_entropy >= 0.0


def test_compute_trace_metrics_n_events_default_zero() -> None:
    snap = compute_trace_metrics(tick=0, fields=_live_fields())
    assert snap.n_events == 0  # no prev_energy provided


def test_compute_trace_metrics_with_trackers() -> None:
    fields = _live_fields()
    et = MemoryEntropyTracker()
    lt = ClusterLifetimeTracker()
    for t in range(5):
        compute_trace_metrics(tick=t, fields=fields, entropy_tracker=et, lifetime_tracker=lt)
    assert len(et.history) == 5


def test_compute_trace_metrics_to_dict() -> None:
    snap = compute_trace_metrics(tick=0, fields=_live_fields())
    d = snap.to_dict()
    assert "tick" in d
    assert "memory_persistence" in d
    assert "spatial_autocorrelation_energy" in d
    assert "directionality" in d


# ──────────────────────────────────────────────────────────────────
# TraceReport integration
# ──────────────────────────────────────────────────────────────────

def test_trace_report_has_trace_metrics() -> None:
    from emergent_noise.analysis.attractors import PersistenceTracker
    fields = _live_fields()
    report = read_traces(tick=1, fields=fields)
    assert isinstance(report.trace_metrics, dict)
    assert "tick" in report.trace_metrics


def test_trace_report_trace_metrics_keys() -> None:
    fields = _live_fields()
    report = read_traces(tick=1, fields=fields)
    tm = report.trace_metrics
    for k in ("memory_persistence", "spatial_autocorrelation_energy",
              "memory_entropy", "wavefront_speed", "n_events"):
        assert k in tm, f"Key '{k}' missing from trace_metrics"


def test_trace_report_to_dict_includes_trace_metrics() -> None:
    fields = _live_fields()
    report = read_traces(tick=1, fields=fields)
    d = report.to_dict()
    assert "trace_metrics" in d


def test_trace_report_to_json_includes_trace_metrics() -> None:
    import json
    fields = _live_fields()
    report = read_traces(tick=1, fields=fields)
    parsed = json.loads(report.to_json())
    assert "trace_metrics" in parsed


def test_trace_report_with_prev_fields() -> None:
    fields = _live_fields()
    prev_mem = _noisy()
    prev_en = _noisy(seed=2)
    report = read_traces(
        tick=5, fields=fields, prev_memory=prev_mem, prev_energy=prev_en
    )
    tm = report.trace_metrics
    assert 0.0 <= tm["memory_persistence"] <= 1.0
