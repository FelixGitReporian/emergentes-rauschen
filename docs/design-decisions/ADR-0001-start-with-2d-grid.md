# ADR-0001 – Start with 2D Grid Model

**Date:** 2026-05-08  
**Status:** Accepted  
**Context:** Phase 1 of the Emergentes Rauschen project

## Context

The project requires a simulatable, visualisable base structure. Three alternatives
were considered: 2D grid, particle system and graph/hypergraph.

## Decision

We start with a **2D grid** (periodic boundary conditions, toroidal topology).

## Rationale

- Easy to visualise (a heatmap suffices).
- Well known from cellular automata, reaction-diffusion systems and Lenia.
- NumPy operations on 2D arrays are fast and readable.
- Periodic boundary conditions avoid edge effects without complex logic.
- Low barrier to entry for junior-friendly development.

## Alternatives

- **Particle system:** More realistic for motion, but collision detection and
  rasterisation are complex. Planned for Phase 3.
- **Graph/Hypergraph:** Closer to Wolfram models and CDT, but harder to visualise
  and initially implement. Planned for Phase 4.

## Consequences

- Space is predefined, not emergent (changed in Phase 4).
- Cellular-automaton-style rules fit well.
- Spatial resolution is fixed; architecture must be extended for multi-scale models.

## Change Note

First implementation (v0.1.0):
- `core/state.py`: `GridState` with 9 fields (8 parameters + flow as flow_x/flow_y).
- `core/tick.py`: deterministic tick loop with documented rule order.
- `rules/diffusion.py`, `rules/reaction.py`, `rules/memory.py`.
- `noise/structured_noise.py`: sinusoidal superposition as structured noise.
- `analysis/entropy.py`: normalised Shannon entropy.
- `visualization/render.py`: panel PNG and RGB-composite.
- `examples/run_500.py`: 500-tick example run.
- `tests/`: pytest suite for init, determinism, value ranges, rules.
