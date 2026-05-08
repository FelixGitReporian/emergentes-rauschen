# ADR-0007: Bewusstseins-Marker + Lern-Dashboard (Epic 7–8)

**Status:** Accepted  
**Datum:** 2026-05-08  
**Bezug:** Arbeitsmappe Kap. 13 – Leben, Intelligenz, Bewusstsein

---

## Kontext

Epic 8 fordert vorsichtige, messbare Marker für Proto-Leben, Intelligenz
und Bewusstseins-Theorien. Parallel soll das Dashboard als Lernumgebung
für Complex Systems Science und Artificial Life dienen.

---

## Entscheidung

### Bewusstseins-Marker (`interpretation/consciousness.py`)

Vier Marker-Typen, alle als Proxies implementiert:

| Marker | Theorie | Implementierung |
|--------|---------|----------------|
| Φ-Proxy | IIT (Tononi 2004) | coherence × (1 − local_var) × mi_proxy |
| Active Inference | Free-Energy (Friston 2010) | memory-energy Korrelation |
| Proto-Leben | Arbeitsmappe Kap. 13.1 | 6 Kriterien (je 1/6 Punkt) |
| Global Workspace | GWT (Baars/Dehaene) | Gini-Koeffizient der Information |

**Integrierter Score:** 0.3·Φ + 0.2·AI + 0.3·PL + 0.2·GW

**Wichtige Einschränkungen:**
- Echter IIT-Φ ist NP-schwer zu berechnen; dieser Proxy ist eine Heuristik.
- Active-Inference-Marker testet keine echten prädiktiven Schleifen.
- Global-Workspace-Score ≠ Bewusstseinsnachweis.
- Alle Marker dienen der Exploration, nicht der Verifikation von Theorien.

### Lern-Dashboard (Tab 4)

Drei Vertiefungsebenen:

| Ebene | Inhalt |
|-------|--------|
| 🟢 Einstieg | Zelluläre Automaten, Emergenz, Attraktoren; Bücher + Links |
| 🟡 Mittelstufe | IIT, Free-Energy, GWT, Assembly Theory; Primärquellen |
| 🔴 Forschungsfront | Offene Fragen, Experiment-Ideen, aktuelle Konferenzen |

Integrierte Quellen:
- Bücher: Mitchell (Complexity), Levy (ALife)
- Online: natureofcode.com, wolframscience.com, SFI Explorer
- Demos: Lenia, Avida, OpenWorm, Framsticks
- Podcasts: Complexity SFI, Sara Walker (Mindscape, Big Biology)
- Papers: Tononi 2004, Friston 2010, Walker & Davies 2013

### Experiment-Framework (`experiments/`)

- 7 vordefinierte Experimente mit wissenschaftlichen Fragen verknüpft.
- Reproduzierbarkeit: Git-Hash + Seed + Config in `experiment_meta.json`.
- CSV-Output: 15 Metriken pro Analyse-Tick.

---

## Wissenschaftliche Leitprinzip

> "Wir bauen ein offenes Forschungsinstrument, kein Orakel.
> Jede Metrik ist eine Lesart, keine Wahrheit."
> — Arbeitsmappe Kap. 4

Alle Bewusstseins-Marker tragen explizite Wissenschaftsvorbehalte in:
- Docstrings (`consciousness.py`)
- Dashboard-Warnungen (`st.warning`)
- Dieses ADR
