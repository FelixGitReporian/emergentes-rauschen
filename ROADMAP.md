# Roadmap – Emergentes Rauschen

> Based on the [Professional Workbook](emergentes-rauschen-professionelle-arbeitsmappe.md) (v2.0).  
> Each epic corresponds to a phase of the simulation architecture (workbook sections 10–16).  
> Status: ✅ Done · 🔄 In Progress · 📋 Planned · 💡 Research
>
> **Current: v2.6.0 — Epics 9–14 complete — 398 tests, all passing.**

---

## Epic 0 – Foundation (Phase 1: 2D Grid) ✅

**Goal:** Minimal, deterministic, test-driven prototype.

| # | Task | Status |
|---|------|--------|
| 0.1 | Project structure, `pyproject.toml`, module scaffold | ✅ |
| 0.2 | `core/state.py` – `GridState` + `SimConfig` | ✅ |
| 0.3 | `core/tick.py` – deterministic tick loop | ✅ |
| 0.4 | `rules/diffusion.py` – 5-point Laplace (energy, information) | ✅ |
| 0.5 | `rules/reaction.py` – activation + decay rule | ✅ |
| 0.6 | `rules/memory.py` – EMA memory (decay + imprint) | ✅ |
| 0.7 | `noise/structured_noise.py` – sinusoidal superposition, seed+tick | ✅ |
| 0.8 | `analysis/entropy.py` – normalised Shannon entropy | ✅ |
| 0.9 | `visualization/render.py` – panel PNG + RGB-composite | ✅ |
| 0.10 | 33 pytest tests (init, determinism, value ranges) | ✅ |
| 0.11 | `examples/run_500.py` + entropy CSV | ✅ |

---

## Epic 1 – Relation Fields + Vector Dynamics ✅

**Goal:** All 8 core parameters active; coupling creates networks; flow creates vortices.

| # | Task | Status |
|---|------|--------|
| 1.1 | `rules/coupling.py` – binding, decay, coherence synchronisation | ✅ |
| 1.2 | `rules/flow.py` – gradient flow, damping, advective transport, curl | ✅ |
| 1.3 | `analysis/attractors.py` – persistence, clusters, phase-transition indicator | ✅ |
| 1.4 | Numba-JIT for Laplace kernel (optional, transparent fallback) | ✅ |
| 1.5 | Streamlit live dashboard (`visualization/dashboard.py`) | ✅ |
| 1.6 | Tests for coupling, flow, attractors (15+ new tests) | ✅ |
| 1.7 | GitHub setup, full documentation, roadmap | ✅ |
| 1.8 | ADR-0002: coupling + flow architecture decision | ✅ |
| 1.9 | `examples/run_analysis.py` – attractors + cluster analysis | ✅ |

---

## Epic 2 – Trace Reading Engine (Analysis Layer) ✅

**Goal:** The system can read patterns, reconstruct the past, hypothesise the future.  
*(Workbook ch. 11–12)*

| # | Task | Status |
|---|------|--------|
| 2.1 | `analysis/morphology.py` – boundary complexity, holes, filaments | ✅ |
| 2.2 | `analysis/mutual_information.py` – MI between fields and regions | ✅ |
| 2.3 | `analysis/trace_reading.py` – trace reading engine (JSON output) | ✅ |
| 2.4 | `interpretation/regime_classifier.py` – 8 regime types, confidence | ✅ |
| 2.5 | `interpretation/narratives.py` – language interpretation, past/future | ✅ |
| 2.6 | Dashboard extension: trace reading, regime labels, confidence | ✅ |
| 2.7 | Tests for all analysis modules (26 new tests) | ✅ |
| 2.8 | Connected-component tracking over time | 📋 |

---

## Epic 3 – Meta-Rules + Rule Evolution ✅

**Goal:** Local rule profiles emerge, vary and self-select.  
*(Workbook ch. 9)*

