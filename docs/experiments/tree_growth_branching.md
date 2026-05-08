# Tree Growth / Branching Morphogenesis

**Category:** Morphogenesis  
**ID:** `tree_growth_branching`  
**Experimental:** No

---

## Purpose

Explore tree-like growth, branching and resource-seeking morphogenesis through memory
stabilisation, flow gradients and local reinforcement. The memory field acts as stabilised
"woody tissue" while energy gradients drive directional expansion.

---

## Inspiration

Inspired by plant growth, vascular transport, diffusion-limited aggregation (Witten & Sander,
1981) and morphogenetic self-organisation (Turing, 1952; Meinhardt, 1982).

Energy corresponds abstractly to light/nutrients, memory to stabilised grown tissue,
flow to transport channels, and coupling to local reinforcement of existing branches.
No hormones, leaves, roots or actual plant physiology are modelled.

---

## How to Run

**Dashboard:** Select *Morphogenesis → Tree Growth / Branching Morphogenesis* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset tree_growth_branching --steps 1000
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `memory_decay` | 0.998 | Very slow decay = grown structures persist |
| `memory_imprint_strength` | 0.45 | Strong imprinting = clear branch traces |
| `flow_gradient_strength` | 0.08 | Directional transport along branches |
| `coupling_gain` | 0.10 | Local reinforcement of existing growth |
| `diffusion_energy` | 0.04 | Low diffusion = localised energy pockets |
| `noise_amplitude` | 0.025 | Noise drives asymmetric branching |

---

## Expected Patterns

- Branch-like memory structures accumulating over time
- Expanding growth fronts
- Locally reinforced stems
- Asymmetric branching driven by noise and local gradients

---

## Suggested Observations

1. Watch the **memory field** for branching tree-like structures.
2. Run for at least 500–1000 ticks — branching structures take time to develop.
3. Vary `noise_amplitude` (0.01 vs 0.05) — low noise gives symmetric trees, high noise gives irregular branching.
4. Increase `memory_decay` toward 1.0 (0.9995) for denser, more persistent structures.
5. Compare memory and coupling fields — coupling should trace branch boundaries.

---

## Suggested Metrics

- Branch count (cluster count in memory field)
- Memory field mean over time (growth rate)
- Spatial entropy (decreases as structure forms)
- Growth front velocity

---

## Limitations

- Not a biological tree model — no hormones, roots, leaves or vascular tissue
- Branching is field-driven, not governed by plant physiology
- No directed initial conditions (seed/root from bottom) yet — planned for Epic 10
- Fractal dimension and skeleton analysis not yet implemented — planned for Epic 12
- Results depend heavily on initial random state (seed)

---

## Future Extensions

- Epic 10: Add bottom-up energy gradient (light from above, root from below)
- Epic 10: Add a centered seed as initial growth point
- Epic 12: Add branch skeleton extraction and branch count metric
- Epic 12: Add fractal dimension estimate
- Epic 12: Add mycelium-like and river-network-like variants
