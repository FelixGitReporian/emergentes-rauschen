# ADR-0003: Meta-Rule Evolution as Decentralised Rule Genome

**Status:** Accepted  
**Date:** 2026-05-08  
**Author:** FelixGitReporian  
**Reference:** Workbook ch. 9 – Evolving Rules and Meta-Evolution

---

## Context

The system consists of global rule parameters (`SimConfig`) that are identical
for all cells. To enable open-ended evolution — i.e. the emergence of spatially
differentiated rule profiles — a mechanism is needed where local parameters can
vary, be selected and be retained.

Workbook ch. 9 requires:
- Each region has a local rule profile (rule genome).
- Rule profiles can mutate.
- Successful profiles spread through selection.
- Persistently successful profiles leave memory traces.

---

## Decision

### Representation

The rule genome is stored as **two float32 arrays** (`genome_strength`,
`genome_threshold`) of shape `(height, width)` directly in `GridState` —
no separate object per cell.

**Rationale:**
- NumPy-native arrays enable vectorised operations without Python loops.
- Uniform with all other state fields (same shape, same value range).
- `clip_all()` and `as_dict()` can be extended consistently.
- Genomes are deliberately excluded from `as_dict()` to avoid contaminating
  analysis modules.

### Genome Parameters

| Parameter          | Meaning                                      |
|--------------------|----------------------------------------------|
| `genome_strength`  | Local reaction strength (rule 1)             |
| `genome_threshold` | Local energy activation threshold            |

Only reaction rule 1 is genome-controlled, as it is the dominant transformation
rule. Further rules can follow in later epics.

### Evolution Steps (per tick, step 7)

1. **Fitness** = `coherence × (1 − local_energy_variance)` — heuristic proxy
   for a stable, ordered local profile.
2. **Mutation** — randomly selected cells receive `±meta_mutation_strength`
   on one genome parameter.
3. **Selection** — local 3×3 neighbourhood: weaker cells adopt profiles from
   fitter neighbours.
4. **Retention** — cells with fitness > threshold reinforce the memory field
   (weak signal, factor 0.01).

### Controls

- `meta_enabled` (bool): complete on/off switch.
- `meta_mutation_rate`, `meta_mutation_strength`: control genetic diversity.
- `meta_selection_rate`: controls selection speed.
- `meta_retention_threshold`: determines which profiles write to memory.

---

## Rejected Alternatives

| Alternative | Reason for rejection |
|-------------|----------------------|
| Object-oriented rule genome per cell (class) | Python objects in H×W arrays = massive overhead, no vectorisation possible |
| Fully evolved rule sets (each rule has its own genes) | Too complex for v0.4.0; incremental extension planned |
| Genetic algorithm with crossover | Spatial locality would be lost; local selection fits the grid architecture better |
| External fitness function (hand-designed) | Contradicts the emergence principle; internal metrics preferred |

---

## Consequences

**Positive:**
- Spatially heterogeneous reaction behaviour emerges spontaneously.
- Genomes are directly analysable (`genome_diversity`, `genome_entropy`).
- `meta_enabled=False` completely disables evolution → backward compatible.
- Fully deterministic (seed + tick as RNG basis).

**Negative / Risks:**
- Selection step contains a Python loop over selected cells
  → performance bottleneck for large grids. To be refactored as a NumPy
  vector operation in v0.5.0.
- Fitness proxy is heuristic: coherence ≠ biological fitness.

---

## Scientific Caution

Meta-rule evolution is an abstract model, not a model of real genetics or
evolution. Emerging patterns are interesting emergent phenomena, not evidence
of biological or cognitive processes.