| # | Task | Status |
|---|------|--------|
| 3.1 | `rules/meta_rules.py` – local rule profile per cell (rule genome) | ✅ |
| 3.2 | Mutation: rule parameter variation with configurable rate | ✅ |
| 3.3 | Selection: coherence × (1 − local energy variance) as fitness proxy | ✅ |
| 3.4 | Retention: successful rule profiles backed up in the memory field | ✅ |
| 3.5 | Parameter candidate tracking via `analysis/novelty.py` | ✅ |
| 3.6 | `analysis/novelty.py` – BehaviorVector, NoveltyTracker, genome_diversity | ✅ |
| 3.7 | Tests for all Epic 3 modules (32 tests, 110 total) | ✅ |
| 3.8 | ADR-0003: meta-rule evolution design | ✅ |

---

## Epic 4 – Particle-Field Hybrid (Phase 3) ✅

**Goal:** Particles move through fields; active matter, swarms, proto-cellular dynamics.  
*(Workbook ch. 10.3, 13.1)*

| # | Task | Status |
|---|------|--------|
| 4.1 | `core/particles.py` – ParticleSystem (vectorised, NumPy arrays) | ✅ |
| 4.2 | Field-to-particle coupling: gradient, flow drag, reactivity boost | ✅ |
| 4.3 | Particle-to-field coupling: energy, matter, coupling, information | ✅ |
| 4.4 | Collision + aggregation (O(N²), mass-weighted) | ✅ |
| 4.5 | `analysis/compartments.py` – field + particle compartments, proto-life score | ✅ |
| 4.6 | Dashboard Tab 3: particle heatmap, density map, compartment table, genome | ✅ |

---

## Epic 5 – Graph / Hypergraph Mode (Phase 4) ✅

**Goal:** Space emerges from relations; Wolfram-style rewriting experiments; emergent geometry.  
*(Workbook ch. 10.4, 14)*

| # | Task | Status |
|---|------|--------|
| 5.1 | `core/graph_state.py` – GraphState with NetworkX (small_world/scale_free/random/grid) | ✅ |
| 5.2 | Hypergraph rewriting engine (active nodes form new edges) | ✅ |
| 5.3 | Emergent distance metric (weighted path length, Dijkstra) | ✅ |
| 5.4 | Dashboard Tab 5: graph visualisation + distance matrix + topology comparison | ✅ |
| 5.5 | ADR-0005: relational geometry | ✅ |

---

## Epic 6 – Multiscale Model + Performance (Phase 5) ✅

**Goal:** Micro-meso-macro coupling; GPU acceleration for large grids.  
*(Workbook ch. 10.5, 16.2)*

| # | Task | Status |
|---|------|--------|
| 6.1 | Taichi/JAX backend | 📋 (deferred – focus on functionality) |
| 6.2 | `core/multiscale.py` – MesoLayer (cluster entities + tracker) | ✅ |
| 6.3 | `core/multiscale.py` – MacroLayer (attractor trajectory, transitions) | ✅ |
| 6.4 | MultiscaleController + dashboard integration (Tab 4) | ✅ |
| 6.5 | Benchmark suite (`examples/benchmark_10k.py`) | ✅ |

---

## Epic 7 – Experiment Framework + Scientific Infrastructure ✅

**Goal:** Reproducible experiments, tracking, versioning, publication preparation.  
*(Workbook ch. 17–18)*

| # | Task | Status |
|---|------|--------|
| 7.1 | `experiments/runner.py` – experiment runner (config sweep, CSV output) | ✅ |
| 7.2 | `experiments/configs.py` – 8 predefined experiment configs | ✅ |
| 7.3 | Git commit hash in experiment output | ✅ |
| 7.4 | MLflow / W&B integration | 📋 |
| 7.5 | DVC for data versioning | 📋 |
| 7.6 | FastAPI endpoints | 📋 |
| 7.7 | Notebook templates | 📋 |

---

## Epic 8 – Interpretation + Consciousness Research ✅

**Goal:** Careful, measurable markers for proto-life, intelligence and consciousness indicators.  
*(Workbook ch. 13)*

| # | Task | Status |
|---|------|--------|
| 8.1 | `interpretation/consciousness.py` – Φ-Proxy (IIT), Active Inference, Proto-Life (6 criteria), Global Workspace | ✅ |
| 8.2 | `ConsciousnessAnalyzer` – live marker computation + history | ✅ |
| 8.3 | Dashboard Tab 4: live markers + 3 depth levels + glossary | ✅ |
| 8.4 | Learning sources (books, links, podcasts, demos) per depth level | ✅ |
| 8.5 | Scientific disclaimers in all modules (docstrings + dashboard warnings) | ✅ |

