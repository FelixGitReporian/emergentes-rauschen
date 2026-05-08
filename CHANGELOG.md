# Changelog

All notable changes are documented here.
Format: [Semantic Versioning](https://semver.org/).

---

## [2.0.0] – 2026-05-08

### Added (Epic 7–8 – Experiment Framework + Consciousness Research)

- `experiments/__init__.py`, `experiments/configs.py`, `experiments/runner.py`:
  - 8 predefined experiments: STABILITY_SWEEP, REACTION_SWEEP, META_EVOLUTION,
    MEMORY_EFFECT, COUPLING_STUDY, PROTO_LIFE_SEARCH, REACTION_DIFFUSION_MEMORY,
    CONSCIOUSNESS_SCAN.
  - Cartesian product sweep over arbitrary `SimConfig` parameters.
  - Git commit hash + full metadata saved to `experiment_meta.json`.
  - CSV output with entropy, persistence, compartments, regime, Φ-proxy.
  - CLI: `python -m emergent_noise.experiments.runner -e <name>`.
- `interpretation/consciousness.py` – `ConsciousnessAnalyzer`:
  - Φ-Proxy (simplified IIT approximation): global coherence × (1 − local variance).
  - Active-Inference marker (Friston Free-Energy proxy): memory–energy correlation.
  - Proto-Life score (6 criteria: boundaries, energy flow, self-maintenance,
    adaptation, memory, variation).
  - Global-Workspace proxy (Baars / Dehaene): Gini coefficient of information field.
  - Integrated score: 0.3×Φ + 0.2×AI + 0.3×PL + 0.2×GW.
- Dashboard `visualization/dashboard.py` v2.0.0:
  - **Tab 4 🎓 Learning & Theory** with 3 depth levels (Entry / Intermediate /
    Research Front), live consciousness markers, multiscale model visualisation,
    attractor trajectory, concept glossary.
  - Integrated sources: Mitchell, Levy, natureofcode.com, Wolfram NKS, SFI Explorer,
    Lenia, Avida, OpenWorm, Framsticks, ALIFE, Tononi / Friston / Walker primary
    sources, Sara Walker podcasts.
- `examples/benchmark_10k.py`: 10k-tick stability sweep across 6 noise levels,
  metric snapshots every 500 ticks, timing CSV + results CSV.
- `examples/capture_dashboard.py`: Playwright-based screenshot capturer for all
  5 dashboard tabs.
- `docs/scientific-scope.md`: explicit claims and non-claims of the project.
- `docs/research-context.md`: relationship to CA, ALife, Wolfram, IIT, Free-Energy.

### Scientific Caution

Φ-Proxy, Active-Inference score and Proto-Life score are heuristic proxies.
They are NOT evidence of consciousness, life or experience. High scores mean
"structurally interesting" — nothing more.

---

## [1.0.0] – 2026-05-08

### Added (Epic 5–6 – Graph Mode + Multiscale Model)

- `core/graph_state.py` – `GraphState` + `GraphConfig`:
  - 4 topologies: small_world (Watts–Strogatz), scale_free (Barabási–Albert),
    random (Erdős–Rényi), grid.
  - Weighted energy diffusion, local reaction, edge decay.
  - Hypergraph rewriting: active nodes form new edges each tick.
  - Emergent distance matrix (Dijkstra, 1/weight).
  - `graph_summary`: density, clustering, connectedness, components.
- `core/multiscale.py` – `MesoLayer`, `AttractorLandscape`, `MultiscaleController`:
  - MesoLayer: connected clusters as trackable entities with centroid velocity.
  - AttractorLandscape: phase-space trajectory (energy × coherence), transition detection.
  - MultiscaleController: micro + meso + macro in one update call.
- Dashboard `visualization/dashboard.py`:
  - **Tab 5 🕸️ Graph Mode**: NetworkX visualisation, distance matrix,
    energy histogram, topology comparison, Wolfram Physics explanation.
  - Tab 4 Learn tab: live meso/macro metrics + attractor trajectory.
- `networkx` as new optional dependency.
- `tests/test_epics5to8.py`: 35 tests (172 total, all passing).

---

## [0.5.0] – 2026-05-08

### Added (Epic 4 – Particle-Field Hybrid)

- `core/particles.py`: `ParticleConfig` + `ParticleSystem` (vectorised):
  - Particles as NumPy arrays `(N, 2)` / `(N,)` (positions, velocities,
    energy, mass, active, age).
  - `apply_field_to_particles`: gradient attraction, flow drag, energy
    absorption, reactivity boost via bilinear interpolation.
  - `apply_particles_to_field`: energy, matter, coupling, information
    deposition via `np.add.at`.
  - `apply_collisions`: O(N²) aggregation fusion with mass-weighted
    position, momentum and energy.
  - `step_particles`: complete particle tick.
  - `summary`: compact statistics including proto-compartment count.
- `analysis/compartments.py`:
  - `detect_compartments`: field-based compartment detection (SciPy
    `label` + compactness + heuristic proto-life score).
  - `particle_compartments`: particle-based density map + aggregate markers.
  - `CompartmentResult` / `Compartment` dataclasses.
- Dashboard `visualization/dashboard.py` v0.5.0:
  - Tab 3 ⚗️ Particles: live scatter over energy heatmap, density map with
    aggregate markers (★), compartment table, rule-genome heatmap.
  - Sidebar: particle configuration (count, attraction, drag, damping,
    collision radius, on/off toggle).
  - Particle tick integrated into simulation loop.
- `docs/design-decisions/ADR-0004-particle-field-hybrid.md`.
- `tests/test_epic4.py`: 27 tests (137 total, all passing).

### Scientific Caution

Particle dynamics is a simplified abstraction without momentum or energy
conservation. Proto-life scores are structural proxies, not evidence of
biological processes. Emergent aggregates are exploratory phenomena.

---

## [0.4.0] – 2026-05-08

### Added (Epic 3 – Meta-Rules + Rule Evolution)

- `core/state.py`: two new genome fields in `GridState`:
  - `genome_strength`   – local reaction strength per cell (float32 array)
  - `genome_threshold`  – local energy threshold per cell (float32 array)
  - Initialised with slight variation around global config values.
  - `genome_dict()` helper. `clip_all()` now also clips genome arrays.
- `core/state.py`: `SimConfig` gains five new meta-rule parameters:
  `meta_mutation_rate`, `meta_mutation_strength`, `meta_selection_rate`,
  `meta_retention_threshold`, `meta_enabled`.
- `rules/meta_rules.py`: `apply_meta_rules` with three steps per tick:
  - **Mutation**: random genome variation with configurable rate / strength.
  - **Selection**: local 3×3 neighbourhood selection (fitter profiles spread).
  - **Retention**: memory field reinforcement by successful profiles.
  - Fitness = `coherence × (1 − local_energy_variance)` (heuristic proxy).
- `rules/reaction.py`: rule 1 now uses `genome_threshold` and
  `genome_strength` instead of global config constants → spatially
  heterogeneous reaction behaviour.
- `core/tick.py`: meta-rules integrated as step 7 in the tick loop.
- `analysis/novelty.py`:
  - `BehaviorVector` – compressed state vector for novelty comparison.
  - `NoveltyTracker` – archive-based k-NN novelty metric.
  - `genome_diversity` – spatial diversity of genome distributions.
  - `genome_entropy` – Shannon entropy of genome value distributions.
- `docs/design-decisions/ADR-0003-meta-rule-evolution.md`.
- `tests/test_epic3.py`: 32 new tests (110 total, all passing).

### Scientific Caution

Rule-genome evolution is an abstract model, not a model of real genetics.
Fitness proxies are heuristic. Emergent differentiation is an exploratory
phenomenon, not a biological claim.

---

## [0.3.1] – 2026-05-08

### Changed – Dashboard (Epic 2.6)

- `visualization/dashboard.py` fully extended to **v0.3.1**:
  - **Tab 1 🔬 Simulation**: live heatmap (with mean/std in title),
    RGB-composite, entropy time series, persistence bar, cluster statistics,
    phase indicator.
  - **Tab 2 🧭 Trace Reading**: full trace reading integration from Epic 2:
    - Regime banner (icon + name + confidence) visible above all tabs.
    - Manual "Run trace analysis now" button + auto-trigger every
      `trace_interval` ticks.
    - **Regime classification**: primary / secondary / confidence + description
      + collapsible evidence values.
    - **Narrative**: metaphoric interpretation families, probable past,
      possible future paths, embedded scientific disclaimer (3-column layout).
    - **Morphology**: components, holes, Euler number, boundary complexity,
      elongation, compactness + binary threshold image.
    - **MI-matrix heatmap**: normalised mutual information as colour raster
      with numeric values.
    - **Field statistics table**: mean, std, min, max, active fraction.
    - **Phase transition indicator**: susceptibility + energy variance.
    - **JSON export**: full `TraceReport` in collapsible expander.
  - Sidebar: new sliders for `reactivity_recovery`, `reactivity_rest`,
    `matter_erosion_rate`, `matter_deposition_rate`, `trace_interval`,
    `show_mi_heatmap`, `show_morphology`.

---

## [0.3.0] – 2026-05-08

### Added (Epic 2 – Trace Reading Engine)

- `analysis/morphology.py`: `compute_morphology` — boundary complexity,
  hole count, Euler number, elongation, compactness for 2D fields.
- `analysis/mutual_information.py`: `field_mi`, `mi_matrix`, `local_mi` —
  normalised mutual information between fields (histogram method).
- `analysis/trace_reading.py`: `read_traces` + `TraceReport` — full trace
  reading engine integrating all analysis modules, JSON-exportable.
- `interpretation/regime_classifier.py`: `classify_regime` + `RegimeResult` —
  8 heuristic regime types (QUIESCENT, DIFFUSE, CLUSTERED, VORTEX,
  COHERENT, FILAMENTARY, CRITICAL, COMPLEX) with confidence score.
- `interpretation/narratives.py`: `build_narrative` + `Narrative` —
  language interpretation: metaphors, probable past, possible futures,
  scientific caution notice.
- `tests/test_epic2.py`: 26 new tests (78 total, all passing).

### Scientific Caution

All regime labels, interpretations and narratives are readings,
not truth labels. Every result contains explicit caution formulations.

---

## [0.2.1] – 2026-05-08

### Changed / Fixed

- `rules/reaction.py`: `reactivity` dynamics (EMA recovery + consumption
  on activation) and `matter` dynamics (erosion by flow, deposition in
  calm regions) implemented. All 8 core parameters of the workbook are
  now **fully dynamic**.
- `rules/coupling.py`: basal decay term added, prevents saturation in
  homogeneous fields.
- `rules/reaction.py`: deposition formula changed to
  `deposition * coupling * (1 - matter)`, prevents `matter` saturation at 1.0.
- `core/state.py`: new default parameters `reactivity_recovery=0.98`,
  `reactivity_rest=0.5`, `matter_erosion_rate=0.02`,
  `matter_deposition_rate=0.005`.
- `examples/run_analysis.py`: new analysis script with persistence, cluster,
  phase and field summary output (5 CSVs + PNGs).

### Tests

- 4 new tests: `test_reactivity_recovers_toward_rest`,
  `test_reactivity_consumed_by_activation`, `test_matter_erodes_with_flow`,
  `test_matter_deposits_in_calm_regions` (52 total).

### Equilibrium values (Seed 42, 300 ticks, 64×64)

```
energy=0.398  matter=0.563  information=0.199  coupling=0.480
reactivity=0.500  memory=0.119  coherence=0.150  flow≈0.003
```

---

## [0.2.0] – 2026-05-08

### Added

- `src/emergent_noise/rules/coupling.py`: binding, decay, coherence synchronisation.
- `src/emergent_noise/rules/flow.py`: gradient flow, damping, curl vortex, advective transport.
- `src/emergent_noise/analysis/attractors.py`: `PersistenceTracker`, `find_clusters`,
  `compute_phase_indicator`, `field_summary`.
- `src/emergent_noise/visualization/dashboard.py`: Streamlit live dashboard with
  sidebar config, heatmap, RGB-composite, entropy time series, cluster analysis.
- Numba-JIT optional in `rules/diffusion.py` (transparent fallback to NumPy).
- 7 new parameters in `SimConfig` (`coupling_*`, `flow_*`).
- 15 new pytest tests (48 total).
- `.github/`: CI workflow, issue templates (bug, feature, experiment), PR template.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- `ROADMAP.md` with 8 epics following the workbook.
- `docs/design-decisions/ADR-0002-coupling-flow-architecture.md`.

### Changed

- `core/tick.py`: rule order extended to 8 steps (coupling + flow).
- `README.md`: fully revised for GitHub collaboration.

### Scientific Caution

All new fields (coupling, flow) are now active — all 8 core parameters
of the workbook are alive in the simulation. Interpretations remain
exploratory and hypothetical.

---

## [0.1.0] – 2026-05-08

### Added

- `pyproject.toml` with hatchling build backend, dependencies and pytest configuration.
- `src/emergent_noise/core/state.py`: `SimConfig` (Pydantic) and `GridState` (dataclass)
  with 8 core parameters + flow_x/flow_y.
- `src/emergent_noise/core/tick.py`: `TickLoop` with documented, deterministic
  rule order; callback support.
- `src/emergent_noise/rules/diffusion.py`: 5-point Laplace diffusion for energy + information.
- `src/emergent_noise/rules/reaction.py`: activation and decay reaction.
- `src/emergent_noise/rules/memory.py`: memory decay + imprint.
- `src/emergent_noise/noise/structured_noise.py`: sinusoidal superposition with seed + tick.
- `src/emergent_noise/analysis/entropy.py`: normalised Shannon entropy.
- `src/emergent_noise/visualization/render.py`: panel PNG (9 fields) + RGB-composite.
- `examples/run_500.py`: example run with CLI arguments, PNG output, entropy CSV.
- `tests/`: 30+ pytest tests for init, determinism, value ranges, rules, noise, entropy.
- `docs/design-decisions/ADR-0001-start-with-2d-grid.md`.

### Scientific Caution

All interpretations in this version are exploratory. No claims about
consciousness, real physics or life.
