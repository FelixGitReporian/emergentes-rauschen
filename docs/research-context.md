# Research Context — Wissenschaftlicher Einordnungsrahmen

Dieses Dokument erklärt, **wie** sich Emergentes Rauschen zu bestehenden Feldern verhält —
und wo die Grenzen der Analogien liegen.

---

## Cellular Automata & Reaction-Diffusion

**Direkte Verwandtschaft.** Das Kernsystem ist ein zellulärer Automat mit
kontinuierlichen Zustandswerten und mehreren gekoppelten Feldern.

- Conway's Game of Life: diskret, 2 Zustände — ER: kontinuierlich, 8 Felder
- Reaction-Diffusion (Turing, Gray-Scott): chemische Aktivator-Inhibitor-Systeme
  mit Diffusion → stabile Muster. ER enthält Diffusion + Reaktion als Teilschritte.
- **Lenia** (Chan 2019): kontinuierlicher CA mit Glättungskern — eleganter als ER,
  aber ohne Gedächtnis, Kopplung oder Meta-Evolution.
- **Flow-Lenia** (Plantec et al. 2023): Lenia + Strömungsfeld. ER implementiert
  ähnliche Advektion unabhängig.

---

## Artificial Life

**Direkte Forschungsfrage.** ER sucht nach Strukturen, die ALife-Kriterien erfüllen:
Grenzen, Energiefluss, Selbsterhaltung, Adaptation, Gedächtnis, Variation.

- **Avida** (Ofria & Wilke): selbstreplizierende Programme. ER hat keine Replikation.
- **OpenWorm**: vollständiges C. elegans Nervensystem — biologisch detailliert.
  ER ist prinzipienbasiert, nicht biologisch.
- **Tierra** (Ray): digitale Evolution durch Mutation und Selektion.
  ER hat Meta-Evolution der Regelparameter (Genome), aber keine selbstreplizierende Einheiten.

---

## Wolfram Physics / Hypergraph Rewriting

**Strukturelle Analogie, keine physikalische Äquivalenz.**

Wolfram schlägt vor, dass Raumzeit und Physik aus dem Umschreiben von Hypergraph-Relationen
entstehen. ER's Graph-Modus testet **nicht** diese Hypothese. Es untersucht, ob
relationale Geometrien aus lokalen Regelanwendungen emergieren können.

- Kein echter Hypergraph (nur gewichteter Graph mit Knoten-Attributen).
- Keine kausale Invarianz, keine branchiale Geometrie.
- Keine Äquivalenz zu physikalischen Gesetzen.

**Was es tatsächlich leistet:** Exploration emergenter Distanzmetriken und
Topologieeffekte (small_world vs. scale_free vs. random).

---

## Integrated Information Theory (IIT, Tononi)

**Proxy-Metrik, kein IIT-Test.**

Echter IIT-Φ berechnet, wie viel mehr Information ein System als Ganzes hat
verglichen mit der Summe seiner Teile. Das ist NP-schwer für große Systeme.

ER's Φ-Proxy = `globale Kohärenz × (1 − lokale Varianz) × MI-Proxy`.
Das misst strukturelle Integration — keine echte Φ-Berechnung.

Primärquellen:
- Tononi (2004): *An information integration theory of consciousness*, BMC Neuroscience 5, 42
- Albantakis et al. (2023): IIT 4.0

---

## Free-Energy-Prinzip / Active Inference (Friston)

**Konzeptuell verwandt, nicht implementiert.**

Das Free-Energy-Prinzip beschreibt, wie Systeme interne Modelle ihrer Umgebung
aufbauen und durch Aktion und Wahrnehmung Überraschung minimieren.

ER's Active-Inference-Score misst die Korrelation zwischen `memory`-Feld
(als Proxy für interne Modell-Spur) und aktuellem `energy`-Feld.
Das ist eine sehr vereinfachte Analogie — kein Variational Bayes, kein Belief-Updating.

Primärquelle:
- Friston (2010): *The free-energy principle: a unified brain theory?*,
  Nature Reviews Neuroscience 11, 127–138

---

## Global Workspace Theory (Baars / Dehaene)

**Strukturelle Analogie via Gini-Koeffizient.**

GWT beschreibt Bewusstsein als globale Übertragung (Broadcast) lokaler Information
im Gehirn. ER misst den Gini-Koeffizienten der Information — als Proxy für
"lokale Dominanz einer Informationsquelle".

Hoher Gini ≠ Bewusstsein. Es bedeutet: die Informationsverteilung ist ungleich,
eine Region dominiert strukturell.

---

## Assembly Theory (Walker & Davies)

**Konzeptuell im Hintergrund.**

Assembly Theory definiert Komplexität als die Anzahl der benötigten Schritte
zum Aufbau einer Struktur (Assembly Index). ER misst keine Assembly-Komplexität direkt.

Primärquelle:
- Walker & Davies (2013): *The algorithmic origins of life*,
  J. Royal Society Interface 10, 20120869

---

## Zusammenfassung: Verhältnis zu Referenzfeldern

| Feld | Verhältnis |
|------|-----------|
| Cellular Automata | **direkte Implementierung** (kontinuierlich, 8 Felder) |
| Reaction-Diffusion | **Teilmenge** (Diffusion + Reaktion als Schritte) |
| Lenia / Flow-Lenia | **konzeptuell verwandt**, unabhängig implementiert |
| Artificial Life | **Forschungsfrage** — Proto-ALife-Kriterien als Metriken |
| Wolfram Physics | **strukturelle Analogie** im Graph-Modus |
| IIT / GWT / Active Inference | **heuristische Proxy-Metriken** |
| Assembly Theory | **konzeptuell im Hintergrund** |
