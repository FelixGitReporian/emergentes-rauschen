"""
experiments/runner.py – Reproduzierbarer Experiment-Runner (Epic 7).

Führt Config-Sweeps aus, protokolliert Ergebnisse und speichert sie
als CSV + JSON für spätere Analyse.

Features:
    - Vollständige Reproduzierbarkeit: git-Hash + seed + config werden gespeichert.
    - Mehrdimensionale Parameter-Sweeps (Cartesian Product).
    - Pro Lauf: Entropie, Persistenz, Regime, Kompartimente, Bewusstseins-Marker.
    - Fortschrittsanzeige (tqdm optional, sonst print).
    - Ausgabe in outputs/<experiment_name>/<timestamp>/

Verwendung:
    python -m emergent_noise.experiments.runner --experiment stability_sweep
    python -m emergent_noise.experiments.runner --list
"""

from __future__ import annotations

import csv
import itertools
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np

from emergent_noise.analysis.entropy import state_entropy_summary
from emergent_noise.analysis.attractors import PersistenceTracker, compute_phase_indicator
from emergent_noise.analysis.compartments import detect_compartments
from emergent_noise.analysis.novelty import genome_diversity
from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop
from emergent_noise.experiments.configs import ALL_EXPERIMENTS, ExperimentConfig
from emergent_noise.interpretation.consciousness import ConsciousnessAnalyzer
from emergent_noise.interpretation.regime_classifier import classify_regime


def _get_git_hash() -> str:
    """Gibt den aktuellen Git-Commit-Hash zurück (oder 'unknown')."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _param_combinations(sweeps: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Erzeuge kartesisches Produkt aller Parameter-Sweep-Werte."""
    if not sweeps:
        return [{}]
    keys = list(sweeps.keys())
    values = list(sweeps.values())
    combos = []
    for combo in itertools.product(*values):
        combos.append(dict(zip(keys, combo)))
    return combos


def _apply_params(base: SimConfig, params: Dict[str, Any]) -> SimConfig:
    """Erzeuge neue SimConfig mit überschriebenen Parametern."""
    d = base.model_dump()
    d.update(params)
    return SimConfig(**d)


def _run_single(
    config: SimConfig,
    n_ticks: int,
    run_id: str,
    params: Dict[str, Any],
    analyze_every: int = 20,
) -> List[dict]:
    """Führe einen einzelnen Simulationslauf aus und sammle Metriken.

    Returns
    -------
    Liste von Metrik-Dicts (ein Dict pro Analyse-Tick).
    """
    state = GridState.initialize(config)
    loop  = TickLoop(config)
    tracker = PersistenceTracker(window=10)
    canalyzer = ConsciousnessAnalyzer()
    records = []

    for tick in range(n_ticks):
        loop.step(state)
        tracker.update(state.as_dict())

        if tick % analyze_every == 0 or tick == n_ticks - 1:
            entropy = state_entropy_summary(state)
            phase   = compute_phase_indicator(tick, state.as_dict())
            comp    = detect_compartments(state, min_area=4)
            gdiv    = genome_diversity(state)
            regime  = classify_regime(state.tick, state.as_dict())
            cmark   = canalyzer.analyze(state)

            record = {
                "run_id": run_id,
                "tick": state.tick,
                **params,
                "entropy_energy": round(entropy.get("energy", 0.0), 5),
                "persistence_score": round(float(np.mean(list(tracker.persistence.values()))) if tracker.persistence else 0.0, 5),
                "n_compartments": comp.n_compartments,
                "proto_life_score": comp.max_proto_life_score,
                "phi_proxy": cmark.phi_proxy,
                "active_inference": cmark.active_inference_score,
                "proto_life_cmark": cmark.proto_life_score,
                "integrated_score": cmark.integrated_score,
                "regime_primary": regime.primary_regime.value,
                "regime_confidence": round(regime.confidence, 4),
                "genome_diversity_entropy": round(gdiv.get("joint_entropy", 0.0), 5),
                "phase_susceptibility": round(float(getattr(phase, "susceptibility", 0.0)), 5),
            }
            records.append(record)

    return records


