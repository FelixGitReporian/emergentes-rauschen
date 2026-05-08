"""
tests/test_learning.py - Tests for the Learning Layer (Epics 14/15).
"""

from __future__ import annotations

import pytest

from emergent_noise.learning.resources import (
    RESOURCES,
    LearningResource,
    get_resource,
    list_resources,
)
from emergent_noise.learning.concepts import (
    CONCEPTS,
    ConceptNote,
    concepts_for_preset,
    get_concept,
    list_concepts,
)
from emergent_noise.learning.modules import (
    LEARNING_MODULES,
    GuidedExperiment,
    LearningModule,
    ParameterLearningNote,
    get_learning_module,
    list_learning_modules,
)
from emergent_noise.experiments.presets import PRESETS
from emergent_noise.core.state import SimConfig


# ──────────────────────────────────────────────────────────────────
# Resource registry
# ──────────────────────────────────────────────────────────────────

def test_resources_not_empty() -> None:
    assert len(RESOURCES) > 0


def test_all_resources_have_title_and_type() -> None:
    for rid, r in RESOURCES.items():
        assert r.title, f"Resource '{rid}' has empty title"
        assert r.type, f"Resource '{rid}' has empty type"


def test_all_resource_ids_are_unique() -> None:
    assert len(RESOURCES) == len(set(RESOURCES.keys()))


def test_all_resources_url_nonempty_when_set() -> None:
    for rid, r in RESOURCES.items():
        if r.url is not None:
            assert r.url.strip(), f"Resource '{rid}' has empty url string"


def test_all_resources_doi_nonempty_when_set() -> None:
    for rid, r in RESOURCES.items():
        if r.doi is not None:
            assert r.doi.strip(), f"Resource '{rid}' has empty doi string"


def test_get_resource_returns_correct_type() -> None:
    r = get_resource("mitchell_complexity")
    assert isinstance(r, LearningResource)
    assert r.id == "mitchell_complexity"


def test_get_resource_raises_for_unknown() -> None:
    with pytest.raises(KeyError):
        get_resource("does_not_exist_xyz")


def test_list_resources_all() -> None:
    rs = list_resources()
    assert len(rs) == len(RESOURCES)


def test_list_resources_filter_level() -> None:
    beginner = list_resources(level="beginner")
    assert all(r.level == "beginner" for r in beginner)
    assert len(beginner) > 0


def test_list_resources_filter_type() -> None:
    books = list_resources(resource_type="book")
    assert all(r.type == "book" for r in books)
    assert len(books) > 0


def test_list_resources_filter_tag() -> None:
    tagged = list_resources(tag="complexity")
    assert all("complexity" in r.tags for r in tagged)


def test_resources_include_required_entries() -> None:
    required = [
        "mitchell_complexity", "levy_artificial_life", "wolfram_nks",
        "shiffman_nature_of_code", "reynolds_boids", "turing_morphogenesis",
        "lenia_paper", "complexityexplorer_abm",
    ]
    for rid in required:
        assert rid in RESOURCES, f"Required resource '{rid}' missing"


def test_resources_podcasts_exist() -> None:
    podcasts = list_resources(resource_type="podcast")
    assert len(podcasts) >= 2


def test_resources_projects_exist() -> None:
    projects = list_resources(resource_type="project")
    assert len(projects) >= 3


# ──────────────────────────────────────────────────────────────────
# Concept registry
# ──────────────────────────────────────────────────────────────────

def test_concepts_not_empty() -> None:
    assert len(CONCEPTS) > 0


def test_all_concepts_have_title_and_explanations() -> None:
    for cid, c in CONCEPTS.items():
        assert c.title, f"Concept '{cid}' has empty title"
        assert c.short_explanation, f"Concept '{cid}' has empty short_explanation"
        assert c.deeper_explanation, f"Concept '{cid}' has empty deeper_explanation"


def test_all_concept_ids_are_unique() -> None:
    assert len(CONCEPTS) == len(set(CONCEPTS.keys()))


def test_get_concept_returns_correct() -> None:
    c = get_concept("emergence")
    assert isinstance(c, ConceptNote)
    assert c.id == "emergence"


def test_get_concept_raises_for_unknown() -> None:
    with pytest.raises(KeyError):
        get_concept("does_not_exist_xyz")


def test_list_concepts_all() -> None:
    cs = list_concepts()
    assert len(cs) == len(CONCEPTS)


def test_concepts_for_preset_returns_list() -> None:
    cs = concepts_for_preset("stigmergy_ant_trails")
    assert isinstance(cs, list)
    assert len(cs) >= 1


def test_concepts_for_unknown_preset_empty() -> None:
    cs = concepts_for_preset("nonexistent_preset_xyz")
    assert cs == []


def test_required_concepts_present() -> None:
    required = [
        "emergence", "cellular_automata", "artificial_life", "reaction_diffusion",
        "stigmergy", "self_organization", "morphogenesis", "autopoiesis",
        "boids_flocking", "entropy_information", "agent_based_modeling", "trace_reading",
    ]
    for cid in required:
        assert cid in CONCEPTS, f"Required concept '{cid}' missing"


