"""
experiments/presets.py – Simulation Gallery: reproducible ExperimentPresets (Epic 9).

Each preset is a small research object combining a SimConfig with rich metadata:
description, inspiration, expected patterns, key parameters, limitations and
suggested metrics. Presets are designed for use in the dashboard gallery and
as standalone reproducible experiments.

Scientific caution:
    Presets are not claims of exact biological, physical or cognitive realism.
    They are exploratory field experiments for studying emergent analogues.
    Labels like "ant trails", "boids", "tree growth" refer to the structural
    inspiration, not to accurate simulations of those systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from emergent_noise.core.initial_conditions import (
    InitialCondition,
    BottomSeed,
    BottomUpEnergyGradient,
    CenteredSeed,
    CompoundInitialCondition,
    RadialBurst,
    RandomClusteredSeed,
    SinusoidalDisturbance,
    TopDownEnergyGradient,
    UniformBaseline,
)
from emergent_noise.core.state import SimConfig


# ──────────────────────────────────────────────────────────────────
# Supporting dataclasses
# ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ParticleSettings:
    """Recommended particle system settings for a preset.

    These map directly onto ParticleConfig fields and can be applied
    when loading a preset in the dashboard.
    """

    enabled: bool = False
    count: int = 50
    field_attraction: float = 0.05
    flow_drag: float = 0.3
    velocity_damping: float = 0.92
    collision_radius: float = 1.5
    min_mass_for_compartment: float = 3.0


@dataclass(frozen=True)
class ExperimentPreset:
    """A simulation gallery entry: config + rich research metadata.

    Attributes
    ----------
    id:
        Unique snake_case identifier.
    title:
        Human-readable display title.
    category:
        Broad category for grouping in the gallery UI.
    description:
        Short description of purpose and expected behaviour.
    inspiration:
        Conceptual / scientific inspiration with explicit caveats.
    config:
        The SimConfig that defines this simulation.
    expected_patterns:
        List of patterns a user should look for.
    key_parameters:
        SimConfig field names that most strongly influence this preset.
    limitations:
        Honest description of what the model cannot do yet.
    suggested_metrics:
        Analysis metrics recommended for evaluating this preset.
    particle_settings:
        Recommended particle system configuration.
    tags:
        Free-form tags for search and filtering.
    experimental:
        If True, the dashboard shows a caution banner.
    """

    id: str
    title: str
    category: str
    description: str
    inspiration: str
    config: SimConfig
    expected_patterns: List[str] = field(default_factory=list)
    key_parameters: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    suggested_metrics: List[str] = field(default_factory=list)
    particle_settings: ParticleSettings = field(default_factory=ParticleSettings)
    tags: List[str] = field(default_factory=list)
    experimental: bool = False
    initial_condition: Optional[InitialCondition] = None


# ──────────────────────────────────────────────────────────────────
# Preset definitions
# ──────────────────────────────────────────────────────────────────

STIGMERGY_ANT_TRAILS = ExperimentPreset(
    id="stigmergy_ant_trails",
    title="Stigmergy / Ant Trails",
    category="Collective Behavior",
    description=(
        "Explores indirect coordination through persistent memory traces. "
        "Inspired by ant pheromone trails and stigmergic reinforcement loops. "
        "This is an abstract field-particle model, not an ant colony simulation."
    ),
    inspiration=(
        "In ant colonies, individuals deposit pheromone-like chemicals into the environment. "
        "Other individuals are then attracted to these traces, creating positive feedback loops "
        "and stabilising paths. This preset approximates that dynamic through memory imprinting, "
        "slow decay and particle-field coupling — without explicit agent decisions or nest/food logic."
    ),
    config=SimConfig(
        height=64, width=64, seed=42,
        diffusion_energy=0.03,
        diffusion_information=0.02,
        reaction_energy_threshold=0.45,
        reaction_strength=0.06,
        memory_decay=0.995,
        memory_imprint_strength=0.6,
        coupling_gain=0.08,
        coupling_loss=0.02,
        coupling_sync_rate=0.03,
        noise_amplitude=0.01,
        flow_damping=0.98,
        flow_gradient_strength=0.04,
    ),
    particle_settings=ParticleSettings(
        enabled=True,
        count=150,
        field_attraction=0.12,
        min_mass_for_compartment=3.0,
        flow_drag=0.1,
    ),
    expected_patterns=[
        "persistent trail-like memory structures",
        "local reinforcement loops",
        "path stabilisation over time",
        "slow decay of previously active routes",
    ],
    key_parameters=[
        "memory_decay",
        "memory_imprint_strength",
        "coupling_gain",
        "diffusion_energy",
        "noise_amplitude",
    ],
    limitations=[
        "Not a full ant colony model — no explicit food sources, nest locations or agent decisions.",
        "Particles are field-driven and do not have individual behavioural policies.",
        "Trail formation depends on initial conditions and may require many ticks to stabilise.",
    ],
    suggested_metrics=[
        "memory field persistence",
        "path density (memory field mean)",
        "cluster connectivity",
        "entropy reduction over time",
    ],
    tags=["stigmergy", "ants", "pheromones", "collective-behavior", "memory"],
    initial_condition=RandomClusteredSeed(n_clusters=6, cluster_radius=3.0, energy_value=0.8, seed=42),
)


BOIDS_FIELD_APPROX = ExperimentPreset(
    id="boids_field_approx",
    title="Boids Field Approximation",
    category="Collective Behavior",
    description=(
        "Explores flock-like collective movement through field coupling, coherence and flow dynamics. "
        "This is a field-based approximation — not a classical Boids implementation with explicit "
        "separation, alignment and cohesion rules between agents."
    ),
    inspiration=(
        "Classical Boids (Reynolds 1987) use three local rules: separation, alignment, cohesion. "
        "This preset approximates some flock-like dynamics through coherent coupling fields and "
        "flow-driven particle drift. True velocity alignment between neighbouring particles is "
        "not yet implemented — that is planned for the real agent layer (Epic 11)."
    ),
    config=SimConfig(
        height=64, width=64, seed=7,
        diffusion_energy=0.12,
        diffusion_information=0.06,
        reaction_energy_threshold=0.50,
        reaction_strength=0.10,
        memory_decay=0.92,
        memory_imprint_strength=0.15,
        coupling_gain=0.12,
        coupling_loss=0.015,
        coupling_sync_rate=0.08,
        flow_damping=0.85,
        flow_gradient_strength=0.10,
        noise_amplitude=0.04,
    ),
    particle_settings=ParticleSettings(
        enabled=True,
        count=200,
        field_attraction=0.06,
        min_mass_for_compartment=1.0,
        flow_drag=0.15,
    ),
    expected_patterns=[
        "field-driven collective drift",
        "loose flock-like particle streams",
        "rotational or wave-like flow patterns",
        "temporary coherent particle clusters",
    ],
    key_parameters=[
        "flow_gradient_strength",
        "flow_damping",
        "coupling_gain",
        "noise_amplitude",
    ],
    limitations=[
        "Not a true Boids model — no explicit velocity alignment between particles.",
        "No direct separation or cohesion rules between neighbouring agents.",
        "Collective movement emerges from field gradients, not inter-agent communication.",
    ],
    suggested_metrics=[
        "mean particle velocity coherence",
        "particle clustering",
        "flow curl magnitude",
        "coherence field variance",
    ],
    tags=["boids", "swarm", "flocking", "flow", "collective-behavior"],
    experimental=True,
)


TREE_GROWTH_BRANCHING = ExperimentPreset(
    id="tree_growth_branching",
    title="Tree Growth / Branching Morphogenesis",
    category="Morphogenesis",
    description=(
        "Explores tree-like growth, branching and resource-seeking morphogenesis "
        "through memory stabilisation, flow gradients and local reinforcement. "
        "This is an abstract branching field simulation, not a botanical model."
    ),
    inspiration=(
        "Inspired by plant growth, vascular transport, diffusion-limited aggregation "
        "and morphogenetic self-organisation. Energy corresponds abstractly to light/nutrients, "
        "memory to stabilised woody tissue, flow to transport channels, "
        "and coupling to local reinforcement of existing branches. "
        "No hormones, leaves or actual plant physiology are modelled."
    ),
    config=SimConfig(
        height=96, width=96, seed=21,
        diffusion_energy=0.04,
        diffusion_information=0.08,
        reaction_energy_threshold=0.38,
        reaction_strength=0.09,
        memory_decay=0.998,
        memory_imprint_strength=0.45,
        coupling_gain=0.10,
        coupling_loss=0.01,
        coupling_sync_rate=0.04,
        flow_damping=0.94,
        flow_gradient_strength=0.08,
        noise_amplitude=0.025,
    ),
    particle_settings=ParticleSettings(
        enabled=True,
        count=80,
        field_attraction=0.10,
        min_mass_for_compartment=2.5,
        flow_drag=0.08,
    ),
    expected_patterns=[
        "branch-like memory structures",
        "expanding growth fronts",
        "locally reinforced stems",
        "asymmetric branching driven by noise and gradients",
    ],
    key_parameters=[
        "memory_decay",
        "memory_imprint_strength",
        "flow_gradient_strength",
        "coupling_gain",
        "reaction_energy_threshold",
        "noise_amplitude",
    ],
    limitations=[
        "Not a biological tree model — no explicit hormones, roots, leaves or vascular tissue.",
        "Branching is field-driven rather than governed by plant physiology.",
        "No directed initial conditions (seed/root from bottom) yet — planned for Epic 10.",
        "Fractal dimension and skeleton analysis not yet implemented — planned for Epic 12.",
    ],
    suggested_metrics=[
        "branch count (cluster count in memory field)",
        "memory field persistence",
        "growth front velocity",
        "spatial entropy over time",
    ],
    tags=["tree-growth", "morphogenesis", "branching", "plants", "growth"],
    initial_condition=CompoundInitialCondition([
        TopDownEnergyGradient(top_value=0.15, bottom_value=0.85),
        BottomSeed(band_height=5, energy_value=0.9, also_matter=True),
    ]),
)


REACTION_DIFFUSION_TURING = ExperimentPreset(
    id="reaction_diffusion_turing",
    title="Reaction-Diffusion / Turing-like Patterns",
    category="Pattern Formation",
    description=(
        "Explores spot, stripe and wave-like pattern formation through local reaction "
        "and global diffusion dynamics. Inspired by Turing's morphogenesis hypothesis."
    ),
    inspiration=(
        "Turing (1952) showed that a simple reaction-diffusion system with a short-range activator "
        "and long-range inhibitor can spontaneously form spatial patterns. "
        "This preset uses the existing abstract energy/information fields rather than a strict "
        "two-species model (e.g. Gray-Scott). The diffusion asymmetry between energy and information "
        "fields provides the activator-inhibitor-like dynamics."
    ),
    config=SimConfig(
        height=96, width=96, seed=13,
        diffusion_energy=0.16,
        diffusion_information=0.045,
        reaction_energy_threshold=0.48,
        reaction_strength=0.14,
        memory_decay=0.96,
        memory_imprint_strength=0.2,
        coupling_gain=0.06,
        coupling_loss=0.025,
        coupling_sync_rate=0.04,
        flow_damping=0.9,
        flow_gradient_strength=0.02,
        noise_amplitude=0.03,
    ),
    expected_patterns=[
        "spots and stripe-like domains",
        "reaction fronts propagating across the field",
        "spatially localised pattern domains",
        "wavelength selection through diffusion ratio",
    ],
    key_parameters=[
        "diffusion_energy",
        "diffusion_information",
        "reaction_strength",
        "reaction_energy_threshold",
    ],
    limitations=[
        "Not a strict two-species reaction-diffusion model.",
        "Uses abstract fields instead of named activator/inhibitor variables.",
        "Pattern wavelength and type depend sensitively on initial conditions.",
    ],
    suggested_metrics=[
        "spatial entropy",
        "dominant pattern wavelength",
        "cluster count",
        "field variance over time",
    ],
    tags=["reaction-diffusion", "turing-patterns", "morphogenesis", "pattern-formation"],
    initial_condition=SinusoidalDisturbance(wavelength=20.0, amplitude=0.15, axis=0),
)


EXCITABLE_MEDIA_WAVES = ExperimentPreset(
    id="excitable_media_waves",
    title="Excitable Media / Wave Propagation",
    category="Bio-inspired Dynamics",
    description=(
        "Explores threshold-driven excitation waves, refractory-like memory suppression "
        "and propagating activity fronts. Inspired by excitable media in biology and chemistry."
    ),
    inspiration=(
        "Excitable media (neural tissue, cardiac muscle, Belousov-Zhabotinsky reaction) support "
        "threshold-triggered waves that leave a refractory zone behind them. "
        "This preset uses high reaction thresholds and strong memory decay to approximate "
        "excitation-refractory dynamics. No physiological ion channels or actual neuroscience "
        "is modelled."
    ),
    config=SimConfig(
        height=96, width=96, seed=31,
        diffusion_energy=0.10,
        diffusion_information=0.08,
        reaction_energy_threshold=0.62,
        reaction_strength=0.22,
        memory_decay=0.88,
        memory_imprint_strength=0.35,
        coupling_gain=0.13,
        coupling_loss=0.04,
        coupling_sync_rate=0.06,
        flow_damping=0.91,
        flow_gradient_strength=0.03,
        noise_amplitude=0.02,
    ),
    expected_patterns=[
        "propagating activity fronts",
        "temporary refractory-like suppression zones",
        "spiral or ring-like waves if conditions allow",
        "oscillatory excitation patterns",
    ],
    key_parameters=[
        "reaction_energy_threshold",
        "reaction_strength",
        "memory_decay",
        "coupling_gain",
    ],
    limitations=[
        "No explicit refractory state variable yet — memory field approximates this.",
        "No real neuron, cardiac cell or BZ-reaction chemistry.",
        "Wave speed and frequency depend on grid resolution and tick rate.",
    ],
    suggested_metrics=[
        "wavefront speed (cluster propagation)",
        "activation density over time",
        "oscillation frequency",
        "spatial coherence",
    ],
    tags=["excitable-media", "waves", "neural-inspired", "bio-inspired", "oscillation"],
    initial_condition=RadialBurst(ring_width=3.0, energy_value=0.95),
)


TRACE_READING_FOSSIL_FIELD = ExperimentPreset(
    id="trace_reading_fossil_field",
    title="Trace Reading / Fossil Field",
    category="Trace Reading",
    description=(
        "Explores how past events leave persistent, partially readable traces in memory, "
        "information and coherence fields. Designed for trace-reading analysis workflows."
    ),
    inspiration=(
        "Inspired by tracking, forensics, geological sedimentation and abductive inference. "
        "The field is treated as a landscape where past activity leaves structural residues. "
        "Very slow memory decay (≈0.999) means events accumulate like sediment layers. "
        "This aligns with the project's core idea: treating fields as readable historical records."
    ),
    config=SimConfig(
        height=96, width=96, seed=55,
        diffusion_energy=0.05,
        diffusion_information=0.035,
        reaction_energy_threshold=0.52,
        reaction_strength=0.08,
        memory_decay=0.999,
        memory_imprint_strength=0.5,
        coupling_gain=0.04,
        coupling_loss=0.01,
        coupling_sync_rate=0.02,
        flow_damping=0.97,
        flow_gradient_strength=0.045,
        noise_amplitude=0.015,
    ),
    expected_patterns=[
        "long-lived persistent trace structures",
        "sediment-like residual memory accumulation",
        "directional deformation from flow gradients",
        "historical memory scars from early high-energy events",
    ],
    key_parameters=[
        "memory_decay",
        "memory_imprint_strength",
        "diffusion_information",
        "flow_gradient_strength",
    ],
    limitations=[
        "Trace inference is not yet a full Bayesian reconstruction.",
        "Memory field accumulates linearly — no selective forgetting yet.",
        "Analysis layer currently provides descriptive metrics only.",
    ],
    suggested_metrics=[
        "trace persistence (memory field mean over time)",
        "memory entropy",
        "directional flow alignment",
        "field autocorrelation",
    ],
    tags=["trace-reading", "memory", "forensics", "tracking", "history", "sedimentation"],
)


AUTOPOIESIS_MEMBRANE = ExperimentPreset(
    id="autopoiesis_membrane",
    title="Autopoiesis / Membrane Formation",
    category="Artificial Life",
    description=(
        "Explores boundary formation, inside/outside differentiation and self-maintaining structures. "
        "Inspired by autopoiesis and protocell research — this is a conceptual ALife preset."
    ),
    inspiration=(
        "Maturana & Varela's autopoiesis concept describes systems that continuously reproduce "
        "their own boundary conditions. Protocell research (Luisi, Szostak) explores how simple "
        "chemical systems can form self-enclosing membranes. "
        "This preset uses strong coherence coupling and high memory retention to explore "
        "whether the field self-organises into persistent bounded regions. "
        "No biochemistry or metabolism is modelled."
    ),
    config=SimConfig(
        height=96, width=96, seed=89,
        diffusion_energy=0.07,
        diffusion_information=0.04,
        reaction_energy_threshold=0.44,
        reaction_strength=0.12,
        memory_decay=0.985,
        memory_imprint_strength=0.32,
        coupling_gain=0.15,
        coupling_loss=0.018,
        coupling_sync_rate=0.07,
        flow_damping=0.93,
        flow_gradient_strength=0.035,
        noise_amplitude=0.02,
    ),
    expected_patterns=[
        "localised coherent regions with sharper boundaries",
        "inside/outside coherence differentiation",
        "temporary self-maintaining clusters",
        "boundary-like coupling structures",
    ],
    key_parameters=[
        "coupling_gain",
        "coupling_sync_rate",
        "memory_decay",
        "reaction_strength",
    ],
    limitations=[
        "No explicit membrane chemistry or lipid bilayer analogue.",
        "No metabolism variable — energy is not consumed or regenerated.",
        "No reproduction mechanism — structures do not self-replicate.",
    ],
    suggested_metrics=[
        "boundary sharpness (coherence field gradient)",
        "cluster persistence over time",
        "inside/outside coherence contrast",
        "proto-life score from consciousness module",
    ],
    tags=["autopoiesis", "artificial-life", "membrane", "proto-life", "protocell"],
)


ECOSYSTEM_PATCH_DYNAMICS = ExperimentPreset(
    id="ecosystem_patch_dynamics",
    title="Ecosystem Patch Dynamics",
    category="Ecology",
    description=(
        "Explores resource patches, regeneration cycles, disturbance and succession-like dynamics. "
        "Inspired by landscape ecology and patch dynamics theory."
    ),
    inspiration=(
        "Ecosystem patch models (Levin, Paine, Tilman) study how disturbance, colonisation "
        "and local resource dynamics create heterogeneous landscapes. "
        "Energy corresponds abstractly to resources/productivity, memory to ecological legacy, "
        "noise to disturbance and coupling to local biotic interactions. "
        "No species, trophic networks or seasonal forcing are modelled."
    ),
    config=SimConfig(
        height=96, width=96, seed=144,
        diffusion_energy=0.06,
        diffusion_information=0.03,
        reaction_energy_threshold=0.40,
        reaction_strength=0.07,
        memory_decay=0.992,
        memory_imprint_strength=0.25,
        coupling_gain=0.09,
        coupling_loss=0.012,
        coupling_sync_rate=0.05,
        flow_damping=0.96,
        flow_gradient_strength=0.025,
        noise_amplitude=0.035,
    ),
    expected_patterns=[
        "resource patches expanding and contracting",
        "succession-like spatial dynamics",
        "collapse and recovery zones driven by noise",
        "heterogeneous landscape memory patterns",
    ],
    key_parameters=[
        "reaction_strength",
        "memory_decay",
        "coupling_gain",
        "noise_amplitude",
    ],
    limitations=[
        "No explicit species variables — one abstract energy field only.",
        "No trophic network — no predator-prey interactions.",
        "No seasonal or periodic forcing yet.",
    ],
    suggested_metrics=[
        "patch count over time",
        "patch persistence",
        "spatial entropy",
        "landscape heterogeneity (field variance)",
    ],
    tags=["ecology", "succession", "patch-dynamics", "resources", "landscape"],
)


BOIDS_AGENTS = ExperimentPreset(
    id="boids_agents",
    title="Boids — Real Agent Flock",
    category="Collective Behavior",
    description=(
        "Reynolds (1987) Boids with explicit heading, separation, alignment and cohesion. "
        "Agents are layered on top of the field simulation — they both follow and perturb "
        "the energy field."
    ),
    inspiration=(
        "Craig Reynolds (1987) introduced three local rules — separation, alignment, cohesion — "
        "that generate realistic flock behaviour. This is a faithful implementation of those "
        "rules in a continuous toroidal space, coupled to the abstract energy field."
    ),
    config=SimConfig(
        height=64, width=64, seed=11,
        noise_amplitude=0.03,
        diffusion_energy=0.12,
        flow_gradient_strength=0.06,
        coupling_gain=0.06,
        memory_decay=0.92,
    ),
    expected_patterns=[
        "local flocking groups converging toward alignment",
        "velocity coherence rising over 50+ ticks",
        "agents clustering near high-energy field zones",
        "heading histogram narrowing (flock direction selection)",
    ],
    key_parameters=[
        "flow_gradient_strength",
        "diffusion_energy",
        "coupling_gain",
        "memory_decay",
        "noise_amplitude",
    ],
    limitations=[
        "No nest or food sources — agents have no goal beyond flocking.",
        "No obstacle avoidance.",
        "Field coupling is one-directional (field → agents via flow drag); "
        "agents deposit minimal energy only.",
    ],
    suggested_metrics=[
        "velocity coherence over time",
        "heading std (decreases as flock forms)",
        "mean speed",
        "spatial clustering of agent positions",
    ],
    tags=["boids", "flocking", "collective-behavior", "agents", "reynolds"],
    initial_condition=RandomClusteredSeed(n_clusters=4, cluster_radius=5.0, energy_value=0.85, seed=11),
)


ANT_TRAILS_AGENTS = ExperimentPreset(
    id="ant_trails_agents",
    title="Ant Trails — Pheromone Agents",
    category="Collective Behavior",
    description=(
        "Real agents following memory-field pheromone gradients with random exploration. "
        "Agents deposit into the memory field, creating positive feedback that reinforces "
        "existing trails — emergent path formation without central coordination."
    ),
    inspiration=(
        "Deneubourg et al. (1990) showed that simple local pheromone rules produce complex "
        "colony-level path selection and shortest-path behaviour. "
        "This preset uses the abstract memory field as the pheromone substrate. "
        "No nest, food, or task assignment is modelled."
    ),
    config=SimConfig(
        height=64, width=64, seed=7,
        noise_amplitude=0.02,
        memory_decay=0.997,
        memory_imprint_strength=0.45,
        diffusion_information=0.03,
        coupling_gain=0.04,
        flow_gradient_strength=0.05,
    ),
    expected_patterns=[
        "trail-like memory structures forming and stabilising",
        "positive feedback loop: agents reinforce their own trails",
        "path convergence over 200+ ticks",
        "memory field branching network patterns",
    ],
    key_parameters=[
        "memory_decay",
        "memory_imprint_strength",
        "diffusion_information",
        "flow_gradient_strength",
        "coupling_gain",
    ],
    limitations=[
        "No nest or food source — agents have no destination.",
        "No shortest-path selection without source/sink geometry.",
        "Pheromone evaporation is approximated by memory_decay only.",
    ],
    suggested_metrics=[
        "memory field mean over time (trail accumulation rate)",
        "memory entropy (trail structure complexity)",
        "agent spatial clustering (trail following)",
        "path persistence",
    ],
    tags=["ants", "pheromones", "stigmergy", "trail-formation", "agents", "self-organization"],
    initial_condition=RandomClusteredSeed(n_clusters=3, cluster_radius=4.0, energy_value=0.8, seed=7),
)


# ──────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────

PRESETS: Dict[str, ExperimentPreset] = {
    p.id: p
    for p in [
        STIGMERGY_ANT_TRAILS,
        BOIDS_FIELD_APPROX,
        TREE_GROWTH_BRANCHING,
        REACTION_DIFFUSION_TURING,
        EXCITABLE_MEDIA_WAVES,
        TRACE_READING_FOSSIL_FIELD,
        AUTOPOIESIS_MEMBRANE,
        ECOSYSTEM_PATCH_DYNAMICS,
        BOIDS_AGENTS,
        ANT_TRAILS_AGENTS,
    ]
}


# ──────────────────────────────────────────────────────────────────
# Registry helpers
# ──────────────────────────────────────────────────────────────────

def get_preset(preset_id: str) -> ExperimentPreset:
    """Return a preset by ID. Raises KeyError with a helpful message if not found."""
    if preset_id not in PRESETS:
        available = ", ".join(sorted(PRESETS))
        raise KeyError(
            f"Unknown preset '{preset_id}'. Available: {available}"
        )
    return PRESETS[preset_id]


def list_presets() -> List[ExperimentPreset]:
    """Return all presets in registration order."""
    return list(PRESETS.values())


def list_categories() -> List[str]:
    """Return sorted list of unique category names."""
    return sorted({p.category for p in PRESETS.values()})


def list_presets_by_category(category: str) -> List[ExperimentPreset]:
    """Return all presets belonging to the given category."""
    return [p for p in PRESETS.values() if p.category == category]
