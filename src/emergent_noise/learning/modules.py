"""
learning/modules.py - LearningModule registry linking presets to learning content (Epic 14).

Each LearningModule is associated with one ExperimentPreset by ID.
Modules contain: learning goals, concepts, intuition, math background,
parameter notes, observation questions, guided experiments, resources.

Scientific caution:
    All descriptions are educational analogies, not exact scientific claims.
    Parameter effects described here are qualitative tendencies observed in
    the abstract field model, not quantitative predictions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ParameterLearningNote:
    """Educational explanation of a single SimConfig parameter.

    Attributes
    ----------
    parameter:
        Exact SimConfig field name.
    plain_language:
        One-sentence intuitive description.
    mathematical_role:
        How this parameter acts mathematically.
    concept_links:
        Concept IDs from the CONCEPTS registry.
    what_happens_if_increased:
        Qualitative description of increasing this parameter.
    what_happens_if_decreased:
        Qualitative description of decreasing this parameter.
    suggested_experiments:
        Short experiment suggestions (plain text).
    """

    parameter: str
    plain_language: str
    mathematical_role: str
    concept_links: List[str] = field(default_factory=list)
    what_happens_if_increased: str = ""
    what_happens_if_decreased: str = ""
    suggested_experiments: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GuidedExperiment:
    """A short guided experiment for a preset.

    Attributes
    ----------
    title:
        Short descriptive name.
    setup:
        What parameter changes to make.
    question:
        The observation question to answer.
    hint:
        Optional hint or expected outcome.
    """

    title: str
    setup: str
    question: str
    hint: str = ""


@dataclass(frozen=True)
class LearningModule:
    """Complete learning content for one ExperimentPreset.

    Attributes
    ----------
    preset_id:
        Must match an existing preset ID in PRESETS.
    learning_goals:
        What a learner should understand after exploring this preset.
    core_concepts:
        Concept IDs from CONCEPTS relevant to this preset.
    intuition:
        Plain-language explanation of what the user is watching.
    mathematical_background:
        Key mathematical ideas in plain language.
    parameter_notes:
        Per-parameter educational notes.
    observation_questions:
        Open questions to guide watching the simulation.
    guided_experiments:
        Step-by-step mini-experiments.
    resource_ids:
        IDs from RESOURCES especially relevant here.
    next_steps:
        Suggestions for where to go deeper.
    """

    preset_id: str
    learning_goals: List[str]
    core_concepts: List[str]
    intuition: str
    mathematical_background: str
    parameter_notes: List[ParameterLearningNote] = field(default_factory=list)
    observation_questions: List[str] = field(default_factory=list)
    guided_experiments: List[GuidedExperiment] = field(default_factory=list)
    resource_ids: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────

LEARNING_MODULES: Dict[str, LearningModule] = {}


def _reg(module: LearningModule) -> None:
    LEARNING_MODULES[module.preset_id] = module


# ──────────────────────────────────────────────────────────────────
# Shared parameter notes (reused across modules)
# ──────────────────────────────────────────────────────────────────

_NOTE_NOISE = ParameterLearningNote(
    parameter="noise_amplitude",
    plain_language="How much random variation is added to the fields every tick.",
    mathematical_role="Additive Gaussian noise on the energy field — controls the noise floor.",
    concept_links=["entropy_information", "self_organization"],
    what_happens_if_increased="More randomness; patterns break up, system explores more state space.",
    what_happens_if_decreased="Less exploration; patterns stabilise but may become rigid or monotonous.",
    suggested_experiments=[
        "Run the preset with noise_amplitude=0.005, 0.03, 0.08 and compare pattern stability.",
    ],
)

_NOTE_MEMORY_DECAY = ParameterLearningNote(
    parameter="memory_decay",
    plain_language="How long traces persist in the memory field before fading.",
    mathematical_role="Multiplicative decay: memory(t+1) = memory(t) * memory_decay each tick.",
    concept_links=["stigmergy", "trace_reading"],
    what_happens_if_increased="Traces persist longer; paths and structures become more stable.",
    what_happens_if_decreased="Traces fade quickly; the system becomes more forgetful and exploratory.",
    suggested_experiments=[
        "Compare memory_decay = 0.80, 0.95, 0.999 — when do stable trails persist?",
    ],
)

_NOTE_MEMORY_IMPRINT = ParameterLearningNote(
    parameter="memory_imprint_strength",
    plain_language="How strongly active energy cells write into the memory field.",
    mathematical_role="Linear imprint: memory += imprint_strength * energy (clipped to [0,1]).",
    concept_links=["stigmergy", "trace_reading"],
    what_happens_if_increased="Memory field fills up faster; traces become more prominent.",
    what_happens_if_decreased="Memory is barely written; traces are faint and transient.",
    suggested_experiments=[
        "Set imprint to 0.1 vs 0.8 — compare how quickly the memory field saturates.",
    ],
)

_NOTE_DIFFUSION_ENERGY = ParameterLearningNote(
    parameter="diffusion_energy",
    plain_language="How quickly energy spreads to neighbouring cells.",
    mathematical_role="Discrete Laplacian with coefficient D: u(t+1) += D * nabla^2(u).",
    concept_links=["reaction_diffusion", "morphogenesis"],
    what_happens_if_increased="Energy spreads faster; local peaks are smoothed, patterns become larger.",
    what_happens_if_decreased="Energy stays localised; sharper, more isolated patterns form.",
    suggested_experiments=[
        "Compare diffusion_energy = 0.01, 0.1, 0.3 — when do spots merge into bands?",
    ],
)

_NOTE_REACTION = ParameterLearningNote(
    parameter="reaction_strength",
    plain_language="How strongly the reaction rule fires when the threshold is crossed.",
    mathematical_role="Reaction term in energy update: energy += reaction_strength when above threshold.",
    concept_links=["reaction_diffusion", "emergence"],
    what_happens_if_increased="Reactions are stronger; patterns form faster and more intensely.",
    what_happens_if_decreased="Weak reactions; system may not produce clear patterns at all.",
    suggested_experiments=[
        "Vary reaction_strength from 0.05 to 0.5 — when do Turing-like patterns appear?",
    ],
)

_NOTE_REACTION_THRESHOLD = ParameterLearningNote(
    parameter="reaction_energy_threshold",
    plain_language="The energy level a cell must exceed before the reaction rule fires.",
    mathematical_role="Heaviside threshold: reaction fires only where energy > threshold.",
    concept_links=["reaction_diffusion", "emergence"],
    what_happens_if_increased="Fewer cells react; pattern is sparser.",
    what_happens_if_decreased="More cells react; reaction spreads broadly and may saturate.",
    suggested_experiments=[
        "Shift threshold from 0.3 to 0.7 — when does the reaction stop producing structure?",
    ],
)

_NOTE_COUPLING_GAIN = ParameterLearningNote(
    parameter="coupling_gain",
    plain_language="How strongly a cell's activity amplifies its neighbours.",
    mathematical_role="Positive feedback term in the coupling field update.",
    concept_links=["self_organization", "stigmergy"],
    what_happens_if_increased="Stronger local amplification; clusters become more pronounced.",
    what_happens_if_decreased="Weak coupling; cells behave more independently.",
    suggested_experiments=[
        "Run at coupling_gain=0.01, 0.05, 0.15 — when do clusters self-organise?",
    ],
)

_NOTE_FLOW_GRADIENT = ParameterLearningNote(
    parameter="flow_gradient_strength",
    plain_language="How strongly the flow field follows energy gradients (downhill tendency).",
    mathematical_role="Flow velocity += gradient_strength * grad(energy) at each step.",
    concept_links=["morphogenesis", "emergence"],
    what_happens_if_increased="Flow is strongly directed; growth or movement becomes more channelled.",
    what_happens_if_decreased="Flow is weak; patterns are more isotropic and diffuse.",
    suggested_experiments=[
        "Increase flow_gradient_strength to 0.3 — does growth become directionally biased?",
    ],
)

_NOTE_COHERENCE = ParameterLearningNote(
    parameter="coupling_sync_rate",
    plain_language="How quickly neighbouring cells synchronise their coupling field values.",
    mathematical_role="Coupling synchronisation rate applied per tick to local neighbourhoods.",
    concept_links=["autopoiesis", "self_organization"],
    what_happens_if_increased="Coupling synchronises quickly; boundaries sharpen and stabilise.",
    what_happens_if_decreased="Coupling synchronises slowly; boundary-like structures are more diffuse.",
    suggested_experiments=[
        "Vary coupling_sync_rate from 0.01 to 0.2 — when do membrane-like rings appear?",
    ],
)


# ──────────────────────────────────────────────────────────────────
# Module: Stigmergy / Ant Trails
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="stigmergy_ant_trails",
    learning_goals=[
        "Understand how indirect coordination (stigmergy) produces path optimisation.",
        "Observe how memory decay and imprint rate balance exploration vs exploitation.",
        "See how positive feedback in a diffusing medium creates attractor paths.",
    ],
    core_concepts=["stigmergy", "self_organization", "emergence", "trace_reading"],
    intuition=(
        "You are watching an abstract field system where the memory field acts like a "
        "pheromone medium. When energy is high in a region, it imprints into the memory field. "
        "That imprint, in turn, attracts more activity. Over time, paths form through positive "
        "feedback — not because any agent planned them, but because they reinforce themselves. "
        "This is an emergent analogue of stigmergic coordination, not a full ant-colony model."
    ),
    mathematical_background=(
        "The memory field follows: memory(t+1) = memory(t) * decay + energy * imprint_strength. "
        "This is a leaky integrator — it accumulates evidence of past activity but forgets "
        "at a rate determined by memory_decay. When decay is close to 1.0, traces persist; "
        "when it is low, the system is forgetful. "
        "Positive feedback occurs because high memory attracts flow (via coupling), "
        "which brings more energy, which writes more memory — a self-amplifying loop. "
        "This loop is stabilised by diffusion (energy spreads) and noise (prevents lock-in)."
    ),
    parameter_notes=[_NOTE_MEMORY_DECAY, _NOTE_MEMORY_IMPRINT, _NOTE_NOISE, _NOTE_COUPLING_GAIN],
    observation_questions=[
        "At what tick do stable paths first appear in the memory field?",
        "Does the system converge to one path or several?",
        "What happens to paths when you increase noise_amplitude?",
        "Do paths ever collapse and reform differently?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Forgetful field",
            setup="Set memory_decay = 0.80, run 300 ticks.",
            question="Do stable trails still emerge, or does the field stay diffuse?",
            hint="Low decay means fast forgetting — paths compete and fade quickly.",
        ),
        GuidedExperiment(
            title="Overpersistent traces",
            setup="Set memory_decay = 0.999, run 300 ticks.",
            question="Does the system become too rigid? Can new paths form?",
            hint="Very high decay locks the system into early patterns.",
        ),
        GuidedExperiment(
            title="Exploration vs exploitation",
            setup="Compare noise_amplitude = 0.005, 0.03, 0.08.",
            question="When does noise help discover new paths, and when does it destroy them?",
        ),
    ],
    resource_ids=["complexityexplorer_abm", "mitchell_complexity", "sfi_complexity_podcast"],
    next_steps=[
        "Explore Ant Colony Optimisation (ACO) algorithms for combinatorial optimisation.",
        "Read about stigmergy in termite mound construction and wasp nest building.",
        "Try the ant_trails_agents preset which adds explicit agent bodies.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Boids Field Approximation
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="boids_field_approx",
    learning_goals=[
        "Understand Reynolds' three flocking rules as field-level coupling.",
        "See how collective motion emerges without central coordination.",
        "Explore the relationship between local alignment and global coherence.",
    ],
    core_concepts=["boids_flocking", "self_organization", "agent_based_modeling", "emergence"],
    intuition=(
        "This preset uses the flow field to approximate Reynolds' Boids behaviour at the "
        "field level: the coupling field encodes a local alignment signal, and flow advection "
        "spreads it. The result is field-level coherent motion that resembles flocking dynamics. "
        "For actual individual-level Boids with explicit agents, see the boids_agents preset."
    ),
    mathematical_background=(
        "Reynolds (1987) showed that three vector rules — separation (avoid crowding), "
        "alignment (match neighbour headings) and cohesion (move toward centre of mass) — "
        "produce emergent flock behaviour. "
        "Here, the coupling field acts as an alignment signal, and the flow field carries "
        "directed momentum. Coherence is measured as the mean cosine similarity of local "
        "velocity vectors. A coherence value near 1.0 means fully aligned; near 0 means "
        "disordered motion."
    ),
    parameter_notes=[_NOTE_COUPLING_GAIN, _NOTE_FLOW_GRADIENT, _NOTE_NOISE],
    observation_questions=[
        "Does the flow field develop a dominant direction, or remain disordered?",
        "What is the velocity coherence score over time?",
        "How does noise_amplitude change the degree of collective alignment?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="No coupling — pure noise",
            setup="Set coupling_gain = 0.0, run 200 ticks.",
            question="Without alignment signal, does coherent motion still emerge?",
        ),
        GuidedExperiment(
            title="Strong flow gradient",
            setup="Set flow_gradient_strength = 0.3, run 200 ticks.",
            question="Does the flow field develop a dominant direction?",
        ),
    ],
    resource_ids=["reynolds_boids", "shiffman_nature_of_code", "complexityexplorer_abm"],
    next_steps=[
        "Try the boids_agents preset for explicit agent-level Boids.",
        "Read Reynolds (1987) original SIGGRAPH paper.",
        "Explore starling murmuration videos as a real-world analogue.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Tree Growth / Branching Morphogenesis
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="tree_growth_branching",
    learning_goals=[
        "Understand how branching structures emerge from gradient-following dynamics.",
        "Connect fractal dimension to complexity of grown structure.",
        "Explore the role of resource gradients in directional growth.",
    ],
    core_concepts=["morphogenesis", "emergence", "self_organization"],
    intuition=(
        "This preset explores how trunk-like and branching structures emerge when energy "
        "flows along gradients and memory imprints the flow paths. The flow field acts as "
        "a resource carrier — where energy flows, it leaves traces that channel future flow. "
        "Over time, these traces branch and extend, producing dendritic or tree-like patterns. "
        "This is a structural analogue of morphogenetic branching, not a developmental model."
    ),
    mathematical_background=(
        "Growth here is driven by positive feedback between flow and memory imprinting. "
        "Flow follows energy gradients: v = v * damping + grad_strength * grad(energy). "
        "Memory records flow paths: memory += imprint_strength * energy. "
        "Branching occurs when a single flow channel bifurcates due to local instabilities. "
        "The fractal dimension (box-counting) of the memory field characterises structural complexity: "
        "a straight line has D~1, a space-filling shape D~2. Typical branching patterns: D~1.3-1.7."
    ),
    parameter_notes=[
        _NOTE_FLOW_GRADIENT, _NOTE_MEMORY_IMPRINT, _NOTE_MEMORY_DECAY,
        _NOTE_REACTION_THRESHOLD, _NOTE_NOISE,
    ],
    observation_questions=[
        "At what tick does the first branching event occur?",
        "Does the structure grow upward, downward or radially?",
        "What is the fractal dimension of the memory field after 200 ticks?",
        "How does the skeleton branch count change over time?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Strong memory, weak noise",
            setup="Set memory_decay=0.998, noise_amplitude=0.01.",
            question="Does growth become more trunk-like with few branches?",
        ),
        GuidedExperiment(
            title="High noise branching",
            setup="Increase noise_amplitude to 0.08.",
            question="Do more side branches appear? Does the fractal dimension increase?",
        ),
        GuidedExperiment(
            title="Strong flow gradient",
            setup="Set flow_gradient_strength = 0.25.",
            question="Does growth become directionally biased (anisotropic)?",
        ),
    ],
    resource_ids=["turing_morphogenesis", "tero_physarum", "mitchell_complexity"],
    next_steps=[
        "Explore L-systems (Lindenmayer Systems) for formal grammar-based plant growth.",
        "Compare with the mycelium_network and river_network presets.",
        "Read about diffusion-limited aggregation (DLA) fractals.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Reaction-Diffusion (Turing)
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="reaction_diffusion_turing",
    learning_goals=[
        "Understand how activator-inhibitor dynamics produce spatial patterns.",
        "See how Turing instability breaks spatial symmetry spontaneously.",
        "Connect reaction-diffusion to biological pattern formation.",
    ],
    core_concepts=["reaction_diffusion", "morphogenesis", "emergence", "cellular_automata"],
    intuition=(
        "You are watching an abstract reaction-diffusion system inspired by Turing (1952). "
        "The energy field acts as an activator that promotes itself locally, "
        "while the information field acts as a diffusing inhibitor that suppresses it at distance. "
        "When the inhibitor diffuses faster than the activator, the uniform state becomes "
        "unstable and breaks into stable spots, stripes or spirals. "
        "This is a structural analogue of how animal coat patterns, shell markings and "
        "some developmental patterns are thought to form — not a biochemically accurate model."
    ),
    mathematical_background=(
        "The Turing mechanism requires two conditions: (1) a self-activating component "
        "that is locally amplified, and (2) a faster-diffusing inhibitor that suppresses "
        "it at longer range. The discrete update is: "
        "u(t+1) = u(t) + D_u * nabla^2(u) + f(u,v); "
        "v(t+1) = v(t) + D_v * nabla^2(v) + g(u,v). "
        "Pattern wavelength scales with sqrt(D / reaction_rate). "
        "Higher diffusion_energy with lower diffusion_information tends to produce stripes; "
        "the reverse produces spots. This is a known Turing bifurcation property."
    ),
    parameter_notes=[
        _NOTE_DIFFUSION_ENERGY, _NOTE_REACTION, _NOTE_REACTION_THRESHOLD, _NOTE_NOISE,
    ],
    observation_questions=[
        "Do spots, stripes or other patterns emerge?",
        "What is the spatial autocorrelation (Moran's I) of the energy field?",
        "At what tick do patterns first become stable?",
        "Does the pattern change qualitatively as you adjust diffusion ratios?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Diffusion balance",
            setup="Compare diffusion_energy=0.05 vs 0.25, keeping diffusion_information fixed.",
            question="Which produces spots, stripes or spatial smoothing?",
        ),
        GuidedExperiment(
            title="Threshold shift",
            setup="Change reaction_energy_threshold from 0.3 to 0.7.",
            question="When does the field stop producing distinct patterns?",
        ),
        GuidedExperiment(
            title="Pattern wavelength",
            setup="Vary reaction_strength from 0.1 to 0.5.",
            question="Does the spacing between pattern elements change?",
        ),
    ],
    resource_ids=["turing_morphogenesis", "lenia_paper", "shiffman_ca_chapter"],
    next_steps=[
        "Read Turing's original 1952 paper — it is surprisingly readable.",
        "Explore the Gray-Scott model as a canonical reaction-diffusion system.",
        "Compare with Lenia which generalises this to continuous kernels.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Excitable Media / Waves
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="excitable_media_waves",
    learning_goals=[
        "Understand excitable media and why they produce travelling waves.",
        "Connect wavefront speed to reaction-diffusion dynamics.",
        "See how periodic patterns emerge from threshold-based activation.",
    ],
    core_concepts=["reaction_diffusion", "emergence", "cellular_automata"],
    intuition=(
        "Excitable media have three states: resting (can fire), excited (firing), refractory "
        "(recovering, cannot fire). When a cell fires, it excites its neighbours, which then "
        "fire in turn — producing a wave that travels outward. The refractory period prevents "
        "back-propagation, so waves annihilate when they collide. "
        "This is seen in cardiac tissue (electrical waves), the Belousov-Zhabotinsky reaction "
        "(chemical spiral waves) and cAMP waves in Dictyostelium aggregation. "
        "This preset uses the energy field as an analogue excitable medium."
    ),
    mathematical_background=(
        "Excitable dynamics require: (1) a threshold — cells fire only above a critical value; "
        "(2) autocatalytic activation — firing cells excite neighbours; "
        "(3) a refractory mechanism — recently fired cells cannot re-fire. "
        "Wavefront speed v ~ sqrt(D * reaction_rate), where D is diffusion. "
        "The refractory period in this model emerges from memory-coupled inhibition. "
        "Spiral waves form when a wavefront breaks — a phenomenon also seen in cardiac arrhythmias."
    ),
    parameter_notes=[
        _NOTE_DIFFUSION_ENERGY, _NOTE_REACTION, _NOTE_REACTION_THRESHOLD, _NOTE_NOISE,
    ],
    observation_questions=[
        "Do planar waves, ring waves or spiral waves emerge?",
        "What is the wavefront speed (cells/tick) shown in the Trace Metrics panel?",
        "Does the wave speed change when you adjust reaction_strength?",
        "At what noise level do spirals start to break down?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Wave speed measurement",
            setup="Run for 100 ticks; watch the wavefront speed metric.",
            question="Does wavefront speed correlate with diffusion_energy?",
        ),
        GuidedExperiment(
            title="Spiral formation",
            setup="Start with a partial-ring initial condition; high reaction_strength.",
            question="Does the broken wave tip curl into a spiral?",
        ),
    ],
    resource_ids=["turing_morphogenesis", "mitchell_complexity"],
    next_steps=[
        "Look up Belousov-Zhabotinsky reaction videos for real chemical spiral waves.",
        "Study FitzHugh-Nagumo model — the canonical excitable neuron model.",
        "Explore cardiac arrhythmia as a real-world excitable media failure mode.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Trace Reading / Fossil Field
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="trace_reading_fossil_field",
    learning_goals=[
        "Understand how past dynamics leave readable traces in field patterns.",
        "Practice interpreting spatial structure as historical evidence.",
        "Explore entropy and spatial autocorrelation as trace-reading metrics.",
    ],
    core_concepts=["trace_reading", "entropy_information", "stigmergy", "emergence"],
    intuition=(
        "This preset is optimised for leaving strong, persistent traces. "
        "You are not primarily watching dynamics unfold — you are reading the record "
        "that past dynamics left behind in the memory and energy fields. "
        "The memory field is like sedimentary rock: each layer records the state of the system "
        "at a previous time. High memory_decay means long geological memory. "
        "The goal is to ask: what happened here? What rules produced this pattern? "
        "Can we reconstruct the history from the spatial structure alone?"
    ),
    mathematical_background=(
        "Trace reading uses several metrics: "
        "memory_persistence (Jaccard similarity between consecutive memory states) "
        "measures how stable the trace is; high persistence = slow-changing history. "
        "Spatial autocorrelation (Moran's I) measures whether nearby cells have similar values; "
        "high Moran's I = clustered, structured traces. "
        "Shannon entropy of the memory field measures structural diversity; "
        "decreasing entropy over time = pattern formation from randomness. "
        "Together these metrics describe whether the field is actively writing history "
        "or reading from a stable record."
    ),
    parameter_notes=[_NOTE_MEMORY_DECAY, _NOTE_MEMORY_IMPRINT, _NOTE_NOISE],
    observation_questions=[
        "What is the memory persistence score after 100 ticks?",
        "Is the Moran's I positive (clustered) or near zero (random)?",
        "Does the memory entropy decrease over time (pattern formation) or stay high?",
        "Can you tell from the memory field alone what kind of dynamics occurred?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Deep memory record",
            setup="Set memory_decay = 0.999. Run 500 ticks.",
            question="What layers of history are visible in the memory field?",
        ),
        GuidedExperiment(
            title="Entropy reading",
            setup="Watch the entropy trend chart in the Spurenlesen tab.",
            question="When does entropy decrease — what does that correspond to visually?",
        ),
    ],
    resource_ids=["walker_information_life", "mindscape_walker", "mitchell_complexity"],
    next_steps=[
        "Read Sara Walker's work on information and the origin of life.",
        "Study ichnology — the science of trace fossils in palaeontology.",
        "Explore information-theoretic approaches to fossil record reconstruction.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Autopoiesis / Membrane
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="autopoiesis_membrane",
    learning_goals=[
        "Understand autopoiesis as self-production and boundary maintenance.",
        "Observe how coupling dynamics can produce membrane-like ring structures.",
        "Explore the distinction between operational closure and thermodynamic openness.",
    ],
    core_concepts=["autopoiesis", "self_organization", "emergence", "complex_adaptive_systems"],
    intuition=(
        "This preset explores whether field dynamics can spontaneously produce and maintain "
        "boundary-like structures without being explicitly programmed with a boundary rule. "
        "The coupling field develops ring-like or shell-like structures when local coherence "
        "is above threshold and energy is contained. "
        "This is a structural analogue of autopoietic organisation — a system that produces "
        "and repairs its own boundary. It is not a model of actual cell membranes. "
        "The key question is: does the system maintain its own boundary, or does it dissolve?"
    ),
    mathematical_background=(
        "Autopoiesis (Maturana & Varela 1972) describes operational closure: "
        "the system produces the components (e.g. membrane lipids) that maintain the system. "
        "Here, coupling coherence plays the role of the membrane: "
        "coupling(t+1) = coupling(t) + gain * [coherence > threshold]. "
        "The energy field inside the boundary drives coupling production; "
        "the boundary in turn modulates energy exchange with the exterior. "
        "Proto-life score is computed from 6 criteria: boundaries, energy flux, "
        "self-maintenance, adaptation, memory, variation."
    ),
    parameter_notes=[_NOTE_COHERENCE, _NOTE_COUPLING_GAIN, _NOTE_NOISE],
    observation_questions=[
        "Does a ring or boundary structure form spontaneously?",
        "Does the boundary persist, dissolve or split over time?",
        "What is the proto-life score in the Partikel tab?",
        "Does increasing noise_amplitude dissolve the boundary?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Boundary stability",
            setup="Increase coherence_threshold and coupling_gain.",
            question="Do more persistent boundary-like clusters appear?",
        ),
        GuidedExperiment(
            title="Fragile membranes",
            setup="Increase noise_amplitude to 0.1.",
            question="At what noise level do boundaries dissolve?",
            hint="There may be a sharp transition — a noise-induced phase change.",
        ),
    ],
    resource_ids=["levy_artificial_life", "walker_information_life", "tononi_iit"],
    next_steps=[
        "Read Maturana & Varela 'Autopoiesis and Cognition' (1980).",
        "Explore artificial cell research (synthetic biology).",
        "Study protocell models in origin-of-life research.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Module: Ecosystem Patch Dynamics
# ──────────────────────────────────────────────────────────────────

_reg(LearningModule(
    preset_id="ecosystem_patch_dynamics",
    learning_goals=[
        "Understand patch dynamics and metapopulation ecology.",
        "See how local extinction and recolonisation produce spatial heterogeneity.",
        "Connect cluster lifetime tracking to ecological turnover.",
    ],
    core_concepts=["complex_adaptive_systems", "self_organization", "emergence"],
    intuition=(
        "This preset models a multi-scale patchy landscape. Active patches (high energy) "
        "can go extinct locally (energy drops below threshold) and be recolonised from "
        "neighbouring patches via diffusion-like spread. "
        "The memory field records where activity has been — like a habitat map. "
        "The result is a mosaic landscape with persistent turnover: patches appear, persist "
        "for a characteristic time, and disappear. "
        "This is a structural analogue of ecological patch dynamics and metapopulation models — "
        "not a species-level ecological simulation."
    ),
    mathematical_background=(
        "Patch dynamics models (Levin & Paine 1974) treat a habitat as a mosaic of patches "
        "in different successional states. Local extinction occurs when conditions fall below "
        "a threshold; recolonisation depends on proximity to occupied patches. "
        "Here: energy > reaction_energy_threshold defines an occupied patch; "
        "diffusion_energy controls colonisation rate; memory_decay controls habitat persistence. "
        "Cluster lifetime tracking (Epic 13) directly measures the distribution of patch lifetimes."
    ),
    parameter_notes=[
        _NOTE_DIFFUSION_ENERGY, _NOTE_REACTION_THRESHOLD,
        _NOTE_MEMORY_DECAY, _NOTE_NOISE,
    ],
    observation_questions=[
        "What is the mean cluster lifetime after 200 ticks?",
        "Do patches re-appear in the same locations repeatedly?",
        "How does diffusion_energy affect colonisation speed?",
        "Is the spatial distribution of patches random or clustered (Moran's I)?",
    ],
    guided_experiments=[
        GuidedExperiment(
            title="Fragmented landscape",
            setup="Reduce diffusion_energy to 0.02.",
            question="Do patches become isolated? Does mean cluster lifetime increase?",
        ),
        GuidedExperiment(
            title="Disturbance regime",
            setup="Increase noise_amplitude to 0.1.",
            question="Does turnover accelerate? Do patch lifetimes shorten?",
        ),
    ],
    resource_ids=["mitchell_complexity", "complexityexplorer_abm", "sfi_complexity_podcast"],
    next_steps=[
        "Read about spatially explicit metapopulation models (Hanski 1999).",
        "Explore NetLogo patch dynamics models on the Complexity Explorer.",
        "Study intermediate disturbance hypothesis in ecology.",
    ],
))


# ──────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────

def get_learning_module(preset_id: str) -> Optional[LearningModule]:
    return LEARNING_MODULES.get(preset_id)


def list_learning_modules() -> List[LearningModule]:
    return list(LEARNING_MODULES.values())
