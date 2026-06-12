# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Deliverable 1 — Baseline Classifiers (SVM · Random Forest · 1D-CNN)
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Reads the cleaned parquet/npz produced by **`Dataset_Pipeline.ipynb`** and benchmarks
# three baselines on **two tasks**:
#
# 1. **Tremor / bradykinesia** — ALAMEDA 92 features → 4 binary tremor labels.
# 2. **Freezing of gait (FOG)** — Daphnet windowed features (SVM/RF) and raw windows (1D-CNN).
#
# **Evaluation = subject-grouped K-fold cross-validation** (`GroupKFold`): every subject
# is in the test fold exactly once, no subject spans train+test, and we report
# **mean ± std macro-F1 / AUROC** across folds. This is deliberately *not* a single
# 70/15/15 split: ALAMEDA has only 11 subjects with near-constant per-subject labels, so
# one 2-subject test fold is too fragile (a single split leaves some labels one-class).
# CV gives stable, leakage-safe numbers and is the standard for small clinical cohorts.
#
# Metrics: **macro-F1, AUROC, out-of-fold confusion matrix, RF feature importance**.
# Imbalance handled with `class_weight="balanced"` (SVM/RF) and class-weighted loss (CNN).
#
# > **Why these three?** RF/SVM are the strongest classical baselines on small clinical
# > cohorts (Xing 2022, Rodriguez 2024); the 1D-CNN is the canonical deep baseline
# > (Atri 2022). The D2 Transformer must beat the best of these — see `next-steps.md` §4.2.

# %%
from pathlib import Path
import json
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix

RS = 42
np.random.seed(RS)

# Search for cleaned parquet files — check /kaggle/working first, then any
# notebook-output dataset attached via Add Input (mounted under /kaggle/input/).
def _find_clean_dir():
    # 1. Same-session working dir (pipeline ran in this session)
    p = Path("/kaggle/working/cleaned")
    if p.exists() and any(p.glob("*.parquet")):
        return p
    # 2. Notebook output attached as input (Add Input → Notebook Outputs)
    # Path is /kaggle/input/notebooks/<user>/<notebook-slug>/cleaned/
    for candidate in sorted(Path("/kaggle/input").glob("**/cleaned")):
        if candidate.is_dir() and any(candidate.glob("*.parquet")):
            return candidate
    # 3. Local repo path
    if "__file__" in globals():
        p = Path(__file__).resolve().parents[1] / "results" / "cleaned"
        if p.exists():
            return p
    return Path("/kaggle/working/cleaned")  # fallback — will error with a clear message

CLEAN_DIR = _find_clean_dir()
RESULTS_DIR = Path("/kaggle/working/metrics") if Path("/kaggle/working").exists() else CLEAN_DIR.parent / "metrics"
FIG_DIR = Path("/kaggle/working/figures") if Path("/kaggle/working").exists() else CLEAN_DIR.parent / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)
print("Reading cleaned data from:", CLEAN_DIR)

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print("torch", torch.__version__, "| device:", DEVICE)
except Exception:
    HAS_TORCH = False
    print("torch not available — 1D-CNN skipped (SVM/RF still run). On Kaggle it is preinstalled.")

ALL_METRICS = []


# %% [markdown]
# ## Helpers — model factories, scoring, CV evaluation

# %%
def model_factories():
    """Fresh, unfitted estimators (built per fold). No SVC(probability=True): we read
    SVM scores from decision_function, which is faster and avoids the deprecation."""
    return {
        "SVM": lambda: make_pipeline(
            StandardScaler(),
            SVC(kernel="rbf", class_weight="balanced", random_state=RS)),
        "RandomForest": lambda: RandomForestClassifier(
            n_estimators=400, class_weight="balanced", n_jobs=-1, random_state=RS),
    }


def get_scores(model, X):
    if hasattr(model, "predict_proba"):
        try:
            return model.predict_proba(X)[:, 1]
        except Exception:
            pass
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return model.predict(X)


def plot_confusion(cm, title, fname):
    fig, ax = plt.subplots(figsize=(3.3, 3))
    im = ax.imshow(cm, cmap="Blues")
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, str(int(v)), ha="center", va="center",
                color="white" if v > cm.max() / 2 else "black")
    ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.set_title(title)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    plt.colorbar(im, fraction=0.046); plt.tight_layout()
    plt.savefig(FIG_DIR / fname, dpi=120); plt.close()


