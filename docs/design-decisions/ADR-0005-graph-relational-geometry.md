# ADR-0005: Relationale Geometrie via NetworkX-GraphState

**Status:** Accepted  
**Datum:** 2026-05-08  
**Bezug:** Arbeitsmappe Kap. 10.4, 14 – Graph-/Hypergraph-Modus

---

## Kontext

Das bestehende System ist an ein euklidisches 2D-Gitter gebunden.
Epic 5 fordert einen alternativen Zustandsraum, in dem Distanz aus
Verbindungsstärken entsteht — analog zu Wolfram's Hypergraph Physics.

---

## Entscheidung

`GraphState` (NetworkX-Multigraph mit Knoten- und Kanten-Attributen):

| Merkmal | Entscheidung |
|---------|--------------|
| Bibliothek | NetworkX (pure Python, einfache Integration, kein GPU) |
| Topologien | small_world, scale_free, random, grid |
| Distanz | Dijkstra auf 1/weight (starke Kante = kurze Distanz) |
| Rewriting | Aktivste Knoten × Aktivste Knoten → neue Kante pro Tick |

**Bewusste Vereinfachungen gegenüber Wolfram Physics:**
- Kein echter Hypergraph (nur einfacher Graph mit Gewichten).
- Keine kausale Invarianz, keine Branchiale Geometrie.
- Ziel: Exploration, nicht Physik-Simulation.

---

## Konsequenzen

- Emergente Distanzmatrix erlaubt Topologie-Vergleiche (small_world vs. scale_free).
- Dashboard Tab 5 zeigt NetworkX-Visualisierung + Distanzmatrix interaktiv.
- NetworkX ist neue optionale Abhängigkeit.

## Wissenschaftliche Vorsicht

Dieser Graph-Modus testet **keine** Wolfram-Physik-Hypothesen.
Er ist eine strukturelle Analogie zur Exploration relationaler Geometrie.
