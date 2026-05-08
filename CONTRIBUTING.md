# Contributing – Emergentes Rauschen

Danke für dein Interesse! Dieses Projekt ist offen für Beiträge aus
Informatik, Physik, Biologie, Philosophie und Kunst.

---

## Einstieg

```bash
git clone https://github.com/FelixGitReporian/ermergentes-rauschen.git
cd ermergentes-rauschen
pip install -e ".[dev]"
python -m pytest
```

Für das Dashboard zusätzlich:

```bash
pip install -e ".[dashboard]"
streamlit run src/emergent_noise/visualization/dashboard.py
```

---

## Beitragsarten

- **Bug-Fix** – Kleiner Scope, direkter PR auf `develop`.
- **Feature** – Issue zuerst öffnen, dann Branch `feature/<name>`.
- **Experiment** – Branch `experiment/<name>`, keine Tests erforderlich, aber Config + Seed angeben.
- **Analyse** – Branch `analysis/<name>`, Notebook oder Skript mit Ergebnissen.
- **Dokumentation** – Branch `docs/<name>`.

---

## Code-Qualitätsregeln

1. **Kleine Dateien** – keine Datei > 200 Zeilen ohne guten Grund.
2. **Typisierung** – alle öffentlichen Funktionen haben Type-Hints.
3. **Docstrings** – jede Funktion hat mindestens einen Satz Erklärung.
4. **Konfiguration über `SimConfig`** – keine magischen Zahlen in Modulen.
5. **Tests** – neues Feature → mindestens 2 Tests.
6. **Wissenschaftliche Vorsicht** – keine unbewiesenen Behauptungen über Bewusstsein, Leben oder Physik.

---

## Commit-Konvention

```
feat: add transfer entropy metric
fix: correct memory decay boundary condition
exp: run reactivity sweep 001
docs: document parameter lifecycle
refactor: split diffusion rules
test: add cluster detection edge cases
perf: numba-jit for laplace kernel
```

---

## Pull Request Checkliste

- [ ] Tests laufen durch (`python -m pytest`)
- [ ] Docstring vorhanden
- [ ] Keine magischen Zahlen (alles über `SimConfig`)
- [ ] Wissenschaftliche Interpretationen vorsichtig formuliert
- [ ] ADR oder Änderungsnotiz bei Architekturentscheidungen

---

## Design Decision Records (ADR)

Wichtige Entscheidungen dokumentieren wir in `docs/design-decisions/ADR-XXXX-<titel>.md`.  
Vorlage:

```markdown
# ADR-XXXX – Titel

**Datum:** YYYY-MM-DD
**Status:** Vorschlag / Akzeptiert / Abgelehnt / Abgelöst

## Kontext
## Entscheidung
## Alternativen
## Konsequenzen
## Änderungsnotiz
```

---

## Forschungsethik

- Keine Behauptungen über Bewusstsein oder Leidensfähigkeit ohne klare Evidenzbasis.
- Agentische Dynamiken mit Vorsicht beschreiben und dokumentieren.
- Offene Sprache: „deutet auf", „ist kompatibel mit", „könnte interpretiert werden als".
