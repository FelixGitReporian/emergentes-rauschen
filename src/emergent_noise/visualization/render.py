"""
visualization/render.py – Rendering von GridState-Feldern als PNG.

Jedes Feld wird als Heatmap gerendert. Ein kombiniertes RGB-Bild zeigt
energy (Rot), information (Grün) und coherence (Blau) gleichzeitig.

Abhängigkeiten: matplotlib (kein Anzeige-Backend erforderlich – nutzt 'Agg').
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Kein Display nötig
import matplotlib.pyplot as plt
import numpy as np

from emergent_noise.core.state import GridState


_FIELD_COLORMAPS: dict[str, str] = {
    "energy": "inferno",
    "matter": "YlOrBr",
    "information": "viridis",
    "coupling": "PuBu",
    "reactivity": "hot",
    "memory": "copper",
    "coherence": "cool",
    "flow_x": "bwr",
    "flow_y": "bwr",
}


def save_field_grid(state: GridState, output_path: Path | str, dpi: int = 100) -> None:
    """Speichere alle neun Felder als 3×3-Panel-PNG.

    Jedes Subplot zeigt ein Feld als Heatmap. Tick-Nummer und Feldname werden
    als Titel angezeigt. Wertebereiche werden auf [0, 1] fixiert, damit
    Vergleiche über Ticks hinweg korrekt sind.

    Parameters
    ----------
    state:
        Aktueller GridState.
    output_path:
        Zielpfad für die PNG-Datei. Übergeordnete Verzeichnisse werden
        automatisch erstellt.
    dpi:
        Auflösung in Dots per Inch.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fields = state.as_dict()
    n_fields = len(fields)
    n_cols = 3
    n_rows = (n_fields + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3.5, n_rows * 3.0))
    axes_flat = axes.flatten()

    for idx, (name, arr) in enumerate(fields.items()):
        ax = axes_flat[idx]
        cmap = _FIELD_COLORMAPS.get(name, "viridis")
        vmin, vmax = (-1.0, 1.0) if name in ("flow_x", "flow_y") else (0.0, 1.0)
        im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest")
        ax.set_title(f"{name}", fontsize=9)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    for idx in range(n_fields, len(axes_flat)):
        axes_flat[idx].axis("off")

    fig.suptitle(f"Tick {state.tick:05d}", fontsize=12, y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def save_rgb_composite(state: GridState, output_path: Path | str, dpi: int = 100) -> None:
    """Speichere ein RGB-Composite: Rot=energy, Grün=information, Blau=coherence.

    Dieses Bild gibt einen schnellen visuellen Überblick über die drei
    wichtigsten Felder in einem einzigen Bild. Gut geeignet für Zeitreihen
    und Animationen.

    Parameters
    ----------
    state:
        Aktueller GridState.
    output_path:
        Zielpfad für die PNG-Datei.
    dpi:
        Auflösung in Dots per Inch.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rgb = np.stack(
        [
            np.clip(state.energy, 0.0, 1.0),
            np.clip(state.information, 0.0, 1.0),
            np.clip(state.coherence, 0.0, 1.0),
        ],
        axis=-1,
    )

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(rgb, origin="upper", interpolation="nearest")
    ax.set_title(f"RGB-Composite (R=energy, G=info, B=coherence)  Tick {state.tick:05d}", fontsize=9)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
