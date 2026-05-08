# ADR-0002 – Coupling and Flow Field as Independent Rule Modules

**Date:** 2026-05-08  
**Status:** Accepted

## Context

Epic 1 adds two new active rule modules: `coupling.py` and `flow.py`.
Three alternatives for their integration were considered.

## Decision

Coupling and flow are **independent modules**, each with a single entry point
(`apply_coupling`, `apply_flow`), called by `TickLoop` in the documented order.

## Rationale

- Each module has a clearly defined scope — easier to test and maintain.
- `TickLoop` remains the single place that knows the execution order.
- Modules can be individually disabled (e.g. no flow in baseline experiments).
- Consistent with the established pattern of `diffusion.py`, `reaction.py`, `memory.py`.

## Rule Order (v0.2.0)

```
1. Noise            (symmetry breaking)
2. Diffusion        (transport)
3. Reaction         (local transformation)
4. Coupling         (network formation, coherence synchronisation)
5. Flow             (vector dynamics, vortices, advective transport)
6. Memory           (hysteresis / trace)
7. Clip [0, 1]
8. tick++
```

## Physical Motivation

- Coupling after reaction: reaction creates coherence differences; coupling equalises them.
- Flow after coupling: coupling curl drives vortices; gradients arise from all prior steps.
- Memory last: writes the complete post-transformation state as a trace.

## Alternatives

- **Everything in one file:** Harder to maintain, violates quality rules.
- **Flow inside `diffusion.py`:** Conceptually wrong — diffusion is scalar, flow is vectorial.
- **Coupling as part of `reaction.py`:** Too broad scope; coupling has its own timescale.

## Consequences

- `flow_x` / `flow_y` are now active fields with their own dynamics.
- `coupling` and `coherence` are now dynamic (no longer constant).
- New parameters in `SimConfig`: 7 new fields (`coupling_*`, `flow_*`).
- Entropy CSV log now shows variation in all fields.

## Change Note

v0.2.0 — 2026-05-08:
- Added `rules/coupling.py`, `rules/flow.py`
- `analysis/attractors.py` with persistence, clusters, phase indicator
- `visualization/dashboard.py` (Streamlit)
- Numba-JIT optional in `diffusion.py`
- 15 new tests (48 total)