def test_concept_resource_ids_all_exist() -> None:
    for cid, c in CONCEPTS.items():
        for rid in c.resource_ids:
            assert rid in RESOURCES, (
                f"Concept '{cid}' references unknown resource '{rid}'"
            )


def test_concept_related_presets_all_exist() -> None:
    for cid, c in CONCEPTS.items():
        for pid in c.related_presets:
            assert pid in PRESETS, (
                f"Concept '{cid}' references unknown preset '{pid}'"
            )


# ──────────────────────────────────────────────────────────────────
# Learning module registry
# ──────────────────────────────────────────────────────────────────

def test_learning_modules_not_empty() -> None:
    assert len(LEARNING_MODULES) > 0


def test_all_modules_reference_existing_presets() -> None:
    for pid in LEARNING_MODULES:
        assert pid in PRESETS, f"LearningModule references unknown preset '{pid}'"


def test_no_duplicate_module_ids() -> None:
    assert len(LEARNING_MODULES) == len(set(LEARNING_MODULES.keys()))


def test_get_learning_module_returns_module() -> None:
    m = get_learning_module("stigmergy_ant_trails")
    assert isinstance(m, LearningModule)
    assert m.preset_id == "stigmergy_ant_trails"


def test_get_learning_module_returns_none_for_unknown() -> None:
    assert get_learning_module("nonexistent_xyz") is None


def test_list_learning_modules_all() -> None:
    ms = list_learning_modules()
    assert len(ms) == len(LEARNING_MODULES)


def test_required_modules_present() -> None:
    required = [
        "stigmergy_ant_trails", "tree_growth_branching",
        "reaction_diffusion_turing", "trace_reading_fossil_field",
        "autopoiesis_membrane",
    ]
    for pid in required:
        assert pid in LEARNING_MODULES, f"Required module '{pid}' missing"


def test_all_modules_have_learning_goals() -> None:
    for pid, m in LEARNING_MODULES.items():
        assert len(m.learning_goals) > 0, f"Module '{pid}' has no learning goals"


def test_all_modules_have_intuition() -> None:
    for pid, m in LEARNING_MODULES.items():
        assert m.intuition.strip(), f"Module '{pid}' has empty intuition"


def test_all_modules_have_math_background() -> None:
    for pid, m in LEARNING_MODULES.items():
        assert m.mathematical_background.strip(), f"Module '{pid}' has empty math background"


def test_all_modules_have_observation_questions() -> None:
    for pid, m in LEARNING_MODULES.items():
        assert len(m.observation_questions) >= 2, f"Module '{pid}' needs >= 2 observation questions"


def test_all_modules_have_guided_experiments() -> None:
    for pid, m in LEARNING_MODULES.items():
        assert len(m.guided_experiments) >= 2, f"Module '{pid}' needs >= 2 guided experiments"


def test_guided_experiments_have_title_setup_question() -> None:
    for pid, m in LEARNING_MODULES.items():
        for exp in m.guided_experiments:
            assert isinstance(exp, GuidedExperiment)
            assert exp.title, f"Experiment in '{pid}' has empty title"
            assert exp.setup, f"Experiment in '{pid}' has empty setup"
            assert exp.question, f"Experiment in '{pid}' has empty question"


def test_module_resource_ids_all_exist() -> None:
    for pid, m in LEARNING_MODULES.items():
        for rid in m.resource_ids:
            assert rid in RESOURCES, (
                f"Module '{pid}' references unknown resource '{rid}'"
            )


def test_module_core_concepts_all_exist() -> None:
    for pid, m in LEARNING_MODULES.items():
        for cid in m.core_concepts:
            assert cid in CONCEPTS, (
                f"Module '{pid}' references unknown concept '{cid}'"
            )


def test_parameter_notes_reference_valid_simconfig_fields() -> None:
    valid_fields = set(SimConfig.model_fields.keys())
    for pid, m in LEARNING_MODULES.items():
        for note in m.parameter_notes:
            assert isinstance(note, ParameterLearningNote)
            assert note.parameter in valid_fields, (
                f"Module '{pid}' has ParameterLearningNote for '{note.parameter}' "
                f"which is not a SimConfig field"
            )


def test_parameter_notes_have_plain_language() -> None:
    for pid, m in LEARNING_MODULES.items():
        for note in m.parameter_notes:
            assert note.plain_language.strip(), (
                f"ParameterLearningNote '{note.parameter}' in '{pid}' has empty plain_language"
            )


def test_parameter_notes_have_math_role() -> None:
    for pid, m in LEARNING_MODULES.items():
        for note in m.parameter_notes:
            assert note.mathematical_role.strip(), (
                f"ParameterLearningNote '{note.parameter}' in '{pid}' has empty mathematical_role"
            )


def test_at_least_8_modules() -> None:
    assert len(LEARNING_MODULES) >= 8
