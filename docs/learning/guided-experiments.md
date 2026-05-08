# Guided Experiments

Step-by-step mini-experiments for each preset. Each experiment asks one focused
observation question. Keep a note of what you observe.

Scientific caution: Results are qualitative tendencies in an abstract model,
not quantitative predictions about biological or physical systems.

---

## Stigmergy / Ant Trails (`stigmergy_ant_trails`)

### Experiment 1: Forgetful field
Set `memory_decay = 0.80`. Run 300 ticks.
**Question:** Do stable trails still emerge, or does the field stay diffuse?
*Hint: Low decay means fast forgetting — paths compete and fade quickly.*

### Experiment 2: Overpersistent traces
Set `memory_decay = 0.999`. Run 300 ticks.
**Question:** Does the system become too rigid? Can new paths form after tick 100?

### Experiment 3: Exploration vs exploitation
Compare `noise_amplitude = 0.005`, `0.03`, `0.08`. Run 300 ticks each.
**Question:** When does noise help discover new paths, and when does it destroy them?

---

## Boids Field Approximation (`boids_field_approx`)

### Experiment 1: No coupling — pure noise
Set `coupling_gain = 0.0`. Run 200 ticks.
**Question:** Without alignment signal, does coherent motion still emerge?

### Experiment 2: Strong flow gradient
Set `flow_gradient_strength = 0.3`. Run 200 ticks.
**Question:** Does the flow field develop a dominant direction?

---

## Tree Growth / Branching Morphogenesis (`tree_growth_branching`)

### Experiment 1: Strong memory, weak noise
Set `memory_decay = 0.998`, `noise_amplitude = 0.01`. Run 300 ticks.
**Question:** Does growth become more trunk-like with fewer branches?

### Experiment 2: High noise branching
Set `noise_amplitude = 0.08`. Run 300 ticks.
**Question:** Do more side branches appear? Does the fractal dimension (Morphogenesis panel) increase?

### Experiment 3: Strong flow gradient
Set `flow_gradient_strength = 0.25`. Run 300 ticks.
**Question:** Does growth become directionally biased (anisotropic)?

---

## Reaction-Diffusion / Turing Patterns (`reaction_diffusion_turing`)

### Experiment 1: Diffusion balance
Compare `diffusion_energy = 0.05` vs `0.25`, keeping `diffusion_information` fixed.
**Question:** Which produces spots, stripes or spatial smoothing?

### Experiment 2: Threshold shift
Change `reaction_energy_threshold` from `0.3` to `0.7`.
**Question:** When does the field stop producing distinct patterns?

### Experiment 3: Pattern wavelength
Vary `reaction_strength` from `0.1` to `0.5`.
**Question:** Does the spacing between pattern elements change?

---

## Excitable Media / Waves (`excitable_media_waves`)

### Experiment 1: Wave speed measurement
Run for 100 ticks; watch the **wavefront speed** metric in the Spurenlesen tab.
**Question:** Does wavefront speed correlate with `diffusion_energy`?

### Experiment 2: Noise-induced breakdown
Increase `noise_amplitude` from `0.01` to `0.1` in steps.
**Question:** At what noise level do coherent wave fronts break down?

---

## Trace Reading / Fossil Field (`trace_reading_fossil_field`)

### Experiment 1: Deep memory record
Set `memory_decay = 0.999`. Run 500 ticks.
**Question:** What layers of history are visible in the memory field?

### Experiment 2: Entropy reading
Watch the **entropy trend chart** in the Spurenlesen tab.
**Question:** When does entropy decrease — what does that correspond to visually?

---

## Autopoiesis / Membrane (`autopoiesis_membrane`)

### Experiment 1: Boundary stability
Increase `coupling_sync_rate` and `coupling_gain`.
**Question:** Do more persistent boundary-like clusters appear?

### Experiment 2: Fragile membranes
Increase `noise_amplitude` from `0.02` to `0.12` in steps.
**Question:** At what noise level do boundaries dissolve?
*Hint: There may be a sharp transition — a noise-induced phase change.*

---

## Ecosystem Patch Dynamics (`ecosystem_patch_dynamics`)

### Experiment 1: Fragmented landscape
Reduce `diffusion_energy` to `0.02`.
**Question:** Do patches become isolated? Does mean cluster lifetime increase?

### Experiment 2: Disturbance regime
Increase `noise_amplitude` to `0.1`.
**Question:** Does turnover accelerate? Do patch lifetimes shorten?
