# ADR-0002 – Kopplung und Flussfeld als eigenständige Regelmodule

**Datum:** 2026-05-08  
**Status:** Akzeptiert

## Kontext

Epic 1 fügt zwei neue aktive Regelmodule hinzu: `coupling.py` und `flow.py`.
Es wurden drei Alternativen für deren Integration erwogen.

## Entscheidung

Kopplung und Fluss sind **eigenständige Module** mit je einem einzigen
Einstiegspunkt (`apply_coupling`, `apply_flow`), die vom `TickLoop` in der
dokumentierten Reihenfolge aufgerufen werden.

## Begründung

- Jedes Modul hat einen klar definierten Scope — einfacher zu testen und zu warten.
- Der `TickLoop` bleibt die einzige Stelle, die Reihenfolge kennt.
- Module können einzeln deaktiviert werden (z.B. kein Fluss in Baseline-Experimenten).
- Passt zum etablierten Muster von `diffusion.py`, `reaction.py`, `memory.py`.

## Regelreihenfolge (v0.2.0)

```
1. Rauschen         (Symmetriebrechung)
2. Diffusion        (Transport)
3. Reaktion         (lokale Transformation)
4. Kopplung         (Netzwerkbildung, Kohärenz-Synchronisation)
5. Fluss            (Vektordynamik, Wirbel, advektiver Transport)
6. Gedächtnis       (Hysterese / Spur)
7. Clip [0,1]
8. tick++
```

## Physikalische Motivation

- Kopplung nach Reaktion: Reaktion erzeugt Kohärenz-Unterschiede; Kopplung gleicht sie an.
- Fluss nach Kopplung: Kopplungs-Curl treibt Wirbel an; Gradienten entstehen aus allen vorherigen Schritten.
- Gedächtnis zuletzt: Schreibt den vollständigen Post-Transformations-Zustand als Spur.

## Alternativen

- **Alles in einer Datei:** Schlechter wartbar, verstößt gegen Qualitätsregeln.
- **Fluss in `diffusion.py`:** Konzeptuell falsch — Diffusion ist skalar, Fluss ist vektoriell.
- **Kopplung als Teil von `reaction.py`:** Zu viel Scope; Kopplung hat eigene Zeitskala.

## Konsequenzen

- `flow_x` / `flow_y` sind jetzt aktive Felder mit eigenem Dynamik-Profil.
- `coupling` und `coherence` sind jetzt dynamisch (nicht mehr konstant).
- Neue Parameter in `SimConfig`: 7 neue Felder (`coupling_*`, `flow_*`).
- CSV-Entropie-Log zeigt jetzt Variation in allen Feldern.

## Änderungsnotiz

v0.2.0 — 2026-05-08:
- `rules/coupling.py`, `rules/flow.py` hinzugefügt
- `analysis/attractors.py` mit Persistenz, Cluster, Phasenindikator
- `visualization/dashboard.py` (Streamlit)
- Numba-JIT optional in `diffusion.py`
- 15 neue Tests (48 gesamt)
