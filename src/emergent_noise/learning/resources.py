"""
learning/resources.py - Curated research resource registry (Epic 14/15).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


ResourceType = Literal[
    "book", "paper", "website", "course", "video", "podcast", "project", "documentation",
]

ResourceLevel = Literal["beginner", "intermediate", "advanced", "research"]


@dataclass(frozen=True)
class LearningResource:
    id: str
    title: str
    type: ResourceType
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    description: str = ""
    level: ResourceLevel = "beginner"
    tags: List[str] = field(default_factory=list)


RESOURCES: Dict[str, LearningResource] = {}


def _reg(*resources: LearningResource) -> None:
    for r in resources:
        RESOURCES[r.id] = r


_reg(
    LearningResource(
        id="mitchell_complexity",
        title="Complexity: A Guided Tour",
        type="book",
        authors=["Melanie Mitchell"],
        year=2009,
        description="Accessible introduction to complexity science, emergence and computation.",
        level="beginner",
        tags=["complexity", "emergence", "computation", "biology"],
    ),
    LearningResource(
        id="levy_artificial_life",
        title="Artificial Life: A Report from the Frontier",
        type="book",
        authors=["Steven Levy"],
        year=1992,
        description="Narrative history of the artificial life field.",
        level="beginner",
        tags=["artificial-life", "digital-organisms", "history"],
    ),
    LearningResource(
        id="wolfram_nks",
        title="A New Kind of Science",
        type="book",
        authors=["Stephen Wolfram"],
        year=2002,
        url="https://www.wolframscience.com/nks/",
        description="Wolfram's exploration of cellular automata and computational equivalence.",
        level="intermediate",
        tags=["cellular-automata", "computation", "emergence"],
    ),
    LearningResource(
        id="shiffman_nature_of_code",
        title="The Nature of Code",
        type="book",
        authors=["Daniel Shiffman"],
        year=2024,
        url="https://natureofcode.com/",
        description="Creative coding guide: cellular automata, flocking, neural nets.",
        level="beginner",
        tags=["simulation", "creative-coding", "cellular-automata", "agents"],
    ),
    LearningResource(
        id="shiffman_ca_chapter",
        title="The Nature of Code - Cellular Automata Chapter",
        type="website",
        authors=["Daniel Shiffman"],
        url="https://natureofcode.com/cellular-automata/",
        description="Interactive chapter on 1-D and 2-D cellular automata.",
        level="beginner",
        tags=["cellular-automata", "tutorial", "interactive"],
    ),
    LearningResource(
        id="flake_computational_beauty",
        title="The Computational Beauty of Nature",
        type="book",
        authors=["Gary William Flake"],
        year=1998,
        description="Chaos, fractals, complex systems and adaptation with clear mathematics.",
        level="intermediate",
        tags=["chaos", "fractals", "complex-systems"],
    ),
    LearningResource(
        id="strogatz_sync",
        title="Sync: The Emerging Science of Spontaneous Order",
        type="book",
        authors=["Steven H. Strogatz"],
        year=2003,
        description="Self-organization, synchronisation and coupled oscillators.",
        level="beginner",
        tags=["synchronisation", "self-organization", "dynamical-systems"],
    ),
    LearningResource(
        id="lenia_paper",
        title="Lenia: Biology of Artificial Life",
        type="paper",
        authors=["Bert Wang-Chak Chan"],
        year=2019,
        url="https://arxiv.org/abs/1812.05433",
        doi="10.25088/ComplexSystems.28.3.251",
        description="Continuous generalisation of Conway's Game of Life.",
        level="intermediate",
        tags=["continuous-cellular-automata", "artificial-life", "morphology"],
    ),
    LearningResource(
        id="tero_physarum",
        title="Rules for Biologically Inspired Adaptive Network Design",
        type="paper",
        authors=["Atsushi Tero", "Tetsu Saigusa", "Toshiyuki Nakagaki"],
        year=2010,
        doi="10.1126/science.1177894",
        description="Physarum polycephalum solves transport network problems - mycelium inspiration.",
        level="intermediate",
        tags=["mycelium", "network-formation", "morphogenesis"],
    ),
    LearningResource(
        id="turing_morphogenesis",
        title="The Chemical Basis of Morphogenesis",
        type="paper",
        authors=["Alan M. Turing"],
        year=1952,
        doi="10.1098/rstb.1952.0012",
        description="Turing's classic paper introducing reaction-diffusion systems.",
        level="advanced",
        tags=["reaction-diffusion", "morphogenesis", "pattern-formation"],
    ),
    LearningResource(
        id="reynolds_boids",
        title="Flocks, Herds and Schools: A Distributed Behavioral Model",
        type="paper",
        authors=["Craig W. Reynolds"],
        year=1987,
        doi="10.1145/37401.37406",
        description="Three simple rules that produce lifelike flocking behaviour.",
        level="beginner",
        tags=["boids", "flocking", "agent-based-modeling", "swarm"],
    ),
    LearningResource(
        id="tononi_iit",
        title="Consciousness as Integrated Information: A Provisional Manifesto",
        type="paper",
        authors=["Giulio Tononi"],
        year=2008,
        doi="10.1007/s00422-008-0236-4",
        description="Foundational paper on Integrated Information Theory (IIT) and Phi.",
        level="research",
        tags=["IIT", "consciousness", "integrated-information", "phi"],
    ),
    LearningResource(
        id="walker_information_life",
        title="The informational architecture of the cell",
        type="paper",
        authors=["Sara Imari Walker", "Paul C. W. Davies"],
        year=2013,
        doi="10.1098/rsif.2012.0869",
        description="Top-down causation and information in living systems.",
        level="research",
        tags=["information", "origin-of-life", "assembly-theory"],
    ),
    LearningResource(
        id="complexityexplorer_abm",
        title="Introduction to Agent-Based Modeling",
        type="course",
        authors=["Santa Fe Institute"],
        url="https://www.complexityexplorer.org/courses/183-introduction-to-agent-based-modeling",
        description="Free online ABM course from the Santa Fe Institute.",
        level="beginner",
        tags=["agent-based-modeling", "complexity", "simulation"],
    ),
    LearningResource(
        id="lenia_project",
        title="Lenia (interactive demo)",
        type="project",
        authors=["Bert Wang-Chak Chan"],
        url="https://chakazul.github.io/lenia.html",
        description="Interactive web demo of Lenia continuous cellular automata.",
        level="beginner",
        tags=["continuous-cellular-automata", "artificial-life", "interactive"],
    ),
    LearningResource(
        id="avida_ed",
        title="Avida-ED",
        type="project",
        url="https://avida-ed.github.io/",
        description="Digital evolution platform - self-replicating programs that evolve.",
        level="beginner",
        tags=["digital-evolution", "artificial-life", "education"],
    ),
    LearningResource(
        id="openworm",
        title="OpenWorm",
        type="project",
        url="https://openworm.org/",
        description="Open-science simulation of C. elegans - 302 neurons, full connectome.",
        level="intermediate",
        tags=["virtual-organism", "c-elegans", "computational-biology"],
    ),
    LearningResource(
        id="alife_org",
        title="International Society for Artificial Life (ISAL)",
        type="website",
        url="https://alife.org/",
        description="Research community for artificial life - conferences, papers, news.",
        level="research",
        tags=["artificial-life", "research-community"],
    ),
    LearningResource(
        id="sfi_complexity_podcast",
        title="Complexity Podcast (Santa Fe Institute)",
        type="podcast",
        authors=["Santa Fe Institute"],
        url="https://www.santafe.edu/culture/podcasts",
        description="Short interviews on complexity, emergence and science at the frontier.",
        level="beginner",
        tags=["complexity", "emergence", "systems", "society"],
    ),
    LearningResource(
        id="mindscape_walker",
        title="Sean Carroll Mindscape - Sara Walker on Information and the Origin of Life",
        type="podcast",
        authors=["Sean Carroll", "Sara Imari Walker"],
        year=2020,
        url="https://www.preposterousuniverse.com/podcast/2020/01/13/79-sara-imari-walker-on-information-and-the-origin-of-life/",
        description="Deep conversation on information, life origins and assembly theory.",
        level="intermediate",
        tags=["information", "origin-of-life", "assembly-theory"],
    ),
    LearningResource(
        id="big_biology_walker",
        title="Big Biology Podcast - Sara Walker on Assembly Theory",
        type="podcast",
        url="https://www.bigbiology.org/",
        description="Biology, life, information and assembly theory explored in depth.",
        level="intermediate",
        tags=["biology", "life", "information", "assembly-theory"],
    ),
)


def get_resource(resource_id: str) -> LearningResource:
    if resource_id not in RESOURCES:
        raise KeyError(f"Resource '{resource_id}' not found. Available: {list(RESOURCES)}")
    return RESOURCES[resource_id]


def list_resources(
    level: Optional[ResourceLevel] = None,
    resource_type: Optional[ResourceType] = None,
    tag: Optional[str] = None,
) -> List[LearningResource]:
    results = list(RESOURCES.values())
    if level:
        results = [r for r in results if r.level == level]
    if resource_type:
        results = [r for r in results if r.type == resource_type]
    if tag:
        results = [r for r in results if tag in r.tags]
    return results
