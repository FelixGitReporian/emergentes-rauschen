# ADR-0001 – Start mit 2-D-Grid-Modell

**Datum:** 2026-05-08  
**Status:** Akzeptiert  
**Kontext:** Phase 1 des Projekts „Emergentes Rauschen"

## Kontext

Das Projekt benötigt eine simulierbare, visualisierbare Grundstruktur. Es wurden
drei Alternativen erwogen: 2-D-Grid, Partikel-System und Graph/Hypergraph.

## Entscheidung

Wir starten mit einem **2-D-Grid** (periodische Randbedingungen, toroidale Topologie).

## Begründung

- Einfach visualisierbar (Heatmap reicht aus).
- Gut bekannt aus Zellulären Automaten, Reaktions-Diffusions-Systemen und Lenia.
- NumPy-Operationen auf 2-D-Arrays sind schnell und gut lesbar.
- Periodische Randbedingungen vermeiden Randeffekte ohne komplexe Logik.
- Einfacher Einstieg für junior-freundliche Entwicklung.

## Alternativen

- **Partikel-System:** Realistischer für Bewegung, aber Kollisionserkennung und
  Rasterung sind komplex. Für Phase 3 geplant.
- **Graph/Hypergraph:** Näher an Wolfram-Modellen und CDT, aber schwerer zu
  visualisieren und initial zu implementieren. Für Phase 4 geplant.

## Konsequenzen

- Raum ist vorgegeben, nicht emergent (wird in Phase 4 geändert).
- Zelluläre Automaten-artige Regeln passen gut.
- Räumliche Auflösung ist fix; für multi-scale-Modelle muss Architektur erweitert werden.

## Änderungsnotiz

Erste Implementierung (v0.1.0):
- `core/state.py`: `GridState` mit 9 Feldern (8 Parameter + flow als flow_x/flow_y).
- `core/tick.py`: deterministischer Tick-Loop mit dokumentierter Regelreihenfolge.
- `rules/diffusion.py`, `rules/reaction.py`, `rules/memory.py`.
- `noise/structured_noise.py`: Sinus-Superposition als strukturiertes Rauschen.
- `analysis/entropy.py`: normalisierte Shannon-Entropie.
- `visualization/render.py`: Panel-PNG und RGB-Composite.
- `examples/run_500.py`: 500-Tick-Beispiellauf.
- `tests/`: pytest-Suite für Init, Deterministik, Wertebereiche, Regeln.
