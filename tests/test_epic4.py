"""
tests/test_epic4.py – Tests für Epic-4-Module:
    core/particles.py, analysis/compartments.py
"""

from __future__ import annotations

import numpy as np
import pytest

from emergent_noise.core.particles import (
    ParticleConfig,
    ParticleSystem,
    step_particles,
)
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.analysis.compartments import (
    Compartment,
    CompartmentResult,
    detect_compartments,
    particle_compartments,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sim_config() -> SimConfig:
    return SimConfig(height=32, width=32, seed=0)


@pytest.fixture
def state(sim_config: SimConfig) -> GridState:
    return GridState.initialize(sim_config)


@pytest.fixture
def pcfg() -> ParticleConfig:
    return ParticleConfig(
        n_particles=20,
        max_particles=100,
        collision_radius=1.5,
        seed=0,
    )


@pytest.fixture
def particles(pcfg: ParticleConfig, sim_config: SimConfig) -> ParticleSystem:
    return ParticleSystem(pcfg, sim_config.height, sim_config.width)


# ---------------------------------------------------------------------------
# core/particles.py – ParticleConfig
# ---------------------------------------------------------------------------

class TestParticleConfig:
    def test_default_construction(self) -> None:
        cfg = ParticleConfig()
        assert cfg.n_particles > 0
        assert cfg.max_particles >= cfg.n_particles
        assert 0.0 < cfg.velocity_damping < 1.0


# ---------------------------------------------------------------------------
# core/particles.py – ParticleSystem Initialisierung
# ---------------------------------------------------------------------------

class TestParticleSystemInit:
    def test_n_active_equals_n_particles(self, particles: ParticleSystem, pcfg: ParticleConfig) -> None:
        assert particles.n_active == pcfg.n_particles

    def test_positions_in_grid_bounds(self, particles: ParticleSystem, sim_config: SimConfig) -> None:
        pos = particles.active_positions()
        assert (pos[:, 0] >= 0).all() and (pos[:, 0] < sim_config.height).all()
        assert (pos[:, 1] >= 0).all() and (pos[:, 1] < sim_config.width).all()

    def test_masses_are_one(self, particles: ParticleSystem) -> None:
        assert (particles.active_masses() == 1.0).all()

    def test_energies_in_range(self, particles: ParticleSystem) -> None:
        e = particles.active_energies()
        assert (e >= 0.0).all() and (e <= 1.0).all()

    def test_array_shapes(self, particles: ParticleSystem, pcfg: ParticleConfig) -> None:
        N = pcfg.max_particles
        assert particles.positions.shape == (N, 2)
        assert particles.velocities.shape == (N, 2)
        assert particles.energy.shape == (N,)
        assert particles.mass.shape == (N,)
        assert particles.active.shape == (N,)


# ---------------------------------------------------------------------------
# core/particles.py – Feld→Partikel Kopplung
# ---------------------------------------------------------------------------

class TestFieldToParticle:
    def test_high_energy_gradient_changes_velocity(self, particles: ParticleSystem, state: GridState) -> None:
        state.energy[:, :16] = 0.0
        state.energy[:, 16:] = 1.0
        vel_before = particles.velocities.copy()
        particles.apply_field_to_particles(state)
        assert not np.allclose(particles.velocities, vel_before)

    def test_field_to_particle_does_not_produce_nan(self, particles: ParticleSystem, state: GridState) -> None:
        particles.apply_field_to_particles(state)
        assert not np.isnan(particles.velocities).any()
        assert not np.isnan(particles.positions).any()


# ---------------------------------------------------------------------------
# core/particles.py – Partikel→Feld Kopplung
# ---------------------------------------------------------------------------

class TestParticlesToField:
    def test_particles_deposit_energy(self, particles: ParticleSystem, state: GridState) -> None:
        energy_before = state.energy.copy()
        particles.apply_particles_to_field(state)
        assert state.energy.sum() >= energy_before.sum() - 1e-4

    def test_particles_deposit_matter(self, particles: ParticleSystem, state: GridState) -> None:
        matter_before = state.matter.copy()
        particles.apply_particles_to_field(state)
        assert state.matter.sum() > matter_before.sum() - 1e-4

    def test_field_values_stay_clipped_after_step(self, particles: ParticleSystem, state: GridState) -> None:
        particles.apply_particles_to_field(state)
        state.clip_all()
        for arr in state.as_dict().values():
            assert arr.min() >= 0.0 - 1e-5
            assert arr.max() <= 1.0 + 1e-5


# ---------------------------------------------------------------------------
# core/particles.py – Bewegung
# ---------------------------------------------------------------------------

class TestParticleMovement:
    def test_positions_change_after_move(self, particles: ParticleSystem, state: GridState) -> None:
        particles.apply_field_to_particles(state)
        pos_before = particles.active_positions().copy()
        particles.move()
        pos_after = particles.active_positions()
        assert not np.allclose(pos_before, pos_after)

    def test_positions_stay_in_bounds_after_move(self, particles: ParticleSystem, state: GridState) -> None:
        particles.apply_field_to_particles(state)
        for _ in range(10):
            particles.move()
        pos = particles.active_positions()
        assert (pos[:, 0] >= 0).all() and (pos[:, 0] < particles.height).all()
        assert (pos[:, 1] >= 0).all() and (pos[:, 1] < particles.width).all()

    def test_velocity_damped_over_ticks(self, particles: ParticleSystem) -> None:
        idx = particles._active_indices()
        particles.velocities[idx] = 1.0
        for _ in range(20):
            particles.move()
        speeds = np.sqrt(
            particles.velocities[idx, 0]**2 + particles.velocities[idx, 1]**2
        )
        assert speeds.mean() < 0.5


# ---------------------------------------------------------------------------
# core/particles.py – Kollision + Aggregation
# ---------------------------------------------------------------------------

class TestCollisions:
    def test_collision_reduces_particle_count(self) -> None:
        cfg = ParticleConfig(n_particles=2, max_particles=10, collision_radius=100.0, seed=0)
        particles = ParticleSystem(cfg, 32, 32)
        idx = particles._active_indices()
        # Beide Partikel auf gleiche Position setzen
        particles.positions[idx[0]] = [16.0, 16.0]
        particles.positions[idx[1]] = [16.0, 16.0]
        before = particles.n_active
        particles.apply_collisions()
        assert particles.n_active < before

    def test_collision_increases_mass(self) -> None:
        cfg = ParticleConfig(n_particles=2, max_particles=10, collision_radius=100.0, seed=0)
        particles = ParticleSystem(cfg, 32, 32)
        idx = particles._active_indices()
        particles.positions[idx[0]] = [16.0, 16.0]
        particles.positions[idx[1]] = [16.0, 16.0]
        total_mass_before = particles.mass[idx].sum()
        particles.apply_collisions()
        surviving = particles._active_indices()
        total_mass_after = particles.mass[surviving].sum()
        assert abs(total_mass_after - total_mass_before) < 1e-4  # Massenerhalt

    def test_no_collision_when_far_apart(self) -> None:
        cfg = ParticleConfig(n_particles=2, max_particles=10, collision_radius=0.1, seed=0)
        particles = ParticleSystem(cfg, 32, 32)
        idx = particles._active_indices()
        particles.positions[idx[0]] = [0.0, 0.0]
        particles.positions[idx[1]] = [30.0, 30.0]
        before = particles.n_active
        particles.apply_collisions()
        assert particles.n_active == before


# ---------------------------------------------------------------------------
# core/particles.py – step_particles + summary
# ---------------------------------------------------------------------------

class TestStepParticles:
    def test_step_particles_runs(self, particles: ParticleSystem, state: GridState) -> None:
        step_particles(particles, state)

    def test_summary_keys(self, particles: ParticleSystem) -> None:
        s = particles.summary()
        assert "n_active" in s
        assert "mean_mass" in s
        assert "n_compartments" in s

    def test_full_tick_loop_with_particles(self, sim_config: SimConfig) -> None:
        pcfg = ParticleConfig(n_particles=10, max_particles=50, seed=0)
        particles = ParticleSystem(pcfg, sim_config.height, sim_config.width)
        state = GridState.initialize(sim_config)
        loop = TickLoop(sim_config)
        for _ in range(5):
            loop.step(state)
            step_particles(particles, state, do_collisions=True)
        assert particles.n_active > 0
        assert not np.isnan(state.energy).any()


# ---------------------------------------------------------------------------
# analysis/compartments.py – detect_compartments
# ---------------------------------------------------------------------------

class TestDetectCompartments:
    def test_no_compartments_in_empty_field(self, state: GridState) -> None:
        state.energy[:] = 0.0
        result = detect_compartments(state)
        assert result.n_compartments == 0

    def test_detects_high_energy_blob(self, state: GridState) -> None:
        state.energy[:] = 0.0
        state.coupling[:] = 0.0
        state.energy[12:20, 12:20] = 0.9
        state.coupling[12:20, 12:20] = 0.8
        result = detect_compartments(state, energy_threshold=0.5, coupling_threshold=0.3)
        assert result.n_compartments >= 1

    def test_compartment_result_fields(self, state: GridState) -> None:
        state.energy[10:20, 10:20] = 0.9
        state.coupling[10:20, 10:20] = 0.7
        result = detect_compartments(state)
        assert isinstance(result, CompartmentResult)
        assert result.tick == state.tick
        assert result.mean_proto_life_score >= 0.0
        if result.n_compartments > 0:
            c = result.compartments[0]
            assert 0.0 <= c.proto_life_score <= 1.0
            assert c.area >= 1

    def test_proto_life_score_high_for_good_compartment(self, state: GridState) -> None:
        state.energy[:] = 0.0
        state.coupling[:] = 0.0
        state.energy[8:24, 8:24] = 0.9
        state.coupling[8:24, 8:24] = 0.8
        result = detect_compartments(state, energy_threshold=0.5, coupling_threshold=0.3)
        assert result.max_proto_life_score >= 0.5


# ---------------------------------------------------------------------------
# analysis/compartments.py – particle_compartments
# ---------------------------------------------------------------------------

class TestParticleCompartments:
    def test_empty_particles_returns_zero(self) -> None:
        result = particle_compartments(
            np.empty((0, 2)), np.empty((0,)), 32, 32
        )
        assert result["n_heavy_particles"] == 0
        assert result["density_map"].shape == (32, 32)

    def test_heavy_particle_detected(self) -> None:
        positions = np.array([[16.0, 16.0], [5.0, 5.0]], dtype=np.float32)
        masses    = np.array([5.0, 1.0], dtype=np.float32)
        result = particle_compartments(positions, masses, 32, 32, min_mass=3.0)
        assert result["n_heavy_particles"] == 1
        assert result["mean_aggregate_mass"] == pytest.approx(5.0)

    def test_density_map_shape(self) -> None:
        positions = np.random.default_rng(0).uniform(0, 32, (10, 2)).astype(np.float32)
        masses    = np.ones(10, dtype=np.float32)
        result = particle_compartments(positions, masses, 32, 32)
        assert result["density_map"].shape == (32, 32)
        assert result["density_map"].sum() > 0.0
