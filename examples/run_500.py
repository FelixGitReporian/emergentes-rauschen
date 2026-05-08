"""
examples/run_500.py – Beispiellauf mit 500 Ticks.

Führt 500 Simulationsschritte aus und speichert:
- Alle 50 Ticks: Panel-PNG (alle 9 Felder)
- Alle 10 Ticks: RGB-Composite (energy / information / coherence)
- Nach jedem Tick: Entropie-Log als CSV

Ausgabe: outputs/run_500/

Verwendung:
    python examples/run_500.py
    python examples/run_500.py --seed 123 --steps 200 --height 128 --width 128
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.visualization.render import save_field_grid, save_rgb_composite


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Emergentes Rauschen – 500-Tick-Beispiellauf")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--height", type=int, default=64)
    p.add_argument("--width", type=int, default=64)
    p.add_argument("--output-dir", type=str, default="outputs/run_500")
    p.add_argument("--panel-every", type=int, default=50, help="Panel-PNG alle N Ticks")
    p.add_argument("--rgb-every", type=int, default=10, help="RGB-Composite alle N Ticks")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = SimConfig(
        height=args.height,
        width=args.width,
        seed=args.seed,
    )

    print(f"Starte Simulation: {args.steps} Ticks, Grid {args.height}×{args.width}, Seed {args.seed}")
    print(f"Ausgabe: {out_dir.resolve()}")

    state = GridState.initialize(config)
    loop = TickLoop(config)

    entropy_log: list[dict] = []
    t_start = time.perf_counter()

    for tick_idx in range(args.steps):
        loop.step(state)

        # Entropie messen
        entropy = state_entropy_summary(state)
        entropy_log.append({"tick": state.tick, **entropy})

        # Panel-PNG
        if state.tick % args.panel_every == 0 or state.tick == args.steps:
            save_field_grid(state, out_dir / "panels" / f"panel_{state.tick:05d}.png")

        # RGB-Composite
        if state.tick % args.rgb_every == 0 or state.tick == args.steps:
            save_rgb_composite(state, out_dir / "rgb" / f"rgb_{state.tick:05d}.png")

        # Konsolenausgabe alle 100 Ticks
        if state.tick % 100 == 0:
            elapsed = time.perf_counter() - t_start
            mean_energy = float(state.energy.mean())
            mean_memory = float(state.memory.mean())
            print(
                f"  Tick {state.tick:4d} | "
                f"energy_mean={mean_energy:.3f} | "
                f"memory_mean={mean_memory:.3f} | "
                f"elapsed={elapsed:.1f}s"
            )

    # Entropie-Log als CSV speichern
    csv_path = out_dir / "entropy_log.csv"
    if entropy_log:
        fieldnames = list(entropy_log[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entropy_log)

    total = time.perf_counter() - t_start
    print(f"\nFertig. {args.steps} Ticks in {total:.2f}s ({args.steps/total:.1f} Ticks/s)")
    print(f"Panel-PNGs:    {out_dir/'panels'}")
    print(f"RGB-Composites:{out_dir/'rgb'}")
    print(f"Entropie-Log:  {csv_path}")


if __name__ == "__main__":
    main()
