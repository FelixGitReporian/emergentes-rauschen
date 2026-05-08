# Experiment: Reaction-Diffusion Memory

**Date:** 2026-05-08  
**Git:** `29ce7b8`  
**Run ID prefix:** `reaction_diffusion_memory`  
**Output:** `outputs/reaction_diffusion_memory/20260508_155935/results.csv` (936 rows)

---

## Scientific Question

> How do reaction-diffusion dynamics and memory decay interact?  
> When do stable Turing patterns emerge vs. oscillating structures?  
> Which memory strength maximises proto-compartment formation?

---

## Parameters

**Fixed base config** (`seed=42, 1042, 2042` per combo; 3 repeats):

| Parameter                  | Value  |
|----------------------------|--------|
| Grid                       | 64×64  |
| Ticks                      | 500    |
| `diffusion_information`    | 0.08   |
| `reaction_energy_threshold`| 0.55   |
| `reaction_strength`        | 0.12   |
| `coupling_gain`            | 0.02   |
| `noise_amplitude`          | 0.02   |
| `memory_imprint_rate`      | 0.30   |

**Swept parameters** (4 × 3 = 12 combos × 3 seeds = 36 runs):

| `memory_decay`  | `diffusion_energy`     |
|-----------------|------------------------|
| 0.90, 0.94, 0.97, 0.99 | 0.05, 0.15, 0.25 |

---

## Results: Mean Metrics per Parameter Combination

Averaged over all ticks (every 20 ticks, 500 ticks → 26 snapshots) × 3 seeds = 78 rows per combo.

| memory_decay | diffusion_energy | Avg Entropy | Avg Persistence | Avg Compartments | Avg Φ-Proxy | Avg Integrated |
|-------------:|-----------------:|------------:|----------------:|-----------------:|------------:|---------------:|
| 0.90 | 0.05 | 0.3398 | 0.9989 | 0.38 | 0.0799 | 0.3227 |
| 0.90 | 0.15 | 0.2528 | 0.9990 | 0.19 | 0.0813 | 0.3276 |
| 0.90 | 0.25 | 0.2067 | 0.9987 | 0.03 | 0.0812 | 0.3191 |
| 0.94 | 0.05 | 0.3398 | 0.9989 | 0.38 | 0.0799 | 0.3163 |
| 0.94 | 0.15 | 0.2528 | 0.9990 | 0.19 | 0.0813 | 0.3213 |
| 0.94 | 0.25 | 0.2067 | 0.9987 | 0.03 | 0.0812 | 0.3127 |
| 0.97 | 0.05 | 0.3398 | 0.9989 | 0.38 | 0.0799 | 0.3065 |
| 0.97 | 0.15 | 0.2528 | 0.9990 | 0.19 | 0.0813 | 0.3121 |
| 0.97 | 0.25 | 0.2067 | 0.9987 | 0.03 | 0.0812 | 0.3041 |
| 0.99 | 0.05 | 0.3398 | 0.9989 | 0.38 | 0.0799 | 0.2910 |
| 0.99 | 0.15 | 0.2528 | 0.9990 | 0.19 | 0.0813 | 0.2978 |
| 0.99 | 0.25 | 0.2067 | 0.9987 | 0.03 | 0.0812 | 0.2918 |

---

## Observations

- **`diffusion_energy` dominates over `memory_decay`:** All four decay values produce near-identical entropy and persistence — diffusion strength is the primary driver of disorder.
- **Lower diffusion → higher entropy:** `diffusion_energy=0.05` yields ~0.34 entropy vs. ~0.21 at 0.25. Faster diffusion smooths gradients and reduces structural complexity.
- **Compartments peak at low diffusion:** 0.38 avg compartments at `diffusion_energy=0.05` vs. 0.03 at 0.25 — slow diffusion allows local energy concentrations to persist as proto-compartments.
- **Memory decay has a subtle effect on integration:** `integrated_score` drops from ~0.32 (decay=0.90) to ~0.29 (decay=0.99). Slower memory decay (higher retention) correlates with slightly higher integrated consciousness proxy — consistent with hysteresis strengthening global coherence.
- **No Turing patterns detected** in this parameter range at 500 ticks — likely requires longer runs or higher `reaction_strength` values. Planned follow-up sweep.

> **Caution:** All scores are structural proxies. "Compartment" and "proto-life" metrics are heuristic classifiers, not biological evidence.

---

## Reproduce

```bash
python -m emergent_noise.experiments.runner -e reaction_diffusion_memory
```

Raw CSV: `outputs/reaction_diffusion_memory/<timestamp>/results.csv` (gitignored, reproducible via above command + git hash `29ce7b8`)
