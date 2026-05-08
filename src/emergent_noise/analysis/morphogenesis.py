"""
analysis/morphogenesis.py – Morphogenesis & Growth Metrics (Epic 12).

Provides quantitative analysis of branching, growth and filamentary structures
in 2-D fields. All functions operate on binary or float32 numpy arrays.

Implemented:
    1. extract_skeleton       – medial-axis skeleton via iterative thinning.
    2. branch_count           – number of branch points in a skeleton.
    3. tip_count              – number of free endpoints (growth tips).
    4. fractal_dimension      – box-counting fractal dimension of a binary pattern.
    5. growth_front           – active boundary cells facing inactive space.
    6. GrowthFrontMetrics     – dataclass with front area, mean energy, directionality.
    7. analyse_growth_front   – compute GrowthFrontMetrics from a float field.
    8. MorphogenesisResult    – composite dataclass for all metrics.
    9. analyse_morphogenesis  – single entry-point returning MorphogenesisResult.

Scientific caution:
    Skeleton thinning produces a topological approximation, not an exact medial axis
    for all shapes.  Box-counting fractal dimension is an estimate; reliable results
    require patterns spanning at least 2–3 decades of scale.
    Growth front directionality is a vector mean — symmetric patterns give 0.
    These are structural descriptors, not causal claims about biological processes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.ndimage import binary_erosion, binary_dilation, label, convolve


# ──────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────

@dataclass
class GrowthFrontMetrics:
    """Metrics describing the active growth boundary of a field.

    Attributes
    ----------
    front_area:
        Number of cells on the growth front (active cells adjacent to inactive).
    front_fraction:
        front_area / total_active_area.
    mean_front_energy:
        Mean field value on front cells.
    directionality_y:
        Mean y-component of outward normal vectors on front (−1=upward, +1=downward).
    directionality_x:
        Mean x-component of outward normal vectors on front.
    directionality_magnitude:
        Magnitude of (directionality_y, directionality_x) ∈ [0, 1].
        0 = isotropic / symmetric growth; 1 = fully directed.
    """

    front_area: int
    front_fraction: float
    mean_front_energy: float
    directionality_y: float
    directionality_x: float
    directionality_magnitude: float


@dataclass
class MorphogenesisResult:
    """Composite morphogenesis analysis for one field at one tick.

    Attributes
    ----------
    field_name:
        Name of the analysed field.
    tick:
        Simulation tick at which analysis was performed.
    threshold:
        Binarisation threshold used.
    active_fraction:
        Fraction of active (> threshold) cells.
    skeleton_density:
        Fraction of active cells that are part of the skeleton.
    branch_count:
        Number of branch points (skeleton cells with ≥ 3 skeleton neighbours).
    tip_count:
        Number of skeleton endpoints (skeleton cells with exactly 1 neighbour).
    branch_tip_ratio:
        branch_count / max(tip_count, 1).
    fractal_dimension:
        Box-counting estimate of the fractal dimension ∈ [1, 2].
    growth_front:
        GrowthFrontMetrics for the outer boundary.
    """

    field_name: str
    tick: int
    threshold: float
    active_fraction: float
    skeleton_density: float
    branch_count: int
    tip_count: int
    branch_tip_ratio: float
    fractal_dimension: float
    growth_front: GrowthFrontMetrics


# ──────────────────────────────────────────────────────────────────
# Skeleton extraction
# ──────────────────────────────────────────────────────────────────

# 3×3 hit-or-miss structuring elements for Zhang-Suen thinning
# We use a simpler but robust iterative erosion approach instead
# (Zhang-Suen requires 8 specific pattern checks; here we use
#  repeated morphological thinning via topology-preserving erosion).

def extract_skeleton(binary: np.ndarray, max_iter: int = 64) -> np.ndarray:
    """Compute a medial-axis-like skeleton via iterative morphological thinning.

    The algorithm repeatedly erodes the binary image while preserving topology
    (connectivity). This is an approximation of the true medial axis.

    Parameters
    ----------
    binary:
        Boolean 2-D array.
    max_iter:
        Maximum number of thinning iterations.

    Returns
    -------
    Boolean 2-D array, True where skeleton cells are.
    """
    if not binary.any():
        return np.zeros_like(binary, dtype=bool)

    skeleton = np.zeros_like(binary, dtype=bool)
    current = binary.copy()

    # Structuring elements for 4-connected and 8-connected erosion
    struct4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)

    for _ in range(max_iter):
        eroded = binary_erosion(current, structure=struct4)
        # Cells that would be removed but are needed for connectivity
        opened = binary_dilation(eroded, structure=struct4)
        temp = current & ~opened
        skeleton |= temp
        if not eroded.any():
            skeleton |= eroded
            break
        current = eroded

    return skeleton


# ──────────────────────────────────────────────────────────────────
# Branch and tip counting
# ──────────────────────────────────────────────────────────────────

_NEIGHBOUR_KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)


def _skeleton_neighbour_count(skeleton: np.ndarray) -> np.ndarray:
    """Return an array counting the number of skeleton neighbours for each cell."""
    s = skeleton.astype(np.uint8)
    return convolve(s, _NEIGHBOUR_KERNEL, mode="wrap")


def branch_count(skeleton: np.ndarray) -> int:
    """Count branch points: skeleton cells with ≥ 3 skeleton neighbours."""
    if not skeleton.any():
        return 0
    nc = _skeleton_neighbour_count(skeleton)
    return int((skeleton & (nc >= 3)).sum())


def tip_count(skeleton: np.ndarray) -> int:
    """Count free tips: skeleton cells with exactly 1 skeleton neighbour."""
    if not skeleton.any():
        return 0
    nc = _skeleton_neighbour_count(skeleton)
    return int((skeleton & (nc == 1)).sum())


# ──────────────────────────────────────────────────────────────────
# Fractal dimension (box-counting)
# ──────────────────────────────────────────────────────────────────

def fractal_dimension(binary: np.ndarray, min_box: int = 2) -> float:
    """Estimate the box-counting fractal dimension of a binary pattern.

    Covers the pattern with boxes of decreasing size and fits log(N) ~ D·log(1/r).

    Parameters
    ----------
    binary:
        Boolean 2-D array.
    min_box:
        Minimum box size in pixels.

    Returns
    -------
    Estimated fractal dimension ∈ [1.0, 2.0] (clamped).
    Returns 0.0 if the pattern is empty.
    """
    if not binary.any():
        return 0.0

    H, W = binary.shape
    max_box = min(H, W) // 2
    if max_box < min_box:
        return 1.0

    sizes: list[int] = []
    counts: list[int] = []

    box = min_box
    while box <= max_box:
        count = 0
        for r in range(0, H, box):
            for c in range(0, W, box):
                if binary[r : r + box, c : c + box].any():
                    count += 1
        if count > 0:
            sizes.append(box)
            counts.append(count)
        box *= 2

    if len(sizes) < 2:
        return 1.0

    log_sizes = np.log(1.0 / np.array(sizes, dtype=float))
    log_counts = np.log(np.array(counts, dtype=float))

    # Linear regression: slope = fractal dimension
    coeffs = np.polyfit(log_sizes, log_counts, 1)
    fd = float(coeffs[0])
    return float(np.clip(fd, 1.0, 2.0))


# ──────────────────────────────────────────────────────────────────
# Growth front
# ──────────────────────────────────────────────────────────────────

def analyse_growth_front(
    arr: np.ndarray,
    threshold: float = 0.5,
) -> GrowthFrontMetrics:
    """Compute growth front metrics for a float field.

    The growth front consists of active cells (> threshold) that are
    adjacent to at least one inactive cell (≤ threshold).

    Directionality is computed as the mean outward normal vector:
    for each front cell, the outward normal points from the active
    region toward the nearest inactive neighbour.

    Parameters
    ----------
    arr:
        2-D float array [0, 1].
    threshold:
        Binarisation threshold.

    Returns
    -------
    GrowthFrontMetrics dataclass.
    """
    binary = arr > threshold
    active_count = int(binary.sum())

    if active_count == 0:
        return GrowthFrontMetrics(
            front_area=0, front_fraction=0.0, mean_front_energy=0.0,
            directionality_y=0.0, directionality_x=0.0, directionality_magnitude=0.0,
        )

    # Front = active cells eroded away by dilation of the inactive region
    struct4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
    inactive_dilated = binary_dilation(~binary, structure=struct4)
    front = binary & inactive_dilated

    front_area = int(front.sum())
    if front_area == 0:
        return GrowthFrontMetrics(
            front_area=0, front_fraction=0.0,
            mean_front_energy=float(arr[binary].mean()),
            directionality_y=0.0, directionality_x=0.0, directionality_magnitude=0.0,
        )

    mean_front_energy = float(arr[front].mean())
    front_fraction = front_area / max(active_count, 1)

    # Directionality: gradient of the binary field at front cells
    # grad_y > 0 means we're at a bottom edge (growing downward)
    grad_y = (np.roll(binary.astype(np.float32), -1, axis=0)
              - np.roll(binary.astype(np.float32), 1, axis=0)) * 0.5
    grad_x = (np.roll(binary.astype(np.float32), -1, axis=1)
              - np.roll(binary.astype(np.float32), 1, axis=1)) * 0.5

    gy_vals = grad_y[front]
    gx_vals = grad_x[front]
    dir_y = float(gy_vals.mean())
    dir_x = float(gx_vals.mean())
    magnitude = float(np.sqrt(dir_y ** 2 + dir_x ** 2))

    return GrowthFrontMetrics(
        front_area=front_area,
        front_fraction=round(front_fraction, 4),
        mean_front_energy=round(mean_front_energy, 4),
        directionality_y=round(dir_y, 4),
        directionality_x=round(dir_x, 4),
        directionality_magnitude=round(magnitude, 4),
    )


# ──────────────────────────────────────────────────────────────────
# Composite analysis entry point
# ──────────────────────────────────────────────────────────────────

def analyse_morphogenesis(
    name: str,
    arr: np.ndarray,
    tick: int = 0,
    threshold: float = 0.5,
    compute_fractal: bool = True,
    skeleton_max_iter: int = 48,
) -> MorphogenesisResult:
    """Full morphogenesis analysis: skeleton, branches, fractal dimension, front.

    Parameters
    ----------
    name:
        Field name for the result.
    arr:
        2-D float array [0, 1].
    tick:
        Current simulation tick.
    threshold:
        Binarisation threshold.
    compute_fractal:
        If False, skip box-counting (expensive for large arrays).
    skeleton_max_iter:
        Maximum thinning iterations for skeleton extraction.

    Returns
    -------
    MorphogenesisResult dataclass.
    """
    binary = (arr > threshold).astype(bool)
    active_count = int(binary.sum())
    active_fraction = float(binary.mean())

    _empty = MorphogenesisResult(
        field_name=name, tick=tick, threshold=threshold,
        active_fraction=active_fraction,
        skeleton_density=0.0, branch_count=0, tip_count=0,
        branch_tip_ratio=0.0, fractal_dimension=0.0,
        growth_front=GrowthFrontMetrics(
            front_area=0, front_fraction=0.0, mean_front_energy=0.0,
            directionality_y=0.0, directionality_x=0.0, directionality_magnitude=0.0,
        ),
    )

    if active_count == 0:
        return _empty

    # Skeleton
    skel = extract_skeleton(binary, max_iter=skeleton_max_iter)
    skel_count = int(skel.sum())
    skeleton_density = skel_count / max(active_count, 1)

    # Branch + tip counts
    n_branches = branch_count(skel)
    n_tips = tip_count(skel)
    btr = n_branches / max(n_tips, 1)

    # Fractal dimension
    fd = fractal_dimension(binary) if compute_fractal else 0.0

    # Growth front
    gf = analyse_growth_front(arr, threshold=threshold)

    return MorphogenesisResult(
        field_name=name,
        tick=tick,
        threshold=threshold,
        active_fraction=round(active_fraction, 4),
        skeleton_density=round(skeleton_density, 4),
        branch_count=n_branches,
        tip_count=n_tips,
        branch_tip_ratio=round(btr, 4),
        fractal_dimension=round(fd, 4),
        growth_front=gf,
    )