def groupkfold_eval(X, y, groups, task, label, n_splits=5, want_importance=False,
                    feature_names=None):
    """Subject-grouped K-fold CV. Records mean±std macro-F1/AUROC per model and saves an
    out-of-fold confusion matrix. Returns mean RF importances if requested."""
    y = np.asarray(y); groups = np.asarray(groups)
    n_splits = max(2, min(n_splits, len(np.unique(groups))))
    gkf = GroupKFold(n_splits=n_splits)
    rf_importance = None

    for mname, factory in model_factories().items():
        f1s, aucs = [], []
        oof_true, oof_pred = [], []
        imps = []
        for tr, te in gkf.split(X, y, groups):
            if len(np.unique(y[tr])) < 2:
                continue  # degenerate training fold (single class) — skip
            model = factory().fit(X[tr], y[tr])
            pred = model.predict(X[te])
            f1s.append(f1_score(y[te], pred, average="macro"))
            if len(np.unique(y[te])) > 1:
                aucs.append(roc_auc_score(y[te], get_scores(model, X[te])))
            oof_true.append(y[te]); oof_pred.append(pred)
            if want_importance and mname == "RandomForest":
                imps.append(model.feature_importances_)

        if not f1s:
            print(f"  {mname:>12s} | {label:<18s} skipped (all folds degenerate)")
            continue
        row = {"task": task, "label": label, "model": mname,
               "macro_f1_mean": round(float(np.mean(f1s)), 4),
               "macro_f1_std": round(float(np.std(f1s)), 4),
               "auroc_mean": round(float(np.mean(aucs)), 4) if aucs else float("nan"),
               "auroc_std": round(float(np.std(aucs)), 4) if aucs else float("nan"),
               "n_folds": len(f1s), "pos_rate": round(float(np.mean(y)), 4)}
        ALL_METRICS.append(row)
        print(f"  {mname:>12s} | {label:<18s} "
              f"macro-F1={row['macro_f1_mean']:.3f}±{row['macro_f1_std']:.3f}  "
              f"AUROC={row['auroc_mean']:.3f}")
        cm = confusion_matrix(np.concatenate(oof_true), np.concatenate(oof_pred))
        plot_confusion(cm, f"{mname} · {label} (OOF)", f"cm_{task}_{label}_{mname}.png")
        if imps:
            rf_importance = np.mean(imps, axis=0)

    if rf_importance is not None and feature_names is not None:
        imp = pd.Series(rf_importance, index=feature_names).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(6, 6))
        imp.head(20)[::-1].plot.barh(ax=ax, color="seagreen")
        ax.set_title(f"RF feature importance · {label}"); ax.set_xlabel("mean importance")
        plt.tight_layout(); plt.savefig(FIG_DIR / f"fi_{task}_{label}.png", dpi=120); plt.close()
        return imp
    return None


# %% [markdown]
# ## 1D-CNN (PyTorch)
# Input `(N, channels, length)`. ALAMEDA → single-channel length-92 feature "sequence"
# (the only option for pre-extracted features — a documented limitation). Daphnet → raw
# `(9, 256)` windows, the natural 1D-CNN input. Evaluated on the held-out **test split**
# from the pipeline (subject-disjoint) to keep CNN cost reasonable.

# %%
if HAS_TORCH:
    class CNN1D(nn.Module):
        def __init__(self, in_ch, n_classes=2):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(in_ch, 32, 5, padding=2), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
                nn.Conv1d(32, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.AdaptiveAvgPool1d(1),
            )
            self.head = nn.Linear(64, n_classes)

        def forward(self, x):
            return self.head(self.net(x).squeeze(-1))

    def train_eval_cnn(Xtr, ytr, Xte, yte, in_ch, task, label, epochs=40, bs=64):
        ytr = np.asarray(ytr); yte = np.asarray(yte)
        counts = np.bincount(ytr, minlength=2)
        w = torch.tensor(counts.sum() / (2 * np.maximum(counts, 1)), dtype=torch.float32).to(DEVICE)
        model = CNN1D(in_ch).to(DEVICE)
        opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
        lossf = nn.CrossEntropyLoss(weight=w)
        dl = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(torch.tensor(Xtr, dtype=torch.float32),
                                           torch.tensor(ytr, dtype=torch.long)),
            batch_size=bs, shuffle=True)
        model.train()
        for _ in range(epochs):
            for xb, yb in dl:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                opt.zero_grad(); lossf(model(xb), yb).backward(); opt.step()
        model.eval()
        with torch.no_grad():
            logits = model(torch.tensor(Xte, dtype=torch.float32).to(DEVICE))
            score = torch.softmax(logits, 1)[:, 1].cpu().numpy()
            pred = logits.argmax(1).cpu().numpy()
        f1 = f1_score(yte, pred, average="macro")
        auc = roc_auc_score(yte, score) if len(np.unique(yte)) > 1 else float("nan")
        ALL_METRICS.append({"task": task, "label": label, "model": "1D-CNN",
                            "macro_f1_mean": round(f1, 4), "macro_f1_std": 0.0,
                            "auroc_mean": round(auc, 4), "auroc_std": 0.0,
                            "n_folds": 1, "pos_rate": round(float(np.mean(yte)), 4)})
        print(f"  {'1D-CNN':>12s} | {label:<18s} macro-F1={f1:.3f}  AUROC={auc:.3f} (held-out test)")
        plot_confusion(confusion_matrix(yte, pred), f"1D-CNN · {label}", f"cm_{task}_{label}_cnn.png")


