# Benchmark: 10k-Tick Stability Sweep

**Date:** 2026-05-08  
**Git:** `29ce7b8`  
**Script:** `examples/benchmark_10k.py`  
**Ticks:** 10,000 per noise level · 6 noise levels (0.0 – 0.20)

---

## Results – 32×32 Grid

| Noise | Avg Entropy | Avg Persistence | Avg Compartments | Final Regime | ticks/s | Wall Time |
|------:|------------:|----------------:|-----------------:|:------------|--------:|----------:|
| 0.00  | 0.0324      | 1.0000          | 0.0              | quiescent   | 188     | 53.3 s    |
| 0.01  | 0.0697      | 0.9996          | 0.0              | quiescent   | 189     | 52.8 s    |
| 0.02  | 0.2331      | 0.9992          | 0.0              | quiescent   | 186     | 53.9 s    |
| 0.05  | 0.4466      | 0.9979          | 1.0              | vortex      | 186     | 53.7 s    |
| 0.10  | 0.6289      | 0.9959          | 7.1              | vortex      | 183     | 54.7 s    |
| 0.20  | 0.8114      | 0.9917          | 1.3              | vortex      | 180     | 55.5 s    |

## Results – 64×64 Grid

| Noise | Avg Entropy | Avg Persistence | Avg Compartments | Final Regime | ticks/s | Wall Time |
|------:|------------:|----------------:|-----------------:|:------------|--------:|----------:|
| 0.00  | 0.0415      | 1.0000          | 0.1              | quiescent   | 115     | 86.7 s    |
| 0.01  | 0.1716      | 0.9996          | 0.1              | quiescent   | 115     | 87.2 s    |
| 0.02  | 0.2347      | 0.9992          | 0.1              | quiescent   | 112     | 89.1 s    |
| 0.05  | 0.4327      | 0.9981          | 0.2              | vortex      | 115     | 86.8 s    |
| 0.10  | 0.6148      | 0.9962          | 31.0             | vortex      | 112     | 89.6 s    |
| 0.20  | 0.8016      | 0.9923          | 2.2              | vortex      | 123     | 81.2 s    |

---

## Observations

- **Regime transition** occurs between noise=0.02 (quiescent) and noise=0.05 (vortex) — consistent across both grid sizes.
- **Entropy** rises monotonically with noise amplitude, confirming the noise-driven disorder relationship.
- **Compartments** peak at noise=0.10 (64×64: 31 compartments), then drop at noise=0.20 — suggesting an optimal noise window for structural self-organisation.
- **Persistence** stays near 1.0 throughout, indicating stable local patterns dominate even at high noise.
- **Performance:** 32×32 sustains ~185 ticks/s; 64×64 scales to ~115 ticks/s (4× area, ~1.6× slower — sublinear scaling from NumPy vectorisation).

> **Caution:** These are observational summaries, not controlled experiments. Regime labels and compartment counts are heuristic classifiers.

---

## Reproduce

```bash
python examples/benchmark_10k.py --grid 32
python examples/benchmark_10k.py --grid 64 --output outputs/bench_64
```

Raw CSV: `outputs/benchmark_10k/` and `outputs/bench_64/` (gitignored, reproducible on demand)
