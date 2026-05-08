# Concept Library

Core concepts from complex systems science, artificial life and information theory,
as implemented or explored in Emergent Noise.

---

## Emergence
Global patterns arise from local rules without being explicitly programmed.
A traffic jam, a termite mound, a Turing pattern — none are encoded centrally.
*Mathematical keywords:* nonlinearity, local interactions, phase transitions, attractor landscapes.
*Visible in:* reaction_diffusion_turing, stigmergy_ant_trails, tree_growth_branching.

## Cellular Automata
A grid of cells updating in parallel according to fixed local neighbourhood rules.
Despite simplicity, CAs can produce universal computation (Wolfram Rule 110).
Emergent Noise uses a continuous multi-field variant.
*Mathematical keywords:* discrete dynamical systems, neighbourhoods, universality.
*Visible in:* reaction_diffusion_turing, excitable_media_waves.

## Artificial Life
Study and synthesis of life-like processes in non-biological substrates.
Key projects: Avida (digital evolution), Lenia (continuous CA), OpenWorm (virtual C. elegans).
This simulator provides abstract field analogues — not accurate biological models.
*Mathematical keywords:* self-replication, open-ended evolution, proto-metabolism.
*Visible in:* autopoiesis_membrane, ecosystem_patch_dynamics.

## Reaction-Diffusion Systems
Two interacting chemicals with different diffusion rates spontaneously form spatial patterns.
Turing (1952): short-range activation + long-range inhibition breaks spatial symmetry.
*Mathematical keywords:* activator-inhibitor, Laplacian, Turing instability, symmetry breaking.
*Visible in:* reaction_diffusion_turing.

## Stigmergy
Indirect coordination through traces left in a shared environment.
Ants deposit pheromone; others follow the strongest trail; paths reinforce.
The memory field acts as the shared trace medium.
*Mathematical keywords:* positive feedback, decay, path reinforcement, distributed coordination.
*Visible in:* stigmergy_ant_trails, trace_reading_fossil_field.

## Self-Organisation
Order arising spontaneously from local interactions without external control.
Examples: snowflakes, sand dunes, bird flocking, neural development.
*Mathematical keywords:* feedback loops, instabilities, dissipative structures.
*Visible in:* stigmergy_ant_trails, autopoiesis_membrane, boids_field_approx.

## Morphogenesis
The process by which organisms develop shape, structure and form.
Turing reaction-diffusion, Wolpert's positional information and mechanical forces all play roles.
*Mathematical keywords:* gradient fields, branching processes, fractal dimension, skeleton extraction.
*Visible in:* tree_growth_branching, mycelium_network, reaction_diffusion_turing.

## Autopoiesis
A system that continuously produces and maintains the components that constitute it.
Maturana & Varela (1972): operationally closed but thermodynamically open.
This simulator explores structural analogues of boundary maintenance — not actual autopoiesis.
*Mathematical keywords:* operational closure, self-production, boundary formation.
*Visible in:* autopoiesis_membrane.

## Boids / Flocking
Three simple rules (separation, alignment, cohesion) produce lifelike flocking.
Reynolds (1987): no central coordination needed.
*Mathematical keywords:* vector averages, local perception radius, velocity coherence.
*Visible in:* boids_field_approx, boids_agents.

## Entropy and Information
Shannon entropy H(X) = -sum(p_i * log2(p_i)) measures uncertainty.
High entropy = many equally likely outcomes. Structured patterns have lower entropy.
Mutual information measures how much knowing one field reduces uncertainty about another.
*Mathematical keywords:* Shannon entropy, mutual information, KL divergence.
*Visible in:* trace_reading_fossil_field, reaction_diffusion_turing.

## Agent-Based Modeling
Autonomous agents follow local rules; collective behaviour emerges.
Captures heterogeneity, discrete events and spatial structure naturally.
*Mathematical keywords:* autonomous agents, spatial hashing, neighbourhood search.
*Visible in:* boids_agents, ant_trails_agents, ecosystem_patch_dynamics.

## Trace Reading
Inferring history and structure from field patterns left behind.
Reverses simulation direction: pattern → what rules/history produced this?
In palaeontology, trace fossils (ichnology) reveal extinct organisms.
*Mathematical keywords:* inverse problem, persistence, spatial autocorrelation, wavefront speed.
*Visible in:* trace_reading_fossil_field, stigmergy_ant_trails.

## Complex Adaptive Systems
Systems whose components learn and adapt, changing the system's own behaviour.
Studied by the Santa Fe Institute across ecology, economics, social science and biology.
*Mathematical keywords:* adaptation, selection pressure, co-evolution, bounded rationality.
*Visible in:* ecosystem_patch_dynamics, autopoiesis_membrane.

## Open-Ended Evolution
Evolution that continues producing novelty indefinitely without converging.
One of the central unsolved problems in ALife.
*Mathematical keywords:* fitness landscapes, neutral evolution, evolvability.
*Visible in:* ecosystem_patch_dynamics.