# %% [markdown]
# ---
# ## Task 1 — Tremor / bradykinesia (ALAMEDA), subject-grouped CV

# %%
ALAMEDA_LABELS = ["Rest_tremor", "Postural_tremor", "Kinetic_tremor", "Constancy_of_rest"]
alameda = pd.read_parquet(CLEAN_DIR / "alameda_all.parquet")
non_feat = {"start_timestamp", "end_timestamp", "subject_id", "any_tremor", *ALAMEDA_LABELS}
A_FEATS = [c for c in alameda.columns if c not in non_feat]
Xa = alameda[A_FEATS].to_numpy(); ga = alameda["subject_id"].to_numpy()
print(f"ALAMEDA: {len(alameda)} windows · {alameda['subject_id'].nunique()} subjects · {len(A_FEATS)} features")

for lab in ALAMEDA_LABELS:
    if alameda[lab].nunique() < 2:
        print(f"[ALAMEDA] {lab}: single class overall — skip"); continue
    print(f"[ALAMEDA] {lab}  (pos rate {alameda[lab].mean():.2f})")
    groupkfold_eval(Xa, alameda[lab].to_numpy(), ga, "tremor", lab,
                    want_importance=(lab == "Rest_tremor"), feature_names=A_FEATS)

if HAS_TORCH:
    # CNN on the pipeline's subject-disjoint test split for the primary label.
    a_tr = pd.read_parquet(CLEAN_DIR / "alameda_train.parquet")
    a_te = pd.read_parquet(CLEAN_DIR / "alameda_test.parquet")
    sc = StandardScaler().fit(a_tr[A_FEATS])
    Xtr_c = sc.transform(a_tr[A_FEATS])[:, None, :].astype(np.float32)
    Xte_c = sc.transform(a_te[A_FEATS])[:, None, :].astype(np.float32)
    lab = "Constancy_of_rest" if a_te["Constancy_of_rest"].nunique() > 1 else "any_tremor"
    if a_te[lab].nunique() > 1:
        print(f"[ALAMEDA] {lab} (1D-CNN)")
        train_eval_cnn(Xtr_c, a_tr[lab], Xte_c, a_te[lab], 1, "tremor", lab)


# %% [markdown]
# ---
# ## Task 2 — Freezing of gait (Daphnet)
# SVM/RF via subject-grouped CV on engineered features; 1D-CNN on raw `(9,256)` windows.

# %%
daphnet = pd.read_parquet(CLEAN_DIR / "daphnet_all.parquet")
D_FEATS = [c for c in daphnet.columns if c not in {"fog", "subject", "session"}]
Xd = daphnet[D_FEATS].to_numpy(); gd = daphnet["subject"].to_numpy()
print(f"Daphnet: {len(daphnet)} windows · {daphnet['subject'].nunique()} subjects · "
      f"{len(D_FEATS)} features · FOG rate {daphnet['fog'].mean():.3f}")
print("[Daphnet] FOG")
groupkfold_eval(Xd, daphnet["fog"].to_numpy(), gd, "fog", "FOG",
                want_importance=True, feature_names=D_FEATS)

if HAS_TORCH and (CLEAN_DIR / "daphnet_raw_windows.npz").exists():
    npz = np.load(CLEAN_DIR / "daphnet_raw_windows.npz", allow_pickle=True)
    X, y, split = npz["X"], npz["y"], npz["split"]
    Xtr = X[split == "train"].transpose(0, 2, 1); Xte = X[split == "test"].transpose(0, 2, 1)
    mu = Xtr.mean((0, 2), keepdims=True); sd = Xtr.std((0, 2), keepdims=True) + 1e-6
    Xtr = ((Xtr - mu) / sd).astype(np.float32); Xte = ((Xte - mu) / sd).astype(np.float32)
    print("[Daphnet] FOG (1D-CNN on raw windows)", Xtr.shape)
    train_eval_cnn(Xtr, y[split == "train"], Xte, y[split == "test"], Xtr.shape[1], "fog", "FOG-raw")


# %% [markdown]
# ---
# ## Results summary

# %%
metrics_df = pd.DataFrame(ALL_METRICS)
metrics_df.to_csv(RESULTS_DIR / "baseline_metrics.csv", index=False)
with open(RESULTS_DIR / "baseline_metrics.json", "w") as fh:
    json.dump(ALL_METRICS, fh, indent=2)

print("\n===== BASELINE METRICS (subject-grouped CV; CNN = held-out test) =====")
print(metrics_df.to_string(index=False))
print("\nSaved:", RESULTS_DIR / "baseline_metrics.csv", "| figures:", FIG_DIR)

if not metrics_df.empty:
    best = metrics_df.sort_values("macro_f1_mean", ascending=False).groupby("task").first()
    print("\nBest baseline per task (the bar D2's Transformer must beat):")
    print(best[["label", "model", "macro_f1_mean", "auroc_mean"]].to_string())
