# Changelog

Alle wichtigen Änderungen werden hier dokumentiert.
Format: [Semantic Versioning](https://semver.org/).

---

## [0.5.0] – 2026-05-08

### Hinzugefügt (Epic 4 – Partikel-Feld-Hybrid)

- `core/particles.py`: `ParticleConfig` + `ParticleSystem` (vektorisiert):
  - Partikel als NumPy-Arrays `(N, 2)` / `(N,)` (positions, velocities,
    energy, mass, active, age).
  - `apply_field_to_particles`: Gradient-Attraktion, Fluss-Drag, Energie-
    Absorption, Reaktivitäts-Boost via bilinearer Interpolation.
  - `apply_particles_to_field`: Energie, Materie, Kopplung, Information
    Deposition via `np.add.at`.
  - `apply_collisions`: O(N²) Aggregations-Fusion mit Masse-gewichteter
    Position, Impuls und Energie.
  - `step_particles`: vollständiger Partikel-Tick.
  - `summary`: kompakte Statistik inkl. Proto-Kompartiment-Zählung.
- `analysis/compartments.py`:
  - `detect_compartments`: feldbasierte Kompartiment-Erkennung (SciPy
    `label` + Compactness + heuristischer Proto-Leben-Score).
  - `particle_compartments`: partikelbasierte Dichtekarte + Aggregat-Marker.
  - `CompartmentResult` / `Compartment` Dataclasses.
- Dashboard `visualization/dashboard.py` v0.5.0:
  - Tab 3 ⚗️ Partikel: Live-Scatter über Energie-Heatmap, Dichtekarte mit
    Aggregat-Markern (★), Kompartiment-Tabelle, Regelgenom-Heatmap.
  - Sidebar: Partikel-Konfiguration (Anzahl, Attraktion, Drag, Dämpfung,
    Kollisionsradius, Ein/Aus-Toggle).
  - Partikel-Tick in Simulations-Loop integriert.
- `docs/design-decisions/ADR-0004-particle-field-hybrid.md`.
- `tests/test_epic4.py`: 27 Tests (137 gesamt, alle grün).

### Wissenschaftliche Vorsicht

Partikel-Dynamik ist eine vereinfachte Abstraktion ohne Impuls-/Energie-
erhaltung. Proto-Leben-Scores sind strukturelle Proxies, kein Nachweis
biologischer Prozesse. Emergente Aggregate sind Explorations-Phänomene.

---

## [0.4.0] – 2026-05-08

### Hinzugefügt (Epic 3 – Meta-Regeln + Regel-Evolution)

- `core/state.py`: Zwei neue Genome-Felder in `GridState`:
  - `genome_strength`   – lokale Reaktionsstärke pro Zelle (float32 Array)
  - `genome_threshold`  – lokaler Energie-Schwellwert pro Zelle (float32 Array)
  - Initialisierung mit leichter Variation um globale Config-Werte.
  - `genome_dict()` Hilfsmethode. `clip_all()` clippt jetzt auch Genome.
- `core/state.py`: `SimConfig` erhält fünf neue Meta-Regel-Parameter:
  `meta_mutation_rate`, `meta_mutation_strength`, `meta_selection_rate`,
  `meta_retention_threshold`, `meta_enabled`.
- `rules/meta_rules.py`: `apply_meta_rules` mit drei Schritten pro Tick:
  - **Mutation**: zufällige Genome-Variation mit konfigurierbarer Rate/Stärke.
  - **Selektion**: lokale 3×3-Nachbarschaftsselektion (fittere Profile breiten sich aus).
  - **Retention**: Gedächtnisfeld-Verstärkung durch erfolgreiche Profile.
  - Fitness = `coherence × (1 - lokale_energievarianz)` (heuristischer Proxy).
- `rules/reaction.py`: Regel 1 nutzt jetzt `genome_threshold` und
  `genome_strength` statt globaler Config-Konstanten → räumlich heterogenes
  Reaktionsverhalten.
- `core/tick.py`: Meta-Regeln als Schritt 7 im Tick-Loop integriert.
- `analysis/novelty.py`:
  - `BehaviorVector` – komprimierter Zustandsvektor für Novelty-Vergleiche.
  - `NoveltyTracker` – Archiv-basierte k-NN Novelty-Metrik.
  - `genome_diversity` – räumliche Diversität der Genome-Verteilung.
  - `genome_entropy` – Shannon-Entropie der Genome-Wert-Verteilung.
- `docs/design-decisions/ADR-0003-meta-rule-evolution.md`: Architektur-
  Entscheidung mit Begründung, Alternativen und wissenschaftlichem Vorbehalt.
- `tests/test_epic3.py`: 32 neue Tests (110 gesamt, alle grün).

### Wissenschaftliche Vorsicht

Regelgenom-Evolution ist eine abstrakte Abstraktion, kein Modell realer
Genetik. Fitness-Proxies sind heuristisch. Emergente Differenzierung ist
ein Explorationsphänomen, keine biologische Aussage.

---

## [0.3.1] – 2026-05-08

### Geändert – Dashboard (Epic 2.6)

- `visualization/dashboard.py` komplett erweitert auf **v0.3.1**:
  - **Tab 1 🔬 Simulation**: Live-Heatmap (mit mean/std im Titel), RGB-Composite,
    Entropie-Zeitreihe, Persistenz-Balken, Cluster-Statistiken, Phasenindikator.
  - **Tab 2 🧭 Spurenlesen**: Vollständige Spurenlese-Integration aus Epic 2:
    - Regime-Banner (Icon + Name + Konfidenz) dauerhaft über den Tabs sichtbar.
    - Manueller "Spurenanalyse jetzt ausführen"-Button + automatischer Trigger
      alle `trace_interval` Ticks.
    - **Regime-Klassifikation**: Primär/Sekundär/Konfidenz + Beschreibung +
      aufklappbare Evidence-Werte.
    - **Narrativ**: Metaphorische Interpretationsfamilien, wahrscheinliche
      Vergangenheit, mögliche Zukunftspfade, eingebetteter Wissenschafts-
      vorbehalt (3-spaltig).
    - **Morphologie**: Komponenten, Löcher, Euler-Zahl, Randkomplexität,
      Elongation, Compactness + binäres Schwellwert-Bild.
    - **MI-Matrix-Heatmap**: Normalisierte Mutual Information als Farbraster
      mit eingetragenen Zahlenwerten.
    - **Feldstatistik-Tabelle**: mean, std, min, max, aktive Fraktion.
    - **Phasenübergangs-Indikator**: Suszeptibilität + Energie-Varianz.
    - **JSON-Export**: Vollständiger TraceReport aufklappbar.
  - Sidebar: neue Slider für `reactivity_recovery`, `reactivity_rest`,
    `matter_erosion_rate`, `matter_deposition_rate`, `trace_interval`,
    `show_mi_heatmap`, `show_morphology`.

---

## [0.3.0] – 2026-05-08

### Hinzugefügt (Epic 2 – Spurenlese-Engine)

- `analysis/morphology.py`: `compute_morphology` — Randkomplexität, Lochigkeit,
  Euler-Zahl, Elongation, Compactness für 2-D-Felder.
- `analysis/mutual_information.py`: `field_mi`, `mi_matrix`, `local_mi` —
  normalisierte Mutual Information zwischen Feldern (Histogramm-Methode).
- `analysis/trace_reading.py`: `read_traces` + `TraceReport` — vollständige
  Spurenlese-Engine, integriert alle Analyse-Module, JSON-exportierbar.
- `interpretation/regime_classifier.py`: `classify_regime` + `RegimeResult` —
  8 heuristische Regime-Typen (QUIESCENT, DIFFUSE, CLUSTERED, VORTEX,
  COHERENT, FILAMENTARY, CRITICAL, COMPLEX) mit Konfidenz-Score.
- `interpretation/narratives.py`: `build_narrative` + `Narrative` —
  sprachliche Interpretation: Metaphern, wahrscheinliche Vergangenheit,
  mögliche Zukunft, wissenschaftlicher Vorsichtshinweis.
- `tests/test_epic2.py`: 26 neue Tests (78 gesamt, alle grün).

### Wissenschaftliche Vorsicht

Alle Regime-Labels, Interpretationen und Narrative sind Lesarten,
keine Wahrheitsetiketten. Jedes Ergebnis enthält explizite Vorsichtsformulierungen.

---

## [0.2.1] – 2026-05-08

### Geändert / Gefixt

- `rules/reaction.py`: `reactivity`-Dynamik (EMA-Erholung + Verbrauch bei Aktivierung) und
  `matter`-Dynamik (Erosion durch Fluss, Ablagerung in ruhigen Regionen) implementiert.
  Alle 8 Grundparameter der Arbeitsmappe sind jetzt **vollständig dynamisch**.
- `rules/coupling.py`: Basalzerfall-Term ergänzt, verhindert Sättigung bei homogenen Feldern.
- `rules/reaction.py`: Ablagerungsformel auf `deposition * coupling * (1 - matter)` geändert,
  verhindert Sättigung von `matter` bei 1.0.
- `core/state.py`: Neue Default-Parameter `reactivity_recovery=0.98`, `reactivity_rest=0.5`,
  `matter_erosion_rate=0.02`, `matter_deposition_rate=0.005`.
- `examples/run_analysis.py`: Neues Analyse-Skript mit Persistenz-, Cluster-, Phasen-
  und Feld-Summary-Output (5 CSVs + PNGs).

### Tests

- 4 neue Tests: `test_reactivity_recovers_toward_rest`, `test_reactivity_consumed_by_activation`,
  `test_matter_erodes_with_flow`, `test_matter_deposits_in_calm_regions` (52 gesamt).

### Gleichgewichtswerte (Seed 42, 300 Ticks, 64×64)

```
energy=0.398  matter=0.563  information=0.199  coupling=0.480
reactivity=0.500  memory=0.119  coherence=0.150  flow≈0.003
```

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
