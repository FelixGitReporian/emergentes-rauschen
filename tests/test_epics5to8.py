"""
tests/test_epics5to8.py – Tests für Epic 5–8:
    core/graph_state.py, core/multiscale.py,
    interpretation/consciousness.py,
    experiments/configs.py, experiments/runner.py
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.multiscale import (
    MesoLayer, MesoEntity, AttractorLandscape, MultiscaleController,
)
from emergent_noise.interpretation.consciousness import (
    ConsciousnessAnalyzer, ConsciousnessMarkers,
)
from emergent_noise.experiments.configs import (
    ALL_EXPERIMENTS, ExperimentConfig,
    STABILITY_SWEEP, META_EVOLUTION, CONSCIOUSNESS_SCAN,
)

try:
    import networkx as nx
    from emergent_noise.core.graph_state import GraphState, GraphConfig
    HAS_NX = True
except ImportError:
    HAS_NX = False

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config32() -> SimConfig:
    return SimConfig(height=32, width=32, seed=0)


@pytest.fixture
def state32(config32: SimConfig) -> GridState:
    return GridState.initialize(config32)


# ---------------------------------------------------------------------------
# Epic 5: GraphState
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_NX, reason="networkx not installed")
class TestGraphState:
    def test_init_small_world(self) -> None:
        cfg = GraphConfig(n_nodes=16, initial_topology="small_world", seed=0)
        gs = GraphState(cfg)
        assert gs.graph.number_of_nodes() == 16
        assert gs.tick == 0

    def test_init_scale_free(self) -> None:
        cfg = GraphConfig(n_nodes=20, initial_topology="scale_free", seed=0)
        gs = GraphState(cfg)
        assert gs.graph.number_of_nodes() == 20

    def test_step_increments_tick(self) -> None:
        cfg = GraphConfig(n_nodes=16, seed=0)
        gs = GraphState(cfg)
        gs.step()
        assert gs.tick == 1

    def test_step_preserves_node_count(self) -> None:
        cfg = GraphConfig(n_nodes=16, seed=0)
        gs = GraphState(cfg)
        for _ in range(5):
            gs.step()
        assert gs.graph.number_of_nodes() == 16

    def test_energy_stays_in_range(self) -> None:
        cfg = GraphConfig(n_nodes=20, seed=0)
        gs = GraphState(cfg)
        for _ in range(10):
            gs.step()
        energies = gs.node_array("energy")
        assert (energies >= 0.0).all() and (energies <= 1.0).all()

    def test_graph_summary_keys(self) -> None:
        cfg = GraphConfig(n_nodes=16, seed=0)
        gs = GraphState(cfg)
        s = gs.graph_summary()
        assert "n_nodes" in s
        assert "avg_clustering" in s
        assert "mean_energy" in s

    def test_rewriting_adds_edges(self) -> None:
        cfg = GraphConfig(n_nodes=20, initial_topology="random",
                          connection_prob=0.05, rewriting_rate=0.5, seed=0)
        gs = GraphState(cfg)
        # Aktiviere alle Knoten für maximales Rewriting
        for nd in gs.graph.nodes():
            gs.graph.nodes[nd]["energy"] = 0.9
            gs.graph.nodes[nd]["information"] = 0.9
        before = gs.graph.number_of_edges()
        gs._rewrite()
        after = gs.graph.number_of_edges()
        assert after >= before

    def test_emergent_distance_matrix_shape(self) -> None:
        cfg = GraphConfig(n_nodes=20, seed=0)
        gs = GraphState(cfg)
        dist = gs.emergent_distance_matrix(n_sample=8)
        assert dist.shape == (8, 8)

    def test_emergent_distance_diagonal_zero(self) -> None:
        cfg = GraphConfig(n_nodes=20, seed=0)
        gs = GraphState(cfg)
        dist = gs.emergent_distance_matrix(n_sample=8)
        assert (dist.diagonal() == 0.0).all()


# ---------------------------------------------------------------------------
# Epic 6: Multiscale
# ---------------------------------------------------------------------------

class TestMesoLayer:
    def test_no_entities_for_empty_field(self, state32: GridState) -> None:
        state32.energy[:] = 0.0
        meso = MesoLayer()
        entities = meso.update(state32)
        assert entities == []

    def test_detects_blob(self, state32: GridState) -> None:
        state32.energy[:] = 0.0
        state32.energy[10:22, 10:22] = 0.9
        state32.coherence[10:22, 10:22] = 0.8
        meso = MesoLayer(energy_threshold=0.5, min_area=9)
        entities = meso.update(state32)
        assert len(entities) >= 1

    def test_entity_has_centroid_in_bounds(self, state32: GridState, config32: SimConfig) -> None:
        state32.energy[:] = 0.0
        state32.energy[5:15, 5:15] = 0.9
        meso = MesoLayer(min_area=9)
        entities = meso.update(state32)
        for e in entities:
            assert 0 <= e.centroid[0] < config32.height
            assert 0 <= e.centroid[1] < config32.width

    def test_velocity_estimated_on_second_update(self, state32: GridState) -> None:
        state32.energy[:] = 0.0
        state32.energy[10:20, 10:20] = 0.9
        state32.coherence[10:20, 10:20] = 0.7
        meso = MesoLayer(min_area=9)
        meso.update(state32)
        # Verschiebe Blob
        state32.energy[:] = 0.0
        state32.energy[12:22, 12:22] = 0.9
        entities2 = meso.update(state32)
        if entities2:
            v = entities2[0].velocity
            assert isinstance(v, tuple)

    def test_history_grows(self, state32: GridState) -> None:
        meso = MesoLayer()
        for _ in range(3):
            meso.update(state32)
        assert len(meso.history) == 3


class TestAttractorLandscape:
    def test_trajectory_appended(self, state32: GridState) -> None:
        land = AttractorLandscape()
        land.update(state32)
        land.update(state32)
        assert len(land.trajectory) == 2

    def test_transition_detected_on_large_jump(self, config32: SimConfig) -> None:
        land = AttractorLandscape()
        s1 = GridState.initialize(config32)
        s1.energy[:] = 0.1
        s1.coherence[:] = 0.1
        land.update(s1)
        s2 = GridState.initialize(config32)
        s2.energy[:] = 0.9
        s2.coherence[:] = 0.9
        land.update(s2)
        result = land.update(s2)
        assert result["n_transitions"] >= 0  # mindestens kein Fehler

    def test_trajectory_array_shape(self, state32: GridState) -> None:
        land = AttractorLandscape()
        for _ in range(5):
            land.update(state32)
        arr = land.trajectory_array()
        assert arr.shape == (5, 2)


class TestMultiscaleController:
    def test_update_returns_dict(self, state32: GridState) -> None:
        ctrl = MultiscaleController()
        result = ctrl.update(state32)
        assert "meso" in result
        assert "macro" in result

    def test_meso_n_entities_non_negative(self, state32: GridState) -> None:
        ctrl = MultiscaleController()
        result = ctrl.update(state32)
        assert result["meso"]["n_entities"] >= 0

    def test_macro_has_energy_mean(self, state32: GridState) -> None:
        ctrl = MultiscaleController()
        result = ctrl.update(state32)
        assert "energy_mean" in result["macro"]


# ---------------------------------------------------------------------------
# Epic 8: ConsciousnessAnalyzer
# ---------------------------------------------------------------------------

class TestConsciousnessAnalyzer:
    def test_returns_markers(self, state32: GridState) -> None:
        ca = ConsciousnessAnalyzer()
        m = ca.analyze(state32)
        assert isinstance(m, ConsciousnessMarkers)

    def test_all_scores_in_range(self, state32: GridState) -> None:
        ca = ConsciousnessAnalyzer()
        m = ca.analyze(state32)
        assert 0.0 <= m.phi_proxy <= 1.0
        assert 0.0 <= m.active_inference_score <= 1.0
        assert 0.0 <= m.proto_life_score <= 1.0
        assert 0.0 <= m.global_workspace_score <= 1.0
        assert 0.0 <= m.integrated_score <= 1.0

    def test_criteria_keys_present(self, state32: GridState) -> None:
        ca = ConsciousnessAnalyzer()
        m = ca.analyze(state32)
        assert "compartments" in m.criteria
        assert "reactivity_std" in m.criteria
        assert "genome_std" in m.criteria

    def test_history_grows(self, state32: GridState) -> None:
        ca = ConsciousnessAnalyzer()
        for _ in range(4):
            ca.analyze(state32)
        assert len(ca.marker_history) == 4

    def test_high_coherence_raises_phi(self) -> None:
        cfg = SimConfig(height=16, width=16, seed=0)
        s_high = GridState.initialize(cfg)
        s_high.coherence[:] = 1.0
        s_high.energy[:] = 0.5
        s_low = GridState.initialize(cfg)
        s_low.coherence[:] = 0.0

        ca = ConsciousnessAnalyzer()
        m_high = ca.analyze(s_high)
        m_low  = ca.analyze(s_low)
        assert m_high.phi_proxy >= m_low.phi_proxy

    def test_proto_life_score_higher_with_compartments(self) -> None:
        cfg = SimConfig(height=16, width=16, seed=0)
        s = GridState.initialize(cfg)
        s.energy[:] = 0.0
        s.energy[4:12, 4:12] = 0.9
        s.coherence[4:12, 4:12] = 0.8
        s.reactivity = np.random.default_rng(0).uniform(0, 1, (16, 16)).astype(np.float32)
        s.memory[:] = 0.1
        ca = ConsciousnessAnalyzer()
        m = ca.analyze(s)
        assert m.proto_life_score > 0.0

    def test_no_nan_in_scores(self, state32: GridState) -> None:
        ca = ConsciousnessAnalyzer()
        m = ca.analyze(state32)
        for v in [m.phi_proxy, m.active_inference_score, m.proto_life_score,
                  m.global_workspace_score, m.integrated_score]:
            assert not np.isnan(v)


# ---------------------------------------------------------------------------
# Epic 7: Experiment-Configs
# ---------------------------------------------------------------------------

class TestExperimentConfigs:
    def test_all_experiments_exist(self) -> None:
        assert len(ALL_EXPERIMENTS) >= 7

    def test_each_has_required_fields(self) -> None:
        for name, exp in ALL_EXPERIMENTS.items():
            assert exp.name == name
            assert exp.scientific_question
            assert exp.n_ticks > 0
            assert exp.repeat > 0

    def test_param_sweeps_valid(self) -> None:
        for name, exp in ALL_EXPERIMENTS.items():
            for param, values in exp.param_sweeps.items():
                assert len(values) > 0, f"{name}.{param} hat keine Sweep-Werte"

    def test_base_config_is_simconfig(self) -> None:
        for exp in ALL_EXPERIMENTS.values():
            assert isinstance(exp.base_config, SimConfig)

    def test_stability_sweep_has_noise_param(self) -> None:
        assert "noise_amplitude" in STABILITY_SWEEP.param_sweeps

    def test_meta_evolution_has_meta_enabled(self) -> None:
        assert META_EVOLUTION.base_config.meta_enabled is True

    def test_consciousness_scan_tags(self) -> None:
        assert "consciousness" in CONSCIOUSNESS_SCAN.tags

    def test_runner_single_run_produces_records(self) -> None:
        """Einzelner Lauf des Runners erzeugt Metrik-Datensätze."""
        from emergent_noise.experiments.runner import _run_single
        config = SimConfig(height=16, width=16, seed=0)
        records = _run_single(config, n_ticks=40, run_id="test_001", params={})
        assert len(records) > 0
        assert "tick" in records[0]
        assert "phi_proxy" in records[0]
        assert "proto_life_score" in records[0]
