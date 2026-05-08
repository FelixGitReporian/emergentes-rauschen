# Stigmergy / Ant Trails

**Category:** Collective Behavior  
**ID:** `stigmergy_ant_trails`  
**Experimental:** No

---

## Purpose

Explore indirect coordination through persistent memory traces. The memory field acts as an
abstract pheromone layer: particles imprint traces, traces attract more particles, creating
self-reinforcing path structures through stigmergic feedback.

---

## Inspiration

In ant colonies, individuals deposit pheromone chemicals into the environment. Other individuals
are attracted to these traces, creating positive feedback loops and stable foraging paths
(Deneubourg et al., 1990; Dorigo & Stützle, 2004).

This preset is an **abstract field-particle model**, not an ant colony simulation.
There are no explicit food sources, nests, agent decisions or pheromone chemistry.

---

## How to Run

**Dashboard:** Select *Collective Behavior → Stigmergy / Ant Trails* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset stigmergy_ant_trails --steps 500
```

**Python:**
```python
from emergent_noise.experiments.presets import get_preset
preset = get_preset("stigmergy_ant_trails")
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `memory_decay` | 0.995 | Slow decay = traces persist (pheromone evaporation rate) |
| `memory_imprint_strength` | 0.6 | Strong imprinting = clear trace deposition |
| `diffusion_energy` | 0.03 | Low diffusion = localised paths, not spreading blobs |
| `coupling_gain` | 0.08 | Local reinforcement (recruitment-like feedback) |
| `noise_amplitude` | 0.01 | Low noise = structure dominates over randomness |

---

## Expected Patterns

- Persistent trail-like memory structures
- Local reinforcement loops
- Path stabilisation over time
- Slow decay of previously active routes

---

## Suggested Observations

1. Watch the **memory field** — traces should accumulate and persist over hundreds of ticks.
2. Observe the **particle tab** — particles should concentrate along existing memory ridges.
3. Note **entropy reduction** over time as structure dominates.
4. Increase `noise_amplitude` to see trace erosion (pheromone disruption).
5. Increase `memory_decay` toward 1.0 to see permanent fossilisation of traces.

---

## Suggested Metrics

- Memory field mean and persistence
- Path density (memory field clustering)
- Cluster connectivity
- Entropy reduction over time

---

## Limitations

- Not a full ant colony model — no food sources, nest locations or agent decisions
- Particles have no heading or orientation — movement is field-gradient-driven
- Trace branching depends on initial noise conditions, not active decision-making
- No pheromone chemistry or evaporation dynamics — memory decay is a global parameter

---

## Future Extensions

- Epic 10: Add a food source seed and a nest seed as initial conditions
- Epic 11: Add real agent policies with heading, local sampling and pheromone deposition
- Epic 13: Add spatial autocorrelation and path persistence metrics
