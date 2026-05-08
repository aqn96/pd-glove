"""Generate the flex bench characterization figure for paper Fig. 5 (right panel).

Reads `data/flex_bench_thumb_2026-05-07.csv` and produces a box-plus-strip plot
of ADC values at 0/30/60 deg. The 90 deg condition is excluded from the figure
because it sits in the SEN-10264 hysteresis regime (see
`docs/flex-bench-characterization.md`); it is retained in the CSV for
reproducibility.

Output: `images/flex_bench_scatter.png`

Run from the repo root:

    .venv/bin/python3 scripts/flex_bench/plot_bench.py

Requires matplotlib + numpy (not in `requirements.txt`; install locally for
figure generation only — the Pi runtime does not need them).
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "data" / "flex_bench_thumb_2026-05-07.csv"
OUT_PATH = REPO_ROOT / "images" / "flex_bench_scatter.png"
ANGLES = [0, 30, 60]


def load_data(path):
    by_angle = defaultdict(list)
    with path.open() as f:
        for row in csv.DictReader(f):
            angle = int(row["angle_deg"])
            by_angle[angle].append(float(row["adc_value"]))
    return by_angle


def main():
    data = load_data(CSV_PATH)
    series = [data[a] for a in ANGLES]

    fig, ax = plt.subplots(figsize=(5.0, 4.0))

    bp = ax.boxplot(
        series,
        positions=ANGLES,
        widths=8,
        patch_artist=True,
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": 6,
        },
        medianprops={"color": "black", "linewidth": 1.2},
        boxprops={"facecolor": "lightgray", "edgecolor": "black"},
        whiskerprops={"color": "black"},
        capprops={"color": "black"},
        flierprops={
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "black",
        },
    )

    rng = np.random.default_rng(42)
    for angle, values in zip(ANGLES, series):
        jitter = rng.uniform(-2.5, 2.5, size=len(values))
        ax.scatter(
            np.full(len(values), angle) + jitter,
            values,
            color="steelblue",
            alpha=0.75,
            s=32,
            zorder=3,
            edgecolor="black",
            linewidth=0.4,
        )

    ax.set_xlabel("Bench-jig angle (°)")
    ax.set_ylabel("ADC value (12-bit)")
    ax.set_xticks(ANGLES)
    ax.set_xticklabels([f"{a}°" for a in ANGLES])
    ax.set_xlim(-15, 75)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    legend_elements = [
        plt.Line2D(
            [0], [0],
            marker="D", color="w",
            markerfacecolor="black", markeredgecolor="black",
            markersize=7, label="Mean",
        ),
        plt.Line2D(
            [0], [0],
            color="black", linewidth=1.2, label="Median",
        ),
        plt.Line2D(
            [0], [0],
            marker="o", color="w",
            markerfacecolor="steelblue", markeredgecolor="black",
            markersize=7, label="Trial (N=10/angle)",
        ),
    ]
    ax.legend(handles=legend_elements, loc="lower left", framealpha=0.9, fontsize=9)

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
