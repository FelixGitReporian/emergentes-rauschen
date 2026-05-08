"""
visualization/dashboard.py – Streamlit Live-Dashboard (v0.5.0).

Startet eine interaktive Echtzeit-Visualisierung der Simulation mit
vollständiger Spurenlese-Integration (Epic 2) und Partikel-System (Epic 4).

Verwendung:
    streamlit run src/emergent_noise/visualization/dashboard.py

Tabs:
    1. 🔬 Simulation  – Live-Heatmap, RGB-Composite, Entropie-Zeitreihe,
                        Persistenz, Cluster, Phasenindikator.
    2. 🧭 Spurenlesen – Regime-Klassifikation, Narrativ (Vergangenheit /
                        Zukunft / Metaphern), Morphologie, MI-Matrix,
                        vollständiger JSON-TraceReport.
    3. ⚗️ Partikel    – Partikel-System (Epic 4): Positionen, Aggregate,
                        Proto-Kompartimente, Dichtekarte, Statistiken.

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

from emergent_noise.core.initial_conditions import (
    get_initial_condition,
    list_initial_condition_names,
)
from emergent_noise.experiments.presets import (
    ExperimentPreset,
    list_categories,
    list_presets_by_category,
    get_preset,
)
from emergent_noise.analysis.attractors import (
    PersistenceTracker,
    compute_phase_indicator,
    find_clusters,
)
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.analysis.compartments import detect_compartments, particle_compartments
from emergent_noise.analysis.morphology import compute_morphology
from emergent_noise.analysis.mutual_information import mi_matrix
from emergent_noise.analysis.novelty import genome_diversity, genome_entropy
from emergent_noise.analysis.trace_reading import TraceReport, read_traces
from emergent_noise.core.multiscale import MultiscaleController
from emergent_noise.core.agents import AgentConfig, AgentSystem, step_agents
from emergent_noise.core.particles import ParticleConfig, ParticleSystem, step_particles
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.interpretation.consciousness import ConsciousnessAnalyzer
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

    # ── Simulation Gallery ──────────────────────────────────────────
    st.subheader("🧪 Simulation Gallery")
    _categories = ["— manual —"] + list_categories()
    _sel_category = st.selectbox("Preset Category", _categories, key="preset_category")

    _active_preset: ExperimentPreset | None = None
    if _sel_category != "— manual —":
        _cat_presets = list_presets_by_category(_sel_category)
        _sel_preset = st.selectbox(
            "Preset",
            _cat_presets,
            format_func=lambda p: p.title,
            key="preset_choice",
        )
        if _sel_preset is not None:
            _active_preset = _sel_preset
            if _sel_preset.experimental:
                st.warning("⚠️ Experimental preset — interpret results carefully.")
            with st.expander("📋 Preset info", expanded=False):
                st.markdown(f"**{_sel_preset.title}**")
                st.caption(_sel_preset.description)
                st.markdown("**Expected patterns:**")
                for _pat in _sel_preset.expected_patterns:
                    st.markdown(f"- {_pat}")
                st.markdown("**Key parameters:**")
                st.markdown(", ".join(f"`{k}`" for k in _sel_preset.key_parameters))
                st.markdown("**Limitations:**")
                for _lim in _sel_preset.limitations:
                    st.markdown(f"- {_lim}")
            _apply_preset = st.button("▶ Apply Preset & Reset", key="apply_preset_btn")
        else:
            _apply_preset = False
    else:
        _apply_preset = False

    st.divider()

    # ── Manual Initial Condition ────────────────────────────────
    st.subheader("🌱 Initial Condition")
    _ic_names = list_initial_condition_names()
    _sel_ic_name = st.selectbox(
        "Starting pattern",
        _ic_names,
        index=_ic_names.index("none"),
        key="manual_ic",
        help="Applied on Reset / Apply Preset. Injects a structured seed into the initial state.",
    )
    _manual_ic = get_initial_condition(_sel_ic_name) if _sel_ic_name != "none" else None

    st.divider()

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

    st.subheader("⚗️ Partikel (Epic 4)")
    particles_enabled = st.checkbox("Partikel-System aktiv", value=True)
    n_particles = st.slider("Anzahl Partikel", 5, 200, 50, step=5)
    p_field_attr = st.slider("Feld-Attraktion", 0.0, 0.2, 0.05, step=0.005)
    p_flow_drag  = st.slider("Fluss-Drag", 0.0, 1.0, 0.3, step=0.05)
    p_damping    = st.slider("Geschw.-Dämpfung", 0.5, 1.0, 0.92, step=0.01)
    p_coll_radius = st.slider("Kollisionsradius", 0.5, 5.0, 1.5, step=0.5)


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


def _build_particle_config() -> ParticleConfig:
    """Erstelle ParticleConfig aus aktuellen Sidebar-Werten."""
    return ParticleConfig(
        n_particles=n_particles,
        max_particles=max(n_particles * 4, 200),
        field_attraction=p_field_attr,
        flow_drag=p_flow_drag,
        velocity_damping=p_damping,
        collision_radius=p_coll_radius,
        seed=int(seed),
    )


def _apply_preset_to_session(preset: ExperimentPreset) -> None:
    """Reset simulation using the preset config and particle settings."""
    cfg = preset.config
    ps = preset.particle_settings
    pcfg = ParticleConfig(
        n_particles=ps.count,
        max_particles=max(ps.count * 4, 200),
        field_attraction=ps.field_attraction,
        flow_drag=ps.flow_drag,
        velocity_damping=ps.velocity_damping,
        collision_radius=ps.collision_radius,
        min_mass_for_compartment=ps.min_mass_for_compartment,
        seed=cfg.seed,
    )
    ic = preset.initial_condition
    st.session_state.sim_state = GridState.initialize(cfg, initial_condition=ic)
    st.session_state.sim_config = cfg
    st.session_state.loop = TickLoop(cfg)
    st.session_state.running = False
    st.session_state.entropy_history = deque(maxlen=200)
    st.session_state.tracker = PersistenceTracker(window=20)
    st.session_state.last_trace = None
    st.session_state.last_trace_tick = -1
    st.session_state.particles = ParticleSystem(pcfg, cfg.height, cfg.width)
    st.session_state.multiscale = MultiscaleController()
    st.session_state.consciousness = ConsciousnessAnalyzer()
    st.session_state.last_cmarkers = None
    st.session_state.active_preset_id = preset.id
    _policy = "ant" if "ant" in preset.id or "stigmergy" in preset.id else "boids"
    _acfg = AgentConfig(
        n_agents=60, max_agents=240, policy=_policy, seed=cfg.seed
    )
    st.session_state.agents = AgentSystem(_acfg, cfg.height, cfg.width)


if _apply_preset and _active_preset is not None:
    _apply_preset_to_session(_active_preset)
    st.success(f"✅ Preset '{_active_preset.title}' applied — press ▶ Start to run.")

if "sim_state" not in st.session_state:
    cfg = _build_config()
    pcfg = _build_particle_config()
    st.session_state.sim_state = GridState.initialize(cfg)
    st.session_state.sim_config = cfg
    st.session_state.loop = TickLoop(cfg)
    st.session_state.running = False
    st.session_state.entropy_history: deque = deque(maxlen=max_history)
    st.session_state.tracker = PersistenceTracker(window=20)
    st.session_state.last_trace: TraceReport | None = None
    st.session_state.last_trace_tick: int = -1
    st.session_state.particles = ParticleSystem(pcfg, cfg.height, cfg.width)
    st.session_state.multiscale = MultiscaleController()
    st.session_state.consciousness = ConsciousnessAnalyzer()
    st.session_state.last_cmarkers = None
    st.session_state.agents = AgentSystem(
        AgentConfig(n_agents=60, max_agents=240, policy="boids", seed=cfg.seed),
        cfg.height, cfg.width,
    )


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
        pcfg = _build_particle_config()
        st.session_state.sim_state = GridState.initialize(cfg, initial_condition=_manual_ic)
        st.session_state.sim_config = cfg
        st.session_state.loop = TickLoop(cfg)
        st.session_state.running = False
        st.session_state.entropy_history = deque(maxlen=max_history)
        st.session_state.tracker = PersistenceTracker(window=20)
        st.session_state.last_trace = None
        st.session_state.last_trace_tick = -1
        st.session_state.particles = ParticleSystem(pcfg, cfg.height, cfg.width)
        st.session_state.multiscale = MultiscaleController()
        st.session_state.consciousness = ConsciousnessAnalyzer()
        _a_policy = st.session_state.get("agent_policy", "boids")
        st.session_state.agents = AgentSystem(
            AgentConfig(n_agents=60, max_agents=240, policy=_a_policy, seed=cfg.seed),
            cfg.height, cfg.width,
        )
        st.session_state.last_cmarkers = None
with col_btn4:
    if st.button("⏭ +1 Tick"):
        st.session_state.loop.step(st.session_state.sim_state)


# ------------------------------------------------------------------
# Simulation ausführen (wenn laufend)
# ------------------------------------------------------------------
state: GridState = st.session_state.sim_state
loop: TickLoop = st.session_state.loop

particles: ParticleSystem = st.session_state.particles
agents: AgentSystem = st.session_state.agents

multiscale_ctrl: MultiscaleController = st.session_state.multiscale
consciousness_analyzer: ConsciousnessAnalyzer = st.session_state.consciousness

if st.session_state.running:
    for _ in range(steps_per_frame):
        loop.step(state)
        if particles_enabled:
            step_particles(particles, state, do_collisions=True)
        step_agents(agents, state)
    multiscale_ctrl.update(state)
    st.session_state.last_cmarkers = consciousness_analyzer.analyze(state)

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
tab_sim, tab_trace, tab_particles, tab_learn, tab_graph = st.tabs([
    "\U0001f52c Simulation",
    "\U0001f9ed Spurenlesen",
    "\u2697\ufe0f Partikel",
    "\U0001f393 Lernen & Theorie",
    "\U0001f578\ufe0f Graph-Modus",
])


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


# ══════════════════════════════════════════════════════════════
# TAB 3: Partikel
# ══════════════════════════════════════════════════════════════
with tab_particles:
    if not particles_enabled:
        st.info("⚗️ Partikel-System ist deaktiviert. Aktiviere es in der Sidebar.")
    else:
        p_sum = particles.summary()

        # ── Schnellübersicht ─────────────────────────────────────────
        st.subheader("⚗️ Partikel-System")
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        pc1.metric("Aktive Partikel",    p_sum["n_active"])
        pc2.metric("Ø Masse",            f"{p_sum['mean_mass']:.2f}")
        pc3.metric("Max. Masse",         f"{p_sum['max_mass']:.2f}")
        pc4.metric("Ø Geschwindigkeit",  f"{p_sum['mean_speed']:.4f}")
        pc5.metric("Proto-Kompartimente",p_sum["n_compartments"])

        # ── Visualisierung: Partikel über Energie-Heatmap ───────────
        st.subheader("📍 Partikel-Positionen")
        col_pv1, col_pv2 = st.columns(2)

        with col_pv1:
            fig_p, ax_p = plt.subplots(figsize=(5, 5))
            ax_p.imshow(
                state.energy, cmap="inferno", vmin=0, vmax=1,
                origin="upper", interpolation="nearest",
            )
            pos = particles.active_positions()
            masses_arr = particles.active_masses()
            if len(pos) > 0:
                # Größe des Punktes proportional zur Masse, Farbe zur Energie
                sizes = np.clip(masses_arr * 15, 5, 200)
                energies_p = particles.active_energies()
                ax_p.scatter(
                    pos[:, 1], pos[:, 0],  # x=col, y=row
                    c=energies_p, cmap="cool", s=sizes,
                    alpha=0.8, edgecolors="white", linewidths=0.5,
                    vmin=0.0, vmax=1.0,
                )
            ax_p.set_title(
                f"Partikel (• = Energie, Größe ∝ Masse)  |  {len(pos)} aktiv",
                fontsize=8,
            )
            ax_p.axis("off")
            st.pyplot(fig_p, use_container_width=True)
            plt.close(fig_p)

        with col_pv2:
            # Partikel-Dichtekarte
            if len(pos) > 0:
                pc_result = particle_compartments(
                    pos, masses_arr,
                    particles.height, particles.width,
                    min_mass=3.0,
                )
                fig_dens, ax_dens = plt.subplots(figsize=(5, 5))
                im_dens = ax_dens.imshow(
                    pc_result["density_map"], cmap="plasma",
                    origin="upper", interpolation="nearest",
                )
                plt.colorbar(im_dens, ax=ax_dens, fraction=0.046)
                # Kompartiment-Positionen markieren
                comp_pos = pc_result["compartment_positions"]
                if len(comp_pos) > 0:
                    ax_dens.scatter(
                        comp_pos[:, 1], comp_pos[:, 0],
                        marker="*", c="yellow", s=80,
                        label=f"Aggregate (m≥3): {pc_result['n_heavy_particles']}",
                        edgecolors="black", linewidths=0.5,
                    )
                    ax_dens.legend(fontsize=7, loc="upper right")
                ax_dens.set_title("Partikel-Dichtekarte (geglättet)", fontsize=8)
                ax_dens.axis("off")
                st.pyplot(fig_dens, use_container_width=True)
                plt.close(fig_dens)
            else:
                st.info("Keine aktiven Partikel.")

        # ── Feldbasierte Kompartiment-Erkennung ───────────────────
        st.subheader("🧱 Proto-Kompartimente (Feldbasis)")
        comp_result = detect_compartments(
            state, energy_threshold=0.5, coupling_threshold=0.3, min_area=4
        )
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Anzahl Kompartimente",    comp_result.n_compartments)
        cc2.metric("Ø Proto-Leben-Score",      f"{comp_result.mean_proto_life_score:.2f}")
        cc3.metric("Max Proto-Leben-Score",    f"{comp_result.max_proto_life_score:.2f}")

        if comp_result.compartments:
            st.caption(
                "Proto-Leben-Score = Energie > 0.4 + Kopplung > 0.3 + "
                "Fläche ≥ 4 + Compactness > 0.3 (je 0.25 Punkte)."
            )
            rows_table = []
            for c in comp_result.compartments[:10]:  # max 10 anzeigen
                rows_table.append({
                    "ID": c.id,
                    "Fläche": c.area,
                    "Ø Energie": f"{c.mean_energy:.3f}",
                    "Ø Kopplung": f"{c.mean_coupling:.3f}",
                    "Compactness": f"{c.compactness:.3f}",
                    "PL-Score": f"{c.proto_life_score:.2f}",
                })
            st.table(rows_table)

        # ── Regelgenom-Diversität (Epic 3 + 4 Verbindung) ───────
        st.subheader("🧬 Regelgenom-Diversität")
        gdiv = genome_diversity(state)
        gent = genome_entropy(state)
        gcols = st.columns(4)
        gcols[0].metric("strength std",    f"{gdiv['strength_std']:.4f}")
        gcols[1].metric("threshold std",   f"{gdiv['threshold_std']:.4f}")
        gcols[2].metric("joint entropy",   f"{gdiv['joint_entropy']:.3f}")
        gcols[3].metric("strength entropy",f"{gent:.3f}")

        # Genome-Heatmap
        fig_g, axes_g = plt.subplots(1, 2, figsize=(8, 3))
        im_gs = axes_g[0].imshow(
            state.genome_strength, cmap="RdYlGn", vmin=0, vmax=0.3,
            origin="upper", interpolation="nearest",
        )
        axes_g[0].set_title("genome_strength (Reaktionsstärke)", fontsize=8)
        axes_g[0].axis("off")
        plt.colorbar(im_gs, ax=axes_g[0], fraction=0.046)
        im_gt = axes_g[1].imshow(
            state.genome_threshold, cmap="RdYlGn", vmin=0.4, vmax=1.0,
            origin="upper", interpolation="nearest",
        )
        axes_g[1].set_title("genome_threshold (Aktivierungsschwelle)", fontsize=8)
        axes_g[1].axis("off")
        plt.colorbar(im_gt, ax=axes_g[1], fraction=0.046)
        fig_g.tight_layout()
        st.pyplot(fig_g, use_container_width=True)
        plt.close(fig_g)

        st.caption(
            "⚠️ Partikel-Dynamik ist eine vereinfachte Abstraktion (kein Impulserhält, "
            "keine korrekte Physik). Proto-Leben-Scores sind strukturelle Proxies, "
            "kein Nachweis von Lebensprozessen."
        )

        # ── Agent System (Epic 11) ────────────────────────────────
        st.divider()
        st.subheader("🐜 Agent System (Epic 11)")
        st.caption(
            "Echte Agenten mit Heading, Geschwindigkeit und Verhaltenspolitik. "
            "Boids: Separation + Alignment + Kohäsion. Ant: Pheromon-Gradienten-Folgen."
        )

        _astats = agents.stats()
        ac1, ac2, ac3, ac4 = st.columns(4)
        ac1.metric("🐞 Aktive Agenten", _astats["n_active"])
        ac2.metric("💨 Ø Speed",           f"{_astats['mean_speed']:.3f}")
        ac3.metric("🧲 Kohärenz",          f"{_astats['velocity_coherence']:.3f}")
        ac4.metric("🕧 Ø Alter (Ticks)",    f"{_astats['mean_age']:.0f}")

        _aidx = agents._idx()
        if len(_aidx) > 0:
            _a_pos = agents.positions[_aidx]
            _a_col1, _a_col2 = st.columns(2)

            with _a_col1:
                fig_ag, ax_ag = plt.subplots(figsize=(4, 4))
                ax_ag.imshow(
                    state.energy, cmap="viridis", origin="upper",
                    interpolation="nearest", alpha=0.6,
                )
                _speeds = np.sqrt(
                    agents.velocities[_aidx, 0] ** 2 + agents.velocities[_aidx, 1] ** 2
                )
                sc = ax_ag.scatter(
                    _a_pos[:, 1], _a_pos[:, 0],
                    c=_speeds, cmap="hot", s=12,
                    vmin=0, vmax=agents.config.max_speed,
                )
                plt.colorbar(sc, ax=ax_ag, fraction=0.046, label="Speed")
                ax_ag.set_title(
                    f"Agenten ({agents.config.policy}) auf Energiefeld",
                    fontsize=8,
                )
                ax_ag.axis("off")
                st.pyplot(fig_ag, use_container_width=True)
                plt.close(fig_ag)

            with _a_col2:
                fig_hd, ax_hd = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
                ax_hd.hist(
                    agents.heading[_aidx], bins=36,
                    range=(-3.14159, 3.14159), color="steelblue", alpha=0.8,
                )
                ax_hd.set_title("Heading-Verteilung", fontsize=8, pad=15)
                st.pyplot(fig_hd, use_container_width=True)
                plt.close(fig_hd)
        else:
            st.info("Keine aktiven Agenten.")

        st.caption(
            "⚠️ Boids implementiert die drei Reynolds-Regeln (1987). "
            "AntPolicy nutzt das abstrakte Memory-Feld als Pheromon. "
            "Kein Nachweis echter Schwarm- oder Ameisen-Intelligenz."
        )


# ══════════════════════════════════════════════════════════════════════
# TAB 4: LERNEN & THEORIE
# ══════════════════════════════════════════════════════════════════════
with tab_learn:
    st.subheader("🎓 Complex Systems Science & Artificial Life — Live-Lernumgebung")
    st.caption(
        "Alle angezeigten Metriken sind direkt mit wissenschaftlichen Konzepten verknüpft. "
        "Starte die Simulation und beobachte, wie sich Kennzahlen verändern — dann lies tiefer."
    )

    # ── Simulation Gallery ──────────────────────────────────────────────
    st.markdown("### 🧪 Simulation Gallery")
    st.caption(
        "These presets are not exact biological, physical or cognitive simulations. "
        "They are reproducible field experiments designed to explore emergent analogues. "
        "Select a preset in the sidebar to apply it."
    )

    _gallery_cats = list_categories()
    _gallery_tab_labels = _gallery_cats
    _gallery_tabs = st.tabs(_gallery_tab_labels)

    from emergent_noise.experiments.presets import list_presets_by_category as _lpbc

    for _gtab, _gcat in zip(_gallery_tabs, _gallery_cats):
        with _gtab:
            _gpresets = _lpbc(_gcat)
            for _gp in _gpresets:
                with st.expander(
                    f"{'⚠️ ' if _gp.experimental else ''}{_gp.title}",
                    expanded=False,
                ):
                    st.markdown(f"**Description:** {_gp.description}")
                    st.markdown(f"*Inspiration: {_gp.inspiration}*")
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.markdown("**Expected patterns:**")
                        for _ep in _gp.expected_patterns:
                            st.markdown(f"- {_ep}")
                        st.markdown("**Key parameters:**")
                        st.markdown(", ".join(f"`{k}`" for k in _gp.key_parameters))
                        st.markdown("**Suggested metrics:**")
                        for _sm in _gp.suggested_metrics:
                            st.markdown(f"- {_sm}")
                    with col_g2:
                        st.markdown("**Limitations:**")
                        for _lm in _gp.limitations:
                            st.markdown(f"- {_lm}")
                        st.markdown("**Tags:** " + " · ".join(f"`{t}`" for t in _gp.tags))
                        if _gp.experimental:
                            st.warning("⚠️ Experimental preset — results are exploratory.")
                    st.info(
                        f"To run: select **{_gp.category}** → **{_gp.title}** "
                        f"in the sidebar, then click **▶ Apply Preset & Reset**."
                    )

    st.divider()

    # ── Aktuelle Bewusstseins-Marker live ──────────────────────────────
    st.markdown("### 🧠 Live: Bewusstseins- & Proto-Leben-Marker")
    cmark = st.session_state.last_cmarkers
    if cmark is None:
        cmark = consciousness_analyzer.analyze(state)

    lc1, lc2, lc3, lc4, lc5 = st.columns(5)
    lc1.metric("Φ-Proxy (IIT)", f"{cmark.phi_proxy:.3f}",
               help="Integrated Information Theory (Tononi). Misst, wie viel Information "
                    "das System als Ganzes integriert. 0=fragmentiert, 1=maximal integriert.")
    lc2.metric("Active Inference", f"{cmark.active_inference_score:.3f}",
               help="Free-Energy-Prinzip (Friston). Misst Korrelation zwischen Gedächtnis "
                    "und Energiefeld — Proxy für internes Vorhersagemodell.")
    lc3.metric("Proto-Leben", f"{cmark.proto_life_score:.3f}",
               help="6 Kriterien: Grenzen, Energiefluss, Selbsterhaltung, Adaptation, "
                    "Gedächtnis, Variation (je 0.167 Punkte).")
    lc4.metric("Global Workspace", f"{cmark.global_workspace_score:.3f}",
               help="Global Workspace Theory (Baars/Dehaene). Gini-Koeffizient der "
                    "Information: hoher Score = dominante Informationsquelle = GWT-ähnlich.")
    lc5.metric("Integriert", f"{cmark.integrated_score:.3f}",
               help="Gewichteter Gesamt-Score: 0.3×Φ + 0.2×AI + 0.3×PL + 0.2×GW.")

    st.warning(
        "⚠️ **Wissenschaftliche Vorsicht:** Alle Marker sind heuristische Proxies, "
        "kein Nachweis von Bewusstsein oder Leben. Hohe Scores = strukturell interessant, "
        "nicht = bewusst."
    )

    st.divider()

    # ── VERTIEFUNGSEBENEN ───────────────────────────────────────────────
    st.markdown("### 📚 Vertiefungsebenen — wähle deinen Einstieg")

    level = st.radio(
        "Vertiefung",
        ["🟢 Einstieg", "🟡 Mittelstufe", "🔴 Forschungsfront"],
        horizontal=True,
    )

    if level == "🟢 Einstieg":
        st.markdown("""
