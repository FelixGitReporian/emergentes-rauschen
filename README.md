# Emergentes Rauschen

> **Eine offene Simulations- und Interpretationsmaschine für emergente Zustandsfelder.**

[![CI](https://github.com/FelixGitReporian/ermergentes-rauschen/actions/workflows/ci.yml/badge.svg)](https://github.com/FelixGitReporian/ermergentes-rauschen/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Was ist Emergentes Rauschen?

Dieses Projekt entwickelt kein klassisches Simulationsspiel und keine gewöhnliche Physik-Engine.
Es entwirft eine **offene Emergenzmaschine**: ein dynamisches, mehrschichtiges Zustandsfeld aus
acht Grundparametern:

| Parameter | Bedeutung |
|---|---|
| `energy` | Aktivierungspotenzial, Reaktionsfähigkeit |
| `matter` | Lokale Dichte, Trägheit, Substrat |
| `information` | Komprimierbare Ordnung, lokaler Mustergehalt |
| `coupling` | Stärke der Nachbarschaftsverbindungen |
| `reactivity` | Wahrscheinlichkeit lokaler Transformationen |
| `memory` | Sedimentierte Vergangenheit, lokale Hysterese |
| `coherence` | Lokale Synchronität, Musterstabilität |
| `flow` | Gerichteter Fluss, Vektordynamik, Wirbel |

Aus **lokalen Regeln, strukturiertem Rauschen, Diffusion, Reaktion, Kopplung und Gedächtnis**
entstehen komplexe Muster. Ein Analyse-Layer liest diese Muster wie Spuren:
*Was war vorher? Was könnte als Nächstes passieren? Welche Attraktoren, Cluster, Wirbel oder
proto-lebensähnlichen Formen entstehen?*

> **Wissenschaftliche Vorsicht:** Alle Interpretationen sind Hypothesen und Modelle.
> Wir beweisen keine Theorie von allem. Wir bauen ein offenes Forschungsinstrument.

Inspiriert von: Complex Systems, Artificial Life, Reaktions-Diffusion, Lenia, Flow-Lenia,
Informationsphysik, Emergenter Raumzeit, Causal Sets, Wolfram-Hypergraphen, Aktiver Inferenz.

---

## Schnellstart

```bash
git clone https://github.com/FelixGitReporian/ermergentes-rauschen.git
cd ermergentes-rauschen
pip install -e ".[dev]"

# 500 Ticks simulieren, PNGs + Entropie-CSV ausgeben
python examples/run_500.py

# Live-Dashboard (benötigt streamlit)
pip install -e ".[dashboard]"
streamlit run src/emergent_noise/visualization/dashboard.py
```

---

## Tests

```bash
python -m pytest          # alle Tests
python -m pytest -v       # mit Details
```

Aktuell: **48 Tests**, alle grün.

---

## Projektstruktur

```
src/emergent_noise/
  core/
    state.py          SimConfig (Pydantic) + GridState (dataclass)
    tick.py           Deterministischer Tick-Loop (8 Schritte)
  rules/
    diffusion.py      5-Punkt-Laplace, Numba-JIT optional
    reaction.py       Aktivierungs- + Zerfallsregel
    memory.py         EMA-Gedächtnis (Zerfall + Imprint)
    coupling.py       Bindung, Zerfall, Kohärenz-Synchronisation
    flow.py           Gradienten-Fluss, Curl-Wirbel, Advektion
  noise/
    structured_noise.py  Sinus-Superposition, deterministisch per Seed+Tick
  analysis/
    entropy.py        Normalisierte Shannon-Entropie
    attractors.py     Persistenz, Cluster, Phasenübergangs-Indikator
  visualization/
    render.py         Panel-PNG (9 Felder) + RGB-Composite
    dashboard.py      Streamlit Live-Dashboard

examples/
  run_500.py          CLI: 500 Ticks, PNG-Output, Entropie-CSV

tests/                48 pytest-Tests
docs/
  design-decisions/   ADR-0001, ADR-0002, ...
outputs/              Simulationsergebnisse (gitignore)
.github/              CI, Issue-Templates, PR-Template
```

---

## Konfiguration

Alle Parameter sind in `SimConfig` definiert — **keine magischen Zahlen in Modulen**:

```python
from emergent_noise.core.state import SimConfig, GridState
from emergent_noise.core.tick import TickLoop

config = SimConfig(
    height=128, width=128, seed=42,
    diffusion_energy=0.2,
    coupling_gain=0.01,
    flow_gradient_strength=0.1,
    memory_decay=0.97,
    noise_amplitude=0.02,
    # ... alle Parameter dokumentiert in SimConfig
)

state = GridState.initialize(config)
loop = TickLoop(config)
loop.run(state, n_ticks=1000)
```

---

## Tick-Reihenfolge

Jeder Simulationsschritt führt 8 Regeln in dieser fixen, dokumentierten Reihenfolge aus:

```
1. Strukturiertes Rauschen    (Symmetriebrechung)
2. Diffusion                  (Energie + Information)
3. Reaktion                   (lokale Transformation)
4. Kopplung                   (Netzwerkbildung, Kohärenz-Synchronisation)
5. Fluss                      (Vektordynamik, Wirbel, Advektion)
6. Gedächtnis                 (Hysterese / Spurenbildung)
7. Clip auf [0, 1]
8. tick++
```

---

## Analyse-Layer

```python
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.analysis.attractors import (
    PersistenceTracker, find_clusters, compute_phase_indicator
)

entropy = state_entropy_summary(state)          # Entropie aller Felder
clusters = find_clusters("energy", state.energy, threshold=0.6)
phase = compute_phase_indicator(state.tick, state.as_dict())

print(f"Energie-Cluster: {clusters.n_clusters}")
print(f"Phasenübergang nahe: {phase.near_transition}")
```

---

## Live-Dashboard

```bash
streamlit run src/emergent_noise/visualization/dashboard.py
```

Features:
- Alle Config-Parameter per Sidebar live anpassbar
- Heatmap des gewählten Feldes
- RGB-Composite (energy / information / coherence)
- Entropie-Zeitreihe
- Persistenz + Cluster-Statistiken
- Phasenübergangs-Indikator

---

## Roadmap

Siehe [ROADMAP.md](ROADMAP.md) für alle 8 Epics:

| Version | Epic | Ziel |
|---|---|---|
| ✅ v0.1.0 | Epic 0 | Fundament: Grid, Regeln, Tests |
| 🔄 v0.2.0 | Epic 1 | Alle 8 Parameter aktiv, Dashboard |
| 📋 v0.3.0 | Epic 2 | Spurenlese-Engine |
| 📋 v0.4.0 | Epic 3 | Regel-Evolution |
| 📋 v0.5.0 | Epic 4 | Partikel-Feld-Hybrid |
| 📋 v1.0.0 | Epic 5–6 | Graph-Modus, Performance |

---

## Beitragen

Beiträge sind willkommen! Bitte lies [CONTRIBUTING.md](CONTRIBUTING.md) und
halte den [Code of Conduct](CODE_OF_CONDUCT.md) ein.

```bash
# Feature-Branch
git checkout -b feature/mein-feature

# Tests laufen lassen
python -m pytest

# Pull Request auf develop
```

---

## Lizenz

MIT — siehe [LICENSE](LICENSE).

---

## Wissenschaftliche Abgrenzung

> Dieses Projekt ist ein experimentelles Forschungsinstrument.
> Es kann generative Selbstorganisations-Experimente durchführen,
> Muster analysieren und Hypothesen entwickeln.
> Es beweist keine Theorie von allem, kein Bewusstsein,
> keine echte Physik und kein echtes Leben.
> Alle Interpretationen sind vorsichtig formulierte Modelle.
