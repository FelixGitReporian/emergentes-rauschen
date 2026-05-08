# ADR-0007: Consciousness Markers + Learning Dashboard (Epic 7–8)

**Status:** Accepted  
**Date:** 2026-05-08  
**Reference:** Workbook ch. 13 – Life, Intelligence, Consciousness

---

## Context

Epic 8 requires careful, measurable markers for proto-life, intelligence
and consciousness theories. In parallel the dashboard should serve as a
learning environment for complex systems science and artificial life.

---

## Decision

### Consciousness Markers (`interpretation/consciousness.py`)

Four marker types, all implemented as proxies:

| Marker | Theory | Implementation |
|--------|--------|----------------|
| Φ-Proxy | IIT (Tononi 2004) | coherence × (1 − local_var) × mi_proxy |
| Active Inference | Free-Energy (Friston 2010) | memory–energy correlation |
| Proto-Life | Workbook ch. 13.1 | 6 criteria (1/6 point each) |
| Global Workspace | GWT (Baars/Dehaene) | Gini coefficient of information field |

**Integrated score:** 0.3·Φ + 0.2·AI + 0.3·PL + 0.2·GW

**Key limitations:**
- True IIT-Φ is NP-hard to compute; this proxy is a heuristic.
- Active-Inference marker does not test genuine predictive loops.
- Global-Workspace score ≠ evidence of consciousness.
- All markers serve exploration, not theory verification.

### Learning Dashboard (Tab 4)

Three depth levels:

| Level | Content |
|-------|---------|
| 🟢 Entry | Cellular automata, emergence, attractors; books + links |
| 🟡 Intermediate | IIT, Free-Energy, GWT, Assembly Theory; primary sources |
| 🔴 Research Front | Open questions, experiment ideas, current conferences |

Integrated sources:
- Books: Mitchell (Complexity), Levy (ALife)
- Online: natureofcode.com, wolframscience.com, SFI Explorer
- Demos: Lenia, Avida, OpenWorm, Framsticks
- Podcasts: Complexity SFI, Sara Walker (Mindscape, Big Biology)
- Papers: Tononi 2004, Friston 2010, Walker & Davies 2013

### Experiment Framework (`experiments/`)

- 8 predefined experiments linked to scientific questions.
- Reproducibility: git hash + seed + config in `experiment_meta.json`.
- CSV output: 15 metrics per analysis tick.

---

## Scientific Guiding Principle

> "We build an open research instrument, not an oracle.
> Every metric is a reading, not a truth."
> — Workbook ch. 4

All consciousness markers carry explicit scientific disclaimers in:
- Docstrings (`consciousness.py`)
- Dashboard warnings (`st.warning`)
- This ADR
