"""
analysis/trace_metrics.py – Quantitative Trace Reading Metrics (Epic 13).

Implements seven independent, stateless metric functions plus two stateful
tracker classes for time-series analysis.

Metrics
-------
1. memory_persistence        – how stable the memory field is over time.
2. spatial_autocorrelation   – Moran's I for any 2-D field.
3. directionality            – dominant flow direction + anisotropy index.
4. memory_entropy_timeseries – append-only entropy log for the memory field.
5. cluster_lifetimes         – track when labelled clusters appear/disappear.
6. event_reconstruction      – detect discrete activation events in a field.
7. wavefront_speed           – estimate propagation speed of an excitable wavefront.

All pure functions take numpy arrays and return scalars, dicts or dataclasses.
Tracker classes accumulate state across ticks; they are designed to be stored
in session state or passed between loop iterations.

Scientific caution:
    Moran's I is an asymptotic statistic; interpretation requires N >> 1.
    Wavefront speed estimation uses frame differencing — it is an approximation
    valid only when a single dominant front is present.
    Cluster lifetimes assume label consistency across ticks (labels may shuffle
    between ticks if the labelling order changes — this implementation tracks
    by approximate centroid proximity, not by exact label identity).
    None of these metrics constitute proof of biological or physical processes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import label, center_of_mass


# ──────────────────────────────────────────────────────────────────
# 1. Memory persistence
# ──────────────────────────────────────────────────────────────────

def memory_persistence(
    prev: np.ndarray,
    curr: np.ndarray,
    threshold: float = 0.3,
) -> float:
    """Measure how much of the memory field persists between two ticks.

    Persistence = Jaccard similarity of the active regions in ``prev`` and
    ``curr``.  A value of 1.0 means the active region is identical; 0.0 means
    no overlap.

    Parameters
    ----------
    prev, curr:
        Memory field at consecutive ticks (float32, shape (H, W)).
    threshold:
        Cells above this value are considered 'active'.

    Returns
    -------
    Jaccard similarity ∈ [0, 1].
    """
    a = prev > threshold
    b = curr > threshold
    intersection = int((a & b).sum())
    union = int((a | b).sum())
    if union == 0:
        return 1.0  # both empty → perfectly stable (nothing to change)
    return round(intersection / union, 5)


# ──────────────────────────────────────────────────────────────────
# 2. Spatial autocorrelation (Moran's I)
# ──────────────────────────────────────────────────────────────────

def spatial_autocorrelation(arr: np.ndarray) -> float:
    """Compute Moran's I spatial autocorrelation for a 2-D field.

    Moran's I ∈ (−1, 1]:
        +1  = perfectly clustered (similar values adjacent)
         0  = random spatial pattern
        −1  = perfectly dispersed (checkerboard)

    Uses a first-order queen adjacency weight matrix (8-connected, toroidal).
    For computational efficiency a convolutional approximation is used:
    the spatial lag is computed as the mean of 8 immediate neighbours.

    Parameters
    ----------
    arr:
        2-D float array (any range).

    Returns
    -------
    Moran's I estimate ∈ (−1, 1].
    """
    z = arr - arr.mean()
    n = z.size
    variance = float((z ** 2).sum())
    if variance < 1e-12:
        return 0.0

    # Spatial lag: mean of 8-connected toroidal neighbours
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.float32) / 8.0
    from scipy.ndimage import convolve
    lag = convolve(z.astype(np.float32), kernel, mode="wrap")

    # Moran's I numerator: sum of z_i * lag_i
    numerator = float((z * lag).sum())

    # W = n (each cell has 8 neighbours, weight = 1/8, W = n * 8 * (1/8) = n)
    W = float(n)
    I = (n / W) * (numerator / variance)
    return round(float(np.clip(I, -1.0, 1.0)), 5)


# ──────────────────────────────────────────────────────────────────
# 3. Flow directionality
# ──────────────────────────────────────────────────────────────────

@dataclass
class DirectionalityResult:
    """Result of flow directionality analysis.

    Attributes
    ----------
    mean_angle_rad:
        Mean flow angle in radians ∈ (−π, π].
    mean_angle_deg:
        Mean flow angle in degrees ∈ (−180, 180].
    anisotropy:
        Vector strength ∈ [0, 1]. 1 = perfectly directional, 0 = isotropic.
    dominant_vy:
        y-component of mean unit flow vector.
    dominant_vx:
        x-component of mean unit flow vector.
    mean_speed:
        Mean flow speed (√(vy² + vx²)) over all cells.
    """

    mean_angle_rad: float
    mean_angle_deg: float
    anisotropy: float
    dominant_vy: float
    dominant_vx: float
    mean_speed: float


def flow_directionality(
    flow_y: np.ndarray,
    flow_x: np.ndarray,
) -> DirectionalityResult:
    """Compute flow directionality metrics from two flow component fields.

    Uses circular statistics (unit vector mean) to handle angular wrap-around
    correctly.

    Parameters
    ----------
    flow_y, flow_x:
        2-D float arrays of the y- and x-components of the flow field.

    Returns
    -------
    DirectionalityResult dataclass.
    """
    speeds = np.sqrt(flow_y ** 2 + flow_x ** 2) + 1e-10
    # Unit vectors
    uy = flow_y / speeds
    ux = flow_x / speeds

    mean_uy = float(uy.mean())
    mean_ux = float(ux.mean())
    anisotropy = float(np.sqrt(mean_uy ** 2 + mean_ux ** 2))
    angle = float(np.arctan2(mean_uy, mean_ux))

    return DirectionalityResult(
        mean_angle_rad=round(angle, 5),
        mean_angle_deg=round(float(np.degrees(angle)), 3),
        anisotropy=round(anisotropy, 5),
        dominant_vy=round(mean_uy, 5),
        dominant_vx=round(mean_ux, 5),
        mean_speed=round(float(speeds.mean()), 5),
    )


# ──────────────────────────────────────────────────────────────────
# 4. Memory entropy tracker (time series)
# ──────────────────────────────────────────────────────────────────

def _field_entropy_local(arr: np.ndarray, n_bins: int = 32) -> float:
    """Shannon entropy of the field value histogram."""
    counts, _ = np.histogram(arr.ravel(), bins=n_bins, range=(0.0, 1.0))
    p = counts / max(counts.sum(), 1)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p + 1e-15)))


class MemoryEntropyTracker:
    """Accumulate memory field entropy over time.

    Attributes
    ----------
    history:
        List of (tick, entropy) tuples in chronological order.
    window:
        Number of recent values used for trend estimation.
    """

    def __init__(self, window: int = 20) -> None:
        self.history: List[Tuple[int, float]] = []
        self.window = window

    def update(self, tick: int, memory: np.ndarray) -> float:
        """Compute and record entropy for ``memory`` at ``tick``."""
        e = _field_entropy_local(memory)
        self.history.append((tick, round(e, 5)))
        return e

    def trend(self) -> float:
        """Linear trend of entropy over the last ``window`` values.

        Returns
        -------
        Slope of the linear fit (positive = increasing entropy, negative = decreasing).
        0.0 if fewer than 2 data points.
        """
        if len(self.history) < 2:
            return 0.0
        recent = self.history[-self.window :]
        ticks = np.array([t for t, _ in recent], dtype=float)
        vals = np.array([v for _, v in recent], dtype=float)
        if ticks.std() < 1e-10:
            return 0.0
        coeffs = np.polyfit(ticks, vals, 1)
        return round(float(coeffs[0]), 7)

    def current_entropy(self) -> float:
        """Return the most recently recorded entropy value (0.0 if empty)."""
        if not self.history:
            return 0.0
        return self.history[-1][1]

    def to_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return (ticks, entropies) as numpy arrays for plotting."""
        if not self.history:
            return np.empty(0), np.empty(0)
        ticks = np.array([t for t, _ in self.history], dtype=np.int32)
        vals = np.array([v for _, v in self.history], dtype=np.float32)
        return ticks, vals


