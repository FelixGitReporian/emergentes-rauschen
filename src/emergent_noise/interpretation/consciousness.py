"""
interpretation/consciousness.py – Bewusstseins- und Proto-Leben-Marker (Epic 8).

Dieses Modul implementiert heuristische Marker für Bewusstseins-Theorien
und Proto-Leben-Kriterien. Es ist ein vorsichtiges Forschungswerkzeug,
KEIN Nachweis von Bewusstsein oder Leben.

Implementierte Marker:

1. Φ-Proxy (IIT-Näherung):
   Integrierte Information nach Tononi et al. (stark vereinfacht).
   Misst, wie viel Information ein System als Ganzes integriert
   über das hinaus, was seine Teile einzeln liefern.

2. Active-Inference-Marker (Friston):
   Prädiktion-Fehler und Selbstmodellierungs-Ansätze.
   Misst, ob das System Vorhersagen über seinen eigenen Zustand macht.

3. Proto-Leben-Score (Arbeitsmappe Kap. 13.1):
   Strukturierter Score über 6 Kriterien (Grenzen, Energiefluss,
   Selbsterhaltung, Adaptation, Gedächtnis, Variation).

4. Global-Workspace-Proxy (Baars/Dehaene):
   Misst, ob Information lokal konzentriert ist (wie im globalen Workspace).

Wissenschaftliche Vorsicht:
    Alle Marker sind HEURISTIKEN, keine validierten wissenschaftlichen Maße.
    Hohe Scores bedeuten 'strukturell interessant', NICHT 'bewusst' oder 'lebendig'.
    Diese Module dienen der Exploration und dem Lernen über Theorien,
    nicht dem Belegen von Bewusstseinsansprüchen.

Quellen und Weiterführung:
    - Tononi, G. (2004). An information integration theory of consciousness.
      BMC Neuroscience, 5, 42. https://doi.org/10.1186/1471-2202-5-42
    - Friston, K. (2010). The free-energy principle: a unified brain theory?
      Nature Reviews Neuroscience, 11, 127–138.
    - Walker, S.I. & Davies, P.C.W. (2013). The algorithmic origins of life.
      Journal of the Royal Society Interface, 10, 20120869.
    - Arbeitsmappe Kap. 13: Leben, Intelligenz und Bewusstsein als Forschungsstrang
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.ndimage import label


@dataclass
class ConsciousnessMarkers:
    """Vollständiges Ergebnis aller Bewusstseins-Marker für einen Tick.

    Attribute
    ----------
    tick:
        Simulationsschritt.
    phi_proxy:
        Normalisierter Φ-Proxy (IIT-Näherung) [0, 1].
    active_inference_score:
        Active-Inference-Marker (Prädiktion-Fehler-basiert) [0, 1].
    proto_life_score:
        Proto-Leben-Score über 6 Kriterien [0, 1].
    global_workspace_score:
        Global-Workspace-Proxy (lokale Information) [0, 1].
    integrated_score:
        Gewichteter Gesamt-Score [0, 1].
    criteria:
        Detaillierte Einzel-Kriterien.
    """

    tick: int
    phi_proxy: float
    active_inference_score: float
    proto_life_score: float
    global_workspace_score: float
    integrated_score: float
    criteria: Dict[str, float]


class ConsciousnessAnalyzer:
    """Berechnet Bewusstseins- und Proto-Leben-Marker aus GridState-Daten.

    Parameters
    ----------
    prediction_window:
        Länge des Vorher-Nachher-Vergleichsfensters für Active Inference.
    """

    def __init__(self, prediction_window: int = 5) -> None:
        self.prediction_window = prediction_window
        self._history: List[dict] = []
        self.marker_history: List[ConsciousnessMarkers] = []

    def analyze(self, state) -> ConsciousnessMarkers:
        """Berechne alle Marker für den aktuellen GridState.

        Parameters
        ----------
        state:
            GridState-Objekt mit energy, coherence, memory, information,
            coupling, reactivity, flow_x, flow_y.

        Returns
        -------
        ConsciousnessMarkers mit allen berechneten Werten.
        """
        # Snapshot für Verlauf
        snap = {
            "tick":      state.tick,
            "energy":    state.energy.copy(),
            "coherence": state.coherence.copy(),
            "memory":    state.memory.copy(),
        }
        self._history.append(snap)
        if len(self._history) > self.prediction_window + 2:
            self._history.pop(0)

        phi    = self._compute_phi_proxy(state)
        ai     = self._compute_active_inference(state)
        pl     = self._compute_proto_life(state)
        gw     = self._compute_global_workspace(state)
        criteria = self._compute_criteria(state)

        integrated = round(
            0.3 * phi + 0.2 * ai + 0.3 * pl + 0.2 * gw, 4
        )

        markers = ConsciousnessMarkers(
            tick=state.tick,
            phi_proxy=phi,
            active_inference_score=ai,
            proto_life_score=pl,
            global_workspace_score=gw,
            integrated_score=integrated,
            criteria=criteria,
        )
        self.marker_history.append(markers)
        return markers

    def _compute_phi_proxy(self, state) -> float:
        """Vereinfachter Φ-Proxy (IIT-Näherung).

        Idee: Φ misst, wie stark das System als Ganzes mehr Information
        integriert als seine Teile einzeln. Hier: Differenz zwischen
        globaler MI (energy × coherence) und Summe lokaler Varianzen.

        Stark vereinfacht: Φ_proxy ≈ global_coherence × (1 - mean_local_variance)
        Normalisiert auf [0, 1].

        Wissenschaftliche Vorsicht: Dies ist KEIN echter IIT-Φ-Wert.
        Echter Φ ist NP-schwer zu berechnen und erfordert kausale Struktur.
        """
        # Globale Kohärenz (Integration aller Felder)
        global_coh = float(state.coherence.mean())

        # Lokale Varianz (Maß für lokale Fragmentierung)
        from scipy.ndimage import uniform_filter
        local_mean = uniform_filter(state.energy.astype(np.float64), size=5)
        local_var = float(np.mean((state.energy - local_mean) ** 2))
        local_var_norm = min(local_var / 0.25, 1.0)

        # MI-Proxy: Kohärenz × Information
        mi_proxy = float(state.coherence.mean() * state.information.mean())

        phi = float(global_coh * (1 - local_var_norm) * (1 + mi_proxy)) / 2.0
        return round(np.clip(phi, 0.0, 1.0), 4)

    def _compute_active_inference(self, state) -> float:
        """Active-Inference-Marker (Friston Free-Energy Proxy).

        Friston's Free-Energy-Prinzip: Biologische Systeme minimieren
        Vorhersage-Fehler über ihr internes Modell der Welt.

        Hier: Wie gut 'erinnert' sich das System an seinen letzten Zustand?
        Proxy = Korrelation zwischen memory und aktuellem Energiefeld.
        Hohes memory-energy-Overlap → System hat internes Modell.

        Wissenschaftliche Vorsicht: Dies ist ein sehr grober Proxy.
        """
        if len(self._history) < 2:
            return 0.0

        memory_flat = state.memory.ravel()
        energy_flat = state.energy.ravel()

        # Korrelation als Proxy für Vorhersage-Güte
        if memory_flat.std() < 1e-6 or energy_flat.std() < 1e-6:
            return 0.0
        corr = float(np.corrcoef(memory_flat, energy_flat)[0, 1])
        return round(np.clip((corr + 1) / 2, 0.0, 1.0), 4)  # Normalisiert [0,1]

    def _compute_proto_life(self, state) -> float:
        """Proto-Leben-Score basierend auf 6 Kriterien (Arbeitsmappe Kap. 13.1).

        Kriterien (je 1/6 Punkt):
        1. Grenze/Kompartiment: Es gibt abgegrenzte Energie-Regionen.
        2. Energiefluss-Regulation: Reaktivität ist nicht homogen.
        3. Selbsterhaltung: Gedächtnis > 0 (Strukturhistorie).
        4. Adaptive Reaktion: Kohärenz reagiert auf Energie.
        5. Gedächtnis/Strukturhistorie: Gedächtnis nicht leer.
        6. Variation: genome_strength hat Diversität (wenn vorhanden).
        """
        score = 0.0

        # 1. Kompartimentierung
        mask = state.energy > 0.6
        labeled, n_comp = label(mask)
        if n_comp >= 1 and mask.sum() > 4:
            score += 1 / 6

        # 2. Reaktivitäts-Regulation (Nicht-Homogenität)
        if state.reactivity.std() > 0.05:
            score += 1 / 6

        # 3. Selbsterhaltung (Gedächtnis-Inhalt)
        if state.memory.mean() > 0.02:
            score += 1 / 6

        # 4. Adaptive Kohärenz-Kopplung
        corr_ec = float(np.corrcoef(state.energy.ravel(), state.coherence.ravel())[0, 1])
        if abs(corr_ec) > 0.2:
            score += 1 / 6

        # 5. Strukturhistorie (Gedächtnis-Entropie > 0)
        hist, _ = np.histogram(state.memory, bins=8, range=(0, 1))
        hist = hist / max(hist.sum(), 1)
        h = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-12))
        if h > 1.0:
            score += 1 / 6

        # 6. Variation (Regelgenom-Diversität, falls vorhanden)
        if hasattr(state, "genome_strength") and state.genome_strength.std() > 0.01:
            score += 1 / 6

        return round(float(score), 4)

    def _compute_global_workspace(self, state) -> float:
        """Global-Workspace-Proxy (Baars/Dehaene).

        Global Workspace Theory: Bewusstsein entspricht einer
        'globalen Ausstrahlung' von Information aus einem lokalen
        Fokusbereich an den Rest des Systems.

        Proxy: Gibt es eine Region mit stark überdurchschnittlicher
        Informationsdichte, die das Gesamtmuster dominiert?
        → Gini-Koeffizient der Information (Ungleichheitsmaß).

        Hoher Gini = dominante Informationsquelle = GW-ähnlich.

        Wissenschaftliche Vorsicht: Gini ≠ GWT-Bewusstsein.
        """
        info = state.information.ravel()
        if info.max() < 1e-6:
            return 0.0
        # Gini-Koeffizient
        sorted_info = np.sort(info)
        n = len(sorted_info)
        cumsum = np.cumsum(sorted_info)
        gini = float(
            (2 * np.sum(np.arange(1, n + 1) * sorted_info) - (n + 1) * cumsum[-1])
            / (n * cumsum[-1] + 1e-12)
        )
        return round(np.clip(gini, 0.0, 1.0), 4)

    def _compute_criteria(self, state) -> Dict[str, float]:
        """Alle Einzel-Kriterien als Dictionary."""
        from scipy.ndimage import label as scipy_label

        mask = state.energy > 0.6
        _, n_comp = scipy_label(mask)

        return {
            "compartments":      int(n_comp),
            "reactivity_std":    round(float(state.reactivity.std()), 5),
            "memory_mean":       round(float(state.memory.mean()), 5),
            "energy_coh_corr":   round(float(np.corrcoef(
                state.energy.ravel(), state.coherence.ravel())[0, 1]), 4),
            "information_mean":  round(float(state.information.mean()), 5),
            "coherence_mean":    round(float(state.coherence.mean()), 5),
            "genome_std":        round(float(
                state.genome_strength.std()
                if hasattr(state, "genome_strength") else 0.0
            ), 5),
        }