---

## Epic 9 – Experiment Presets & Simulation Gallery ✅

**Goal:** Clickable, reproducible simulation presets with rich metadata, dashboard gallery and CLI runner.

| # | Task | Status |
|---|------|--------|
| 9.1 | `ExperimentPreset` and `ParticleSettings` dataclasses | ✅ |
| 9.2 | Preset registry (`PRESETS` dict) with helpers | ✅ |
| 9.3 | Stigmergy / Ant Trails preset | ✅ |
| 9.4 | Boids Field Approximation preset (experimental) | ✅ |
| 9.5 | Tree Growth / Branching Morphogenesis preset | ✅ |
| 9.6 | Reaction-Diffusion / Turing-like Patterns preset | ✅ |
| 9.7 | Excitable Media / Wave Propagation preset | ✅ |
| 9.8 | Trace Reading / Fossil Field preset | ✅ |
| 9.9 | Autopoiesis / Membrane Formation preset | ✅ |
| 9.10 | Ecosystem Patch Dynamics preset | ✅ |
| 9.11 | Dashboard preset selector (sidebar + gallery in Lernen tab) | ✅ |
| 9.12 | `examples/run_preset.py` CLI runner | ✅ |
| 9.13 | `docs/experiments/` documentation (index + 8 preset docs) | ✅ |
| 9.14 | `tests/test_presets.py` — 27 tests (registry, validity, determinism) | ✅ |

---

## Epic 10 – Initial Conditions & Pattern Seeds ✅

**Goal:** Let presets define starting conditions (seed points, gradients, bursts) for reproducible pattern types.

| # | Task | Status |
|---|------|--------|
| 10.1 | `InitialCondition` abstract base + `CompoundInitialCondition` + `+` operator | ✅ |
| 10.2 | `CenteredSeed` — high-energy spot at grid centre | ✅ |
| 10.3 | `BottomSeed` — root zone / nutrient band at bottom edge | ✅ |
| 10.4 | `TopSeed` — light / atmospheric input from top edge | ✅ |
| 10.5 | `TopDownEnergyGradient` — smooth gradient, top high → bottom low | ✅ |
| 10.6 | `BottomUpEnergyGradient` — smooth gradient, bottom high → top low | ✅ |
| 10.7 | `RadialBurst` — ring of high energy at configurable radius | ✅ |
| 10.8 | `LineSeed` — horizontal or vertical energy line | ✅ |
| 10.9 | `PointSeed` — spot at arbitrary (row, col) with wrap | ✅ |
| 10.10 | `RandomClusteredSeed` — N random circular energy blobs | ✅ |
| 10.11 | `SinusoidalDisturbance` — stripe-like sinusoidal overlay | ✅ |
| 10.12 | Named registry (`INITIAL_CONDITIONS`) + `get_initial_condition` helper | ✅ |
| 10.13 | `GridState.initialize(initial_condition=...)` — zero-breakage hook | ✅ |
| 10.14 | `ExperimentPreset.initial_condition` field; 4 presets updated | ✅ |
| 10.15 | Dashboard: IC selector in sidebar; preset IC applied on Apply & Reset | ✅ |
| 10.16 | `tests/test_initial_conditions.py` — 37 tests | ✅ |

---

## Epic 11 – Real Agent Layer ✅

**Goal:** True agent-based dynamics: heading, velocity, neighbour interaction, pheromone deposition.

