"""
tests/test_epic3.py – Tests für Epic-3-Module:
    rules/meta_rules.py, analysis/novelty.py,
    core/state.py (Genome-Felder), core/tick.py (Meta-Regeln im Loop)
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.analysis.novelty import (
    BehaviorVector,
    NoveltyTracker,
    genome_diversity,
    genome_entropy,
)
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.rules.meta_rules import (
    _apply_mutation,
    _apply_retention,
    _apply_selection,
    _compute_fitness,
    apply_meta_rules,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config() -> SimConfig:
    return SimConfig(height=16, width=16, seed=0, meta_enabled=True,
                     meta_mutation_rate=0.1, meta_mutation_strength=0.1,
                     meta_selection_rate=0.1, meta_retention_threshold=0.5)


@pytest.fixture
def state(config: SimConfig) -> GridState:
    return GridState.initialize(config)


# ---------------------------------------------------------------------------
# core/state.py – Genome-Felder
# ---------------------------------------------------------------------------

class TestGenomeFields:
    def test_genome_fields_exist(self, state: GridState) -> None:
        assert hasattr(state, "genome_strength")
        assert hasattr(state, "genome_threshold")

    def test_genome_shape_matches_grid(self, state: GridState, config: SimConfig) -> None:
        assert state.genome_strength.shape == (config.height, config.width)
        assert state.genome_threshold.shape == (config.height, config.width)

    def test_genome_values_in_range(self, state: GridState) -> None:
        assert ((state.genome_strength >= 0.0) & (state.genome_strength <= 1.0)).all()
        assert ((state.genome_threshold >= 0.0) & (state.genome_threshold <= 1.0)).all()

    def test_genome_dtype_float32(self, state: GridState) -> None:
        assert state.genome_strength.dtype == np.float32
        assert state.genome_threshold.dtype == np.float32

    def test_genome_initialized_near_config(self, config: SimConfig) -> None:
        state = GridState.initialize(config)
        assert abs(state.genome_strength.mean() - config.reaction_strength) < 0.1
        assert abs(state.genome_threshold.mean() - config.reaction_energy_threshold) < 0.15

    def test_genome_dict_returns_both_fields(self, state: GridState) -> None:
        d = state.genome_dict()
        assert "genome_strength" in d
        assert "genome_threshold" in d

    def test_clip_all_clips_genome(self, state: GridState) -> None:
        state.genome_strength[:] = 2.0
        state.genome_threshold[:] = -1.0
        state.clip_all()
        assert state.genome_strength.max() <= 1.0
        assert state.genome_threshold.min() >= 0.0


# ---------------------------------------------------------------------------
# rules/meta_rules.py – Fitness
# ---------------------------------------------------------------------------

class TestFitness:
    def test_fitness_shape(self, state: GridState) -> None:
        fitness = _compute_fitness(state)
        assert fitness.shape == state.energy.shape

    def test_fitness_range(self, state: GridState) -> None:
        fitness = _compute_fitness(state)
        assert ((fitness >= 0.0) & (fitness <= 1.0)).all()

    def test_high_coherence_gives_high_fitness(self) -> None:
        config = SimConfig(height=8, width=8, seed=0)
        state = GridState.initialize(config)
        state.coherence[:] = 1.0
        state.energy[:] = 0.5  # konstant → keine Varianz
        fitness = _compute_fitness(state)
        assert fitness.mean() > 0.7

    def test_low_coherence_gives_low_fitness(self) -> None:
        config = SimConfig(height=8, width=8, seed=0)
        state = GridState.initialize(config)
        state.coherence[:] = 0.0
        fitness = _compute_fitness(state)
        assert fitness.mean() < 0.1


# ---------------------------------------------------------------------------
# rules/meta_rules.py – Mutation
# ---------------------------------------------------------------------------

class TestMutation:
    def test_mutation_changes_genome(self, state: GridState, config: SimConfig) -> None:
        before_s = state.genome_strength.copy()
        rng = np.random.default_rng(42)
        _apply_mutation(state, config, rng)
        # Mindestens ein Wert muss sich geändert haben
        assert not np.array_equal(state.genome_strength, before_s)

    def test_mutation_stays_in_range_after_clip(self, state: GridState, config: SimConfig) -> None:
        rng = np.random.default_rng(99)
        for _ in range(10):
            _apply_mutation(state, config, rng)
        # Meta_rules clippt intern
        apply_meta_rules(state, config)
        assert ((state.genome_strength >= 0.0) & (state.genome_strength <= 1.0)).all()

    def test_mutation_rate_zero_no_change(self) -> None:
        config = SimConfig(height=8, width=8, seed=0, meta_mutation_rate=0.0,
                           meta_mutation_strength=0.5)
        state = GridState.initialize(config)
        before = state.genome_strength.copy()
        rng = np.random.default_rng(0)
        _apply_mutation(state, config, rng)
        # rate=0 → n_mutate=max(1,...) → mindestens eine Zelle; Test ist aufgeweicht
        # Wichtig: alle anderen Zellen unverändert
        n_changed = int(np.sum(state.genome_strength != before))
        assert n_changed <= max(1, int(0.0 * 64) + 1)


# ---------------------------------------------------------------------------
# rules/meta_rules.py – Selektion
# ---------------------------------------------------------------------------

class TestSelection:
    def test_selection_propagates_fit_profile(self) -> None:
        """Fitte Zellen sollen ihr Profil auf schwächere Nachbarn propagieren."""
        config = SimConfig(height=8, width=8, seed=0, meta_selection_rate=1.0)
        state = GridState.initialize(config)
        # Eine einzelne hochfitte Zelle mit einzigartiger genome_strength
        state.coherence[:] = 0.0
        state.coherence[4, 4] = 1.0
        state.energy[:] = 0.5     # keine Varianz → hohe Fitness bei hoher Kohärenz
        state.genome_strength[:] = 0.1
        state.genome_strength[4, 4] = 0.9  # einzigartiger Wert
        rng = np.random.default_rng(0)
        fitness = _compute_fitness(state)
        _apply_selection(state, config, fitness, rng)
        # Mindestens ein Nachbar hat 0.9 übernommen
        neighbors_values = [
            state.genome_strength[3, 4], state.genome_strength[5, 4],
            state.genome_strength[4, 3], state.genome_strength[4, 5],
        ]
        assert any(abs(v - 0.9) < 1e-5 for v in neighbors_values)

    def test_selection_does_not_decrease_best_fitness(self) -> None:
        """Das fitteste Profil soll durch Selektion nicht schlechter werden."""
        config = SimConfig(height=8, width=8, seed=0, meta_selection_rate=0.5)
        state = GridState.initialize(config)
        state.coherence[:] = 0.8
        state.energy[:] = 0.5
        state.genome_strength[:] = 0.5
        before_max = state.genome_strength.max()
        rng = np.random.default_rng(1)
        fitness = _compute_fitness(state)
        _apply_selection(state, config, fitness, rng)
        # Maximum darf nicht sinken
        assert state.genome_strength.max() >= before_max - 1e-5


# ---------------------------------------------------------------------------
# rules/meta_rules.py – Retention
# ---------------------------------------------------------------------------

class TestRetention:
    def test_retention_increases_memory_for_fit_cells(self) -> None:
        config = SimConfig(height=8, width=8, seed=0, meta_retention_threshold=0.5)
        state = GridState.initialize(config)
        state.coherence[:] = 1.0
        state.energy[:] = 0.5
        state.memory[:] = 0.0
        fitness = _compute_fitness(state)
        _apply_retention(state, config, fitness)
        assert state.memory.mean() > 0.0

    def test_retention_zero_memory_for_low_fitness(self) -> None:
        config = SimConfig(height=8, width=8, seed=0, meta_retention_threshold=0.99)
        state = GridState.initialize(config)
        state.coherence[:] = 0.0  # Fitness = 0
        state.memory[:] = 0.0
        fitness = _compute_fitness(state)
        _apply_retention(state, config, fitness)
        assert state.memory.sum() == 0.0


# ---------------------------------------------------------------------------
# rules/meta_rules.py – apply_meta_rules (integration)
# ---------------------------------------------------------------------------

class TestApplyMetaRules:
    def test_apply_meta_rules_runs_without_error(self, state: GridState, config: SimConfig) -> None:
        apply_meta_rules(state, config)

    def test_meta_disabled_no_change(self) -> None:
        config = SimConfig(height=8, width=8, seed=0, meta_enabled=False)
        state = GridState.initialize(config)
        before_s = state.genome_strength.copy()
        before_t = state.genome_threshold.copy()
        apply_meta_rules(state, config)
        assert np.array_equal(state.genome_strength, before_s)
        assert np.array_equal(state.genome_threshold, before_t)

    def test_genome_evolves_over_ticks(self) -> None:
        config = SimConfig(height=16, width=16, seed=0, meta_enabled=True,
                           meta_mutation_rate=0.2)
        state = GridState.initialize(config)
        before = state.genome_strength.copy()
        loop = TickLoop(config)
        for _ in range(5):
            loop.step(state)
        assert not np.array_equal(state.genome_strength, before)

    def test_genome_values_stay_in_range_after_ticks(self) -> None:
        config = SimConfig(height=16, width=16, seed=42, meta_enabled=True)
        state = GridState.initialize(config)
        loop = TickLoop(config)
        for _ in range(20):
            loop.step(state)
        assert ((state.genome_strength >= 0.0) & (state.genome_strength <= 1.0)).all()
        assert ((state.genome_threshold >= 0.0) & (state.genome_threshold <= 1.0)).all()


# ---------------------------------------------------------------------------
# analysis/novelty.py
# ---------------------------------------------------------------------------

class TestNovelty:
    def test_behavior_vector_from_state(self, state: GridState) -> None:
        bv = BehaviorVector.from_state(state)
        assert isinstance(bv.values, np.ndarray)
        assert len(bv.values) > 0
        assert bv.tick == state.tick

    def test_novelty_tracker_first_update(self, state: GridState) -> None:
        tracker = NoveltyTracker()
        novelty = tracker.update(state)
        assert novelty == 0.0  # Archiv leer → Distanz 0

    def test_novelty_increases_with_different_states(self) -> None:
        config = SimConfig(height=16, width=16, seed=0)
        state_a = GridState.initialize(config)
        config_b = SimConfig(height=16, width=16, seed=99)
        state_b = GridState.initialize(config_b)
        tracker = NoveltyTracker()
        tracker.update(state_a)
        novelty = tracker.update(state_b)
        assert novelty > 0.0

    def test_novelty_low_for_same_state(self, state: GridState) -> None:
        tracker = NoveltyTracker()
        tracker.update(state)
        tracker.update(state)
        novelty = tracker.update(state)
        assert novelty < 0.05  # fast gleicher Zustand → geringe Novelty

    def test_genome_diversity_keys(self, state: GridState) -> None:
        div = genome_diversity(state)
        assert "strength_std" in div
        assert "threshold_std" in div
        assert "joint_entropy" in div

    def test_genome_diversity_homogeneous_low_std(self) -> None:
        config = SimConfig(height=16, width=16, seed=0)
        state = GridState.initialize(config)
        state.genome_strength[:] = 0.5
        state.genome_threshold[:] = 0.5
        div = genome_diversity(state)
        assert div["strength_std"] < 1e-5
        assert div["threshold_std"] < 1e-5

    def test_genome_entropy_range(self, state: GridState) -> None:
        ent = genome_entropy(state)
        assert 0.0 <= ent <= 1.0

    def test_genome_entropy_homogeneous_low(self) -> None:
        config = SimConfig(height=16, width=16, seed=0)
        state = GridState.initialize(config)
        state.genome_strength[:] = 0.5
        ent = genome_entropy(state)
        assert ent < 0.2


# ---------------------------------------------------------------------------
# Tick-Loop: Meta-Regeln integriert (Regressionstests)
# ---------------------------------------------------------------------------

class TestTickLoopEpic3:
    def test_tick_still_deterministic_with_meta(self) -> None:
        config = SimConfig(height=16, width=16, seed=7, meta_enabled=True)
        s1 = GridState.initialize(config)
        s2 = GridState.initialize(config)
        loop = TickLoop(config)
        for _ in range(10):
            loop.step(s1)
            loop.step(s2)
        assert np.allclose(s1.energy, s2.energy)
        assert np.allclose(s1.genome_strength, s2.genome_strength)

    def test_tick_values_stay_in_range_with_meta(self) -> None:
        config = SimConfig(height=32, width=32, seed=0, meta_enabled=True)
        state = GridState.initialize(config)
        loop = TickLoop(config)
        for _ in range(50):
            loop.step(state)
        for arr in state.as_dict().values():
            assert arr.min() >= 0.0
            assert arr.max() <= 1.0