# ──────────────────────────────────────────────────────────────────
# 5. Cluster lifetime tracking
# ──────────────────────────────────────────────────────────────────

@dataclass
class ClusterLifetimeStats:
    """Summary of cluster lifetime statistics.

    Attributes
    ----------
    n_tracked:
        Total number of unique cluster identities tracked so far.
    mean_lifetime:
        Mean lifetime (in ticks) of all completed (gone) clusters.
    max_lifetime:
        Maximum lifetime of any completed cluster.
    n_active:
        Number of clusters currently alive.
    n_completed:
        Number of clusters that have died (lifetime is final).
    """

    n_tracked: int
    mean_lifetime: float
    max_lifetime: int
    n_active: int
    n_completed: int


class ClusterLifetimeTracker:
    """Track cluster birth/death across consecutive ticks.

    Clusters are matched between ticks by centroid proximity (nearest centroid
    within ``match_radius`` grid cells). This is a heuristic — no
    exact identity is guaranteed across large topology changes.

    Parameters
    ----------
    threshold:
        Field binarisation threshold.
    match_radius:
        Max centroid distance (grid cells) to consider two clusters the same.
    """

    def __init__(self, threshold: float = 0.5, match_radius: float = 4.0) -> None:
        self.threshold = threshold
        self.match_radius = match_radius
        # active: {cluster_id: (birth_tick, centroid)}
        self._active: Dict[int, Tuple[int, Tuple[float, float]]] = {}
        self._next_id: int = 0
        self._completed_lifetimes: List[int] = []
        self._current_tick: int = 0

    def update(self, tick: int, arr: np.ndarray) -> ClusterLifetimeStats:
        """Update tracker with the field at ``tick``.

        Parameters
        ----------
        tick:
            Current simulation tick.
        arr:
            2-D float field to threshold and label.

        Returns
        -------
        ClusterLifetimeStats for this tick.
        """
        self._current_tick = tick
        binary = arr > self.threshold
        labeled, n = label(binary)

        if n == 0:
            # All clusters died
            for cid, (birth, _) in self._active.items():
                self._completed_lifetimes.append(tick - birth)
            self._active = {}
            return self._stats()

        # Compute centroids for current clusters
        curr_centroids: List[Tuple[float, float]] = []
        for i in range(1, n + 1):
            cy, cx = center_of_mass(labeled == i)
            curr_centroids.append((float(cy), float(cx)))

        # Match current clusters to existing active clusters
        matched_active: set[int] = set()
        new_active: Dict[int, Tuple[int, Tuple[float, float]]] = {}

        for ci, centroid in enumerate(curr_centroids):
            best_id: Optional[int] = None
            best_dist = self.match_radius

            for cid, (birth, prev_c) in self._active.items():
                if cid in matched_active:
                    continue
                dy = centroid[0] - prev_c[0]
                dx = centroid[1] - prev_c[1]
                dist = float(np.sqrt(dy ** 2 + dx ** 2))
                if dist < best_dist:
                    best_dist = dist
                    best_id = cid

            if best_id is not None:
                # Continuing cluster
                birth = self._active[best_id][0]
                new_active[best_id] = (birth, centroid)
                matched_active.add(best_id)
            else:
                # New cluster
                new_active[self._next_id] = (tick, centroid)
                self._next_id += 1

        # Clusters not matched → died
        for cid, (birth, _) in self._active.items():
            if cid not in matched_active:
                self._completed_lifetimes.append(tick - birth)

        self._active = new_active
        return self._stats()

    def _stats(self) -> ClusterLifetimeStats:
        n_completed = len(self._completed_lifetimes)
        if n_completed > 0:
            mean_lt = round(float(np.mean(self._completed_lifetimes)), 2)
            max_lt = int(max(self._completed_lifetimes))
        else:
            mean_lt = 0.0
            max_lt = 0
        return ClusterLifetimeStats(
            n_tracked=self._next_id,
            mean_lifetime=mean_lt,
            max_lifetime=max_lt,
            n_active=len(self._active),
            n_completed=n_completed,
        )

    def stats(self) -> ClusterLifetimeStats:
        """Return current statistics without updating."""
        return self._stats()


