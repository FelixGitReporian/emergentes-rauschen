# Boids Field Approximation

**Category:** Collective Behavior  
**ID:** `boids_field_approx`  
**Experimental:** ⚠️ Yes

---

## Purpose

Explore flock-like collective movement through field coupling, coherence and flow dynamics.
This is a field-based approximation — not a classical Boids implementation.

---

## Inspiration

Reynolds (1987) showed that three simple local rules — separation, alignment, cohesion —
produce convincing flocking behaviour in discrete agents. This preset approximates some
of those dynamics through coherent flow fields and field-driven particle drift, without
implementing explicit inter-agent rules.

This is explicitly marked **experimental** because the flock-like appearance is field-driven
and not the result of true neighbour interaction. It is a stepping stone toward Epic 11
(Real Agent Layer).

---

## How to Run

**Dashboard:** Select *Collective Behavior → Boids Field Approximation* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset boids_field_approx --steps 300
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `flow_gradient_strength` | 0.10 | Drives collective field drift (alignment proxy) |
| `flow_damping` | 0.85 | Low damping = particles carry momentum (inertia) |
| `coupling_gain` | 0.12 | Field coherence = loose cohesion proxy |
| `memory_decay` | 0.92 | Fast decay = no frozen trails, movement dominates |
| `noise_amplitude` | 0.04 | Individual variation between particles |

---

## Expected Patterns

- Field-driven collective drift
- Loose flock-like particle streams
- Rotational or wave-like flow patterns
- Temporary coherent particle clusters

---

## Suggested Observations

1. Watch the **flow field** (flow_x, flow_y) for coherent directional drift.
2. Observe **particle tab** for stream-like particle movement.
3. Compare with `stigmergy_ant_trails` — movement vs. trace structure.
4. Reduce `flow_damping` further (0.75) to see stronger inertial effects.
5. Increase `coupling_gain` to see tighter cluster formation.

---

## Suggested Metrics

- Mean particle velocity coherence
- Particle clustering
- Flow curl magnitude
- Coherence field variance

---

## Limitations

- **Not a true Boids model** — no explicit velocity alignment between particles
- No direct separation or cohesion rules between neighbouring agents
- Collective movement emerges from field gradients, not inter-agent communication
- "Flock-like" appearance may not be robust across parameter variations

---

## Future Extensions

- Epic 11: Add AgentState with heading + velocity; implement separation, alignment, cohesion
- Epic 11: Add spatial hashing for O(N) neighbour search
- Then rename this to "True Boids" and keep this as "Field Approximation" for comparison
