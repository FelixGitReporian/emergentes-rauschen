"""
examples/run_preset.py – Run a simulation preset from the command line.

Usage:
    python examples/run_preset.py --preset stigmergy_ant_trails --steps 300
    python examples/run_preset.py --list
"""

from __future__ import annotations

import argparse
import sys
import time

import numpy as np

from emergent_noise.analysis.compartments import detect_compartments
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.core.state import GridState
from emergent_noise.core.tick import TickLoop
from emergent_noise.experiments.presets import get_preset, list_categories, list_presets
from emergent_noise.interpretation.consciousness import ConsciousnessAnalyzer
from emergent_noise.interpretation.regime_classifier import classify_regime


def _print_presets() -> None:
    print("\nAvailable presets:\n")
    for cat in list_categories():
        print(f"  [{cat}]")
        for p in list_presets():
            if p.category == cat:
                exp_flag = "  ⚠ experimental" if p.experimental else ""
                print(f"    {p.id:<35}  {p.title}{exp_flag}")
    print()


def run(preset_id: str, steps: int, analyze_every: int = 50) -> None:
    try:
        preset = get_preset(preset_id)
    except KeyError as e:
        print(f"\n❌ {e}\n")
        _print_presets()
        sys.exit(1)

    print(f"\n🧪 Preset:  {preset.title}")
    print(f"   Category: {preset.category}")
    if preset.experimental:
        print("   ⚠️  Experimental — interpret results carefully.")
    print(f"   {preset.description}\n")
    print(f"   Grid:  {preset.config.height}×{preset.config.width}  |  Seed: {preset.config.seed}")
    print(f"   Steps: {steps}  |  Analyzing every {analyze_every} ticks\n")

    state = GridState.initialize(preset.config)
    loop = TickLoop(preset.config)
    canalyzer = ConsciousnessAnalyzer()

    t0 = time.perf_counter()
    records = []

    for tick in range(steps):
        loop.step(state)

        if tick % analyze_every == 0 or tick == steps - 1:
            entropy = state_entropy_summary(state)
            comp = detect_compartments(state, min_area=4)
            regime = classify_regime(state.tick, state.as_dict())
            cmark = canalyzer.analyze(state)

            record = {
                "tick": state.tick,
                "entropy_energy": round(entropy.get("energy", 0.0), 4),
                "n_compartments": comp.n_compartments,
                "proto_life": round(comp.max_proto_life_score, 3),
                "phi_proxy": round(cmark.phi_proxy, 4),
                "integrated": round(cmark.integrated_score, 4),
                "regime": regime.primary_regime.value,
                "confidence": round(regime.confidence, 3),
            }
            records.append(record)

            print(
                f"  tick={state.tick:>5}  "
                f"entropy={record['entropy_energy']:.4f}  "
                f"compartments={record['n_compartments']:>3}  "
                f"proto_life={record['proto_life']:.3f}  "
                f"regime={record['regime']:<14}  "
                f"phi={record['phi_proxy']:.4f}"
            )

    elapsed = time.perf_counter() - t0
    ticks_per_sec = steps / elapsed

    print(f"\n✅ Done — {steps} ticks in {elapsed:.1f}s  ({ticks_per_sec:.0f} ticks/s)")
    print("\n── Final snapshot ──────────────────────────────────────")
    if records:
        last = records[-1]
        print(f"   Regime:          {last['regime']} (confidence {last['confidence']:.2f})")
        print(f"   Entropy energy:  {last['entropy_energy']:.4f}")
        print(f"   Compartments:    {last['n_compartments']}")
        print(f"   Proto-life:      {last['proto_life']:.3f}")
        print(f"   Φ-Proxy:         {last['phi_proxy']:.4f}")
        print(f"   Integrated:      {last['integrated']:.4f}")

    print("\n── Suggested next steps ────────────────────────────────")
    for metric in preset.suggested_metrics:
        print(f"   • {metric}")
    for pat in preset.expected_patterns:
        print(f"   👁 Look for: {pat}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a simulation preset from the Experiment Gallery."
    )
    parser.add_argument(
        "--preset", "-p", type=str, default=None,
        help="Preset ID (use --list to see all available presets)",
    )
    parser.add_argument(
        "--steps", "-s", type=int, default=300,
        help="Number of simulation ticks to run (default: 300)",
    )
    parser.add_argument(
        "--analyze-every", "-a", type=int, default=50,
        help="Print analysis every N ticks (default: 50)",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="List all available presets and exit",
    )
    args = parser.parse_args()

    if args.list or args.preset is None:
        _print_presets()
        if args.preset is None and not args.list:
            parser.print_help()
        sys.exit(0)

    run(args.preset, args.steps, args.analyze_every)


if __name__ == "__main__":
    main()
