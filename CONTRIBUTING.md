# Contributing – Emergentes Rauschen

Contributions from computer science, physics, biology, philosophy and art are welcome!

---

## Getting Started

```bash
git clone https://github.com/FelixGitReporian/emergentes-rauschen.git
cd emergentes-rauschen
pip install -e ".[dev]"
python -m pytest
```

For the dashboard:

```bash
pip install -e ".[dashboard]"
streamlit run src/emergent_noise/visualization/dashboard.py
```

---

## Contribution Types

- **Bug fix** – Small scope, direct PR onto `develop`.
- **Feature** – Open an issue first, then branch `feature/<name>`.
- **Experiment** – Branch `experiment/<name>`, no tests required, but provide config + seed.
- **Analysis** – Branch `analysis/<name>`, notebook or script with results.
- **Documentation** – Branch `docs/<name>`.

---

## Code Quality Rules

1. **Small files** – no file > 200 lines without good reason.
2. **Type hints** – all public functions have type annotations.
3. **Docstrings** – every function has at least one explanatory sentence.
4. **Config via `SimConfig`** – no magic numbers in modules.
5. **Tests** – new feature → at least 2 tests.
6. **Scientific caution** – no unsubstantiated claims about consciousness, life or physics.

---

## Commit Convention

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

## Pull Request Checklist

- [ ] Tests pass (`python -m pytest`)
- [ ] Docstring present
- [ ] No magic numbers (everything via `SimConfig`)
- [ ] Scientific interpretations carefully worded
- [ ] ADR or change note for architecture decisions

---

## Design Decision Records (ADR)

Important decisions are documented in `docs/design-decisions/ADR-XXXX-<title>.md`.  
Template:

```markdown
# ADR-XXXX – Title

**Date:** YYYY-MM-DD
**Status:** Proposed / Accepted / Rejected / Superseded

## Context
## Decision
## Alternatives
## Consequences
## Change Note
```

---

## Research Ethics

- No claims about consciousness or sentience without clear evidence.
- Describe and document agentic dynamics with caution.
- Use open language: "suggests", "is compatible with", "could be interpreted as".