| # | Task | Status |
|---|------|--------|
| 11.1 | `AgentConfig` dataclass with full parameter set | ✅ |
| 11.2 | `AgentSystem` — vectorized NumPy arrays: positions, heading, velocities, energy, age | ✅ |
| 11.3 | Spatial hashing bin map for O(N·k) neighbour search | ✅ |
| 11.4 | Toroidal distance neighbour search (radius + self-exclusion) | ✅ |
| 11.5 | `BoidsPolicy` — separation + alignment + cohesion (Reynolds 1987) | ✅ |
| 11.6 | `AntPolicy` — memory gradient following + random exploration + pheromone deposition | ✅ |
| 11.7 | Bilinear field sampling at continuous positions | ✅ |
| 11.8 | Field deposition (deposit\_to\_field, atomic add + clip) | ✅ |
| 11.9 | Field → agent coupling: flow drag | ✅ |
| 11.10 | Speed clamping + heading sync with velocity direction | ✅ |
| 11.11 | `stats()` dict: coherence, mean speed, heading std, mean age | ✅ |
| 11.12 | `step_agents()` public API matching `step_particles` pattern | ✅ |
| 11.13 | Session state integration in dashboard (init + reset + apply preset) | ✅ |
| 11.14 | Agent panel in Partikel tab: scatter + polar heading histogram | ✅ |
| 11.15 | New preset: `boids_agents` (Collective Behavior) | ✅ |
| 11.16 | New preset: `ant_trails_agents` (Collective Behavior) | ✅ |
| 11.17 | `tests/test_agents.py` — 30 tests | ✅ |

---

## Epic 12 – Morphogenesis & Growth Systems ✅

**Goal:** Branching, skeleton extraction, fractal metrics, growth front analysis.

| # | Task | Status |
|---|------|--------|
| 12.1 | `extract_skeleton` — medial-axis approximation via iterative thinning | ✅ |
| 12.2 | `branch_count` — skeleton cells with ≥ 3 neighbours | ✅ |
| 12.3 | `tip_count` — skeleton endpoints (1 neighbour) | ✅ |
| 12.4 | `fractal_dimension` — box-counting estimate | ✅ |
| 12.5 | `analyse_growth_front` — front area, energy, directionality vector | ✅ |
| 12.6 | `GrowthFrontMetrics` dataclass | ✅ |
| 12.7 | `MorphogenesisResult` dataclass (composite) | ✅ |
| 12.8 | `analyse_morphogenesis` — single entry-point for all metrics | ✅ |
| 12.9 | Dashboard: Morphogenese panel in 🧭 Spurenlesen tab | ✅ |
| 12.10 | `mycelium_network` preset (Pattern Formation) | ✅ |
| 12.11 | `river_network` preset (Pattern Formation) | ✅ |
| 12.12 | `tests/test_morphogenesis.py` — 38 tests | ✅ |

---

## Epic 13 – Trace Reading Metrics ✅

**Goal:** Quantitative trace inference: persistence, directionality, autocorrelation, event reconstruction.

| # | Task | Status |
|---|------|--------|
| 13.1 | `memory_persistence` — Jaccard similarity of active region | ✅ |
| 13.2 | `spatial_autocorrelation` — Moran's I (convolution approximation) | ✅ |
| 13.3 | `flow_directionality` — anisotropy index + mean flow angle | ✅ |
| 13.4 | `MemoryEntropyTracker` — entropy time series + trend slope | ✅ |
| 13.5 | `ClusterLifetimeTracker` — birth/death tracking via centroid proximity | ✅ |
| 13.6 | `reconstruct_events` — detect newly activated regions per tick | ✅ |
| 13.7 | `wavefront_speed` — centroid displacement of excitable front | ✅ |
| 13.8 | `TraceMetricsSnapshot` + `compute_trace_metrics` composite entry-point | ✅ |
| 13.9 | `TraceReport.trace_metrics` field + `read_traces` wired with prev fields | ✅ |
| 13.10 | Dashboard: Spur-Metriken panel in Spurenlesen tab (12 live metrics + entropy chart) | ✅ |
| 13.11 | Session state: entropy/lifetime trackers + prev field storage | ✅ |
| 13.12 | `tests/test_trace_metrics.py` — 50 tests | ✅ |

---

## Epic 14 — Interactive Learning Layer ✅

**Goal:** Learning modules, concept library, resource registry, dashboard Learning Mode.

