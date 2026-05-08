# Roadmap – Emergentes Rauschen

> Basiert auf der [Professionellen Arbeitsmappe](emergentes-rauschen-professionelle-arbeitsmappe.md) (v2.0).  
> Jedes Epic entspricht einer Phase der Simulationsarchitektur (Abschnitte 10–16 der Arbeitsmappe).  
> Status: ✅ Done · 🔄 In Progress · 📋 Planned · 💡 Research

---

## Epic 0 – Fundament (Phase 1: 2-D-Grid) ✅

**Ziel:** Minimaler, deterministischer, testgetriebener Prototyp.

| # | Aufgabe | Status |
|---|---------|--------|
| 0.1 | Projektstruktur, `pyproject.toml`, Module-Gerüst | ✅ |
| 0.2 | `core/state.py` – `GridState` + `SimConfig` | ✅ |
| 0.3 | `core/tick.py` – deterministischer Tick-Loop | ✅ |
| 0.4 | `rules/diffusion.py` – 5-Punkt-Laplace (energy, information) | ✅ |
| 0.5 | `rules/reaction.py` – Aktivierungs- + Zerfallsregel | ✅ |
| 0.6 | `rules/memory.py` – EMA-Gedächtnis (Zerfall + Imprint) | ✅ |
| 0.7 | `noise/structured_noise.py` – Sinus-Superposition, Seed+Tick | ✅ |
| 0.8 | `analysis/entropy.py` – normalisierte Shannon-Entropie | ✅ |
| 0.9 | `visualization/render.py` – Panel-PNG + RGB-Composite | ✅ |
| 0.10 | 33 pytest-Tests (Init, Deterministik, Wertebereiche) | ✅ |
| 0.11 | `examples/run_500.py` + Entropie-CSV | ✅ |

---

## Epic 1 – Relationsfelder + Vektordynamik 🔄

**Ziel:** Alle 8 Grundparameter aktiv; Kopplung erzeugt Netzwerke; Fluss erzeugt Wirbel.

| # | Aufgabe | Status |
|---|---------|--------|
| 1.1 | `rules/coupling.py` – Bindung, Zerfall, Kohärenz-Synchronisation | ✅ |
| 1.2 | `rules/flow.py` – Gradienten-Fluss, Dämpfung, Advektions-Transport, Curl | ✅ |
| 1.3 | `analysis/attractors.py` – Persistenz, Cluster, Phasenübergangs-Indikator | ✅ |
| 1.4 | Numba-JIT für Laplace-Kern (optional, transparenter Fallback) | ✅ |
| 1.5 | Streamlit Live-Dashboard (`visualization/dashboard.py`) | ✅ |
| 1.6 | Tests für Kopplung, Fluss, Attraktoren (15+ neue Tests) | ✅ |
| 1.7 | GitHub-Setup, vollständige Dokumentation, Roadmap | 🔄 |
| 1.8 | ADR-0002: Kopplung + Fluss Architekturentscheidung | 📋 |
| 1.9 | `examples/run_analysis.py` – Attraktoren + Cluster-Analyse nach Lauf | 📋 |

---

## Epic 2 – Spurenlese-Engine (Analyse-Layer)

**Ziel:** Das System kann Muster lesen, Vergangenheit rekonstruieren, Zukunft hypothetisieren.  
*(Arbeitsmappe Kap. 11–12)*

| # | Aufgabe | Status |
|---|---------|--------|
| 2.1 | `analysis/morphology.py` – Randkomplexität, Lochigkeit, Filamente | ✅ |
| 2.2 | `analysis/mutual_information.py` – MI zwischen Feldern und Regionen | ✅ |
| 2.3 | `analysis/trace_reading.py` – Spurenlese-Engine (JSON-Output) | ✅ |
| 2.4 | `interpretation/regime_classifier.py` – 8 Regime-Typen, Konfidenz | ✅ |
| 2.5 | `interpretation/narratives.py` – Sprachliche Interpretation, Vergangenheit/Zukunft | ✅ |
| 2.6 | Dashboard-Erweiterung: Spurenlesen, Regime-Labels, Konfidenz | 📋 |
| 2.7 | Tests für alle Analyse-Module (26 neue Tests) | ✅ |
| 2.8 | Connected-Component-Tracking über Zeit | 📋 |

---

## Epic 3 – Meta-Regeln + Regel-Evolution

**Ziel:** Lokale Regelprofile entstehen, variieren und selektieren sich.  
*(Arbeitsmappe Kap. 9)*

| # | Aufgabe | Status |
|---|---------|--------|
| 3.1 | `rules/meta_rules.py` – lokales Regelprofil pro Zelle (Rule-Genome) | 📋 |
| 3.2 | Mutation: zufällige Regelparameter-Variation mit konfigurierbarer Rate | 📋 |
| 3.3 | Selektion: Persistenz + Kohärenz als Fitness-Proxy | 📋 |
| 3.4 | Retention: erfolgreiche Regelprofile im Gedächtnisfeld sichern | 📋 |
| 3.5 | Parameter-Kandidaten-Tracking: abgeleitete Parameter beobachten | 📋 |
| 3.6 | `analysis/novelty.py` – Neuheitsmetrik (Behavioral Diversity) | 📋 |
| 3.7 | Tests + Experiment-Runner für Regel-Evolution | 📋 |
| 3.8 | ADR-0003: Regel-Evolution Design | 📋 |

---

## Epic 4 – Partikel-Feld-Hybrid (Phase 3)

**Ziel:** Partikel bewegen sich durch Felder; aktive Materie, Schwärme, proto-zelluläre Dynamik.  
*(Arbeitsmappe Kap. 10.3, 13.1)*

