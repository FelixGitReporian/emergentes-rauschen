# Parameter Guide

All core `SimConfig` parameters explained: intuition, mathematical role, and effect of changing them.

---

## noise_amplitude
**Intuition:** How much random variation is added to the fields every tick.
**Mathematical role:** Additive Gaussian noise on the energy field — controls the noise floor.
**Increase:** More randomness; patterns break up, system explores more state space.
**Decrease:** Less exploration; patterns stabilise but may become rigid or monotonous.
**Try:** Compare noise_amplitude = 0.005, 0.03, 0.08 — when does structure survive?

---

## memory_decay
**Intuition:** How long traces persist in the memory field before fading.
**Mathematical role:** Multiplicative decay: `memory(t+1) = memory(t) * memory_decay` each tick.
**Increase:** Traces persist longer; paths and structures become more stable.
**Decrease:** Traces fade quickly; the system becomes more forgetful and exploratory.
**Try:** memory_decay = 0.80, 0.95, 0.999 — compare path persistence after 300 ticks.

---

## memory_imprint_strength
**Intuition:** How strongly active energy cells write into the memory field.
**Mathematical role:** Linear imprint: `memory += imprint_strength * energy` (clipped to [0,1]).
**Increase:** Memory field fills up faster; traces become more prominent.
**Decrease:** Memory is barely written; traces are faint and transient.
**Try:** imprint = 0.1 vs 0.8 — how quickly does the memory field saturate?

---

## diffusion_energy
**Intuition:** How quickly energy spreads to neighbouring cells.
**Mathematical role:** Discrete Laplacian: `u(t+1) += D * nabla^2(u)`.
**Increase:** Energy spreads faster; local peaks smooth out, patterns become larger.
**Decrease:** Energy stays localised; sharper, more isolated patterns form.
**Try:** diffusion_energy = 0.01, 0.1, 0.3 — when do spots merge into bands?

---

## diffusion_information
**Intuition:** How quickly the information field spreads.
**Mathematical role:** Same Laplacian diffusion as energy but applied to the information field.
**Increase:** Information distributes broadly; Turing inhibitor spreads faster.
**Decrease:** Information stays local; can allow activator-dominant dynamics.
**Try:** Vary diffusion_information relative to diffusion_energy — watch for Turing patterns.

---

## reaction_energy_threshold
**Intuition:** The energy level a cell must exceed before the reaction rule fires.
**Mathematical role:** Heaviside threshold: reaction fires only where `energy > threshold`.
**Increase:** Fewer cells react; pattern is sparser.
**Decrease:** More cells react; reaction spreads broadly and may saturate.
**Try:** Shift threshold from 0.3 to 0.7 — when does the reaction stop producing structure?

---

## reaction_strength
**Intuition:** How strongly the reaction rule fires when the threshold is crossed.
**Mathematical role:** `energy += reaction_strength` where threshold is exceeded.
**Increase:** Reactions are stronger; patterns form faster and more intensely.
**Decrease:** Weak reactions; system may not produce clear patterns.
**Try:** Vary from 0.05 to 0.5 — when do Turing-like patterns appear?

---

## coupling_gain
**Intuition:** How strongly a cell's activity amplifies its neighbours.
**Mathematical role:** Positive feedback term in the coupling field update.
**Increase:** Stronger local amplification; clusters become more pronounced.
**Decrease:** Weak coupling; cells behave more independently.
**Try:** coupling_gain = 0.01, 0.05, 0.15 — when do clusters self-organise?

---

## coupling_sync_rate
**Intuition:** How quickly neighbouring cells synchronise their coupling field values.
**Mathematical role:** Coupling synchronisation rate applied per tick to local neighbourhoods.
**Increase:** Coupling synchronises quickly; boundaries sharpen and stabilise.
**Decrease:** Coupling synchronises slowly; boundary-like structures are more diffuse.

---

## coupling_loss
**Intuition:** How quickly the coupling field decays over time.
**Mathematical role:** Multiplicative decay: `coupling(t+1) = coupling(t) * (1 - coupling_loss)`.
**Increase:** Coupling fades quickly; transient patterns dominate.
**Decrease:** Coupling accumulates; persistent coupled structures form.

---

## flow_gradient_strength
**Intuition:** How strongly the flow field follows energy gradients.
**Mathematical role:** `flow_velocity += gradient_strength * grad(energy)` at each step.
**Increase:** Flow is strongly directed; growth or movement becomes channelled.
**Decrease:** Flow is weak; patterns are more isotropic and diffuse.
**Try:** flow_gradient_strength = 0.3 — does growth become directionally biased?

---

## flow_damping
**Intuition:** How quickly flow velocity decays (friction / drag).
**Mathematical role:** `flow(t+1) = flow(t) * (1 - damping)` each tick.
**Increase:** Flow decays fast; short inertia, responsive to local gradients.
**Decrease:** Flow persists; long-range inertia, wave-like advection patterns.

---

## flow_advection_rate
**Intuition:** How strongly the energy field is advected by the flow field.
**Mathematical role:** Energy is transported along flow vectors at each tick.
**Increase:** Energy moves strongly with flow; directed transport patterns form.
**Decrease:** Advection is weak; flow has little effect on energy distribution.

---

## noise_scale
**Intuition:** Spatial scale of structured noise (larger = smoother noise patches).
**Mathematical role:** Controls the correlation length of the Perlin/structured noise field.
**Increase:** Large smooth noise structures; coarser random initial conditions.
**Decrease:** Fine-grained noise; more uniform random initialisation.