# ──────────────────────────────────────────────────────────────────
# 6. Event reconstruction
# ──────────────────────────────────────────────────────────────────

@dataclass
class ActivationEvent:
    """A discrete activation event detected in a field.

    Attributes
    ----------
    tick:
        Tick at which the event was detected.
    centroid_y, centroid_x:
        Approximate spatial centroid of the event region.
    area:
        Number of newly activated cells.
    mean_value:
        Mean field value in the event region.
    """

    tick: int
    centroid_y: float
    centroid_x: float
    area: int
    mean_value: float


def reconstruct_events(
    prev: np.ndarray,
    curr: np.ndarray,
    tick: int,
    threshold: float = 0.5,
    min_area: int = 3,
) -> List[ActivationEvent]:
    """Detect discrete activation events between two consecutive field snapshots.

    An event is a connected region of cells that crossed above ``threshold``
    between ``prev`` and ``curr`` (newly activated cells), with area ≥ ``min_area``.

    Parameters
    ----------
    prev, curr:
        Field snapshots at consecutive ticks.
    tick:
        Current tick (used for event timestamps).
    threshold:
        Activation threshold.
    min_area:
        Minimum event area to report.

    Returns
    -------
    List of ActivationEvent (may be empty).
    """
    was_inactive = prev <= threshold
    now_active = curr > threshold
    new_activations = was_inactive & now_active

    if not new_activations.any():
        return []

    labeled, n = label(new_activations)
    events: List[ActivationEvent] = []

    for i in range(1, n + 1):
        mask = labeled == i
        area = int(mask.sum())
        if area < min_area:
            continue
        cy, cx = center_of_mass(mask)
        mean_val = float(curr[mask].mean())
        events.append(ActivationEvent(
            tick=tick,
            centroid_y=round(float(cy), 2),
            centroid_x=round(float(cx), 2),
            area=area,
            mean_value=round(mean_val, 4),
        ))

    return events