def run_experiment(
    exp: ExperimentConfig,
    output_dir: Optional[Path] = None,
    verbose: bool = True,
) -> Path:
    """Führe vollständiges Experiment mit allen Sweeps + Wiederholungen aus.

    Parameters
    ----------
    exp:
        ExperimentConfig.
    output_dir:
        Ausgabeverzeichnis (default: outputs/<exp.name>/<timestamp>).
    verbose:
        Fortschritt ausgeben.

    Returns
    -------
    Path zum Ausgabeverzeichnis.
    """
    if output_dir is None:
        ts = time.strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs") / exp.name / ts
    output_dir.mkdir(parents=True, exist_ok=True)

    git_hash = _get_git_hash()
    combos   = _param_combinations(exp.param_sweeps)
    n_total  = len(combos) * exp.repeat
    all_records: List[dict] = []

    # Experiment-Metadaten speichern
    meta = {
        "experiment_name": exp.name,
        "description": exp.description,
        "scientific_question": exp.scientific_question,
        "git_hash": git_hash,
        "n_ticks": exp.n_ticks,
        "repeat": exp.repeat,
        "n_param_combos": len(combos),
        "n_total_runs": n_total,
        "tags": exp.tags,
        "base_config": exp.base_config.model_dump(),
        "param_sweeps": exp.param_sweeps,
    }
    with open(output_dir / "experiment_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)

    run_num = 0
    for combo in combos:
        for repeat_idx in range(exp.repeat):
            run_num += 1
            seed = exp.base_config.seed + repeat_idx * 1000
            params_with_seed = {**combo, "seed": seed}
            config = _apply_params(exp.base_config, params_with_seed)
            run_id = f"{exp.name}_{run_num:04d}"

            if verbose:
                print(
                    f"  [{run_num:3d}/{n_total}] {run_id}  "
                    f"params={combo}  seed={seed}"
                )

            try:
                records = _run_single(
                    config, exp.n_ticks, run_id, params_with_seed
                )
                all_records.extend(records)
            except Exception as exc:
                if verbose:
                    print(f"    ERROR: {exc}")

    # CSV speichern
    if all_records:
        csv_path = output_dir / "results.csv"
        fieldnames = list(all_records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)
        if verbose:
            print(f"  Ergebnisse gespeichert: {csv_path} ({len(all_records)} Zeilen)")

    return output_dir


def main() -> None:
    """CLI-Entry-Point für den Experiment-Runner."""
    import argparse
    parser = argparse.ArgumentParser(description="Emergentes Rauschen – Experiment-Runner")
    parser.add_argument("--experiment", "-e", help="Name des Experiments")
    parser.add_argument("--list", "-l", action="store_true", help="Alle Experimente auflisten")
    parser.add_argument("--output", "-o", help="Ausgabeverzeichnis", default=None)
    args = parser.parse_args()

    if args.list:
        print("\nVerfügbare Experimente:")
        for name, exp in ALL_EXPERIMENTS.items():
            print(f"  {name:35s} – {exp.description[:60]}")
        return

    if not args.experiment:
        parser.print_help()
        return

    if args.experiment not in ALL_EXPERIMENTS:
        print(f"Experiment '{args.experiment}' nicht gefunden. Verwende --list für alle.")
        sys.exit(1)

    exp = ALL_EXPERIMENTS[args.experiment]
    output = Path(args.output) if args.output else None

    print(f"\n🔬 Experiment: {exp.name}")
    print(f"   Frage: {exp.scientific_question}")
    print(f"   {len(_param_combinations(exp.param_sweeps)) * exp.repeat} Läufe × {exp.n_ticks} Ticks\n")

    out_dir = run_experiment(exp, output_dir=output, verbose=True)
    print(f"\n✅ Fertig. Ausgabe: {out_dir}")


if __name__ == "__main__":
    main()