| # | Task | Status |
|---|------|--------|
| 14.1 | `LearningResource` dataclass + RESOURCES registry (21 resources) | ✅ |
| 14.2 | `ConceptNote` dataclass + CONCEPTS registry (13 concepts) | ✅ |
| 14.3 | `ParameterLearningNote` + `GuidedExperiment` + `LearningModule` dataclasses | ✅ |
| 14.4 | LEARNING_MODULES registry with 8 modules linked to existing presets | ✅ |
| 14.5 | All modules reference valid preset IDs, SimConfig fields, concept IDs, resource IDs | ✅ |
| 14.6 | Dashboard: Learning Mode panel in Tab 4 (5 inner tabs) | ✅ |
| 14.7 | Dashboard: What am I seeing? — intuition, concepts, observation questions | ✅ |
| 14.8 | Dashboard: Parameters — per-parameter expanders with math role and experiments | ✅ |
| 14.9 | Dashboard: Mathematics — mathematical background + next steps | ✅ |
| 14.10 | Dashboard: Guided Experiments — numbered steps with hints | ✅ |
| 14.11 | Dashboard: Research Trail — filterable by level + type | ✅ |
| 14.12 | `active_preset_id` session state wired to Learning Mode | ✅ |
| 14.13 | `tests/test_learning.py` — 44 tests | ✅ |
| 14.14 | `docs/learning/` — index.md, concepts.md, parameter-guide.md, research-trail.md, guided-experiments.md | ✅ |

---

## Epic 15 — Concept Library & Research Trail 📋

**Goal:** Standalone concept browser, extended resource registry, resource filtering UI.

| # | Task | Status |
|---|------|--------|
| 15.1 | Extend CONCEPTS to 20+ concepts | 📋 |
| 15.2 | Extend RESOURCES to 40+ entries | 📋 |
| 15.3 | Concept browser tab or panel in dashboard | 📋 |
| 15.4 | Resource search (full text across title + description + tags) | 📋 |
| 15.5 | Cross-link concepts to live metrics (e.g. click Moran's I → concept) | 📋 |

---

## Epic 16 — Guided Experiments & Parameter Sensitivity 📋

**Goal:** Parameter sensitivity hints, compare-runs scaffolding, experiment journal.

| # | Task | Status |
|---|------|--------|
| 16.1 | Parameter sensitivity hints (show effect when slider changes) | 📋 |
| 16.2 | Add guided experiments for remaining presets | 📋 |
| 16.3 | Experiment journal: save observation notes per run | 📋 |
| 16.4 | Compare-runs placeholder: side-by-side field snapshots | 📋 |

---

## Milestones

| Milestone | Epics | Goal |
|-----------|-------|------|
| **v0.1.0** | Epic 0 | First working prototype, all tests passing |
| **v0.2.0** | Epic 1 | All 8 parameters active, dashboard, attractors |
| **v0.3.0** | Epic 2 | Trace reading engine, regime classification |
| **v0.4.0** | Epic 3 | Rule evolution, meta-rules |
| **v0.5.0** | Epic 4 | Particle-field hybrid |
| **v1.0.0** | Epic 5–6 | Graph mode, multiscale model (meso/macro) |
| **v2.0.0** | Epic 7–8 | Experiment framework, consciousness markers, learning dashboard |
| **v2.1.0** | Epic 9 | Simulation gallery, 8 presets, dashboard gallery, CLI runner |
| **v2.2.0** | Epic 10 | Initial conditions: 10 condition types, preset integration, dashboard selector |
| **v2.3.0** | Epic 11 | Real agent layer: Boids + Ant policies, spatial hashing, field coupling, 2 new presets |
| **v2.4.0** | Epic 12 | Morphogenesis: skeleton, fractal dim, growth front, 2 new presets (mycelium, river) |
| **v2.5.0** | Epic 13 | Trace metrics: Moran's I, wavefront speed, cluster lifetimes, entropy tracker, event reconstruction |
| **v2.6.0** | Epic 14 | Interactive Learning Layer: LearningModules, concept library, resource registry, dashboard Learning Mode |
| **v3.0.0** | Epics 15–16 | Concept browser, parameter sensitivity hints, experiment journal |

---

## Scientific Guiding Questions (Workbook ch. 4)

These questions guide the experiment design in each epic:

1. What minimal rules reliably generate complex persistent patterns?
2. When does noise become structure-forming rather than destructive?
3. When do boundaries, membranes and inside/outside distinctions emerge?
4. When is a pattern self-maintaining (proto-life-like)?
5. Can geometry-like spaces emerge from graph relations?
6. Which markers correlate with consciousness theories (IIT, GWT, Active Inference)?

> **Caution:** All interpretations are hypotheses and models.  
> We prove no theory of everything. We build an open research instrument.
