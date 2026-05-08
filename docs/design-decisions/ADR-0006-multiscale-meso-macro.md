# ADR-0006: Mehrskalenmodell Mikro/Meso/Makro

**Status:** Accepted  
**Datum:** 2026-05-08  
**Bezug:** Arbeitsmappe Kap. 10.5, 16.2 – Mehrskalenmodell

---

## Kontext

Das System hat bisher nur eine Beschreibungsebene (Mikro: Gitterzellen).
Epic 6 fordert Meso- und Makro-Ebene für Emergenz-Analyse.

---

## Entscheidung

**Drei Ebenen in `core/multiscale.py`:**

| Ebene | Implementierung | Einheit |
|-------|----------------|---------|
| Mikro | GridState (bestehend) | Gitterzellen |
| Meso  | MesoLayer (SciPy label + Tracking) | Cluster-Entitäten |
| Makro | AttractorLandscape (Trajektorie in E×K) | Systemzustand |

**MesoLayer:**
- Verbundene Energie-Regionen (8-Konnektivität, SciPy `label`).
- Tracking via Schwerpunkt-Matching (nächster Vorläufer ≤ 10 Zellen).
- Geschwindigkeitsschätzung: Schwerpunktverschiebung pro Tick.

**MacroLayer:**
- Projektion des Systemzustands auf (energy_mean, coherence_mean).
- Phasenübergang-Detektion: Δ > 0.05 in einer Tick-Periode.
- Trajektorie als (N, 2) Array für Dashboard-Plot.

---

## Konsequenzen

- `MultiscaleController.update(state)` gibt Meso + Makro-Dict zurück.
- Dashboard Tab 4 zeigt Attraktor-Trajektorie live.
- Keine Performance-Einbuße: SciPy `label` ist O(H×W), schnell.

## Wissenschaftliche Vorsicht

Meso-Entitäten sind Label-Artefakte, keine ontologischen Objekte.
Phasenübergänge sind heuristische Sprung-Erkennungen, keine echten
Phasenübergangsnachweise (kein Ordnungsparameter, kein kritisches Verlangsamen).
