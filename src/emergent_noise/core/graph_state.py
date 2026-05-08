"""
core/graph_state.py – GraphState + Hypergraph-Rewriting (Epic 5).

Implementiert einen relationalen Zustandsraum, in dem Knoten (Zellen)
über gewichtete Kanten verbunden sind. Raum entsteht hier nicht aus
einem vordefinierten Gitter, sondern aus den Stärken der Verbindungen.

Architektur (Arbeitsmappe Kap. 10.4, 14):
    - GraphState hält einen NetworkX-Graph mit Knoten-Attributen
      (energy, information, reactivity) und Kanten-Attributen (weight).
    - Hypergraph-Rewriting: Lokale Muster (Motifs) werden erkannt und
      durch neue Konfigurationen ersetzt — analog zu Wolfram Physics.
    - Emergente Distanz: Die effektive Distanz zwischen Knoten ist die
      kürzeste gewichtete Pfadlänge, nicht die euklidische Distanz.

Wolfram Physics Inspiration (vereinfacht):
    Wolfram's Hypergraph-Rewriting basiert auf dem Prinzip, dass Raum
    selbst aus Relationen entsteht. Hier verwenden wir gewichtete
    NetworkX-Graphen als vereinfachtes Analogon.

Wissenschaftliche Vorsicht:
    Dieses Modul ist eine stark vereinfachte Abstraktion der Wolfram
    Physics Ideen. Es ist kein Test dieser Theorie. Die entstehenden
    Graphen-Dynamiken sind Emergenz-Experimente, keine Raumzeit-Modelle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None  # type: ignore


def _require_networkx() -> None:
    if not HAS_NETWORKX:
        raise ImportError(
            "networkx ist erforderlich für GraphState. "
            "Installieren mit: pip install networkx"
        )


@dataclass
class GraphConfig:
    """Konfiguration für den Graph-Zustandsraum.

    Attribute
    ----------
    n_nodes:
        Anzahl der Knoten im Initialgraph.
    initial_topology:
        Startstruktur: 'random', 'grid', 'small_world', 'scale_free'.
    connection_prob:
        Verbindungswahrscheinlichkeit für 'random'.
    rewriting_rate:
        Anteil der Kanten, die pro Tick umgeschrieben werden.
    weight_decay:
        Multiplikativer Zerfall der Kantengewichte pro Tick.
    energy_diffusion:
        Anteil der Energie, die pro Tick über Kanten diffundiert.
    seed:
        Zufalls-Seed.
    """

    n_nodes: int = 64
    initial_topology: str = "small_world"
    connection_prob: float = 0.1
    rewriting_rate: float = 0.05
    weight_decay: float = 0.98
    energy_diffusion: float = 0.1
    seed: int = 42


class GraphState:
    """Relationaler Zustandsraum auf NetworkX-Graph-Basis.

    Jeder Knoten hat:
    - ``energy``      – lokale Energie [0, 1]
    - ``information`` – lokale Information [0, 1]
    - ``reactivity``  – lokale Reaktivität [0, 1]

    Jede Kante hat:
    - ``weight``      – Verbindungsstärke [0, 1]

    Parameters
    ----------
    config:
        GraphConfig mit allen Parametern.
    """

    def __init__(self, config: GraphConfig) -> None:
        _require_networkx()
        self.config = config
        self.tick = 0
        self._rng = np.random.default_rng(config.seed)
        self.graph = self._build_initial_graph()

    def _build_initial_graph(self):
        """Erzeuge initialen Graphen basierend auf Topologie-Einstellung."""
        cfg = self.config
        n = cfg.n_nodes
        seed = int(cfg.seed)
        topo = cfg.initial_topology

        if topo == "random":
            G = nx.erdos_renyi_graph(n, cfg.connection_prob, seed=seed)
        elif topo == "small_world":
            k = max(2, n // 8)
            G = nx.watts_strogatz_graph(n, k, 0.3, seed=seed)
        elif topo == "scale_free":
            G = nx.barabasi_albert_graph(n, max(1, n // 16), seed=seed)
        elif topo == "grid":
            side = int(np.ceil(np.sqrt(n)))
            G = nx.grid_2d_graph(side, side)
            # Knoten neu nummerieren
            G = nx.convert_node_labels_to_integers(G)
            # Auf n Knoten kürzen
            if G.number_of_nodes() > n:
                to_remove = list(G.nodes())[n:]
                G.remove_nodes_from(to_remove)
        else:
            G = nx.watts_strogatz_graph(n, 4, 0.3, seed=seed)

        # Knoten-Attribute initialisieren
        rng = np.random.default_rng(int(cfg.seed) + 1)
        for node in G.nodes():
            G.nodes[node]["energy"]      = float(rng.uniform(0.1, 0.9))
            G.nodes[node]["information"] = float(rng.uniform(0.0, 0.5))
            G.nodes[node]["reactivity"]  = float(rng.uniform(0.3, 0.7))

        # Kanten-Attribute initialisieren
        for u, v in G.edges():
            G[u][v]["weight"] = float(rng.uniform(0.3, 1.0))

        return G

    # ──────────────────────────────────────────────────────────────
    # Tick-Mechaniken
    # ──────────────────────────────────────────────────────────────

    def step(self) -> None:
        """Führe einen vollständigen Graph-Tick aus.

        Schritte:
        1. Energie-Diffusion über Kanten
        2. Lokale Reaktion (Schwellwert-basiert)
        3. Kanten-Gewicht-Zerfall
        4. Hypergraph-Rewriting (neue Verbindungen basierend auf Aktivität)
        5. Tick erhöhen
        """
        self._diffuse_energy()
        self._apply_reaction()
        self._decay_weights()
        self._rewrite()
        self.tick += 1

    def _diffuse_energy(self) -> None:
        """Energie diffundiert gewichtet über Nachbarn."""
        G = self.graph
        alpha = self.config.energy_diffusion
        new_energy = {}
        for node in G.nodes():
            neighbors = list(G.neighbors(node))
            if not neighbors:
                new_energy[node] = G.nodes[node]["energy"]
                continue
            weights = np.array([G[node][nb].get("weight", 1.0) for nb in neighbors])
            energies = np.array([G.nodes[nb]["energy"] for nb in neighbors])
            w_sum = weights.sum()
            if w_sum > 0:
                weighted_avg = float(np.dot(weights, energies) / w_sum)
            else:
                weighted_avg = G.nodes[node]["energy"]
            new_energy[node] = (
                (1 - alpha) * G.nodes[node]["energy"]
                + alpha * weighted_avg
            )
        nx.set_node_attributes(G, new_energy, "energy")

    def _apply_reaction(self) -> None:
        """Lokale Reaktion: hohe Energie + hohe Reaktivität → Information."""
        G = self.graph
        for node in G.nodes():
            e = G.nodes[node]["energy"]
            r = G.nodes[node]["reactivity"]
            if e > 0.6 and r > 0.5:
                G.nodes[node]["energy"]      = max(0.0, e - 0.05)
                G.nodes[node]["information"] = min(1.0, G.nodes[node]["information"] + 0.03)

    def _decay_weights(self) -> None:
        """Kantengewichte zerfallen langsam."""
        decay = self.config.weight_decay
        for u, v in self.graph.edges():
            self.graph[u][v]["weight"] = max(
                0.01, self.graph[u][v]["weight"] * decay
            )

    def _rewrite(self) -> None:
        """Hypergraph-Rewriting: aktive Knoten knüpfen neue Verbindungen.

        Knoten mit hoher Energie + hoher Information suchen neue Partner
        (andere aktive Knoten ohne direkte Verbindung). Verbindet die
        aktivsten Knoten-Paare mit neuer Kante (Rate = rewriting_rate).
        """
        G = self.graph
        rng = np.random.default_rng(self.config.seed + self.tick * 1301)
        nodes = list(G.nodes())
        n_rewrite = max(1, int(self.config.rewriting_rate * len(nodes)))

        # Aktivste Knoten (Energie × Information)
        activity = {
            n: G.nodes[n]["energy"] * G.nodes[n]["information"]
            for n in nodes
        }
        sorted_nodes = sorted(nodes, key=lambda n: activity[n], reverse=True)
        candidates = sorted_nodes[:max(4, n_rewrite * 2)]

        # Versuche neue Kanten zwischen Kandidaten, die noch nicht verbunden sind
        rewired = 0
        for _ in range(n_rewrite * 3):
            if rewired >= n_rewrite:
                break
            if len(candidates) < 2:
                break
            u, v = rng.choice(candidates, size=2, replace=False)
            if u != v and not G.has_edge(u, v):
                w = float(activity[u] * activity[v])
                G.add_edge(u, v, weight=min(1.0, w * 5))
                rewired += 1

    # ──────────────────────────────────────────────────────────────
    # Metriken
    # ──────────────────────────────────────────────────────────────

    def emergent_distance_matrix(self, n_sample: int = 20) -> np.ndarray:
        """Berechne emergente Distanz-Matrix für eine Stichprobe von Knoten.

        Die emergente Distanz = gewichteter kürzester Pfad (1/weight).
        Hohe Kantengewichte = kurze effektive Distanz (starke Verbindung).

        Parameters
        ----------
        n_sample:
            Anzahl zufällig gesampelter Knoten für die Matrix.

        Returns
        -------
        (n_sample × n_sample) float-Array mit Distanzwerten.
            np.inf = kein Pfad vorhanden.
        """
        G = self.graph
        nodes = list(G.nodes())
        n = min(n_sample, len(nodes))
        rng = np.random.default_rng(self.config.seed)
        sampled = rng.choice(nodes, size=n, replace=False).tolist()

        # Invertiere Gewichte für Distanz
        G_dist = nx.Graph()
        for u, v, d in G.edges(data=True):
            w = d.get("weight", 0.01)
            G_dist.add_edge(u, v, weight=1.0 / max(w, 1e-6))

        dist = np.full((n, n), np.inf)
        for i, src in enumerate(sampled):
            lengths = nx.single_source_dijkstra_path_length(
                G_dist, src, weight="weight"
            )
            for j, tgt in enumerate(sampled):
                dist[i, j] = lengths.get(tgt, np.inf)
        return dist

    def graph_summary(self) -> Dict[str, Any]:
        """Gibt kompakte Graph-Statistik zurück."""
        G = self.graph
        n = G.number_of_nodes()
        m = G.number_of_edges()
        energies = [G.nodes[nd]["energy"] for nd in G.nodes()]
        infos    = [G.nodes[nd]["information"] for nd in G.nodes()]
        weights  = [G[u][v]["weight"] for u, v in G.edges()]

        # Verbundenheit
        is_connected = nx.is_connected(G)
        n_components = nx.number_connected_components(G)

        # Clustering-Koeffizient (Maß für lokale Vernetzungsdichte)
        avg_clustering = float(nx.average_clustering(G))

        return {
            "tick":             self.tick,
            "n_nodes":          n,
            "n_edges":          m,
            "density":          round(nx.density(G), 4),
            "is_connected":     is_connected,
            "n_components":     n_components,
            "avg_clustering":   round(avg_clustering, 4),
            "mean_energy":      round(float(np.mean(energies)), 4),
            "mean_information": round(float(np.mean(infos)), 4),
            "mean_weight":      round(float(np.mean(weights)) if weights else 0.0, 4),
        }

    def node_array(self, attribute: str) -> np.ndarray:
        """Gibt Knoten-Attribut als 1-D Array zurück (sortiert nach Knoten-ID)."""
        nodes = sorted(self.graph.nodes())
        return np.array([self.graph.nodes[n].get(attribute, 0.0) for n in nodes])
