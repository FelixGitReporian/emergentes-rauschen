# Reaction-Diffusion / Turing-like Patterns

**Category:** Pattern Formation  
**ID:** `reaction_diffusion_turing`  
**Experimental:** No

---

## Purpose

Explore spot, stripe and wave-like pattern formation through local reaction and diffusion
dynamics. The diffusion asymmetry between energy and information fields provides
activator-inhibitor-like dynamics.

---

## Inspiration

Turing (1952) showed that a reaction-diffusion system with a short-range activator and
long-range inhibitor spontaneously produces spatial patterns — spots, stripes, labyrinths.
Gray-Scott (1984) and Gierer-Meinhardt models are classic implementations.

This preset uses the existing abstract energy/information fields rather than a strict
two-species model. The diffusion ratio (`diffusion_energy / diffusion_information ≈ 3.5`)
provides the activator-inhibitor asymmetry.

---

## How to Run

**Dashboard:** Select *Pattern Formation → Reaction-Diffusion / Turing-like Patterns* in the sidebar, click **▶ Apply Preset & Reset**.

**CLI:**
```bash
python examples/run_preset.py --preset reaction_diffusion_turing --steps 500
```

---

## Key Parameters

| Parameter | Value | Role |
|---|---|---|
| `diffusion_energy` | 0.16 | Fast diffusion = inhibitor-like spreading |
| `diffusion_information` | 0.045 | Slow diffusion = activator-like localisation |
| `reaction_strength` | 0.14 | Strength of local transformation |
| `reaction_energy_threshold` | 0.48 | Threshold for reaction triggering |

---

## Expected Patterns

- Spots and stripe-like domains
- Reaction fronts propagating across the field
- Spatially localised pattern domains
- Wavelength selection through diffusion ratio

---

## Suggested Observations

1. Watch the **energy field** for spot/stripe formation.
2. The **RGB composite** (energy=R, information=G, coherence=B) shows pattern differentiation clearly.
3. Compare energy and information fields — they should form complementary structures.
4. Vary the diffusion ratio: increase `diffusion_energy` → smaller spots; decrease → larger blobs.
5. Change `reaction_strength` (0.08 vs 0.20) to see pattern dissolution vs. sharp boundaries.

---

## Suggested Metrics

- Spatial entropy (drops as patterns form)
- Dominant pattern wavelength (cluster spacing)
- Cluster count over time
- Field variance

---

## Limitations

- Not a strict two-species reaction-diffusion model
- Uses abstract fields instead of named activator/inhibitor variables
- Pattern type (spots vs stripes) is not directly controllable — depends on initial conditions
- No Gray-Scott feed/kill parameters — planned as a possible Epic 12 extension

---

## Future Extensions

- Epic 12: Add a true two-species Gray-Scott or Gierer-Meinhardt model as a separate module
- Epic 10: Add patterned initial conditions (e.g. stripe seed) for reproducible pattern type
- Epic 13: Add wavelength and spatial autocorrelation metrics
