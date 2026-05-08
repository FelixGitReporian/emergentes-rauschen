"""
visualization/dashboard.py – Streamlit Live-Dashboard.

Startet eine interaktive Echtzeit-Visualisierung der Simulation.

Verwendung:
    streamlit run src/emergent_noise/visualization/dashboard.py

Features:
- Sidebar mit allen SimConfig-Parametern (live anpassbar)
- Start / Stop / Reset Buttons
- Live-Heatmap des gewählten Feldes
- RGB-Composite (energy/information/coherence)
- Entropie-Zeitreihe
- Persistenz + Cluster-Statistiken
- Phasenübergangs-Indikator
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
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop


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

    st.subheader("Visualisierung")
    view_field = st.selectbox(
        "Anzuzeigendes Feld",
        ["energy", "matter", "information", "coupling", "reactivity",
         "memory", "coherence", "flow_x", "flow_y"],
        index=0,
    )
    steps_per_frame = st.slider("Schritte pro Frame", 1, 20, 3)
    max_history = st.slider("Entropie-Verlauf (Ticks)", 50, 500, 200)


# ------------------------------------------------------------------
# Session State initialisieren
# ------------------------------------------------------------------
def _build_config() -> SimConfig:
    return SimConfig(
        height=height, width=width, seed=int(seed),
        diffusion_energy=diff_energy, diffusion_information=diff_info,
        reaction_energy_threshold=react_thresh, reaction_strength=react_strength,
        coupling_gain=coup_gain, coupling_loss=coup_loss, coupling_sync_rate=coup_sync,
        flow_gradient_strength=flow_grad, flow_damping=flow_damp,
        flow_advection_rate=flow_adv, flow_curl_strength=flow_curl,
        memory_decay=mem_decay, memory_imprint_strength=mem_imprint,
        noise_amplitude=noise_amp, noise_scale=noise_scale,
    )


if "sim_state" not in st.session_state:
    cfg = _build_config()
    st.session_state.sim_state = GridState.initialize(cfg)
    st.session_state.sim_config = cfg
    st.session_state.loop = TickLoop(cfg)
    st.session_state.running = False
    st.session_state.entropy_history: deque = deque(maxlen=max_history)
    st.session_state.tracker = PersistenceTracker(window=20)


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

# Metriken berechnen
entropy = state_entropy_summary(state)
st.session_state.entropy_history.append(
    {"tick": state.tick, **entropy}
)
st.session_state.tracker.update(state.as_dict())
phase = compute_phase_indicator(state.tick, state.as_dict())
clusters = find_clusters("energy", state.energy, threshold=0.6)


# ------------------------------------------------------------------
# Layout: Hauptansicht
# ------------------------------------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"Tick {state.tick:05d} — Feld: `{view_field}`")

    # Heatmap des gewählten Feldes
    arr = state.as_dict()[view_field]
    cmap_map = {
        "energy": "inferno", "matter": "YlOrBr", "information": "viridis",
        "coupling": "PuBu", "reactivity": "hot", "memory": "copper",
        "coherence": "cool", "flow_x": "bwr", "flow_y": "bwr",
    }
    vmin, vmax = (-1.0, 1.0) if view_field in ("flow_x", "flow_y") else (0.0, 1.0)
    fig_field, ax_field = plt.subplots(figsize=(5, 5))
    im = ax_field.imshow(arr, cmap=cmap_map.get(view_field, "viridis"),
                         vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest")
    plt.colorbar(im, ax=ax_field, fraction=0.046)
    ax_field.axis("off")
    st.pyplot(fig_field, use_container_width=True)
    plt.close(fig_field)

    # RGB-Composite
    rgb = np.stack([
        np.clip(state.energy, 0, 1),
        np.clip(state.information, 0, 1),
        np.clip(state.coherence, 0, 1),
    ], axis=-1)
    fig_rgb, ax_rgb = plt.subplots(figsize=(5, 5))
    ax_rgb.imshow(rgb, origin="upper", interpolation="nearest")
    ax_rgb.set_title("RGB: R=energy  G=information  B=coherence", fontsize=8)
    ax_rgb.axis("off")
    st.pyplot(fig_rgb, use_container_width=True)
    plt.close(fig_rgb)

with col_right:
    st.subheader("📊 Metriken")

    # Tick + Phasenindikator
    st.metric("Tick", state.tick)
    st.metric(
        "Phasenübergang-Indikator (Suszeptibilität)",
        f"{phase.susceptibility:.4f}",
        delta="⚠️ Nahe Übergang" if phase.near_transition else "stabil",
    )

    # Entropie-Balken
    st.write("**Entropie (normalisiert)**")
    for fname, val in entropy.items():
        st.progress(float(val), text=f"{fname}: {val:.3f}")

    # Persistenz
    st.write("**Feld-Persistenz**")
    for fname, val in st.session_state.tracker.persistence.items():
        st.progress(max(0.0, min(1.0, val)), text=f"{fname}: {val:.3f}")

    # Cluster-Info
    st.write("**Energie-Cluster (threshold=0.6)**")
    st.write(f"Anzahl: {clusters.n_clusters} | "
             f"Größter: {clusters.largest_cluster_size} Zellen | "
             f"Aktiv: {clusters.cluster_fraction:.1%}")

    # Feldstatistik
    st.write(f"**Feldmittel `{view_field}`**")
    st.metric("mean", f"{arr.mean():.4f}")
    st.metric("std", f"{arr.std():.4f}")


# ------------------------------------------------------------------
# Entropie-Zeitreihe
# ------------------------------------------------------------------
st.subheader("📈 Entropie-Verlauf")
hist = list(st.session_state.entropy_history)
if len(hist) > 1:
    ticks = [h["tick"] for h in hist]
    fig_ent, ax_ent = plt.subplots(figsize=(10, 3))
    for fname in ["energy", "information", "memory", "coherence"]:
        vals = [h[fname] for h in hist]
        ax_ent.plot(ticks, vals, label=fname, linewidth=1.2)
    ax_ent.set_xlabel("Tick")
    ax_ent.set_ylabel("Normalisierte Entropie")
    ax_ent.legend(loc="upper right", fontsize=8)
    ax_ent.grid(True, alpha=0.3)
    st.pyplot(fig_ent, use_container_width=True)
    plt.close(fig_ent)


# ------------------------------------------------------------------
# Auto-Rerun wenn laufend
# ------------------------------------------------------------------
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
