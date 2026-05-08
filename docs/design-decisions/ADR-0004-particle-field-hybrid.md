# ADR-0004: Particle-Field Hybrid as Vectorised Array System

**Status:** Accepted  
**Date:** 2026-05-08  
**Author:** FelixGitReporian  
**Reference:** Workbook ch. 10.3, 13.1 – Particle-Field Hybrid

---

## Context

The existing system is a pure grid-automaton system. Workbook ch. 10.3 requires
additional particles that move through fields and modify them — for condensation,
collisions, swarms, active matter and proto-cellular dynamics.

---

## Decision

### Representation

Particles are stored as **vectorised NumPy arrays** of shape `(N,)` or
`(N, 2)` — no Python object per particle.

| Array        | Shape  | Meaning                              |
|--------------|--------|--------------------------------------|
| `positions`  | (N, 2) | continuous (y, x) coordinates        |
| `velocities` | (N, 2) | (vy, vx) velocity                    |
| `energy`     | (N,)   | particle energy                      |
| `mass`       | (N,)   | inertia / aggregation counter        |
| `active`     | (N,)   | boolean mask of active particles     |
| `age`        | (N,)   | ticks since creation                 |

**Rationale:**
- Fully vectorisable, no Python loops except collision detection.
- Inactive particles remain in the array (active mask instead of removal).
- Maximum size is fixed → no dynamic reallocation.

### Coupling (bidirectional)

**Field → Particle:**
1. Energy gradient attraction via bilinear interpolation.
2. Flow transport (drag term).
3. Energy absorption (particles draw energy from the field).
4. Reactivity activation (high reactivity accelerates particles).

**Particle → Field:**
1. Energy deposition (`np.add.at`).
2. Matter deposition.
3. Coupling reinforcement by density.
4. Information injection.

### Collision

Simple O(N²) pair scanning over active particles with periodic boundary
conditions. Fusion: heavier particle absorbs lighter one, mass-weighted
position + momentum, energy summed.

Performance limit: ~500 particles. For larger systems → spatial hashing
(Epic 5+).

### Proto-Compartment Detection (`analysis/compartments.py`)

Two methods:
- **Field-based**: connected energy regions (SciPy `label`) with coupling
  and compactness filtering + heuristic proto-life score.
- **Particle-based**: particles with `mass >= min_mass` as aggregate markers,
  smoothed density map.

---

## Rejected Alternatives

| Alternative | Reason for rejection |
|-------------|----------------------|
| Python objects per particle | ~100× slower, no NumPy broadcasting |
| Separate simulation framework (PyBullet, etc.) | Too much overhead, hard to couple with the grid |
| Particles directly in GridState | Mixes continuum and discrete world; cleaner separation preferred |

---

## Consequences

**Positive:**
- Rich interaction: particles react to fields, fields react to particles.
- Proto-cellular aggregates emerge through collision + field coupling.
- `particles_enabled` toggle: system fully disableable.
- Fully visible in dashboard Tab 3.

**Negative / Risks:**
- Collision detection O(N²): performance-critical for N > 200.
- Physics is deliberately simplified (no momentum or energy conservation).

---

## Scientific Caution

The particle system is an exploratory abstraction, not a physical model.
Proto-life scores are structural proxies, not evidence of life processes.
Emergent aggregates are interesting phenomena, not biological organisms.
