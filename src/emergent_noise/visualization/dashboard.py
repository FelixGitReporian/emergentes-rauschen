"""
visualization/dashboard.py – Streamlit Live-Dashboard (v0.3.0).

Startet eine interaktive Echtzeit-Visualisierung der Simulation mit
vollständiger Spurenlese-Integration (Epic 2).

Verwendung:
    streamlit run src/emergent_noise/visualization/dashboard.py

Tabs:
    1. 🔬 Simulation  – Live-Heatmap, RGB-Composite, Entropie-Zeitreihe,
                        Persistenz, Cluster, Phasenindikator.
    2. 🧭 Spurenlesen – Regime-Klassifikation, Narrativ (Vergangenheit /
                        Zukunft / Metaphern), Morphologie, MI-Matrix,
                        vollständiger JSON-TraceReport.

Architektur:
    - Alle Parameter sind über die linke Sidebar live konfigurierbar.
    - Die Spurenlese-Analyse läuft alle ``trace_interval`` Ticks oder
      manuell per Button.
    - Das Dashboard ist deterministisch: gleicher Seed, gleiche Sequenz.

Wissenschaftliche Vorsicht:
    Regime-Labels, Narrative und alle Interpretationen sind heuristische
    Lesarten, keine Wahrheitsetiketten. Konfidenzwerte sind Schätzungen.
"""

from __future__ import annotations

import time
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from emergent_noise.analysis.attractors import (
    PersistenceTracker,
    compute_phase_indicator,
    find_clusters,
)
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.analysis.morphology import compute_morphology
from emergent_noise.analysis.mutual_information import mi_matrix
from emergent_noise.analysis.trace_reading import TraceReport, read_traces
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.interpretation.regime_classifier import RegimeType


# ------------------------------------------------------------------
# Seitenkonfiguration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Emergentes Rauschen",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌀 Emergentes Rauschen — Live-Dashboard")
st.caption("Offene Simulations- und Interpretationsmaschine für emergente Zustandsfelder.")


# ------------------------------------------------------------------
# Sidebar – Konfiguration
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Simulation Config")

    seed = st.number_input("Seed", value=42, min_value=0, step=1)
    height = st.slider("Grid Höhe", 16, 256, 64, step=16)
    width = st.slider("Grid Breite", 16, 256, 64, step=16)

    st.subheader("Diffusion")
    diff_energy = st.slider("diffusion_energy", 0.0, 0.5, 0.2, step=0.01)
    diff_info = st.slider("diffusion_information", 0.0, 0.3, 0.05, step=0.005)

    st.subheader("Reaktion")
    react_thresh = st.slider("reaction_energy_threshold", 0.3, 1.0, 0.7, step=0.05)
    react_strength = st.slider("reaction_strength", 0.0, 0.5, 0.1, step=0.01)

    st.subheader("Kopplung")
    coup_gain = st.slider("coupling_gain", 0.0, 0.1, 0.01, step=0.002)
    coup_loss = st.slider("coupling_loss", 0.0, 0.2, 0.05, step=0.005)
    coup_sync = st.slider("coupling_sync_rate", 0.0, 0.2, 0.05, step=0.005)

    st.subheader("Fluss")
    flow_grad = st.slider("flow_gradient_strength", 0.0, 0.5, 0.1, step=0.01)
    flow_damp = st.slider("flow_damping", 0.5, 1.0, 0.95, step=0.01)
    flow_adv = st.slider("flow_advection_rate", 0.0, 0.2, 0.05, step=0.005)
    flow_curl = st.slider("flow_curl_strength", 0.0, 0.2, 0.03, step=0.005)

    st.subheader("Gedächtnis")
    mem_decay = st.slider("memory_decay", 0.5, 1.0, 0.97, step=0.01)
    mem_imprint = st.slider("memory_imprint_strength", 0.0, 1.0, 0.3, step=0.05)

    st.subheader("Rauschen")
    noise_amp = st.slider("noise_amplitude", 0.0, 0.2, 0.02, step=0.005)
    noise_scale = st.slider("noise_scale", 1.0, 32.0, 8.0, step=1.0)

    st.subheader("Reaktivität")
    react_rec = st.slider("reactivity_recovery", 0.8, 1.0, 0.98, step=0.005)
    react_rest = st.slider("reactivity_rest", 0.0, 1.0, 0.5, step=0.05)

    st.subheader("Materie")
    mat_erosion = st.slider("matter_erosion_rate", 0.0, 0.2, 0.02, step=0.005)
    mat_deposit = st.slider("matter_deposition_rate", 0.0, 0.1, 0.005, step=0.001)

    st.subheader("Visualisierung")
    view_field = st.selectbox(
        "Anzuzeigendes Feld",
        ["energy", "matter", "information", "coupling", "reactivity",
         "memory", "coherence", "flow_x", "flow_y"],
        index=0,
    )
    steps_per_frame = st.slider("Schritte pro Frame", 1, 20, 3)
    max_history = st.slider("Entropie-Verlauf (Ticks)", 50, 500, 200)

    st.subheader("🧭 Spurenlesen")
    trace_interval = st.slider(
        "Spurenanalyse alle N Ticks", 5, 200, 25, step=5,
        help="Alle N Ticks wird eine vollständige Spurenanalyse durchgeführt."
    )
    show_mi_heatmap = st.checkbox("MI-Matrix anzeigen", value=True)
    show_morphology = st.checkbox("Morphologie anzeigen", value=True)