# ──────────────────────────────────────────────────────────────────
# 7. Wavefront speed
# ──────────────────────────────────────────────────────────────────

def wavefront_speed(
    prev: np.ndarray,
    curr: np.ndarray,
    threshold: float = 0.5,
) -> float:
    """Estimate the propagation speed of an excitable wavefront.

    Speed is estimated as the displacement of the active front's centroid
    between two consecutive ticks (in grid cells per tick).

    Returns 0.0 if no front is active in either field, or if the centroid
    cannot be computed.

    Parameters
    ----------
    prev, curr:
        Field snapshots at consecutive ticks.
    threshold:
        Binarisation threshold.

    Returns
    -------
    Estimated speed in grid cells per tick (Euclidean centroid displacement).
    """
    from scipy.ndimage import binary_dilation, binary_erosion as _be
    struct4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)

    def _front_centroid(arr: np.ndarray) -> Optional[Tuple[float, float]]:
        binary = arr > threshold
        if not binary.any():
            return None
        front = binary & binary_dilation(~binary, structure=struct4)
        if not front.any():
            return None
        cy, cx = center_of_mass(front)
        return float(cy), float(cx)

    c_prev = _front_centroid(prev)
    c_curr = _front_centroid(curr)
    if c_prev is None or c_curr is None:
        return 0.0
    dy = c_curr[0] - c_prev[0]
    dx = c_curr[1] - c_prev[1]
    return round(float(np.sqrt(dy ** 2 + dx ** 2)), 4)


# ──────────────────────────────────────────────────────────────────
# Composite snapshot function
# ──────────────────────────────────────────────────────────────────