#### Was du hier siehst

Diese Simulation ist ein **zellulärer Automat** mit mehreren gekoppelten Feldern.
Jede Zelle hat Zustände (Energie, Materie, Information, Kopplung, …),
die sich nach lokalen Regeln von Tick zu Tick verändern.

**Schlüsselkonzepte:**
- **Emergenz**: Komplexe globale Muster entstehen aus einfachen lokalen Regeln.
- **Zellulärer Automat**: Gitter, auf dem Zustandsregeln parallel angewendet werden.
  Conway's Game of Life ist das bekannteste Beispiel.
- **Attraktor**: Zustand, zu dem das System immer wieder zurückkehrt (stables Muster).
- **Regime**: Wiederkehrender Zustandstyp (hier: 8 Regime, z. B. COHERENT, CRITICAL).

**Zum Nachlesen:**
""")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
**Bücher:**
- 📖 *Complexity: A Guided Tour* — Melanie Mitchell *(der beste Einstieg)*
- 📖 *Artificial Life: A Report from the Frontier* — Steven Levy

**Online:**
- 🌐 [The Nature of Code — Cellular Automata](https://natureofcode.com/cellular-automata/)
  *(interaktive visuelle Einführung)*
- 🌐 [Wolfram NKS — A New Kind of Science](https://www.wolframscience.com/nks/pix--preface/)
  *(Wolfram's Hauptwerk, gratis online)*
- 🌐 [Complexity Explorer — ABM-Kurs](https://www.complexityexplorer.org/courses/183-introduction-to-agent-based-modeling)
  *(kostenloser Online-Kurs, Santa Fe Institute)*
""")
        with col_b:
            st.markdown("""
**Interaktive Demos:**
- 🎮 [Lenia — kontinuierliche zelluläre Automaten](https://chakazul.github.io/lenia.html)
  *(schöne Visualisierungen)*
- 🎮 [Avida — digitale Evolution](https://avida.devosoft.org/)
  *(selbstreplizierende Programme, die evolvieren)*

**Podcasts:**
- 🎙️ [Complexity Podcast (SFI)](https://www.iheart.com/podcast/269-complexity-51009523/)
  *(Santa Fe Institute, ~30 Min pro Episode)*
""")

    elif level == "🟡 Mittelstufe":
        st.markdown("""
#### Theoretische Grundlagen

**Integrated Information Theory (IIT, Tononi 2004)**

Bewusstsein = das Maß Φ (Phi) an integrierter Information im System.
Ein System mit Φ > 0 hat irgendeine Form von Erfahrung.
Das Phi hier ist ein **stark vereinfachter Proxy** — echter Phi ist NP-schwer.

**Free-Energy-Prinzip (Friston 2010)**

Biologische Systeme minimieren "Surprise" — die Abweichung zwischen
erwartetem und tatsächlichem Sensorinput. Das führt zu aktivem Verhalten
(Active Inference) und Wahrnehmung. Hier gemessen als Gedächtnis-Energie-Korrelation.

**Global Workspace Theory (Baars/Dehaene)**

Bewusstsein entsteht, wenn Information aus einem lokalen "Hot Spot" global
im Gehirn "ausgesendet" wird. Hier gemessen als Gini-Koeffizient der Information
(Ungleichverteilung = lokale Dominanz = GWT-ähnlich).

**Assembly Theory (Walker/Davies)**

Information ist nicht nur passiv gespeichert — sie ist in den Prozessen kodiert,
die Strukturen aufbauen. Komplexität = Anzahl der benötigten Schritte zum Aufbau.
""")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("""
**Primärquellen:**
- 📄 Tononi (2004): *An information integration theory of consciousness*
  BMC Neuroscience 5, 42
- 📄 Friston (2010): *The free-energy principle: a unified brain theory?*
  Nature Reviews Neuroscience 11, 127–138
- 📄 Walker & Davies (2013): *The algorithmic origins of life*
  J. Royal Society Interface 10, 20120869
""")
        with col_m2:
            st.markdown("""
**Podcasts & Vorträge:**
- 🎙️ [Sara Walker — Information and the Origin of Life](https://www.preposterousuniverse.com/podcast/2020/01/13/79-sara-imari-walker-on-information-and-the-origin-of-life/)
  *(Mindscape Podcast, Sean Carroll)*
- 🎙️ [Sara Walker — Assembling Life in the Universe](https://www.bigbiology.org/episodes/2022/12/1/ep-93-assembling-life-in-the-universe-with-sara-walker)
  *(Big Biology Podcast)*
- 🌐 [OpenWorm — digitaler C. elegans Wurm](https://openworm.org/)
  *(vollständiges Nervensystem simuliert)*
- 🌐 [Framsticks — evolvierte 3D-Kreaturen](https://www.framsticks.com/)
""")

    else:  # 🔴 Forschungsfront
        st.markdown("""
#### Forschungsfront — offene Fragen

**Was dieses System erkundet:**
- Unter welchen Parametern entstehen proto-zelluläre Strukturen mit Grenzen?
- Korrelieren Φ-Proxy und Proto-Leben-Score? *(schaue Tab Partikel)*
- Erzeugt Regel-Evolution (Epic 3) messbar mehr Novelty als statische Regeln?
- Wann entstehen Graph-Kompartimente unabhängig von der initialen Topologie?

**Aktuelle Forschungsrichtungen:**
""")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
**ALife & Complexity:**
- 🏛️ [ALIFE — International Conference on Artificial Life](https://alife.org/)
  *(wichtigste ALife-Konferenz)*
- 🏛️ Santa Fe Institute — Complexity Science
- 📄 *Lenia* (Bert Wang-Chak Chan, 2019) — kontinuierliche CA mit reich. Dynamiken
- 📄 *Neural Cellular Automata* (Mordvintsev et al., 2020)

**Bewusstseinsforschung:**
- IIT 4.0 (Albantakis et al., 2023)
- Global Neuronal Workspace 2.0
- Higher-Order Theories of Consciousness (HOT)
- Quantum Mind Hypothesen (Penrose-Hameroff) *(sehr spekulativ!)*
""")
        with col_r2:
            st.markdown("""
**Experiment-Ideen mit diesem System:**
1. Scanne `coupling_gain` × `memory_decay` → Phi-Proxy-Landschaft
2. Vergleiche Genome-Diversität nach 1000 Ticks mit/ohne Meta-Evolution
3. Messe Proto-Leben-Score als Funktion der Partikel-Kollisionsrate
4. Vergleiche emergente Graphdistanz: small-world vs. scale-free Topologie

**Starte einen Sweep:**
```bash
python -m emergent_noise.experiments.runner -e consciousness_marker_scan
python -m emergent_noise.experiments.runner -e proto_life_parameter_search
```
""")

    st.divider()

    # ── Mehrskalenmodell live ──────────────────────────────────────────
    st.markdown("### 🔭 Live: Mehrskalenmodell (Mikro / Meso / Makro)")
    ms_result = multiscale_ctrl.update(state)

    ms_c1, ms_c2, ms_c3, ms_c4 = st.columns(4)
    ms_c1.metric("Meso-Entitäten",  ms_result["meso"]["n_entities"],
                 help="Verbundene aktive Regionen (Meso-Ebene): Cluster mit Eigendynamik.")
    ms_c2.metric("Gesamtfläche",    ms_result["meso"]["total_area"],
                 help="Summe aller Meso-Cluster-Flächen in Gitterzellen.")
    ms_c3.metric("Ø Meso-Geschw.", f"{ms_result['meso']['mean_velocity']:.5f}",
                 help="Mittlere Bewegungsgeschwindigkeit der Meso-Entitäten (Cluster-Drift).")
    ms_c4.metric("Makro-Übergänge", ms_result["macro"]["n_transitions"],
                 help="Erkannte Phasenübergänge in der Attraktor-Trajektorie (Δ > 0.05).")

    # Attraktor-Trajektorie
    traj = multiscale_ctrl.macro.trajectory_array()
    if len(traj) >= 3:
        fig_traj, ax_traj = plt.subplots(figsize=(5, 3))
        ax_traj.plot(traj[:, 0], traj[:, 1], "o-", markersize=2,
                     alpha=0.7, color="cyan", linewidth=0.8)
        ax_traj.scatter([traj[-1, 0]], [traj[-1, 1]],
                        c="red", s=40, zorder=5, label="Aktuell")
        ax_traj.set_xlabel("Energie (Mittel)", fontsize=8)
        ax_traj.set_ylabel("Kohärenz (Mittel)", fontsize=8)
        ax_traj.set_title("Makro-Attraktor-Trajektorie (Energie × Kohärenz)", fontsize=9)
        ax_traj.legend(fontsize=7)
        ax_traj.grid(True, alpha=0.3)
        st.pyplot(fig_traj, use_container_width=True)
        plt.close(fig_traj)
        st.caption(
            "Jeder Punkt = ein Tick. Die Trajektorie zeigt, wohin das System im "
            "Phasenraum driftet. Spiral- oder Kreisbahn → Attraktor. "
            "Plötzlicher Sprung → Phasenübergang."
        )

    st.divider()

    # ── Glossar ────────────────────────────────────────────────────────
    with st.expander("📖 Begriffe-Glossar (Klick zum Öffnen)"):
        st.markdown("""
| Begriff | Bedeutung |
|---------|-----------|
| **Emergenz** | Makroskopische Eigenschaften, die aus mikroskopischen Regeln entstehen und auf Mikro-Ebene nicht vorhersagbar sind |
| **Attraktor** | Stabiler Zustand, zu dem ein dynamisches System immer wieder zurückkehrt |
| **Bifurkation** | Punkt, an dem ein kleiner Parameterunterschied zu qualitativ verschiedenem Verhalten führt |
| **Zellulärer Automat (CA)** | Gitter aus Zellen, deren Zustände nach lokalen Regeln aktualisiert werden (Conway, Wolfram) |
| **Integrated Information (Φ)** | Tononi's Maß für Bewusstsein: wie viel mehr Information das System als Ganzes hat vs. seine Teile |
| **Free-Energy-Prinzip** | Friston: Systeme minimieren Vorhersage-Fehler durch Wahrnehmung + Handlung (Active Inference) |
| **Global Workspace** | Baars/Dehaene: Bewusstsein = globale Übertragung lokaler Information im Gehirn |
| **Proto-Kompartiment** | Abgegrenzte aktive Region mit innerer Kohärenz — Vorläufer zellulärer Strukturen |
| **Meso-Ebene** | Zwischen Mikro (Zellen) und Makro (Gesamtsystem): Cluster, Membranen, Wellen als Einheiten |
| **Phasenübergang** | Sprunghafte Änderung des Systemverhaltens beim Überschreiten eines Parameterschwellwerts |
| **Small-World-Netzwerk** | Wenige lange Verbindungen + viele lokale Cluster (Watts-Strogatz): effiziente Information-Ausbreitung |
| **Scale-Free-Netzwerk** | Wenige stark vernetzte Hubs + viele schwach vernetzte Knoten (Barabási-Albert): Internetstruktur |
| **Hypergraph-Rewriting** | Wolfram Physics: Raum und Zeit entstehen aus dem Umschreiben von Relationen (Kanten) |
| **Assembly Theory** | Walker/Davies: Komplexität = Anzahl Schritte zur Konstruktion einer Struktur |
""")


# ══════════════════════════════════════════════════════════════════════
# TAB 5: GRAPH-MODUS (Epic 5)
# ══════════════════════════════════════════════════════════════════════
with tab_graph:
    st.subheader("🕸️ Graph-Modus — Relationale Simulation (Epic 5)")
    st.caption(
        "Raum entsteht hier aus Relationen (Kanten) zwischen Knoten, nicht aus einem "
        "vordefinierten Gitter. Inspiriert von Wolfram Physics und Netzwerk-Wissenschaft."
    )

    try:
        from emergent_noise.core.graph_state import GraphConfig, GraphState as GState
        HAS_GS = True
    except ImportError:
        HAS_GS = False

    if not HAS_GS:
        st.error("networkx nicht installiert. `pip install networkx`")
    else:
        # Graph-Konfig via Sidebar-ähnliche Spalte
        g_col1, g_col2 = st.columns([1, 2])
        with g_col1:
            g_topo   = st.selectbox("Topologie", ["small_world", "scale_free", "random", "grid"])
            g_nodes  = st.slider("Knoten", 16, 128, 48, step=8)
            g_ticks  = st.slider("Simulations-Ticks", 1, 100, 20)
            g_seed   = st.number_input("Seed (Graph)", value=42, min_value=0, step=1)
            run_graph = st.button("▶ Graph-Simulation starten")

        with g_col2:
            if "graph_state" not in st.session_state or run_graph:
                gcfg = GraphConfig(
                    n_nodes=g_nodes, initial_topology=g_topo, seed=int(g_seed),
                    rewriting_rate=0.1,
                )
                gs = GState(gcfg)
                for _ in range(g_ticks):
                    gs.step()
                st.session_state.graph_state = gs

            gs = st.session_state.graph_state
            gsummary = gs.graph_summary()

            # Metriken
            gm1, gm2, gm3, gm4 = st.columns(4)
            gm1.metric("Knoten",         gsummary["n_nodes"])
            gm2.metric("Kanten",         gsummary["n_edges"])
            gm3.metric("Ø Clustering",   f"{gsummary['avg_clustering']:.3f}",
                       help="Mittlerer Clustering-Koeffizient: wie stark sind Nachbarn untereinander vernetzt?")
            gm4.metric("Verbunden",      "✅ Ja" if gsummary["is_connected"] else f"❌ {gsummary['n_components']} Komp.")

            gm5, gm6, gm7 = st.columns(3)
            gm5.metric("Dichte",         f"{gsummary['density']:.4f}")
            gm6.metric("Ø Energie",      f"{gsummary['mean_energy']:.3f}")
            gm7.metric("Ø Information",  f"{gsummary['mean_information']:.3f}")

        # Graph-Visualisierung
        import networkx as nx
        G = gs.graph
        fig_g, axes_g_tab = plt.subplots(1, 2, figsize=(12, 5))

        # Links: Netzwerk-Layout
        ax_net = axes_g_tab[0]
        try:
            pos = nx.spring_layout(G, seed=42, k=2.0/max(len(G.nodes())**0.5, 1))
        except Exception:
            pos = nx.random_layout(G, seed=42)

        energies_g = [G.nodes[n].get("energy", 0.5) for n in G.nodes()]
        weights_g  = [G[u][v].get("weight", 0.5) for u, v in G.edges()]
        degrees    = dict(G.degree())
        node_sizes = [20 + degrees[n] * 8 for n in G.nodes()]

        nx.draw_networkx_nodes(
            G, pos, ax=ax_net,
            node_color=energies_g, cmap="inferno",
            node_size=node_sizes, vmin=0, vmax=1, alpha=0.9,
        )
        nx.draw_networkx_edges(
            G, pos, ax=ax_net,
            width=[w * 1.5 for w in weights_g],
            alpha=0.4, edge_color="white",
        )
        ax_net.set_facecolor("#0e1117")
        ax_net.set_title(
            f"Netzwerk nach {g_ticks} Ticks\n"
            f"Knotengröße ∝ Grad | Farbe = Energie | Linienstärke ∝ Kantengewicht",
            fontsize=8, color="white"
        )
        ax_net.axis("off")

        # Rechts: Emergente Distanzmatrix
        ax_dist = axes_g_tab[1]
        n_sample = min(20, g_nodes)
        dist_mat = gs.emergent_distance_matrix(n_sample=n_sample)
        dist_finite = np.where(np.isinf(dist_mat), dist_mat[~np.isinf(dist_mat)].max() * 1.5 if np.any(~np.isinf(dist_mat)) else 0, dist_mat)
        im_d = ax_dist.imshow(dist_finite, cmap="viridis", interpolation="nearest")
        plt.colorbar(im_d, ax=ax_dist, fraction=0.046)
        ax_dist.set_title(
            f"Emergente Distanzmatrix ({n_sample} Knoten)\n"
            "1/Kantengewicht = effektive Distanz\n(hell = weit, dunkel = nah)",
            fontsize=8,
        )
        ax_dist.set_xlabel("Knoten-Index", fontsize=7)
        ax_dist.set_ylabel("Knoten-Index", fontsize=7)

        fig_g.tight_layout()
        st.pyplot(fig_g, use_container_width=True)
        plt.close(fig_g)

        # Energie-Histogramm
        energies_arr = gs.node_array("energy")
        fig_eh, ax_eh = plt.subplots(figsize=(6, 2.5))
        ax_eh.hist(energies_arr, bins=20, color="orange", alpha=0.8, edgecolor="white")
        ax_eh.set_xlabel("Knotenenergie", fontsize=8)
        ax_eh.set_ylabel("Anzahl Knoten", fontsize=8)
        ax_eh.set_title("Energieverteilung nach Rewriting", fontsize=9)
        st.pyplot(fig_eh, use_container_width=True)
        plt.close(fig_eh)

        with st.expander("📖 Was passiert hier? — Wolfram Physics & Netzwerk-Wissenschaft"):
            st.markdown("""
**Wolfram Physics (vereinfacht):**
Wolfram schlägt vor, dass Raum, Zeit und physikalische Gesetze aus dem
Umschreiben einfacher Hypergraph-Relationen entstehen. Jeder "Schritt"
ist ein Rewriting-Ereignis. Hier: aktive Knoten knüpfen neue Verbindungen.

**Emergente Distanz:**
Im Gegensatz zu einem euklidischen Gitter ist die Distanz zwischen Knoten
hier die *kürzeste gewichtete Pfadlänge*. Starke Kanten = kurze Distanz.
Die Distanzmatrix zeigt, wie "nah" Knoten funktional verbunden sind.

**Clustering-Koeffizient:**
Misst, ob Nachbarn eines Knotens auch untereinander verbunden sind.
- Small-World-Netze: hoch (wie soziale Netzwerke, Gehirn)
- Random-Netze: niedrig
- Scale-Free-Netze: variable (viele schwach vernetzte Knoten, wenige Hubs)

**Weiterführend:**
- 📖 *Network Science* — Barabási (frei online: networksciencebook.com)
- 📄 Watts & Strogatz (1998): *Collective dynamics of 'small-world' networks*, Nature
- 📄 Barabási & Albert (1999): *Emergence of scaling in random networks*, Science
""")


# ------------------------------------------------------------------
# Auto-Rerun wenn laufend
# ------------------------------------------------------------------
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
