# ADR-0005: Relational Geometry via NetworkX GraphState

**Status:** Accepted  
**Date:** 2026-05-08  
**Reference:** Workbook ch. 10.4, 14 – Graph / Hypergraph Mode

---

## Context

The existing system is bound to a Euclidean 2D grid.
Epic 5 requires an alternative state space where distance emerges from
connection strength — analogous to Wolfram's Hypergraph Physics.

---

## Decision

`GraphState` (NetworkX graph with node and edge attributes):

| Feature | Decision |
|---------|----------|
| Library | NetworkX (pure Python, simple integration, no GPU) |
| Topologies | small_world, scale_free, random, grid |
| Distance | Dijkstra on 1/weight (strong edge = short distance) |
| Rewriting | Most active nodes form a new edge per tick |

**Deliberate simplifications vs. Wolfram Physics:**
- No true hypergraph (only a weighted graph).
- No causal invariance, no branchial geometry.
- Goal: exploration, not physics simulation.

---

## Consequences

- Emergent distance matrix enables topology comparisons (small_world vs. scale_free).
- Dashboard Tab 5 shows NetworkX visualisation + distance matrix interactively.
- NetworkX is a new optional dependency.

## Scientific Caution

This graph mode does **not** test Wolfram Physics hypotheses.
It is a structural analogy for exploring relational geometry.
