"""
interpretation/narratives.py – Sprachliche Interpretation von Zustandsregimen.

Dieses Modul erzeugt narrative Beschreibungen von Simulationszuständen:
- Wahrscheinliche Vergangenheit des beobachteten Zustands
- Mögliche Zukunftspfade
- Metaphorische Familien (Stern-artig, Zell-artig, Wellen-artig, ...)

Wissenschaftliche Vorsicht:
    Alle Narrativen sind *Lesarten*, keine Wahrheitsetiketten.
    Sie dienen der Hypothesenbildung und Intuitionspflege, nicht als
    Faktenaussagen über physikalische Realität. Jede Beschreibung
    enthält explizite Vorsichtsformulierungen.

Orientierung an Arbeitsmappe Kap. 12 (Interpretationslayer):
    - Keine absolute Wahrheitsetikettierung
    - Mehrere alternative Deutungen
    - Sprachliche Mittel: „deutet auf", „könnte", „ist kompatibel mit"
    - Konfidenz-Angabe bei jeder Interpretation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from emergent_noise.interpretation.regime_classifier import RegimeResult, RegimeType


@dataclass
class Narrative:
    """Vollständige narrative Interpretation eines Simulationszustands.

    Folgt dem JSON-Schema aus Arbeitsmappe Kap. 11.3.
    """

    tick: int
    observed_regime: str
    interpretations: List[str]   # Metaphorische Familien
    likely_past: List[str]       # Wahrscheinliche Vorgeschichte
    likely_future: List[str]     # Mögliche Zukunftspfade
    confidence: float
    scientific_caveat: str       # Pflicht-Vorsichtshinweis


# ------------------------------------------------------------------
# Interpretationsfamilien (Arbeitsmappe Kap. 12.2)
# ------------------------------------------------------------------

_INTERPRETATIONS: dict[RegimeType, list[str]] = {
    RegimeType.QUIESCENT: [
        "vakuum-artig (minimale freie Energie)",
        "Ruhezustand nach Dissipation",
        "homogenes Substrat vor Symmetriebrechung",
    ],
    RegimeType.DIFFUSE: [
        "thermisch-chaotisch (hohe effektive Temperatur)",
        "Rauschen-dominierter Zustand",
        "Übergangsphase zwischen stabilen Mustern",
    ],
    RegimeType.CLUSTERED: [
        "zell-artig (lokale Kompartimente, proto-Membranen)",
        "molekulare Aggregation (Cluster-Bildung)",
        "Inseln geordneter Aktivität in chaotischer Umgebung",
    ],
    RegimeType.VORTEX: [
        "wirbel-artig (Rotation, Zirkulation)",
        "sternartig (radiale Anziehung + Rotation)",
        "turbulente Strömung (aktiver Transport)",
    ],
    RegimeType.COHERENT: [
        "kristall-artig (langreichweitige Ordnung)",
        "proto-Organismus-artig (kohärente, selbsterhaltende Struktur)",
        "Attraktor-Zustand (dynamisches Gleichgewicht)",
    ],
    RegimeType.FILAMENTARY: [
        "netzwerk-artig (Filamente, Synapsen-artige Verbindungen)",
        "reaktions-diffusions-artig (Turing-Muster, Streifen/Flecken)",
        "kosmisch-artig (Filamente der großräumigen Struktur)",
    ],
    RegimeType.CRITICAL: [
        "phasenübergangs-artig (kritischer Punkt, Bifurkation)",
        "metastabiler Zustand (auf Kippe zwischen Regimen)",
        "selbst-organisierte Kritikalität (SOC-ähnlich)",
    ],
    RegimeType.COMPLEX: [
        "chimären-artig (Koexistenz verschiedener Ordnungen)",
        "Übergangsphase mit mehreren gleichzeitigen Dynamiken",
        "komplexes adaptives System in Transition",
    ],
    RegimeType.UNKNOWN: [
        "nicht klassifizierbar mit aktuellen Metriken",
    ],
}

# ------------------------------------------------------------------
# Wahrscheinliche Vergangenheit
# ------------------------------------------------------------------

_LIKELY_PAST: dict[RegimeType, list[str]] = {
    RegimeType.QUIESCENT: [
        "Dissipation eines vorherigen aktiven Regimes",
        "Energie-Zerfall ohne ausreichenden Rauschen-Input",
        "vollständige Homogenisierung durch Diffusion",
    ],
    RegimeType.DIFFUSE: [
        "Aufbrechen eines zuvor kohärenten Clusters",
        "Energiezufuhr ohne ausreichende Kopplung",
        "Symmetriebrechung aus quieszentem Zustand",
    ],
    RegimeType.CLUSTERED: [
        "Lokale Energiekonzentration durch Reaktions-Diffusion",
        "Kopplung hat Keimzentren gebildet",
        "diffuses Regime hat sich in Inseln geordnet",
    ],
    RegimeType.VORTEX: [
        "Energiegradient hat Fluss initiiert",
        "Kopplung hat Rotationskeime erzeugt (Curl-Instabilität)",
        "Übergang aus Cluster-Regime mit Flussdynamik",
    ],
    RegimeType.COHERENT: [
        "Cluster-Regime hat sich durch Kopplung konsolidiert",
        "Selbstverstärkungs-Schleife (Kohärenz→Kopplung→Kohärenz)",
        "langsame Annäherung an Attraktor über viele Ticks",
    ],
    RegimeType.FILAMENTARY: [
        "Reaktions-Diffusions-Instabilität (Turing-Typ)",
        "Elongation eines Clusters durch anisotropen Fluss",
        "Filamentaufbau durch Kopplung entlang Energiegradienten",
    ],
    RegimeType.CRITICAL: [
        "System nähert sich von stabiler Phase aus",
        "externe Störung (Rauschen) hat Bifurkation ausgelöst",
        "Parameter-Drift in die Nähe des kritischen Punktes",
    ],
    RegimeType.COMPLEX: [
        "mehrere gleichzeitige Transitions-Prozesse",
        "Koexistenz verschiedener Regime in räumlich getrennten Bereichen",
    ],
    RegimeType.UNKNOWN: ["Vorgeschichte nicht rekonstruierbar"],
}

# ------------------------------------------------------------------
# Mögliche Zukunftspfade
# ------------------------------------------------------------------

_LIKELY_FUTURE: dict[RegimeType, list[str]] = {
    RegimeType.QUIESCENT: [
        "Verbleib im Ruhezustand (stabiler Attraktor)",
        "Symmetriebrechung durch Rauschen → diffuses Regime",
        "Aufbau neuer Cluster bei veränderten Parametern",
    ],
    RegimeType.DIFFUSE: [
        "Zerfall ins Quieszente (Dissipation überwiegt)",
        "Selbstorganisation in Cluster-Regime",
        "kritischer Übergang bei günstiger Fluktuations-Phase",
    ],
    RegimeType.CLUSTERED: [
        "Konsolidierung zu kohärentem Regime",
        "Aufbrechen in diffuses Regime",
        "stabile Koexistenz mehrerer Cluster (persistent)",
    ],
    RegimeType.VORTEX: [
        "Stabilisierung als persistenter Wirbel",
        "Zerfall durch Dämpfung → diffuses Regime",
        "Verschmelzung mit benachbarten Clustern",
    ],
    RegimeType.COHERENT: [
        "persistente Stabilität (Attraktor)",
        "langsame Erosion durch Rauschen → Cluster-Regime",
        "Aufspaltung bei Parametervariationen",
    ],
    RegimeType.FILAMENTARY: [
        "Fragmentierung der Filamente → Cluster",
        "Verstärkung zum Netzwerk-Regime",
        "Kollaps ins Quieszente bei Energieverlust",
    ],
    RegimeType.CRITICAL: [
        "Übergang in kohärentes Regime (Ordnungsphase)",
        "Übergang in diffuses Regime (Unordnungsphase)",
        "Verbleib nahe kritischem Punkt (SOC)",
    ],
    RegimeType.COMPLEX: [
        "Auflösung in dominantes Einzel-Regime",
        "persistente Komplexität (mehrere Attraktoren koexistieren)",
    ],
    RegimeType.UNKNOWN: ["Zukunft nicht vorhersagbar"],
}

_CAVEAT = (
    "Wissenschaftlicher Hinweis: Diese Interpretation ist eine heuristische Lesart "
    "auf Basis von Feldmetriken. Sie ist kein Beweis für spezifische physikalische, "
    "biologische oder bewusstseinsbezogene Prozesse. Alle Beschreibungen sind Hypothesen "
    "und Modelle, nicht Fakten."
)


def build_narrative(regime_result: RegimeResult) -> Narrative:
    """Erzeuge ein vollständiges Narrativ aus einem RegimeResult.

    Parameters
    ----------
    regime_result:
        Ausgabe von ``classify_regime``.

    Returns
    -------
    Narrative mit Interpretationen, Vergangenheit, Zukunft und Vorsichtshinweis.
    """
    rtype = regime_result.primary_regime
    interps = _INTERPRETATIONS.get(rtype, ["unbekannt"])
    # Sekundäre Regime ergänzen die Interpretationen
    for sec in regime_result.secondary_regimes[:2]:
        extras = _INTERPRETATIONS.get(sec, [])
        if extras:
            interps = interps + [extras[0]]

    return Narrative(
        tick=regime_result.tick,
        observed_regime=rtype.value,
        interpretations=interps,
        likely_past=_LIKELY_PAST.get(rtype, ["unbekannt"]),
        likely_future=_LIKELY_FUTURE.get(rtype, ["unbekannt"]),
        confidence=regime_result.confidence,
        scientific_caveat=_CAVEAT,
    )
