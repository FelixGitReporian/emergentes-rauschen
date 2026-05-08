# Excitable Media / Wave Propagation

**Category:** Bio-inspired Dynamics  
**ID:** `excitable_media_waves`  
**Experimental:** No

---

## Purpose

Explore threshold-driven excitation waves, refractory-like suppression and propagating
activity fronts. Inspired by excitable media in biology and chemistry.

---

## Inspiration

Excitable media support waves that trigger at a threshold, propagate, and leave a refractory
zone that temporarily prevents re-excitation. Classic examples:
- Neural action potentials (Hodgkin & Huxley, 1952)
- Cardiac muscle waves and spiral waves
- Belousov-Zhabotinsky (BZ) chemical oscillation

This preset uses a high reaction threshold and fast memory decay to approximate
excitation-refractory dynamics. No physiological ion channels or actual neuroscience is modelled.

---

## How to Run

**Dashboard:** Select *Bio-inspired Dynamics → Excitable Media / Wave Propagation* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset excitable_media_waves --steps 400
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `reaction_energy_threshold` | 0.62 | High threshold = excitation requires strong local energy |
| `reaction_strength` | 0.22 | Strong reaction = fast, sharp wave fronts |
| `memory_decay` | 0.88 | Fast decay = short refractory-like suppression window |
| `coupling_gain` | 0.13 | Lateral coupling = wave propagation to neighbours |

---

## Expected Patterns

- Propagating activity fronts across the field
- Temporary refractory-like suppression zones behind wave fronts
- Spiral or ring-like waves if conditions allow
- Oscillatory excitation-suppression cycles

---

## Suggested Observations

1. Watch the **energy field** for propagating wavefronts.
2. The **reactivity field** shows the refractory-like state.
3. Vary `reaction_energy_threshold` (0.55 vs 0.70) — lower thresholds produce more frequent excitation.
4. Increase `coupling_gain` (0.18) to see faster-spreading waves.
5. Reduce `memory_decay` (0.80) for longer refractory periods — waves become slower and sparser.

---

## Suggested Metrics

- Wavefront speed (cluster propagation velocity)
- Activation density over time
- Oscillation frequency (peaks in entropy time series)
- Spatial coherence

---

## Limitations

- No explicit refractory state variable — memory field approximates this indirectly
- No real neuron, cardiac cell or BZ-reaction chemistry
- Wave speed depends on grid resolution and tick rate — not calibrated to physical units
- Spiral waves require specific initial conditions not yet implemented

---

## Future Extensions

- Epic 10: Add radial burst initial condition to reliably trigger spiral waves
- Epic 12: Add explicit refractory state variable for cleaner excitable dynamics
- Epic 13: Add wavefront speed and oscillation frequency metrics
