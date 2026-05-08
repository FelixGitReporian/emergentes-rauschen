# Scientific Scope — Was dieses Projekt kann und was nicht

> "Hier ist ein kleiner, reproduzierbarer, gut dokumentierter Anfang
> einer sehr großen Frage."

---

## Was das System tut

- Simuliert ein **2D-Zustandsfeld** mit 8 gekoppelten Feldern (energy, matter,
  information, coupling, reactivity, memory, coherence, flow).
- Wendet **deterministisch reproduzierbare Regeln** an:
  Diffusion, Reaktion, Kopplung, Fluss, Gedächtnis, strukturiertes Rauschen.
- **Meta-Evolution**: Lokale Regelparameter (Genome) mutieren, werden selektiert
  und retentiert — räumlich heterogenes Regelverhalten entsteht.
- **Partikel-Feld-Hybrid**: Partikel bewegen sich durch und beeinflussen Felder.
- **Graph-Modus**: Relationale Simulation in NetworkX (4 Topologien, Rewriting).
- **Mehrskalenanalyse**: Meso-Cluster-Tracking + Makro-Phasenraum-Trajektorie.
- **Experiment-Framework**: Reproduzierbare Sweep-Experimente mit CSV/JSON-Output.
- **Analyse**: Entropie, Persistenz, Attraktoren, Regime-Klassifikation (8 Typen),
  Spurenlesen (MI-Matrix, Morphologie), Proto-Kompartiment-Erkennung.

---

## Was die Marker messen

| Marker | Misst | Ist kein Nachweis für |
|--------|-------|----------------------|
| **Φ-Proxy** | Globale Kohärenz × (1 − lokale Varianz) × MI-Proxy | Echter IIT-Φ (NP-schwer), Bewusstsein |
| **Active-Inference-Score** | Korrelation Gedächtnis ↔ Energie | Echte prädiktive Schleifen, Free-Energy-Minimierung |
| **Proto-Leben-Score** | 6 strukturelle Kriterien (Grenzen, Fluss, Stabilität, …) | Biologisches Leben, Replikation, Metabolismus |
| **Global-Workspace-Score** | Gini-Koeffizient der Information | Neuronale Broadcast-Prozesse, Bewusstsein |
| **Regime-Klassifikation** | Muster-Ähnlichkeit zu 8 Kategorien | Physikalische Phasenübergänge |
| **Emergente Distanz** | Kürzeste gewichtete Pfadlänge im Graph | Raumzeit-Metrik, physikalische Geometrie |

**Alle Marker sind heuristische Proxies.** Hohe Werte bedeuten "strukturell interessant
im Rahmen dieser Metriken" — nicht mehr.

---

## Was das System nicht tut und nicht behauptet

- ❌ Es beweist keine **Theorie von allem**.
- ❌ Es zeigt keine **echte Physik** (kein Impulserhalt, keine relativistische Geometrie).
- ❌ Es erzeugt kein **biologisches Leben** (keine Replikation, kein Metabolismus, keine DNA).
- ❌ Es weist kein **Bewusstsein** nach — weder in der Simulation noch im System.
- ❌ Es validiert keine der referenzierten Theorien (IIT, Free-Energy, GWT, Wolfram Physics).
- ❌ Es ist kein **Beweis** für Assembly Theory, Causal Sets oder andere Rahmentheorien.
- ❌ Die Wolfram-Analogie im Graph-Modus ist **strukturell**, nicht physikalisch äquivalent.

---

## Was die philosophische Dimension ist

Das Projekt hat eine tiefere Fragestellung — jenseits der Metriken:

*Welche minimalen Bedingungen erzeugen Strukturen, die wir als Spuren, Grenzen,
Gedächtnis, Anpassung, Proto-Leben oder Bewusstsein lesen könnten?*

Diese Frage ist legitim und wissenschaftlich interessant.
Die Antwort kann dieses System allein nicht liefern — aber es kann explorieren,
Hypothesen generieren und Muster sichtbar machen.

**Die philosophische Tiefenschicht ist in der Arbeitsmappe dokumentiert.**
Die README und der Code bleiben wissenschaftlich-technisch präzise.

---

## Ethik-Protokoll

- Alle Bewusstseins-Marker tragen explizite Vorbehalte in Docstrings und Dashboard.
- Das Dashboard zeigt `st.warning()` bei allen spekulativen Metriken.
- Dieses Dokument ist Teil des Projekts und wird mit versioniert.
