"""
D3 — generate report figures into docs/figures/.

Numbers are hardcoded from the final Kaggle run of D3_TFLite_Fairness (the run
that reported per-subgroup PD rate) and from scripts/benchmark_tflite_latency.py.
They are NOT read from results/d3_tflite/*.json, because those files were
downloaded after an earlier run and are stale relative to the report. Kept
hardcoded so the figures always match docs/D3_report.md.

Usage:
    .venv/bin/python3 scripts/make_d3_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# (label, pd_rate, f1, auroc or None)   auroc None = not computable
SINGLE = [
    ("Female",  0.63, 0.642, 0.713),
    ("Male",    0.91, 0.417, 0.564),
    ("Left",    1.00, 0.283, None),
    ("Right",   0.80, 0.532, 0.661),
    ("<55",     0.67, 0.646, 0.757),
    ("55-70",   0.84, 0.507, 0.618),
    ("70+",     0.85, 0.456, 0.601),
]
POOLED = [
    ("Female",  0.62, 0.571, 0.624),
    ("Male",    0.87, 0.552, 0.711),
    ("Left",    0.62, 0.641, 0.707),
    ("Right",   0.79, 0.574, 0.684),
    ("<55",     0.70, 0.604, 0.689),
    ("55-70",   0.79, 0.553, 0.662),
    ("70+",     0.81, 0.595, 0.718),
]
GROUP_SPANS = [(0, 2, "Gender"), (2, 4, "Handedness"), (4, 7, "Age")]


def fairness_figure():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    for ax, data, title, n_sub in [
        (axes[0], SINGLE, "Single held-out split\n(54 subjects, 1,188 windows)", 54),
        (axes[1], POOLED, "Pooled 5-fold out-of-fold\n(355 subjects, 7,810 windows)", 355),
    ]:
        labels = [d[0] for d in data]
        x = np.arange(len(labels))
        aurocs = [d[3] if d[3] is not None else 0 for d in data]
        colors = ["lightgray" if d[3] is None else "steelblue" for d in data]

        ax.bar(x, aurocs, color=colors, edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="red", linestyle=":", linewidth=1, alpha=0.7)
        ax.text(len(labels) - 0.4, 0.51, "chance", color="red", fontsize=8, ha="right")

        for i, d in enumerate(data):
            if d[3] is None:
                ax.text(i, 0.03, "not\ncomputable", ha="center", va="bottom",
                        fontsize=7, style="italic")
            else:
                ax.text(i, d[3] + 0.012, f"{d[3]:.3f}", ha="center", fontsize=8)

        # separators between demographic groupings
        for start, end, name in GROUP_SPANS:
            if start > 0:
                ax.axvline(start - 0.5, color="gray", linewidth=0.6, alpha=0.5)
            ax.text((start + end - 1) / 2, 0.90, name, ha="center", fontsize=9,
                    fontweight="bold", color="dimgray")

        ax.set_xticks(x)
        # PD rate goes in the tick label so it cannot collide with anything
        ax.set_xticklabels([f"{d[0]}\nPD {d[1]:.2f}" for d in data], fontsize=8)
        ax.set_ylim(0, 0.95)
        ax.set_title(title, fontsize=10)

    axes[0].set_ylabel("AUROC")
    fig.suptitle("D3 fairness audit: apparent subgroup disparities do not survive pooling",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    p = OUT / "d3_fairness_single_vs_pooled.png"
    plt.savefig(p, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"wrote {p}")


def deployment_figure():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))

    # --- left: quantization cost -------------------------------------------
    ax = axes[0]
    metrics = ["macro-F1", "AUROC"]
    f32 = [0.555, 0.680]
    i8 = [0.519, 0.655]
    x = np.arange(len(metrics))
    w = 0.35
    ax.bar(x - w / 2, f32, w, label="Float32 (~78 KB)", color="steelblue",
           edgecolor="black", linewidth=0.5)
    ax.bar(x + w / 2, i8, w, label="INT8 TFLite (19.6 KB)", color="darkorange",
           edgecolor="black", linewidth=0.5)
    for i, (a, b) in enumerate(zip(f32, i8)):
        ax.text(i - w / 2, a + 0.012, f"{a:.3f}", ha="center", fontsize=8)
        ax.text(i + w / 2, b + 0.012, f"{b:.3f}", ha="center", fontsize=8)
        ax.text(i, max(a, b) + 0.06, f"{b - a:+.3f}", ha="center", fontsize=8,
                color="darkred", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("Score")
    ax.set_title("Cost of INT8 quantization\n(4x smaller model)", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")

    # --- right: latency in context (log scale) -----------------------------
    ax = axes[1]
    items = [
        ("Steady-state\ninference", 0.0662, "darkorange"),
        ("Cold start\n(first call)", 0.6435, "goldenrod"),
        ("Sensor window\nbeing scored", 10240.0, "steelblue"),
    ]
    y = np.arange(len(items))
    vals = [i[1] for i in items]
    ax.barh(y, vals, color=[i[2] for i in items], edgecolor="black", linewidth=0.5)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in items], fontsize=9)
    ax.invert_yaxis()
    for i, v in enumerate(vals):
        label = f"{v:,.4g} ms" if v < 1000 else f"{v:,.0f} ms (10.24 s)"
        ax.text(v * 1.4, i, label, va="center", fontsize=8)
    ax.set_xlim(0.02, 3e5)
    ax.set_xlabel("milliseconds (log scale)")
    ax.set_title("Inference latency vs. the window it processes\n"
                 "Apple M3 Pro (ARM64) proxy, NOT a Pi 5 measurement", fontsize=10)

    plt.tight_layout()
    p = OUT / "d3_deployment_cost.png"
    plt.savefig(p, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"wrote {p}")


if __name__ == "__main__":
    fairness_figure()
    deployment_figure()