# ------------------------------------------------------------------
# Session State initialisieren
# ------------------------------------------------------------------
def _build_config() -> SimConfig:
    """Erstelle SimConfig aus aktuellen Sidebar-Werten."""
    return SimConfig(
        height=height, width=width, seed=int(seed),
        diffusion_energy=diff_energy, diffusion_information=diff_info,
        reaction_energy_threshold=react_thresh, reaction_strength=react_strength,
        coupling_gain=coup_gain, coupling_loss=coup_loss, coupling_sync_rate=coup_sync,
        flow_gradient_strength=flow_grad, flow_damping=flow_damp,
        flow_advection_rate=flow_adv, flow_curl_strength=flow_curl,
        memory_decay=mem_decay, memory_imprint_strength=mem_imprint,
        noise_amplitude=noise_amp, noise_scale=noise_scale,
        reactivity_recovery=react_rec, reactivity_rest=react_rest,
        matter_erosion_rate=mat_erosion, matter_deposition_rate=mat_deposit,
    )


if "sim_state" not in st.session_state:
    cfg = _build_config()
    st.session_state.sim_state = GridState.initialize(cfg)
    st.session_state.sim_config = cfg
    st.session_state.loop = TickLoop(cfg)
    st.session_state.running = False
    st.session_state.entropy_history: deque = deque(maxlen=max_history)
    st.session_state.tracker = PersistenceTracker(window=20)
    st.session_state.last_trace: TraceReport | None = None
    st.session_state.last_trace_tick: int = -1


# ------------------------------------------------------------------
# Steuerknöpfe
# ------------------------------------------------------------------
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("▶ Start"):
        st.session_state.running = True
with col_btn2:
    if st.button("⏸ Stop"):
        st.session_state.running = False
with col_btn3:
    if st.button("🔄 Reset"):
        cfg = _build_config()
        st.session_state.sim_state = GridState.initialize(cfg)
        st.session_state.sim_config = cfg
        st.session_state.loop = TickLoop(cfg)
        st.session_state.running = False
        st.session_state.entropy_history = deque(maxlen=max_history)
        st.session_state.tracker = PersistenceTracker(window=20)
        st.session_state.last_trace = None
        st.session_state.last_trace_tick = -1
with col_btn4:
    if st.button("⏭ +1 Tick"):
        st.session_state.loop.step(st.session_state.sim_state)


# ------------------------------------------------------------------
# Simulation ausführen (wenn laufend)
# ------------------------------------------------------------------
state: GridState = st.session_state.sim_state
loop: TickLoop = st.session_state.loop

if st.session_state.running:
    for _ in range(steps_per_frame):
        loop.step(state)

# ------------------------------------------------------------------
# Metriken berechnen
# ------------------------------------------------------------------
fields_dict = state.as_dict()
entropy = state_entropy_summary(state)
st.session_state.entropy_history.append({"tick": state.tick, **entropy})
st.session_state.tracker.update(fields_dict)
phase = compute_phase_indicator(state.tick, fields_dict)
clusters = find_clusters("energy", state.energy, threshold=0.6)

