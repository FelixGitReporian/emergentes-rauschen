"""
learning/concepts.py - Concept library for emergent phenomena (Epic 14/15).

Scientific caution:
    Explanations are designed for educational accessibility, not mathematical
    rigour. All claims are qualified: this model 'explores' or 'provides an
    analogue of' a concept, never 'proves' or 'simulates exactly'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from emergent_noise.learning.resources import LearningResource


@dataclass(frozen=True)
class ConceptNote:
    """A single complex-systems concept with explanation and links.

    Attributes
    ----------
    id:
        Unique snake_case identifier.
    title:
        Human-readable name.
    short_explanation:
        One-sentence plain-language description.
    deeper_explanation:
        2-5 sentence explanation for intermediate readers.
    mathematical_keywords:
        Key mathematical terms / ideas (no formulas required).
    related_presets:
        Preset IDs in which this concept is most visible.
    resource_ids:
        IDs from the RESOURCES registry relevant to this concept.
    """

    id: str
    title: str
    short_explanation: str
    deeper_explanation: str
    mathematical_keywords: List[str] = field(default_factory=list)
    related_presets: List[str] = field(default_factory=list)
    resource_ids: List[str] = field(default_factory=list)


CONCEPTS: Dict[str, ConceptNote] = {}


def _reg(*notes: ConceptNote) -> None:
    for n in notes:
        CONCEPTS[n.id] = n


_reg(
    ConceptNote(
        id="emergence",
        title="Emergence",
        short_explanation="Global patterns arise from local rules without being explicitly programmed.",
        deeper_explanation=(
            "Emergence describes the appearance of higher-level structure or behaviour "
            "that is not present in, and cannot easily be predicted from, the parts alone. "
            "A classic example is the formation of a traffic jam from individually rational drivers. "
            "In field simulations, structures like clusters, boundaries and oscillations emerge "
            "from simple per-cell update rules without any central controller."
        ),
        mathematical_keywords=[
            "nonlinearity", "local interactions", "self-organisation",
            "phase transitions", "attractor landscapes",
        ],
        related_presets=[
            "reaction_diffusion_turing", "excitable_media_waves",
            "tree_growth_branching", "stigmergy_ant_trails",
        ],
        resource_ids=["mitchell_complexity", "wolfram_nks", "flake_computational_beauty"],
    ),
    ConceptNote(
        id="cellular_automata",
        title="Cellular Automata",
        short_explanation="A grid of cells that update their states in parallel according to local rules.",
        deeper_explanation=(
            "A cellular automaton (CA) is a discrete model consisting of a grid of cells, "
            "each in one of a finite number of states. At each time step, every cell updates "
            "its state based on a fixed rule applied to its neighbourhood. "
            "Despite their simplicity, CAs can produce extraordinary complexity — "
            "Wolfram's Rule 110 is Turing-complete. Emergentes Rauschen uses a continuous "
            "multi-field variant rather than a classical binary CA."
        ),
        mathematical_keywords=[
            "discrete dynamical systems", "local rules", "neighbourhoods",
            "universality", "computational equivalence",
        ],
        related_presets=[
            "reaction_diffusion_turing", "excitable_media_waves",
        ],
        resource_ids=["wolfram_nks", "shiffman_ca_chapter", "lenia_paper"],
    ),
    ConceptNote(
        id="artificial_life",
        title="Artificial Life",
        short_explanation="Study and synthesis of life-like processes in non-biological substrates.",
        deeper_explanation=(
            "Artificial life (ALife) is an interdisciplinary field exploring life-as-it-could-be, "
            "not just life-as-it-is. It uses simulations, robotics and chemistry to study "
            "self-replication, evolution, metabolism, adaptation and morphogenesis. "
            "Key projects include Avida (digital evolution), Lenia (continuous CA), "
            "and OpenWorm (virtual C. elegans). This simulator provides an abstract field substrate "
            "for exploring life-like structural analogues — not accurate biological models."
        ),
        mathematical_keywords=[
            "self-replication", "open-ended evolution", "fitness landscapes",
            "digital evolution", "proto-metabolism",
        ],
        related_presets=[
            "autopoiesis_membrane", "ecosystem_patch_dynamics",
            "trace_reading_fossil_field",
        ],
        resource_ids=["levy_artificial_life", "avida_ed", "lenia_project", "alife_org"],
    ),
    ConceptNote(
        id="reaction_diffusion",
        title="Reaction-Diffusion Systems",
        short_explanation="Two interacting chemicals that diffuse and react to produce spatial patterns.",
        deeper_explanation=(
            "Turing (1952) showed that a simple system of two chemicals — an activator and "
            "an inhibitor — with different diffusion rates can spontaneously form stable spatial "
            "patterns including spots, stripes and spirals. These patterns appear in animal "
            "coat markings, shell pigmentation and developmental biology. "
            "The key insight is that short-range activation combined with long-range inhibition "
            "breaks spatial symmetry. This simulator uses abstract energy and information fields "
            "as an analogue, not a biochemically accurate model."
        ),
        mathematical_keywords=[
            "activator-inhibitor", "Laplacian", "diffusion coefficient",
            "Turing instability", "symmetry breaking",
        ],
        related_presets=["reaction_diffusion_turing"],
        resource_ids=["turing_morphogenesis", "lenia_paper"],
    ),
    ConceptNote(
        id="stigmergy",
        title="Stigmergy",
        short_explanation="Indirect coordination through traces left in a shared environment.",
        deeper_explanation=(
            "Stigmergy describes how agents modify their environment and those modifications "
            "guide future actions — without direct communication between agents. "
            "Ant pheromone trails are the canonical example: ants deposit pheromone, "
            "others follow the strongest trail, reinforcing it further. "
            "This creates path optimisation as a collective emergent property. "
            "In this simulator, the memory field acts as the shared trace medium."
        ),
        mathematical_keywords=[
            "positive feedback", "decay", "path reinforcement",
            "distributed coordination", "attractor convergence",
        ],
        related_presets=["stigmergy_ant_trails", "ant_trails_agents", "trace_reading_fossil_field"],
        resource_ids=["complexityexplorer_abm", "mitchell_complexity"],
    ),
    ConceptNote(
        id="self_organization",
        title="Self-Organisation",
        short_explanation="Order arising spontaneously from local interactions without external control.",
        deeper_explanation=(
            "Self-organisation is the process by which a system develops organised structure "
            "or behaviour without an external controller specifying that structure. "
            "Examples include snowflake formation, sand dune patterns, bird flocking and "
            "neural development. The key mechanism is positive and negative feedback loops "
            "acting locally across many components simultaneously."
        ),
        mathematical_keywords=[
            "feedback loops", "instabilities", "symmetry breaking",
            "dissipative structures", "non-equilibrium thermodynamics",
        ],
        related_presets=[
            "stigmergy_ant_trails", "autopoiesis_membrane",
            "boids_field_approx", "ecosystem_patch_dynamics",
        ],
        resource_ids=["strogatz_sync", "mitchell_complexity"],
    ),
    ConceptNote(
        id="morphogenesis",
        title="Morphogenesis",
        short_explanation="The process by which organisms develop shape, structure and form.",
        deeper_explanation=(
            "Morphogenesis (from Greek: 'form' + 'origin') is the biological process by which "
            "cells, tissues and organisms acquire their characteristic forms. "
            "It involves coordinated cell differentiation, movement and communication. "
            "Turing reaction-diffusion, Wolpert's positional information and mechanical forces "
            "all play roles. In this simulator, branching, filamentary and boundary-forming "
            "patterns provide structural analogues of morphogenetic processes."
        ),
        mathematical_keywords=[
            "reaction-diffusion", "gradient fields", "branching processes",
            "fractal dimension", "skeleton extraction",
        ],
        related_presets=[
            "tree_growth_branching", "mycelium_network",
            "river_network", "reaction_diffusion_turing",
        ],
        resource_ids=["turing_morphogenesis", "tero_physarum"],
    ),
    ConceptNote(
        id="autopoiesis",
        title="Autopoiesis",
        short_explanation="A system that continuously produces and maintains the components that constitute it.",
        deeper_explanation=(
            "Autopoiesis (Maturana and Varela, 1972) describes systems that self-produce their "
            "own boundary and internal organisation. A living cell is the paradigmatic example: "
            "it continuously synthesises its membrane and internal components. "
            "The system is operationally closed (it defines itself) but thermodynamically open "
            "(it exchanges energy and matter with its environment). "
            "This simulator explores structural analogues of boundary maintenance and "
            "self-sustaining organisation — not actual autopoiesis."
        ),
        mathematical_keywords=[
            "operational closure", "self-production", "boundary formation",
            "dissipative structures", "proto-metabolism",
        ],
        related_presets=["autopoiesis_membrane"],
        resource_ids=["levy_artificial_life", "walker_information_life"],
    ),
    ConceptNote(
        id="boids_flocking",
        title="Boids / Flocking",
        short_explanation="Three simple rules — separation, alignment, cohesion — produce lifelike flocking.",
        deeper_explanation=(
            "Craig Reynolds (1987) showed that bird-like flocking behaviour emerges from "
            "three local rules applied independently by each agent: avoid crowding neighbours "
            "(separation), steer toward average heading (alignment), and move toward average "
            "position (cohesion). No central coordination is needed. "
            "This simulator implements vectorized Boids agents that interact with the field system."
        ),
        mathematical_keywords=[
            "vector averages", "local perception radius", "Reynolds number (social)",
            "collective motion", "velocity coherence",
        ],
        related_presets=["boids_field_approx", "boids_agents"],
        resource_ids=["reynolds_boids", "shiffman_nature_of_code"],
    ),
    ConceptNote(
        id="entropy_information",
        title="Entropy and Information",
        short_explanation="Entropy measures disorder or uncertainty; information measures structured difference.",
        deeper_explanation=(
            "Shannon entropy H(X) = -sum(p_i * log2(p_i)) measures the average uncertainty "
            "in a probability distribution. High entropy = many equally likely outcomes. "
            "In field simulations, a uniform field has maximum entropy; structured patterns "
            "have lower entropy. Mutual information between two fields measures how much "
            "knowing one field reduces uncertainty about the other. "
            "These are statistical properties of field distributions, not metaphysical claims."
        ),
        mathematical_keywords=[
            "Shannon entropy", "mutual information", "KL divergence",
            "histogram approximation", "information theory",
        ],
        related_presets=["trace_reading_fossil_field", "reaction_diffusion_turing"],
        resource_ids=["walker_information_life", "mindscape_walker"],
    ),
    ConceptNote(
        id="agent_based_modeling",
        title="Agent-Based Modeling",
        short_explanation="Simulations where individual autonomous agents follow local rules, producing collective behaviour.",
        deeper_explanation=(
            "Agent-based models (ABMs) represent systems as collections of autonomous agents "
            "with internal state, perception and behaviour rules. "
            "Unlike equation-based models, ABMs capture heterogeneity, discrete events and "
            "spatial structure naturally. They are used in ecology, economics, social science "
            "and artificial life. NetLogo, Mesa and custom implementations are common tools. "
            "This simulator implements vectorized agents integrated with field dynamics."
        ),
        mathematical_keywords=[
            "autonomous agents", "local rules", "emergent collective behaviour",
            "spatial hashing", "neighbourhood search",
        ],
        related_presets=["boids_agents", "ant_trails_agents", "ecosystem_patch_dynamics"],
        resource_ids=["complexityexplorer_abm", "reynolds_boids"],
    ),
    ConceptNote(
        id="open_ended_evolution",
        title="Open-Ended Evolution",
        short_explanation="Evolution that continues producing novelty indefinitely, without converging to a fixed solution.",
        deeper_explanation=(
            "Most optimisation algorithms converge. Open-ended evolution in biological systems "
            "does not: it keeps producing new species, body plans and ecological relationships "
            "apparently without bound. This is one of the central unsolved problems in ALife. "
            "Key questions include: what conditions allow indefinite innovation? "
            "Is open-endedness a property of the fitness landscape, the representation, "
            "or the environment? This simulator does not implement true evolution, but "
            "provides a substrate for observing spontaneous novelty."
        ),
        mathematical_keywords=[
            "fitness landscapes", "neutral evolution", "evolvability",
            "combinatorial explosion", "major transitions",
        ],
        related_presets=["ecosystem_patch_dynamics"],
        resource_ids=["avida_ed", "levy_artificial_life", "alife_org"],
    ),
    ConceptNote(
        id="trace_reading",
        title="Trace Reading",
        short_explanation="Inferring the history and structure of a system from the patterns it leaves behind.",
        deeper_explanation=(
            "Trace reading treats simulation outputs as evidence to be interpreted: "
            "what kind of dynamics produced this pattern? What happened in the past? "
            "What is likely to happen next? This reverses the usual simulation direction "
            "(rules -> pattern) to ask: pattern -> what rules/history? "
            "In palaeontology, traces (ichnology) tell us about extinct organisms without "
            "direct fossil remains. In this simulator, the memory and coupling fields "
            "accumulate traces of past dynamics that can be read and interpreted."
        ),
        mathematical_keywords=[
            "inverse problem", "persistence", "spatial autocorrelation",
            "cluster lifetimes", "wavefront speed",
        ],
        related_presets=["trace_reading_fossil_field", "stigmergy_ant_trails"],
        resource_ids=["walker_information_life", "mitchell_complexity"],
    ),
    ConceptNote(
        id="complex_adaptive_systems",
        title="Complex Adaptive Systems",
        short_explanation="Systems whose components learn and adapt, changing the system's own behaviour over time.",
        deeper_explanation=(
            "Complex adaptive systems (CAS) combine the properties of complex systems "
            "(emergence, nonlinearity, feedback) with adaptation: components modify their "
            "behaviour based on experience or selection. Examples include immune systems, "
            "economies, ecosystems and neural networks. "
            "The Santa Fe Institute studies CAS as a unifying framework across disciplines. "
            "This simulator explores structural analogues through field coupling and memory-based adaptation."
        ),
        mathematical_keywords=[
            "adaptation", "selection pressure", "co-evolution",
            "fitness", "bounded rationality",
        ],
        related_presets=[
            "ecosystem_patch_dynamics", "autopoiesis_membrane",
        ],
        resource_ids=["mitchell_complexity", "sfi_complexity_podcast", "complexityexplorer_abm"],
    ),
)


def get_concept(concept_id: str) -> ConceptNote:
    if concept_id not in CONCEPTS:
        raise KeyError(f"Concept '{concept_id}' not found. Available: {list(CONCEPTS)}")
    return CONCEPTS[concept_id]


def concepts_for_preset(preset_id: str) -> List[ConceptNote]:
    return [c for c in CONCEPTS.values() if preset_id in c.related_presets]


def list_concepts() -> List[ConceptNote]:
    return list(CONCEPTS.values())