@dataclass
class TraceMetricsSnapshot:
    """All Epic 13 trace metrics for a single tick.

    Attributes
    ----------
    tick:
        Simulation tick.
    memory_persistence:
        Jaccard similarity of memory field vs previous tick.
    spatial_autocorrelation_energy:
        Moran's I for the energy field.
    spatial_autocorrelation_memory:
        Moran's I for the memory field.
    directionality:
        DirectionalityResult from flow fields.
    memory_entropy:
        Current entropy of memory field.
    memory_entropy_trend:
        Linear trend slope of memory entropy over recent window.
    cluster_lifetimes:
        ClusterLifetimeStats for energy field.
    n_events:
        Number of discrete activation events detected this tick.
    wavefront_speed:
        Estimated wavefront speed (0 if no front or excitable media context).
    """

    tick: int
    memory_persistence: float
    spatial_autocorrelation_energy: float
    spatial_autocorrelation_memory: float
    directionality: DirectionalityResult
    memory_entropy: float
    memory_entropy_trend: float
    cluster_lifetimes: ClusterLifetimeStats
    n_events: int
    wavefront_speed: float

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


def compute_trace_metrics(
    tick: int,
    fields: dict,
    prev_memory: Optional[np.ndarray] = None,
    prev_energy: Optional[np.ndarray] = None,
    entropy_tracker: Optional[MemoryEntropyTracker] = None,
    lifetime_tracker: Optional[ClusterLifetimeTracker] = None,
) -> TraceMetricsSnapshot:
    """Compute all Epic 13 trace metrics in a single call.

    Parameters
    ----------
    tick:
        Current simulation tick.
    fields:
        Dict of field name → 2-D array (from GridState.as_dict()).
    prev_memory:
        Memory field from the previous tick (for persistence + events).
        If None, persistence = 1.0 and events = [].
    prev_energy:
        Energy field from the previous tick (for wavefront speed + events).
    entropy_tracker:
        Optional persistent MemoryEntropyTracker.
    lifetime_tracker:
        Optional persistent ClusterLifetimeTracker.

    Returns
    -------
    TraceMetricsSnapshot dataclass.
    """
    memory = fields.get("memory", np.zeros((8, 8), dtype=np.float32))
    energy = fields.get("energy", np.zeros((8, 8), dtype=np.float32))
    flow_y = fields.get("flow_y", np.zeros_like(energy))
    flow_x = fields.get("flow_x", np.zeros_like(energy))

    # 1. Memory persistence
    mp = (
        memory_persistence(prev_memory, memory)
        if prev_memory is not None
        else 1.0
    )

    # 2. Spatial autocorrelation
    sac_e = spatial_autocorrelation(energy)
    sac_m = spatial_autocorrelation(memory)

    # 3. Directionality
    dr = flow_directionality(flow_y, flow_x)

    # 4. Memory entropy
    if entropy_tracker is not None:
        me = entropy_tracker.update(tick, memory)
        me_trend = entropy_tracker.trend()
    else:
        me = _field_entropy_local(memory)
        me_trend = 0.0

    # 5. Cluster lifetimes
    if lifetime_tracker is not None:
        cl_stats = lifetime_tracker.update(tick, energy)
    else:
        cl_stats = ClusterLifetimeStats(
            n_tracked=0, mean_lifetime=0.0, max_lifetime=0,
            n_active=0, n_completed=0,
        )

    # 6. Event reconstruction
    if prev_energy is not None:
        events = reconstruct_events(prev_energy, energy, tick)
        n_ev = len(events)
    else:
        n_ev = 0

    # 7. Wavefront speed
    wfs = (
        wavefront_speed(prev_energy, energy)
        if prev_energy is not None
        else 0.0
    )

    return TraceMetricsSnapshot(
        tick=tick,
        memory_persistence=mp,
        spatial_autocorrelation_energy=sac_e,
        spatial_autocorrelation_memory=sac_m,
        directionality=dr,
        memory_entropy=round(me, 5),
        memory_entropy_trend=me_trend,
        cluster_lifetimes=cl_stats,
        n_events=n_ev,
        wavefront_speed=wfs,
    )
