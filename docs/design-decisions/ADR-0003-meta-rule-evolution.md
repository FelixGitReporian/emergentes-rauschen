# ADR-0003: Meta-Regel-Evolution als dezentrales Regelgenom

**Status:** Accepted  
**Datum:** 2026-05-08  
**Autor:** FelixGitReporian  
**Bezug:** Arbeitsmappe Kap. 9 – Evolvierende Regeln und Meta-Evolution

---

## Kontext

Das System besteht aus globalen Regelparametern (SimConfig), die für alle
Zellen identisch sind. Um offene Evolution zu ermöglichen – d.h. die Entstehung
räumlich differenzierter Regelprofile – wird ein Mechanismus benötigt, bei dem
lokale Parameter variieren, selektiert und gesichert werden können.

Arbeitsmappe Kap. 9 fordert:
- Jede Region besitzt ein lokales Regelprofil (Regelgenom).
- Regelprofile können mutieren.
- Erfolgreiche Profile breiten sich durch Selektion aus.
- Persistent erfolgreiche Profile hinterlassen Gedächtnisspuren.

---

## Entscheidung

### Repräsentation

Das Regelgenom wird als **zwei float32-Arrays** (`genome_strength`,
`genome_threshold`) der Form `(height, width)` direkt im `GridState`
gespeichert – kein separates Objekt pro Zelle.

**Begründung:**
- NumPy-native Arrays ermöglichen vektorisierte Operationen ohne Python-Loop.
- Uniform mit allen anderen Zustandsfeldern (gleiche Shape, gleicher Wertebereich).
- `clip_all()` und `as_dict()` können konsistent erweitert werden.
- Genome werden bewusst aus `as_dict()` ausgelassen, um Analysemodule nicht
  zu kontaminieren.

### Genome-Parameter

| Parameter         | Bedeutung                                  |
|-------------------|--------------------------------------------|
| `genome_strength` | Lokale Reaktionsstärke (Regel 1)           |
| `genome_threshold`| Lokaler Energie-Aktivierungsschwellwert    |

Nur Reaktionsregel 1 wurde genome-gesteuert gemacht, da sie die dominante
Transformationsregel ist. Weitere Regeln können in späteren Epics folgen.

### Evolutionsschritte (pro Tick, Schritt 7)

1. **Fitness** = `coherence * (1 - lokale_energievarianz)` — heuristischer
   Proxy für ein stabiles, geordnetes lokales Profil.
2. **Mutation** — zufällig ausgewählte Zellen erhalten `±meta_mutation_strength`
   auf einen Genome-Parameter.
3. **Selektion** — lokale 3×3-Nachbarschaft: schwächere Zellen übernehmen
   Profile fitterer Nachbarn.
4. **Retention** — Zellen mit Fitness > Schwellwert verstärken das
   Gedächtnisfeld (schwaches Signal, Faktor 0.01).

### Steuerung

- `meta_enabled` (bool): vollständiger Ein/Aus-Schalter.
- `meta_mutation_rate`, `meta_mutation_strength`: steuern genetische Diversität.
- `meta_selection_rate`: steuert Selektion sgeschwindigkeit.
- `meta_retention_threshold`: bestimmt, welche Profile ins Gedächtnis schreiben.

---

## Verworfene Alternativen

| Alternative | Grund für Ablehnung |
|-------------|---------------------|
| Objekt-orientiertes Regelgenom pro Zelle (Klasse) | Python-Objekte in H×W-Arrays = massiver Overhead, keine Vektorisierung möglich |
| Vollständig evolvierte Regelsets (jede Regel hat eigene Gene) | Zu komplex für v0.4.0; schrittweise Erweiterung geplant |
| Genetischer Algorithmus mit Crossover | Räumliche Lokalität wäre verloren; lokale Selektion passt besser zur Grid-Architektur |
| Externe Fitness-Funktion (Hand-designed) | Widerspricht dem Emergenz-Prinzip; interne Metriken bevorzugt |

---

## Konsequenzen

**Positiv:**
- Räumlich heterogenes Reaktionsverhalten entsteht von selbst.
- Genome sind direkt analysierbar (genome_diversity, genome_entropy).
- `meta_enabled=False` schaltet die Evolution vollständig ab → Rückwärtskompatibilität.
- Vollständig deterministisch (seed + tick als RNG-Basis).

**Negativ / Risiken:**
- Selektionsschritt enthält einen Python-Loop über ausgewählte Zellen
  → Performance-Engpass bei großen Grids. Für v0.5.0 als NumPy-Vektoroperation
  refaktorieren.
- Fitness-Proxy ist heuristisch: Kohärenz ≠ biologische Fitness.

---

## Wissenschaftliche Vorsicht

Die Meta-Regel-Evolution ist eine abstrakte Abstraktion, kein Modell realer
Genetik oder Evolution. Entstehende Muster sind interessante Emergenz-
Phänomene, keine Belege für biologische oder kognitive Prozesse.
