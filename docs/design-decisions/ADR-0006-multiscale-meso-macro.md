# ADR-0006: Multiscale Model Micro / Meso / Macro

**Status:** Accepted  
**Date:** 2026-05-08  
**Reference:** Workbook ch. 10.5, 16.2 – Multiscale Model

---

## Context

The system previously had only one description level (micro: grid cells).
Epic 6 requires meso and macro levels for emergence analysis.

---

## Decision

**Three levels in `core/multiscale.py`:**

| Level | Implementation | Unit |
|-------|---------------|------|
| Micro | GridState (existing) | Grid cells |
| Meso  | MesoLayer (SciPy label + tracking) | Cluster entities |
| Macro | AttractorLandscape (trajectory in E×C) | System state |

**MesoLayer:**
- Connected energy regions (8-connectivity, SciPy `label`).
- Tracking via centroid matching (nearest predecessor ≤ 10 cells).
- Velocity estimation: centroid displacement per tick.

**MacroLayer:**
- Projection of system state onto (energy_mean, coherence_mean).
- Phase transition detection: Δ > 0.05 within one tick period.
- Trajectory as (N, 2) array for dashboard plot.

---

## Consequences

- `MultiscaleController.update(state)` returns meso + macro dict.
- Dashboard Tab 4 shows attractor trajectory live.
- No performance penalty: SciPy `label` is O(H×W), fast.

## Scientific Caution

Meso entities are label artefacts, not ontological objects.
Phase transitions are heuristic jump detections, not genuine phase
transition proofs (no order parameter, no critical slowing down).
