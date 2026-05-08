"""
examples/benchmark_10k.py – 10k-Tick Stabilitäts-Sweep Benchmark.

Führt einen 10.000-Tick Lauf für mehrere Rausch-Amplituden durch,
misst Entropie, Persistenz, Regime und Proto-Leben-Score,
und speichert die Ergebnisse als CSV.

Verwendung:
    python examples/benchmark_10k.py
    python examples/benchmark_10k.py --grid 64 --output outputs/bench_64

Das Ergebnis ist vollständig reproduzierbar (Seed 42).
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import time
from pathlib import Path

import numpy as np

from emergent_noise.analysis.attractors import PersistenceTracker, compute_phase_indicator
from emergent_noise.analysis.compartments import detect_compartments
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.interpretation.regime_classifier import classify_regime


def _git_hash() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def run_benchmark(grid_size: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    noise_levels = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20]
    n_ticks = 10_000
    analyze_every = 500   # Metrik-Snapshots alle 500 Ticks → 20 Punkte pro Lauf
    git_hash = _git_hash()

    print(f"\n🔬 Benchmark: 10k-Tick Stability Sweep")
    print(f"   Grid: {grid_size}×{grid_size}  |  Ticks: {n_ticks}  |  Git: {git_hash}")
    print(f"   Noise levels: {noise_levels}")
    print(f"   Output: {output_dir}\n")

    all_records: list[dict] = []
    wall_times: dict[float, float] = {}

    for noise in noise_levels:
        cfg = SimConfig(
            height=grid_size, width=grid_size, seed=42,
            noise_amplitude=noise,
            diffusion_energy=0.15,
            reaction_energy_threshold=0.55,
            reaction_strength=0.12,
            coupling_gain=0.02,
            memory_decay=0.97,
        )
        state = GridState.initialize(cfg)
        loop = TickLoop(cfg)
        tracker = PersistenceTracker(window=20)

        t0 = time.perf_counter()

        for tick in range(n_ticks):
            loop.step(state)
            tracker.update(state.as_dict())

            if tick % analyze_every == 0 or tick == n_ticks - 1:
                entropy = state_entropy_summary(state)
                phase = compute_phase_indicator(state.tick, state.as_dict())
                comp = detect_compartments(state, min_area=4)
                regime = classify_regime(state.tick, state.as_dict())
                persistence = (
                    float(np.mean(list(tracker.persistence.values())))
                    if tracker.persistence else 0.0
                )

                all_records.append({
                    "noise_amplitude": noise,
                    "tick": state.tick,
                    "entropy_energy": round(entropy.get("energy", 0.0), 5),
                    "entropy_information": round(entropy.get("information", 0.0), 5),
                    "persistence_score": round(persistence, 5),
                    "n_compartments": comp.n_compartments,
                    "proto_life_score": round(comp.max_proto_life_score, 5),
                    "regime": regime.primary_regime.value,
                    "regime_confidence": round(regime.confidence, 4),
                    "phase_susceptibility": round(
                        float(getattr(phase, "susceptibility", 0.0)), 5
                    ),
                })

        elapsed = time.perf_counter() - t0
        wall_times[noise] = elapsed
        ticks_per_sec = n_ticks / elapsed

        print(
            f"  noise={noise:.2f}  →  {elapsed:6.1f}s  "
            f"({ticks_per_sec:,.0f} ticks/s)  "
            f"regime={all_records[-1]['regime']}  "
            f"compartments={all_records[-1]['n_compartments']}"
        )

    # CSV speichern
    csv_path = output_dir / "benchmark_10k_results.csv"
    fieldnames = list(all_records[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    # Timing-Summary speichern
    timing_path = output_dir / "benchmark_timing.csv"
    with open(timing_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["noise_amplitude", "wall_time_s", "ticks_per_sec",
                         "grid_size", "n_ticks", "git_hash"])
        for noise, elapsed in wall_times.items():
            writer.writerow([noise, round(elapsed, 3), round(n_ticks / elapsed, 1),
                             grid_size, n_ticks, git_hash])

    print(f"\n✅ Ergebnisse: {csv_path}  ({len(all_records)} Zeilen)")
    print(f"   Timing:     {timing_path}")

    # Kurz-Zusammenfassung
    print("\n── Zusammenfassung ─────────────────────────────────────────")
    print(f"{'Noise':>8}  {'Ø Entropie':>12}  {'Ø Persistenz':>13}  "
          f"{'Ø Komp.':>8}  {'Zeit (s)':>10}")
    for noise in noise_levels:
        rows = [r for r in all_records if r["noise_amplitude"] == noise]
        avg_e = np.mean([r["entropy_energy"] for r in rows])
        avg_p = np.mean([r["persistence_score"] for r in rows])
        avg_c = np.mean([r["n_compartments"] for r in rows])
        print(f"  {noise:>6.2f}  {avg_e:>12.4f}  {avg_p:>13.4f}  "
              f"{avg_c:>8.1f}  {wall_times[noise]:>10.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="10k-Tick Stability Sweep Benchmark"
    )
    parser.add_argument(
        "--grid", type=int, default=32,
        help="Grid-Größe (NxN, default: 32)"
    )
    parser.add_argument(
        "--output", type=str, default="outputs/benchmark_10k",
        help="Ausgabeverzeichnis (default: outputs/benchmark_10k)"
    )
    args = parser.parse_args()
    run_benchmark(grid_size=args.grid, output_dir=Path(args.output))


if __name__ == "__main__":
    main()
