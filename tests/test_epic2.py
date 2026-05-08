"""
tests/test_epic2.py – Tests für Epic-2-Module:
    analysis/morphology.py, analysis/mutual_information.py,
    analysis/trace_reading.py,
    interpretation/regime_classifier.py,
    interpretation/narratives.py
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from emergent_noise.analysis.morphology import compute_morphology
from emergent_noise.analysis.mutual_information import field_mi, mi_matrix, local_mi
from emergent_noise.analysis.attractors import PersistenceTracker
from emergent_noise.analysis.trace_reading import read_traces
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.interpretation.regime_classifier import (
    RegimeType,
    classify_regime,
)
from emergent_noise.interpretation.narratives import build_narrative


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_state() -> GridState:
    config = SimConfig(height=32, width=32, seed=0)
    return GridState.initialize(config)


@pytest.fixture
def energy_blob() -> np.ndarray:
    """Energie-Feld: ein kompakter Klumpen in der Mitte."""
    arr = np.zeros((32, 32), dtype=np.float32)
    arr[12:20, 12:20] = 0.9
    return arr


@pytest.fixture
def energy_filament() -> np.ndarray:
    """Energie-Feld: ein langer horizontaler Filament."""
    arr = np.zeros((32, 32), dtype=np.float32)
    arr[15:17, 2:30] = 0.9
    return arr


@pytest.fixture
def fields_dict(simple_state: GridState) -> dict:
    return simple_state.as_dict()


# ---------------------------------------------------------------------------
# analysis/morphology.py
# ---------------------------------------------------------------------------

class TestMorphology:
    def test_empty_field_all_zero(self) -> None:
        arr = np.zeros((16, 16), dtype=np.float32)
        result = compute_morphology("energy", arr, tick=0)
        assert result.n_components == 0
        assert result.active_fraction == 0.0
        assert result.boundary_complexity == 0.0

    def test_full_field(self) -> None:
        arr = np.ones((16, 16), dtype=np.float32)
        result = compute_morphology("energy", arr, tick=0)
        assert result.n_components == 1
        assert result.active_fraction == 1.0

    def test_blob_has_one_component(self, energy_blob: np.ndarray) -> None:
        result = compute_morphology("energy", energy_blob, tick=5)
        assert result.n_components == 1
        assert result.elongation < 2.0  # kompakt

    def test_filament_has_high_elongation(self, energy_filament: np.ndarray) -> None:
        result = compute_morphology("energy", energy_filament, tick=5)
        assert result.elongation > 5.0

    def test_blob_has_low_boundary_complexity(self, energy_blob: np.ndarray) -> None:
        result = compute_morphology("energy", energy_blob)
        assert result.boundary_complexity < 0.5

    def test_result_fields_present(self, energy_blob: np.ndarray) -> None:
        result = compute_morphology("energy", energy_blob, tick=10)
        assert result.field_name == "energy"
        assert result.tick == 10
        assert 0.0 <= result.compactness <= 1.1  # 4πA/P² ≈1 für Quadrat


# ---------------------------------------------------------------------------
# analysis/mutual_information.py
# ---------------------------------------------------------------------------

class TestMutualInformation:
    def test_identical_fields_high_mi(self) -> None:
        rng = np.random.default_rng(0)
        a = rng.random((16, 16)).astype(np.float32)
        mi = field_mi(a, a)
        assert mi > 0.8

    def test_independent_fields_low_mi(self) -> None:
        rng = np.random.default_rng(1)
        a = rng.random((32, 32)).astype(np.float32)
        b = rng.random((32, 32)).astype(np.float32)
        mi = field_mi(a, b)
        assert mi < 0.3

    def test_mi_symmetric(self) -> None:
        rng = np.random.default_rng(2)
        a = rng.random((16, 16)).astype(np.float32)
        b = rng.random((16, 16)).astype(np.float32)
        assert abs(field_mi(a, b) - field_mi(b, a)) < 1e-9

    def test_mi_in_range(self) -> None:
        rng = np.random.default_rng(3)
        a = rng.random((16, 16)).astype(np.float32)
        b = rng.random((16, 16)).astype(np.float32)
        mi = field_mi(a, b)
        assert 0.0 <= mi <= 1.0

    def test_mi_matrix_has_correct_keys(self, fields_dict: dict) -> None:
        small = {k: fields_dict[k] for k in ("energy", "information", "coupling")}
        result = mi_matrix(small)
        assert ("energy", "information") in result
        assert ("information", "energy") in result

    def test_local_mi_shape(self) -> None:
        rng = np.random.default_rng(4)
        a = rng.random((16, 16)).astype(np.float32)
        b = rng.random((16, 16)).astype(np.float32)
        out = local_mi(a, b, radius=2, n_bins=4)
        assert out.shape == (16, 16)
        assert ((out >= 0.0) & (out <= 1.0)).all()


# ---------------------------------------------------------------------------
# interpretation/regime_classifier.py
# ---------------------------------------------------------------------------

class TestRegimeClassifier:
    def test_returns_regime_result(self, fields_dict: dict) -> None:
        from emergent_noise.interpretation.regime_classifier import RegimeResult
        result = classify_regime(tick=10, fields=fields_dict)
        assert isinstance(result, RegimeResult)
        assert isinstance(result.primary_regime, RegimeType)

    def test_confidence_in_range(self, fields_dict: dict) -> None:
        result = classify_regime(tick=10, fields=fields_dict)
        assert 0.0 <= result.confidence <= 1.0

    def test_quiescent_on_low_energy(self) -> None:
        arr = np.full((16, 16), 0.1, dtype=np.float32)
        fields = {
            "energy": arr, "coherence": arr, "coupling": arr,
            "flow_x": np.zeros((16, 16), dtype=np.float32),
            "flow_y": np.zeros((16, 16), dtype=np.float32),
            "memory": arr, "information": arr, "reactivity": arr,
        }
        result = classify_regime(tick=0, fields=fields, entropy_energy=0.2)
        assert result.primary_regime == RegimeType.QUIESCENT

    def test_vortex_on_high_flow(self) -> None:
        """VORTEX muss erkannt werden wenn flow hoch und energy niedrig (wenig andere Signale)."""
        low = np.full((16, 16), 0.1, dtype=np.float32)
        fields = {
            "energy": low, "coherence": low, "coupling": low,
            "flow_x": np.full((16, 16), 0.05, dtype=np.float32),
            "flow_y": np.full((16, 16), 0.05, dtype=np.float32),
            "memory": low, "information": low, "reactivity": low,
        }
        result = classify_regime(tick=0, fields=fields)
        # VORTEX ist primary oder secondary — bei niedrigen anderen Signalen sollte es klar sein
        all_regimes = [result.primary_regime] + result.secondary_regimes
        assert RegimeType.VORTEX in all_regimes

    def test_evidence_dict_populated(self, fields_dict: dict) -> None:
        result = classify_regime(tick=5, fields=fields_dict)
        assert "energy_mean" in result.evidence
        assert "n_clusters" in result.evidence

    def test_description_is_nonempty(self, fields_dict: dict) -> None:
        result = classify_regime(tick=5, fields=fields_dict)
        assert len(result.description) > 20


# ---------------------------------------------------------------------------
# interpretation/narratives.py
# ---------------------------------------------------------------------------

class TestNarratives:
    def test_narrative_has_required_fields(self, fields_dict: dict) -> None:
        regime = classify_regime(tick=10, fields=fields_dict)
        narrative = build_narrative(regime)
        assert narrative.tick == 10
        assert len(narrative.interpretations) > 0
        assert len(narrative.likely_past) > 0
        assert len(narrative.likely_future) > 0
        assert "Wissenschaftlicher Hinweis" in narrative.scientific_caveat

    def test_narrative_confidence_matches_regime(self, fields_dict: dict) -> None:
        regime = classify_regime(tick=5, fields=fields_dict)
        narrative = build_narrative(regime)
        assert narrative.confidence == regime.confidence

    def test_all_regime_types_have_narrative(self, fields_dict: dict) -> None:
        from emergent_noise.interpretation.regime_classifier import RegimeResult
        for rtype in RegimeType:
            fake = RegimeResult(
                tick=0, primary_regime=rtype, secondary_regimes=[],
                confidence=0.5, evidence={}, description="test",
            )
            n = build_narrative(fake)
            assert len(n.interpretations) > 0


# ---------------------------------------------------------------------------
# analysis/trace_reading.py
# ---------------------------------------------------------------------------

class TestTraceReading:
    def test_trace_report_fields(self, fields_dict: dict) -> None:
        report = read_traces(tick=10, fields=fields_dict)
        assert report.tick == 10
        assert "energy" in report.field_summaries
        assert "n_components" in report.morphology
        assert "near_transition" in report.phase
        assert "primary_regime" in report.regime
        assert "interpretations" in report.narrative

    def test_to_dict_is_json_serializable(self, fields_dict: dict) -> None:
        report = read_traces(tick=5, fields=fields_dict)
        d = report.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 100

    def test_to_json_valid(self, fields_dict: dict) -> None:
        report = read_traces(tick=5, fields=fields_dict)
        parsed = json.loads(report.to_json())
        assert parsed["tick"] == 5
        assert "narrative" in parsed

    def test_mi_matrix_keys_format(self, fields_dict: dict) -> None:
        report = read_traces(tick=1, fields=fields_dict)
        for key in report.mi_matrix:
            assert "|" in key

    def test_with_persistence_tracker(self, simple_state: GridState) -> None:
        tracker = PersistenceTracker(window=5)
        fields = simple_state.as_dict()
        tracker.update(fields)
        tracker.update(fields)
        report = read_traces(tick=2, fields=fields, persistence_tracker=tracker)
        assert report.regime["evidence"]["persistence_energy"] > 0.0
