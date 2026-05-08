# Trace Reading / Fossil Field

**Category:** Trace Reading  
**ID:** `trace_reading_fossil_field`  
**Experimental:** No

---

## Purpose

Explore how past events leave persistent, partially readable traces in memory, information
and coherence fields. Designed as the canonical trace-reading experiment — the field is
treated as a readable historical record.

---

## Inspiration

Inspired by tracking, forensics, geological sedimentation and abductive inference
(Peirce, 1903; Ginzburg, 1989 "Clues"). The field accumulates like sediment: early
high-energy events leave "scars" that remain partially readable much later.

Very slow memory decay (0.999) means the field behaves like a geological record.
This aligns with the project's core concept: treating emergent field dynamics as
interpretable traces of past activity rather than pure noise.

---

## How to Run

**Dashboard:** Select *Trace Reading → Trace Reading / Fossil Field* in the sidebar, click **▶ Apply Preset & Reset**.

The **Spurenlesen** tab is the primary analysis surface for this preset.

**CLI:**
```bash
python examples/run_preset.py --preset trace_reading_fossil_field --steps 600
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `memory_decay` | 0.999 | Near-permanent trace accumulation |
| `memory_imprint_strength` | 0.5 | Strong trace deposition |
| `diffusion_information` | 0.035 | Slow information spread = localised structure |
| `flow_gradient_strength` | 0.045 | Directional deformation of traces |

---

## Expected Patterns

- Long-lived persistent trace structures accumulating over time
- Sediment-like memory layers from early high-energy events
- Directional deformation of the memory field from flow gradients
- Historical "scars" marking past high-activity zones

---

## Suggested Observations

1. Watch the **memory field** — it should accumulate distinct structure over hundreds of ticks.
2. Use the **Spurenlesen** tab for regime classification and narrative reading.
3. Compare the memory field at tick 100 vs tick 500 — traces should deepen, not fade.
4. Check the **Spurenlesen narrative** — it should describe persistent historical structures.
5. Vary `flow_gradient_strength` to see directional "geological strata" effects.

---

## Suggested Metrics

- Memory field mean over time (accumulation rate)
- Memory entropy (increases as diverse traces accumulate)
- Spatial autocorrelation (traces form structured, not random, patterns)
- Field autocorrelation decay length

---

## Limitations

- Trace inference is descriptive — no Bayesian reconstruction of past events
- Memory accumulates monotonically — no selective forgetting or consolidation
- Flow gradient direction is uniform — no spatially varying "wind"
- Trace "age" is not tracked — older and newer traces are indistinguishable

---

## Future Extensions

- Epic 13: Add memory persistence metric and trace lifetime tracking
- Epic 13: Add spatial autocorrelation and directionality metrics
- Epic 10: Add a "disturbance event" that creates a readable intervention
- Future: Add abductive inference module to reconstruct event history from field state
