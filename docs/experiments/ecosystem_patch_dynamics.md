# Ecosystem Patch Dynamics

**Category:** Ecology  
**ID:** `ecosystem_patch_dynamics`  
**Experimental:** No

---

## Purpose

Explore resource patches, regeneration cycles, disturbance and succession-like dynamics
in a heterogeneous abstract landscape. Inspired by landscape ecology and patch dynamics theory.

---

## Inspiration

Levin & Paine (1974) introduced patch dynamics: disturbance creates openings, colonisation
fills them, creating a mosaic of succession stages. Tilman's resource competition models
show how spatial heterogeneity maintains diversity.

In this preset:
- Energy = resources / productivity
- Memory = ecological legacy / soil history
- Noise = stochastic disturbance events
- Coupling = local biotic interactions

No species, trophic networks, seasonal forcing or competitive exclusion are modelled.

---

## How to Run

**Dashboard:** Select *Ecology → Ecosystem Patch Dynamics* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset ecosystem_patch_dynamics --steps 500
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `reaction_strength` | 0.07 | Local growth rate |
| `memory_decay` | 0.992 | Ecological legacy persistence |
| `coupling_gain` | 0.09 | Biotic interaction strength |
| `noise_amplitude` | 0.035 | Disturbance frequency and magnitude |

---

## Expected Patterns

- Resource patches expanding and contracting over time
- Succession-like spatial dynamics (pioneer → climax → collapse)
- Collapse and recovery zones driven by noise disturbances
- Heterogeneous landscape memory patterns

---

## Suggested Observations

1. Watch the **energy field** for patch expansion and contraction.
2. Compare **memory** and **energy** — memory should trail behind energy as a legacy signal.
3. Vary `noise_amplitude` (0.01 vs 0.08) — low noise → stable patches; high noise → rapid disturbance cycling.
4. Use the **Spurenlesen** tab — regime should oscillate between clustered and vortex states.
5. Observe the **cluster count** metric — should show periodic patch formation and dissolution.

---

## Suggested Metrics

- Patch count (energy field clusters) over time
- Patch persistence
- Spatial entropy
- Landscape heterogeneity (field variance)

---

## Limitations

- One abstract energy field only — no explicit species or trophic structure
- No competitive exclusion or predator-prey dynamics
- No seasonal or periodic forcing
- "Succession" is an interpretive label, not a mechanistic succession model

---

## Future Extensions

- Epic 12: Add resource gradient following for more realistic patch expansion
- Future: Add a second field as "consumer" to model predator-prey patch dynamics
- Future: Add seasonal forcing via time-varying noise amplitude
- Epic 13: Add patch persistence and recovery time metrics
