# Experiment Gallery

A growing collection of reproducible simulation presets for exploring emergent phenomena
in the `emergentes-rauschen` field simulation system.

## Scientific Caution

These presets are **not** exact biological, physical or cognitive simulations.
They are exploratory field experiments designed to study **emergent analogues** — structural
behaviours that are *inspired by* natural phenomena without claiming to accurately replicate them.

Labels like "ant trails", "boids", "tree growth" describe the conceptual inspiration,
not the simulation mechanism. Results are heuristic and should be interpreted with care.

---

## Presets by Category

### Collective Behavior
- [Stigmergy / Ant Trails](stigmergy_ant_trails.md)
- [Boids Field Approximation](boids_field_approx.md) ⚠️ experimental

### Morphogenesis
- [Tree Growth / Branching Morphogenesis](tree_growth_branching.md)

### Pattern Formation
- [Reaction-Diffusion / Turing-like Patterns](reaction_diffusion_turing.md)

### Bio-inspired Dynamics
- [Excitable Media / Wave Propagation](excitable_media_waves.md)

### Trace Reading
- [Trace Reading / Fossil Field](trace_reading_fossil_field.md)

### Artificial Life
- [Autopoiesis / Membrane Formation](autopoiesis_membrane.md)

### Ecology
- [Ecosystem Patch Dynamics](ecosystem_patch_dynamics.md)

---

## How to Use

### In the Dashboard

```bash
python -m streamlit run src/emergent_noise/visualization/dashboard.py
```

1. Open the **Lernen & Theorie** tab to browse the full gallery with descriptions.
2. In the **sidebar**, select a **Preset Category** and then a **Preset**.
3. Click **▶ Apply Preset & Reset** to load the config.
4. Press **▶ Start** to run the simulation.

### From the Command Line

```bash
python examples/run_preset.py --preset stigmergy_ant_trails --steps 300
```

### As a Python Import

```python
from emergent_noise.experiments.presets import get_preset
from emergent_noise.core.state import GridState
from emergent_noise.core.tick import TickLoop

preset = get_preset("stigmergy_ant_trails")
state = GridState.initialize(preset.config)
loop = TickLoop(preset.config)

for _ in range(500):
    loop.step(state)
```

---

## Future Extensions

- Epic 10: Initial conditions (seed from bottom, top-down gradients, radial bursts)
- Epic 11: Real agent layer (true Boids, ant pheromone policies)
- Epic 12: Morphogenesis metrics (fractal dimension, skeleton, branch count)
- Epic 13: Trace reading metrics (spatial autocorrelation, event reconstruction)
