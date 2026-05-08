# Roadmap – Emergentes Rauschen

> Based on the [Professional Workbook](emergentes-rauschen-professionelle-arbeitsmappe.md) (v2.0).  
> Each epic corresponds to a phase of the simulation architecture (workbook sections 10–16).  
> Status: ✅ Done · 🔄 In Progress · 📋 Planned · 💡 Research
>
> **Current: v2.1.0 — Epic 9 complete — 199 tests, all passing.**

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

## Epic 10 – Initial Conditions & Pattern Seeds 📋

**Goal:** Let presets define starting conditions (seed points, gradients, bursts) for reproducible pattern types.

| # | Task | Status |
|---|------|--------|
| 10.1 | `InitialCondition` abstraction | 📋 |
| 10.2 | Centered seed (single-point excitation) | 📋 |
| 10.3 | Bottom seed for tree/root growth | 📋 |
| 10.4 | Top-down energy gradient (light model) | 📋 |
| 10.5 | Radial burst event | 📋 |
| 10.6 | Moving disturbance event | 📋 |
| 10.7 | Line/path seed | 📋 |
| 10.8 | Random clustered seed | 📋 |
| 10.9 | Allow presets to define `initial_condition` | 📋 |
| 10.10 | Tests for deterministic initialization | 📋 |

---

## Epic 11 – Real Agent Layer 📋

**Goal:** True agent-based dynamics: heading, velocity, neighbour interaction, pheromone deposition.

| # | Task | Status |
|---|------|--------|
| 11.1 | `AgentState` with position, velocity, heading and memory | 📋 |
| 11.2 | Spatial hashing / grid binning for O(N) neighbour search | 📋 |
| 11.3 | Field sampling for agents | 📋 |
| 11.4 | Field deposition for agents (pheromone model) | 📋 |
| 11.5 | Boids separation rule | 📋 |
| 11.6 | Boids alignment rule | 📋 |
| 11.7 | Boids cohesion rule | 📋 |
| 11.8 | Pheromone-following agent policy | 📋 |
| 11.9 | Nest and food source abstraction | 📋 |
| 11.10 | Real Ant Trail experiment | 📋 |
| 11.11 | Real Boids experiment | 📋 |

---

## Epic 12 – Morphogenesis & Growth Systems 📋

**Goal:** Branching, skeleton extraction, fractal metrics, growth front analysis.

| # | Task | Status |
|---|------|--------|
| 12.1 | `GrowthFront` abstraction | 📋 |
| 12.2 | Branching probability rule | 📋 |
| 12.3 | Resource gradient following | 📋 |
| 12.4 | Memory stabilisation for grown structures | 📋 |
| 12.5 | Pruning / decay dynamics | 📋 |
| 12.6 | Branch skeleton extraction | 📋 |
| 12.7 | Branch count metric | 📋 |
| 12.8 | Fractal dimension estimate | 📋 |
| 12.9 | Tree-growth-specific visualization | 📋 |
| 12.10 | Mycelium-like preset | 📋 |
| 12.11 | River-network-like preset | 📋 |

---

## Epic 13 – Trace Reading Metrics 📋

**Goal:** Quantitative trace inference: persistence, directionality, autocorrelation, event reconstruction.

| # | Task | Status |
|---|------|--------|
| 13.1 | Memory persistence metric | 📋 |
| 13.2 | Spatial autocorrelation metric | 📋 |
| 13.3 | Directionality metric | 📋 |
| 13.4 | Entropy over time (memory field specific) | 📋 |
| 13.5 | Cluster lifetime tracking | 📋 |
| 13.6 | Event reconstruction placeholder | 📋 |
| 13.7 | Trace-reading report panel in dashboard | 📋 |
| 13.8 | Wavefront speed metric (for excitable media) | 📋 |

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
| **v3.0.0** | Epic 10–11 | Initial conditions + real agent layer |
| **v3.1.0** | Epic 12–13 | Morphogenesis metrics + trace reading metrics |

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
