# ADR-0004: Partikel-Feld-Hybrid als vektorisiertes Array-System

**Status:** Accepted  
**Datum:** 2026-05-08  
**Autor:** FelixGitReporian  
**Bezug:** Arbeitsmappe Kap. 10.3, 13.1 – Partikel-Feld-Hybrid

---

## Kontext

Das bestehende System ist ein reines Gitterautomaten-System. Arbeitsmappe
Kap. 10.3 fordert ergänzend Partikel, die sich durch Felder bewegen und
Felder verändern — für Verdichtung, Kollision, Schwärme, aktive Materie
und proto-zelluläre Dynamiken.

---

## Entscheidung

### Repräsentation

Partikel werden als **vektorisierte NumPy-Arrays** der Form `(N,)` oder
`(N, 2)` gespeichert — kein Python-Objekt pro Partikel.

| Array            | Form     | Bedeutung                          |
|------------------|----------|------------------------------------|
| `positions`      | (N, 2)   | kontinuierliche (y, x)-Koordinaten |
| `velocities`     | (N, 2)   | (vy, vx)-Geschwindigkeit           |
| `energy`         | (N,)     | Partikel-Energie                   |
| `mass`           | (N,)     | Trägheit / Aggregationszähler      |
| `active`         | (N,)     | bool-Maske aktiver Partikel        |
| `age`            | (N,)     | Ticks seit Entstehung              |

**Begründung:**
- Vollständig vektorisierbar, keine Python-Loops außer Kollisionserkennung.
- Inaktive Partikel bleiben im Array (aktiv-Maske statt Entfernen).
- Maximalgröße ist fest → kein dynamisches Re-Allozieren.

### Kopplung (bidirektional)

**Feld → Partikel:**
1. Energie-Gradient-Attraktion via bilinearer Interpolation.
2. Fluss-Transport (Drag-Term).
3. Energie-Absorption (Partikel ziehen Energie vom Feld ab).
4. Reaktivitäts-Aktivierung (hohe Reaktivität beschleunigt Partikel).

**Partikel → Feld:**
1. Energie-Deposition (`np.add.at`).
2. Materie-Deposition.
3. Kopplungs-Verstärkung durch Dichte.
4. Information-Injektion.

### Kollision

Einfaches O(N²) Paar-Scanning über aktive Partikel mit periodischen
Randbedingungen. Fusion: schwereres Partikel absorbiert leichteres,
Masse-gewichtete Position + Impuls, Energie addiert.

Performance-Grenze: ~500 Partikel. Für größere Systeme → spatial hashing
(Epic 5+).

### Proto-Kompartiment-Erkennung (analysis/compartments.py)

Zwei Methoden:
- **Feldbasiert**: verbundene Energie-Regionen (SciPy `label`) mit Kopplung
  und Compactness-Filterung + heuristischer Proto-Leben-Score.
- **Partikelbasiert**: Partikel mit `mass >= min_mass` als Aggregat-Marker,
  geglättete Dichtekarte.

---

## Verworfene Alternativen

| Alternative | Grund für Ablehnung |
|-------------|---------------------|
| Python-Objekte pro Partikel | ~100× langsamer, kein numpy-Broadcasting |
| Separates Simulations-Framework (PyBullet, etc.) | Zu viel Overhead, schwer mit Gitter zu koppeln |
| Partikel direkt in GridState | Vermischt Kontinuum- und Diskret-Welt; sauberere Trennung bevorzugt |

---

## Konsequenzen

**Positiv:**
- Reiche Interaktion: Partikel reagieren auf Felder, Felder auf Partikel.
- Proto-zelluläre Aggregate entstehen durch Kollision + Feldkopplung.
- `particles_enabled`-Toggle: System vollständig abschaltbar.
- Vollständig in Tab 3 des Dashboards sichtbar.

**Negativ / Risiken:**
- Kollisionserkennung O(N²): performance-kritisch bei N > 200.
- Physik ist bewusst vereinfacht (kein Impulserhalt, keine Energie-Erhaltung).

---

## Wissenschaftliche Vorsicht

Das Partikel-System ist eine explorative Abstraktion, kein physikalisches
Modell. Proto-Leben-Scores sind strukturelle Proxies, kein Nachweis von
Lebensprozessen. Emergente Aggregate sind interessante Phänomene, keine
biologischen Organismen.
