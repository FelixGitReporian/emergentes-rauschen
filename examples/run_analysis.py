"""
examples/run_analysis.py – Simulations-Lauf mit vollständiger Attraktor-Analyse.

Führt einen konfigurierbaren Lauf durch und erzeugt:
- Entropie-CSV (wie run_500.py)
- Persistenz-Verlauf aller Felder (CSV)
- Cluster-Analyse alle N Ticks (CSV)
- Phasenübergangs-Indikator-Verlauf (CSV)
- Feldstatistik-Übersicht (CSV, Endstand)
- Abschluss-Visualisierung (Panel + RGB)

Verwendung:
    python examples/run_analysis.py
    python examples/run_analysis.py --ticks 1000 --grid 128 --seed 7 --output-dir outputs/analysis_01
    python examples/run_analysis.py --analysis-interval 10
"""

from __future__ import annotations

import argparse
import csv
import time
from dataclasses import asdict
from pathlib import Path

from emergent_noise.analysis.attractors import (
    PersistenceTracker,
    compute_phase_indicator,
    field_summary,
    find_clusters,
)
from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.visualization.render import save_field_grid, save_rgb_composite


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Emergentes-Rauschen Analyse-Lauf")
    p.add_argument("--ticks", type=int, default=500)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-dir", type=str, default="outputs/analysis")
    p.add_argument("--analysis-interval", type=int, default=25,
                   help="Cluster + Phase alle N Ticks berechnen")
    p.add_argument("--snapshot-interval", type=int, default=100,
                   help="PNG-Snapshots alle N Ticks speichern")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir)
    (out / "panels").mkdir(parents=True, exist_ok=True)
    (out / "rgb").mkdir(parents=True, exist_ok=True)

    config = SimConfig(height=args.grid, width=args.grid, seed=args.seed)
    state = GridState.initialize(config)
    loop = TickLoop(config)
    tracker = PersistenceTracker(window=20)

    print(f"Starte Analyse-Lauf: {args.ticks} Ticks, Grid {args.grid}×{args.grid}, Seed {args.seed}")
    print(f"Analyse-Intervall: alle {args.analysis_interval} Ticks")
    print(f"Ausgabe: {out.resolve()}")

    # CSV-Writer vorbereiten
    field_names = list(state.as_dict().keys())

    entropy_rows: list[dict] = []
    persistence_rows: list[dict] = []
    cluster_rows: list[dict] = []
    phase_rows: list[dict] = []

    t0 = time.perf_counter()

    for tick_i in range(1, args.ticks + 1):
        loop.step(state)
        fields = state.as_dict()

        # -- Entropie (jeder Tick) --
        ent = state_entropy_summary(state)
        entropy_rows.append({"tick": state.tick, **ent})

        # -- Persistenz (jeder Tick) --
        tracker.update(fields)
        if tracker.persistence:
            persistence_rows.append({"tick": state.tick, **tracker.persistence})

        # -- Cluster + Phase (alle N Ticks) --
        if tick_i % args.analysis_interval == 0:
            for fname in ["energy", "information", "coherence", "coupling"]:
                cr = find_clusters(fname, fields[fname], threshold=0.6)
                cluster_rows.append({
                    "tick": state.tick,
                    "field": cr.field_name,
                    "n_clusters": cr.n_clusters,
                    "largest": cr.largest_cluster_size,
                    "mean_size": round(cr.mean_cluster_size, 2),
                    "fraction": round(cr.cluster_fraction, 4),
                })

            pi = compute_phase_indicator(state.tick, fields)
            phase_rows.append({
                "tick": pi.tick,
                "energy_var": round(pi.energy_variance, 6),
                "info_var": round(pi.information_variance, 6),
                "susceptibility": round(pi.susceptibility, 6),
                "near_transition": int(pi.near_transition),
            })

        # -- PNG-Snapshots --
        if tick_i % args.snapshot_interval == 0:
            save_field_grid(state, out / "panels" / f"tick_{state.tick:05d}.png")
            save_rgb_composite(state, out / "rgb" / f"tick_{state.tick:05d}.png")

        # -- Konsolen-Progress --
        if tick_i % 100 == 0:
            elapsed = time.perf_counter() - t0
            most_stable = tracker.most_stable() or "–"
            least_stable = tracker.least_stable() or "–"
            print(
                f"  Tick {state.tick:5d} | "
                f"energy={ent['energy']:.3f} | "
                f"memory={ent['memory']:.3f} | "
                f"coupling={ent['coupling']:.3f} | "
                f"stabil={most_stable} | "
                f"instabil={least_stable} | "
                f"elapsed={elapsed:.1f}s"
            )

    # Endzustand speichern
    save_field_grid(state, out / "panels" / f"tick_{state.tick:05d}_final.png")
    save_rgb_composite(state, out / "rgb" / f"tick_{state.tick:05d}_final.png")

    # Feldstatistik-Übersicht (Endzustand)
    summary_path = out / "field_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "mean", "std", "min", "max", "active_fraction"])
        writer.writeheader()
        for fname, arr in state.as_dict().items():
            fs = field_summary(fname, arr)
            writer.writerow({
                "name": fs.name,
                "mean": round(fs.mean, 5),
                "std": round(fs.std, 5),
                "min": round(fs.min, 5),
                "max": round(fs.max, 5),
                "active_fraction": round(fs.active_fraction, 4),
            })

    # CSVs schreiben
    _write_csv(out / "entropy_log.csv", entropy_rows)
    _write_csv(out / "persistence_log.csv", persistence_rows)
    _write_csv(out / "cluster_log.csv", cluster_rows)
    _write_csv(out / "phase_log.csv", phase_rows)

    elapsed_total = time.perf_counter() - t0
    tps = args.ticks / elapsed_total
    print(f"\nFertig. {args.ticks} Ticks in {elapsed_total:.2f}s ({tps:.1f} Ticks/s)")
    print(f"Stabilitiätsergebnis:")
    for name, val in sorted(tracker.persistence.items(), key=lambda x: -x[1]):
        bar = "█" * int(val * 20)
        print(f"  {name:12s} {val:.4f}  {bar}")
    print(f"\nAusgaben:")
    print(f"  Entropie-Log:    {out / 'entropy_log.csv'}")
    print(f"  Persistenz-Log:  {out / 'persistence_log.csv'}")
    print(f"  Cluster-Log:     {out / 'cluster_log.csv'}")
    print(f"  Phase-Log:       {out / 'phase_log.csv'}")
    print(f"  Feld-Summary:    {out / 'field_summary.csv'}")
    print(f"  Panel-PNGs:      {out / 'panels'}")
    print(f"  RGB-Composites:  {out / 'rgb'}")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