# ------------------------------------------------------------------
# Spurenlese-Trigger: automatisch alle trace_interval Ticks
# ------------------------------------------------------------------
ticks_since_last = state.tick - st.session_state.last_trace_tick
if st.session_state.last_trace is None or ticks_since_last >= trace_interval:
    st.session_state.last_trace = read_traces(
        tick=state.tick,
        fields=fields_dict,
        persistence_tracker=st.session_state.tracker,
    )
    st.session_state.last_trace_tick = state.tick

trace: TraceReport | None = st.session_state.last_trace

# ------------------------------------------------------------------
# Regime-Banner: immer sichtbar oben
# ------------------------------------------------------------------
_REGIME_COLORS: dict[str, str] = {
    "quiescent":   "🔵",
    "diffuse":     "🟡",
    "clustered":   "🟢",
    "vortex":      "🌀",
    "coherent":    "✨",
    "filamentary": "🕸️",
    "critical":    "🔴",
    "complex":     "🔮",
    "unknown":     "⚪",
}

if trace is not None:
    regime_name = trace.regime.get("primary_regime", "unknown")
    confidence  = trace.regime.get("confidence", 0.0)
    icon        = _REGIME_COLORS.get(regime_name, "⚪")
    sec         = ", ".join(trace.regime.get("secondary_regimes", []))
    sec_txt     = f"  ·  sekundär: {sec}" if sec else ""
    st.info(
        f"{icon} **Regime:** `{regime_name}`  "
        f"— Konfidenz {confidence:.0%}{sec_txt}  "
        f"— Tick {trace.tick}",
        icon=None,
    )


# ------------------------------------------------------------------
# Tabs: Simulation | Spurenlesen
# ------------------------------------------------------------------
tab_sim, tab_trace = st.tabs(["🔬 Simulation", "🧭 Spurenlesen"])


# ══════════════════════════════════════════════════════════════════
# TAB 1: Simulation
# ══════════════════════════════════════════════════════════════════
with tab_sim:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader(f"Tick {state.tick:05d} — Feld: `{view_field}`")

        arr = fields_dict[view_field]
        cmap_map = {
            "energy": "inferno", "matter": "YlOrBr", "information": "viridis",
            "coupling": "PuBu", "reactivity": "hot", "memory": "copper",
            "coherence": "cool", "flow_x": "bwr", "flow_y": "bwr",
        }
        vmin, vmax = (-1.0, 1.0) if view_field in ("flow_x", "flow_y") else (0.0, 1.0)

        # Heatmap des gewählten Feldes
        fig_field, ax_field = plt.subplots(figsize=(5, 5))
        im = ax_field.imshow(
            arr, cmap=cmap_map.get(view_field, "viridis"),
            vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest",
        )
        plt.colorbar(im, ax=ax_field, fraction=0.046)
        ax_field.set_title(f"{view_field}  |  mean={arr.mean():.3f}  std={arr.std():.3f}", fontsize=8)
        ax_field.axis("off")
        st.pyplot(fig_field, use_container_width=True)
        plt.close(fig_field)

        # RGB-Composite: energy=R, information=G, coherence=B
        rgb = np.stack([
            np.clip(state.energy, 0, 1),
            np.clip(state.information, 0, 1),
            np.clip(state.coherence, 0, 1),
        ], axis=-1)
        fig_rgb, ax_rgb = plt.subplots(figsize=(5, 5))
        ax_rgb.imshow(rgb, origin="upper", interpolation="nearest")
        ax_rgb.set_title("RGB-Composite: R=energy  G=information  B=coherence", fontsize=8)
        ax_rgb.axis("off")
        st.pyplot(fig_rgb, use_container_width=True)
        plt.close(fig_rgb)

    with col_right:
        st.subheader("📊 Metriken")

        st.metric("Tick", state.tick)
        st.metric(
            "Suszeptibilität",
            f"{phase.susceptibility:.4f}",
            delta="⚠️ Nahe Übergang" if phase.near_transition else "stabil",
        )

        st.write("**Entropie (normalisiert)**")
        for fname, val in entropy.items():
            st.progress(float(val), text=f"{fname}: {val:.3f}")

        st.write("**Feld-Persistenz**")
        for fname, val in st.session_state.tracker.persistence.items():
            st.progress(max(0.0, min(1.0, val)), text=f"{fname}: {val:.4f}")

        st.write("**Energie-Cluster (threshold=0.6)**")
        st.write(
            f"Anzahl: **{clusters.n_clusters}**  |  "
            f"Größter: **{clusters.largest_cluster_size}** Zellen  |  "
            f"Aktiv: **{clusters.cluster_fraction:.1%}**"
        )

    # Entropie-Zeitreihe
    st.subheader("📈 Entropie-Verlauf")
    hist = list(st.session_state.entropy_history)
    if len(hist) > 1:
        ticks_x = [h["tick"] for h in hist]
        fig_ent, ax_ent = plt.subplots(figsize=(10, 3))
        for fname in ["energy", "information", "memory", "coherence"]:
            vals = [h[fname] for h in hist]
            ax_ent.plot(ticks_x, vals, label=fname, linewidth=1.2)
        ax_ent.set_xlabel("Tick")
        ax_ent.set_ylabel("Normalisierte Entropie")
        ax_ent.legend(loc="upper right", fontsize=8)
        ax_ent.grid(True, alpha=0.3)
        st.pyplot(fig_ent, use_container_width=True)
        plt.close(fig_ent)


