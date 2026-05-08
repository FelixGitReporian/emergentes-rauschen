# Changelog

Alle wichtigen Änderungen werden hier dokumentiert.
Format: [Semantic Versioning](https://semver.org/).

---

## [0.2.0] – 2026-05-08

### Hinzugefügt

- `src/emergent_noise/rules/coupling.py`: Bindung, Zerfall, Kohärenz-Synchronisation.
- `src/emergent_noise/rules/flow.py`: Gradienten-Fluss, Dämpfung, Curl-Wirbel, advektiver Transport.
- `src/emergent_noise/analysis/attractors.py`: `PersistenceTracker`, `find_clusters`, `compute_phase_indicator`, `field_summary`.
- `src/emergent_noise/visualization/dashboard.py`: Streamlit Live-Dashboard mit Sidebar-Config, Heatmap, RGB-Composite, Entropie-Zeitreihe, Cluster-Analyse.
- Numba-JIT optional in `rules/diffusion.py` (transparenter Fallback auf NumPy).
- 7 neue Parameter in `SimConfig` (`coupling_*`, `flow_*`).
- 15 neue pytest-Tests (48 gesamt).
- `.github/`: CI-Workflow, Issue-Templates (Bug, Feature, Experiment), PR-Template.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- `ROADMAP.md` mit 8 Epics nach Arbeitsmappe.
- `docs/design-decisions/ADR-0002-coupling-flow-architecture.md`.

### Geändert

- `core/tick.py`: Regelreihenfolge auf 8 Schritte erweitert (coupling + flow).
- `README.md`: Vollständig überarbeitet für GitHub-Kollaboration.

### Wissenschaftliche Vorsicht

Alle neuen Felder (coupling, flow) sind jetzt aktiv — alle 8 Grundparameter  
der Arbeitsmappe sind in der Simulation lebendig. Interpretationen bleiben  
explorativ und hypothetisch.

---

## [0.1.0] – 2026-05-08

### Hinzugefügt

- `pyproject.toml` mit hatchling build-backend, Abhängigkeiten und pytest-Konfiguration.
- `src/emergent_noise/core/state.py`: `SimConfig` (Pydantic) und `GridState` (dataclass)
  mit 8 Grundparametern + flow_x/flow_y.
- `src/emergent_noise/core/tick.py`: `TickLoop` mit dokumentierter, deterministischer
  Regelreihenfolge; Callback-Unterstützung.
- `src/emergent_noise/rules/diffusion.py`: 5-Punkt-Laplace-Diffusion für energy + information.
- `src/emergent_noise/rules/reaction.py`: Aktivierungs- und Zerfallsreaktion.
- `src/emergent_noise/rules/memory.py`: Memory decay + imprint.
- `src/emergent_noise/noise/structured_noise.py`: Sinus-Superposition mit Seed + Tick.
- `src/emergent_noise/analysis/entropy.py`: normalisierte Shannon-Entropie.
- `src/emergent_noise/visualization/render.py`: Panel-PNG (9 Felder) + RGB-Composite.
- `examples/run_500.py`: Beispiellauf mit CLI-Argumenten, PNG-Ausgabe, Entropie-CSV.
- `tests/`: 30+ pytest-Tests für Init, Deterministik, Wertebereiche, Regeln, Rauschen, Entropie.
- `docs/design-decisions/ADR-0001-start-with-2d-grid.md`.

### Wissenschaftliche Vorsicht

Alle Interpretationen in dieser Version sind explorativ. Keine Behauptungen über
Bewusstsein, echte Physik oder Leben.
