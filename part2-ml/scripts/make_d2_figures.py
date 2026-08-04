"""
D2 — regenerate docs/figures/moment_vs_baselines.png from the FULL FINE-TUNE run.

The previous version of this figure was produced during the V3 linear-probe run
and was never replaced when full fine-tuning finished, leaving the figure
contradicting the tables in D2_report.md.

Panels differ from the original. The original left panel was MOMENT's averaged
confusion matrix, but the underlying `moment_cms.npy` was written to
/kaggle/working and never downloaded, so it cannot be reproduced locally. The
per-fold panel here uses data that is recorded in the report and the Kaggle run
log, and shows fold-to-fold consistency, which is arguably more useful.

Numbers are hardcoded from the D2 report tables so the figure and the text
cannot drift apart.

Usage:
    .venv/bin/python3 scripts/make_d2_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# (label, macro_f1, f1_std, auroc, auroc_std, is_moment_full_ft)
MODELS = [
    ("SVM",                  0.564, 0.023, 0.693, 0.021, False),
    ("Random\nForest",       0.498, 0.011, 0.726, 0.020, False),
    ("CNN1D",                0.565, 0.022, 0.702, 0.022, False),
    ("MOMENT\nlinear probe", 0.502, 0.012, 0.622, 0.012, False),
    ("MOMENT\nfull FT",      0.626, 0.009, 0.731, 0.019, True),
]

# full fine-tune, per fold (Kaggle run V9-V11)
FOLD_F1 = [0.622, 0.631, 0.612, 0.634, 0.633]
FOLD_AUROC = [0.732, 0.744, 0.702, 0.757, 0.721]


def main():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    # --- left: all five models, both metrics ------------------------------
    ax = axes[0]
    x = np.arange(len(MODELS))
    w = 0.38
    f1 = [m[1] for m in MODELS]
    f1e = [m[2] for m in MODELS]
    au = [m[3] for m in MODELS]
    aue = [m[4] for m in MODELS]
    f1_colors = ["darkorange" if m[5] else "steelblue" for m in MODELS]
    au_colors = ["sandybrown" if m[5] else "lightsteelblue" for m in MODELS]

    ax.bar(x - w / 2, f1, w, yerr=f1e, capsize=3, label="macro-F1",
           color=f1_colors, edgecolor="black", linewidth=0.5)
    ax.bar(x + w / 2, au, w, yerr=aue, capsize=3, label="AUROC",
           color=au_colors, edgecolor="black", linewidth=0.5)

    for i, m in enumerate(MODELS):
        ax.text(i - w / 2, m[1] + m[2] + 0.015, f"{m[1]:.3f}", ha="center", fontsize=7.5)
        ax.text(i + w / 2, m[3] + m[4] + 0.015, f"{m[3]:.3f}", ha="center", fontsize=7.5)

    # best-baseline reference lines (excluding both MOMENT variants)
    best_f1 = max(m[1] for m in MODELS if not m[5] and "MOMENT" not in m[0])
    ax.axhline(best_f1, color="gray", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(len(MODELS) - 0.45, best_f1 + 0.008, "best classical F1",
            fontsize=7, color="gray", ha="right")

    ax.set_xticks(x)
    ax.set_xticklabels([m[0] for m in MODELS], fontsize=8.5)
    ax.set_ylim(0, 0.87)
    ax.set_ylabel("Score")
    ax.set_title("PADS PD vs HC, 5-fold subject-grouped CV\n"
                 "355 subjects, 7,810 windows", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")

    # --- right: per-fold consistency of the full fine-tune ----------------
    ax = axes[1]
    folds = np.arange(1, 6)
    ax.plot(folds, FOLD_F1, "o-", color="darkorange", label="macro-F1", linewidth=2)
    ax.plot(folds, FOLD_AUROC, "s-", color="steelblue", label="AUROC", linewidth=2)
    ax.axhline(np.mean(FOLD_F1), color="darkorange", linestyle=":", alpha=0.6)
    ax.axhline(np.mean(FOLD_AUROC), color="steelblue", linestyle=":", alpha=0.6)

    for f, v in zip(folds, FOLD_F1):
        ax.text(f, v - 0.022, f"{v:.3f}", ha="center", fontsize=7.5, color="darkorange")
    for f, v in zip(folds, FOLD_AUROC):
        ax.text(f, v + 0.014, f"{v:.3f}", ha="center", fontsize=7.5, color="steelblue")

    ax.set_xticks(folds)
    ax.set_xlabel("Fold")
    ax.set_ylim(0.55, 0.80)
    ax.set_ylabel("Score")
    ax.set_title("MOMENT full fine-tune, per fold\n"
                 f"F1 {np.mean(FOLD_F1):.3f} ± {np.std(FOLD_F1):.3f}   "
                 f"AUROC {np.mean(FOLD_AUROC):.3f} ± {np.std(FOLD_AUROC):.3f}",
                 fontsize=10)
    ax.legend(fontsize=8, loc="center right")
    ax.grid(alpha=0.2)

    plt.tight_layout()
    p = OUT / "moment_vs_baselines.png"
    plt.savefig(p, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"wrote {p}")


if __name__ == "__main__":
    main()