# ══════════════════════════════════════════════════════════════════
# TAB 2: Spurenlesen
# ══════════════════════════════════════════════════════════════════
with tab_trace:
    if trace is None:
        st.info("Noch keine Spurenanalyse. Simulation starten oder +1 Tick klicken.")
    else:
        # ── Manueller Trigger ──────────────────────────────────────
        if st.button("🔍 Spurenanalyse jetzt ausführen"):
            st.session_state.last_trace = read_traces(
                tick=state.tick,
                fields=fields_dict,
                persistence_tracker=st.session_state.tracker,
            )
            st.session_state.last_trace_tick = state.tick
            trace = st.session_state.last_trace

        st.caption(
            f"Letzte Analyse: Tick {trace.tick}  "
            f"— nächste automatisch bei Tick {st.session_state.last_trace_tick + trace_interval}"
        )

        # ── Regime + Beschreibung ──────────────────────────────────
        st.subheader("🏷️ Regime-Klassifikation")
        r = trace.regime
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Primäres Regime", r.get("primary_regime", "?").upper())
        col_r2.metric("Konfidenz", f"{r.get('confidence', 0):.0%}")
        col_r3.metric("Sekundär", ", ".join(r.get("secondary_regimes", [])) or "—")

        st.write(f"**Beschreibung:** {r.get('description', '')}")

        with st.expander("📐 Evidence-Werte (gemessene Indikatoren)"):
            ev = r.get("evidence", {})
            ev_cols = st.columns(3)
            for i, (k, v) in enumerate(ev.items()):
                ev_cols[i % 3].metric(k, v)

        # ── Narrativ ──────────────────────────────────────────────
        st.subheader("� Narrativ")
        n = trace.narrative
        st.write(f"**Beobachtetes Regime:** `{n.get('observed_regime', '?')}`  "
                 f"  —  Konfidenz: **{n.get('confidence', 0):.0%}**")

        col_n1, col_n2, col_n3 = st.columns(3)

        with col_n1:
            st.write("**Metaphorische Interpretationsfamilien**")
            for item in n.get("interpretations", []):
                st.write(f"- {item}")

        with col_n2:
            st.write("**Wahrscheinliche Vergangenheit**")
            for item in n.get("likely_past", []):
                st.write(f"- {item}")

        with col_n3:
            st.write("**Mögliche Zukunftspfade**")
            for item in n.get("likely_future", []):
                st.write(f"- {item}")

        st.caption(f"⚠️ {n.get('scientific_caveat', '')}")

        # ── Morphologie ───────────────────────────────────────────
        if show_morphology:
            st.subheader("🔷 Morphologie (energy-Feld)")
            m = trace.morphology
            morph_cols = st.columns(4)
            morph_cols[0].metric("Komponenten",     m.get("n_components", 0))
            morph_cols[1].metric("Löcher",           m.get("n_holes", 0))
            morph_cols[2].metric("Euler-Zahl",       m.get("euler_number", 0))
            morph_cols[3].metric("Aktive Fläche",    f"{m.get('active_fraction', 0):.1%}")

            morph_cols2 = st.columns(3)
            morph_cols2[0].metric("Randkomplexität", f"{m.get('boundary_complexity', 0):.3f}")
            morph_cols2[1].metric("Elongation",      f"{m.get('elongation', 1):.2f}")
            morph_cols2[2].metric("Compactness",     f"{m.get('compactness', 0):.3f}")

            # Morphologie-Visualisierung: Schwellwert-Bild des energy-Feldes
            fig_m, axes_m = plt.subplots(1, 2, figsize=(8, 3))
            axes_m[0].imshow(state.energy, cmap="inferno", vmin=0, vmax=1,
                             origin="upper", interpolation="nearest")
            axes_m[0].set_title("energy (raw)", fontsize=8)
            axes_m[0].axis("off")
            binary = (state.energy > 0.5).astype(float)
            axes_m[1].imshow(binary, cmap="gray", vmin=0, vmax=1,
                             origin="upper", interpolation="nearest")
            axes_m[1].set_title("energy > 0.5 (aktive Zellen)", fontsize=8)
            axes_m[1].axis("off")
            st.pyplot(fig_m, use_container_width=True)
            plt.close(fig_m)

        # ── Mutual Information Matrix ──────────────────────────────
        if show_mi_heatmap:
            st.subheader("🔗 Mutual Information zwischen Feldern")
            st.caption(
                "Normalisierte MI in [0,1]. 0 = statistisch unabhängig, "
                "1 = funktional abhängig. Hohe MI ≠ Kausalität."
            )
            mi_raw = trace.mi_matrix  # {"energy|information": 0.35, ...}
            # Namen extrahieren
            field_names_mi = sorted({p for k in mi_raw for p in k.split("|")})
            n_f = len(field_names_mi)
            mi_grid = np.zeros((n_f, n_f))
            for i, fa in enumerate(field_names_mi):
                for j, fb in enumerate(field_names_mi):
                    if fa == fb:
                        mi_grid[i, j] = 1.0
                    else:
                        key = f"{min(fa,fb)}|{max(fa,fb)}"
                        mi_grid[i, j] = mi_raw.get(key, 0.0)

            fig_mi, ax_mi = plt.subplots(figsize=(5, 4))
            im_mi = ax_mi.imshow(mi_grid, cmap="YlOrRd", vmin=0, vmax=1)
            ax_mi.set_xticks(range(n_f))
            ax_mi.set_yticks(range(n_f))
            ax_mi.set_xticklabels(field_names_mi, rotation=45, ha="right", fontsize=8)
            ax_mi.set_yticklabels(field_names_mi, fontsize=8)
            plt.colorbar(im_mi, ax=ax_mi, fraction=0.046)
            ax_mi.set_title("Normalisierte MI (Histogramm-Näherung)", fontsize=8)
            # Werte in Zellen schreiben
            for i in range(n_f):
                for j in range(n_f):
                    ax_mi.text(j, i, f"{mi_grid[i,j]:.2f}",
                               ha="center", va="center", fontsize=6,
                               color="black" if mi_grid[i, j] < 0.6 else "white")
            fig_mi.tight_layout()
            st.pyplot(fig_mi, use_container_width=True)
            plt.close(fig_mi)

        # ── Feldstatistiken ───────────────────────────────────────
        st.subheader("📋 Feldstatistiken (Snapshot)")
        fs = trace.field_summaries
        rows = []
        for fname, stats in fs.items():
            rows.append({
                "Feld": fname,
                "mean": f"{stats['mean']:.4f}",
                "std":  f"{stats['std']:.4f}",
                "min":  f"{stats['min']:.4f}",
                "max":  f"{stats['max']:.4f}",
                "aktiv (>0.5)": f"{stats['active_fraction']:.1%}",
            })
        st.table(rows)

        # ── Phasenübergang ────────────────────────────────────────
        st.subheader("⚡ Phasenübergangs-Indikator")
        ph = trace.phase
        phase_cols = st.columns(3)
        phase_cols[0].metric("Suszeptibilität", f"{ph.get('susceptibility', 0):.5f}")
        phase_cols[1].metric("Energie-Varianz", f"{ph.get('energy_variance', 0):.5f}")
        phase_cols[2].metric(
            "Status",
            "⚠️ Nahe Übergang" if ph.get("near_transition") else "✅ Stabil",
        )

        # ── JSON-Export ───────────────────────────────────────────
        st.subheader("📄 Vollständiger TraceReport (JSON)")
        with st.expander("JSON anzeigen / kopieren"):
            st.code(trace.to_json(), language="json")


# ------------------------------------------------------------------
# Auto-Rerun wenn laufend
# ------------------------------------------------------------------
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