| # | Aufgabe | Status |
|---|---------|--------|
| 4.1 | `core/particles.py` – Partikel-Klasse mit Position, Geschwindigkeit, Zustand | 📋 |
| 4.2 | Feld-zu-Partikel-Kopplung: Felder beeinflussen Partikel | 📋 |
| 4.3 | Partikel-zu-Feld-Kopplung: Partikel verändern Felder (Quellen/Senken) | 📋 |
| 4.4 | Kollision + Aggregation | 📋 |
| 4.5 | Proto-Kompartiment-Erkennung | 📋 |
| 4.6 | Visualisierung: Partikel über Feld-Heatmap | 📋 |

---

## Epic 5 – Graph-/Hypergraph-Modus (Phase 4)

**Ziel:** Raum entsteht aus Relationen; Wolfram-artige Rewriting-Experimente; emergente Geometrie.  
*(Arbeitsmappe Kap. 10.4, 14)*

| # | Aufgabe | Status |
|---|---------|--------|
| 5.1 | `core/graph_state.py` – GraphState mit NetworkX | 📋 |
| 5.2 | Hypergraph-Rewriting-Engine | 📋 |
| 5.3 | Metrik: emergente Distanz aus Graphrelationen | 📋 |
| 5.4 | Vergleich Grid-Modell vs. Graphmodell für gleiche Anfangsbedingungen | 📋 |
| 5.5 | ADR-0004: Relationale Geometrie | 📋 |

---

## Epic 6 – Mehrskalenmodell + Performance (Phase 5)

**Ziel:** Mikro-Meso-Makro-Kopplung; GPU-Beschleunigung für große Grids.  
*(Arbeitsmappe Kap. 10.5, 16.2)*

| # | Aufgabe | Status |
|---|---------|--------|
| 6.1 | Taichi-Backend für Grid-Simulation (Opt-in) | 📋 |
| 6.2 | JAX-Backend für vektorisierte Simulationen | 📋 |
| 6.3 | Meso-Layer: Cluster-Dynamiken als eigenständige Entitäten | 📋 |
| 6.4 | Makro-Layer: Attraktoren, Regime-Übergänge, Landschaften | 📋 |
| 6.5 | Benchmark-Suite | 📋 |

---

## Epic 7 – Experiment-Framework + Wissenschaftliche Infrastruktur

**Ziel:** Reproduzierbare Experimente, Tracking, Versionierung, Publikationsvorbereitung.  
*(Arbeitsmappe Kap. 17–18)*

| # | Aufgabe | Status |
|---|---------|--------|
| 7.1 | `experiments/runner.py` – Experiment-Runner mit Config-Sweep | 📋 |
| 7.2 | `experiments/configs.py` – Vordefinierte Experiment-Configs | 📋 |
| 7.3 | MLflow- oder W&B-Integration | 📋 |
| 7.4 | DVC für Datenversionierung | 📋 |
| 7.5 | Git-Commit-Hash in Experiment-Output | 📋 |
| 7.6 | FastAPI-Endpunkte für Fernsteuerung von Läufen | 📋 |
| 7.7 | Notebook-Templates für Analyse | 📋 |

---

## Epic 8 – Interpretations- + Bewusstsein-Forschungsstrang

**Ziel:** Vorsichtige, messbare Marker für Proto-Leben, Intelligenz, Bewusstsein-Indikatoren.  
*(Arbeitsmappe Kap. 13)*

| # | Aufgabe | Status |
|---|---------|--------|
| 8.1 | Proto-Leben-Detektor: Grenz- + Kompartiment-Erkennung | 💡 |
| 8.2 | Integrated-Information-Näherung (Φ-Proxy) | 💡 |
| 8.3 | Active-Inference-Marker: prädiktive Schleifen messen | 💡 |
| 8.4 | Selbstmodellierungs-Indikator | 💡 |
| 8.5 | Ethik-Protokoll: Monitoring, Abschaltbarkeit, Sprach-Leitfaden | 💡 |

---

## Meilensteine

| Meilenstein | Epics | Ziel |
|---|---|---|
| **v0.1.0** | Epic 0 | Erster lauffähiger Prototyp, alle Tests grün |
| **v0.2.0** | Epic 1 | Alle 8 Parameter aktiv, Dashboard, Attraktoren |
| **v0.3.0** | Epic 2 | Spurenlese-Engine, Regime-Klassifikation |
| **v0.4.0** | Epic 3 | Regel-Evolution, Meta-Regeln |
| **v0.5.0** | Epic 4 | Partikel-Feld-Hybrid |
| **v1.0.0** | Epic 5–6 | Graph-Modus, Performance, Mehrskaligkeit |
| **v2.0.0** | Epic 7–8 | Vollständiges Forschungs-Framework |

---

## Wissenschaftliche Leitfragen (aus Arbeitsmappe Kap. 4)

Diese Fragen leiten das Experiment-Design in jedem Epic:

1. Welche minimalen Regeln erzeugen dauerhaft komplexe Muster?
2. Wann wird Rauschen strukturbildend statt destruktiv?
3. Wann entstehen Grenzen, Membranen, Innen/Außen?
4. Wann ist ein Muster selbsterhaltend (proto-lebensähnlich)?
5. Können geometrieähnliche Räume aus Graphrelationen entstehen?
6. Welche Marker korrelieren mit Bewusstseins-Theorien (IIT, GWT, Active Inference)?

> **Vorsicht:** Alle Interpretationen sind Hypothesen und Modelle.  
> Wir beweisen keine Theorie von allem. Wir bauen ein offenes Forschungsinstrument.
