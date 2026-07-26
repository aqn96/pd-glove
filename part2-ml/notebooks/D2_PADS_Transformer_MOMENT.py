# %% [markdown]
# # Deliverable 2 — PADS MOMENT Transformer Fine-tuning
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Fine-tunes MOMENT-1-large (pre-trained time series foundation model) on
# PADS wrist IMU windows for PD vs HC classification.
# Compares against D2 baselines: SVM F1=0.564, RF F1=0.498, CNN F1=0.566

# %% Cell 1 — Imports + momentfm install
import os, subprocess, sys, warnings, json, shutil, torch
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Install momentfm from GitHub (bypasses numpy version conflict)
subprocess.run([sys.executable, "-m", "pip", "install",
                "git+https://github.com/moment-timeseries-foundation-model/moment.git",
                "-q"], check=False)

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
torch.manual_seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

# %% Cell 2 — Load cleaned data
DATA_DIR     = Path("/kaggle/input/notebooks/aqn96kag/pd-glove-d2-pads-pipeline/cleaned_d2")
BASELINE_DIR = Path("/kaggle/input/notebooks/aqn96kag/pd-glove-d2-pads-baseline-classifiers")
MODEL_DIR    = Path("/kaggle/input/datasets/aqn96kag/moment-1-large-weights")
EDA_DIR      = Path("/kaggle/working/eda_d2_transformer")
EDA_DIR.mkdir(parents=True, exist_ok=True)

raw      = np.load(DATA_DIR / "pads_raw_windows.npz")
X_raw    = raw["X"]
y_raw    = raw["y"]
subj_raw = raw["subject"]

print(f"Raw windows : {X_raw.shape}")
print(f"PD rate     : {y_raw.mean():.3f}")
print(f"Subjects    : {len(np.unique(subj_raw))}")

# %% Cell 3 — Dataset class (resample 974 → 512 for MOMENT's fixed seq_len)
SEQ_LEN = 512

class PADSDataset(Dataset):
    def __init__(self, X, y):
        X_t = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)
        X_t = F.interpolate(X_t, size=SEQ_LEN, mode='linear', align_corners=False)
        self.X = X_t
        self.y = torch.tensor(y, dtype=torch.long)
    def __len__(self): return len(self.y)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]

# %% Cell 4 — Training and evaluation helpers
def train_epoch(model, loader, optimizer, scheduler, criterion):
    model.train()
    losses = []
    for batch_x, labels in loader:
        batch_x, labels = batch_x.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        output = model(x_enc=batch_x, reduction='mean')
        loss = criterion(output.logits, labels)
        loss.backward()
        optimizer.step()
        scheduler.step()
        losses.append(loss.item())
    return float(np.mean(losses))

def evaluate(model, loader, criterion):
    model.eval()
    all_preds, all_probs, all_labels = [], [], []
    total_loss = 0
    with torch.no_grad():
        for batch_x, labels in loader:
            batch_x, labels = batch_x.to(DEVICE), labels.to(DEVICE)
            output = model(x_enc=batch_x, reduction='mean')
            loss = criterion(output.logits, labels)
            total_loss += loss.item()
            probs = torch.softmax(output.logits, dim=1)[:, 1].cpu().numpy()
            preds = output.logits.argmax(dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_probs.extend(probs)
            all_labels.extend(labels.cpu().numpy())
    return total_loss/len(loader), np.array(all_preds), np.array(all_probs), np.array(all_labels)

# %% Cell 5 — Load model ONCE, reuse across all folds (checkpoint-safe)
from momentfm import MOMENTPipeline
import copy, pathlib

CKPT_DIR = pathlib.Path("/kaggle/working/cleaned_d2")
CKPT_DIR.mkdir(parents=True, exist_ok=True)
scores_path = CKPT_DIR / "moment_fold_scores.csv"
cms_path    = CKPT_DIR / "moment_cms.npy"

N_SPLITS = 5
EPOCHS   = 5
BATCH    = 32
LR_MAX   = 1e-4

# /kaggle/working resets on every new notebook version, so a checkpoint from
# a prior (e.g. timed-out) run only survives if uploaded as its own Kaggle
# dataset and attached as input (self-referencing this notebook's own output
# was tried first but Kaggle doesn't mount it — a real dataset does).
# rglob over /kaggle/input finds it regardless of the dataset's mount path.
if not scores_path.exists():
    found = list(pathlib.Path("/kaggle/input").rglob("moment_fold_scores.csv"))
    if found:
        prior_dir = found[0].parent
        shutil.copy(prior_dir / "moment_fold_scores.csv", scores_path)
        shutil.copy(prior_dir / "moment_cms.npy", cms_path)
        print(f"Found prior checkpoint at {prior_dir} — copied into {CKPT_DIR}")

# Resume any folds already completed
if scores_path.exists() and cms_path.exists():
    prior  = pd.read_csv(scores_path)
    f1s    = prior["f1"].tolist()
    aurocs = prior["auroc"].tolist()
    cms    = list(np.load(cms_path))
    print(f"Resuming: {len(f1s)} fold(s) already done — skipping to fold {len(f1s)+1}")
else:
    f1s, aurocs, cms = [], [], []
    print("No checkpoint found — starting from fold 1")

if len(f1s) < N_SPLITS:
    print(f"Loading MOMENT from local weights...")
    base_model = MOMENTPipeline.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True,
        model_kwargs={
            "task_name":       "classification",
            "n_channels":      6,
            "num_class":       2,
            "freeze_encoder":  False,
            "freeze_embedder": False,
            "freeze_head":     False,
            "reduction":       "mean",
        },
    )
    base_model.init()
    print("Model loaded.")

    gkf = StratifiedGroupKFold(n_splits=N_SPLITS)
    counts  = np.bincount(y_raw)
    weights = torch.tensor(
        len(y_raw) / (len(counts) * counts), dtype=torch.float32
    ).to(DEVICE)
    print(f"Class weights: HC={weights[0]:.2f}  PD={weights[1]:.2f}")
    print(f"Running {N_SPLITS}-fold GroupKFold...\n")

    for fold, (tr_idx, te_idx) in enumerate(gkf.split(X_raw, y_raw, subj_raw)):
        if fold < len(f1s):
            print(f"--- Fold {fold+1}/{N_SPLITS} — already done, skipping ---")
            continue

        print(f"--- Fold {fold+1}/{N_SPLITS} ---", flush=True)

        X_tr, y_tr = X_raw[tr_idx], y_raw[tr_idx]
        X_te, y_te = X_raw[te_idx], y_raw[te_idx]

        train_dl = DataLoader(PADSDataset(X_tr, y_tr), batch_size=BATCH, shuffle=True)
        test_dl  = DataLoader(PADSDataset(X_te, y_te), batch_size=BATCH, shuffle=False)

        model = copy.deepcopy(base_model)
        model.to(DEVICE)

        criterion = torch.nn.CrossEntropyLoss(weight=weights)
        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()), lr=1e-6
        )
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=LR_MAX, total_steps=EPOCHS * len(train_dl)
        )

        for epoch in range(EPOCHS):
            tl = train_epoch(model, train_dl, optimizer, scheduler, criterion)
            _, preds, probs, labels = evaluate(model, test_dl, criterion)
            f1 = f1_score(labels, preds, average="macro")
            print(f"  epoch {epoch+1:2d}/{EPOCHS} — loss={tl:.4f}  F1={f1:.3f}", flush=True)

        _, preds, probs, labels = evaluate(model, test_dl, criterion)
        fold_f1  = f1_score(labels, preds, average="macro")
        fold_auc = roc_auc_score(labels, probs)
        fold_cm  = confusion_matrix(labels, preds)

        f1s.append(fold_f1)
        aurocs.append(fold_auc)
        cms.append(fold_cm)
        print(f"  Fold {fold+1} — F1={fold_f1:.3f}  AUROC={fold_auc:.3f}", flush=True)

        # Save after every fold
        np.save(cms_path, np.array(cms))
        pd.DataFrame({"f1": f1s, "auroc": aurocs}).to_csv(scores_path, index=False)
        print(f"  Checkpoint saved ({len(f1s)}/{N_SPLITS} folds)\n", flush=True)

print("=" * 50)
print(f"MOMENT — macro-F1: {np.mean(f1s):.3f} ± {np.std(f1s):.3f}"
      f"   AUROC: {np.mean(aurocs):.3f} ± {np.std(aurocs):.3f}")
print("All folds complete.")

# %% Cell 6 — Results vs baselines
scores = pd.read_csv("/kaggle/working/cleaned_d2/moment_fold_scores.csv")
f1s    = scores["f1"].tolist()
aurocs = scores["auroc"].tolist()
cms    = np.load("/kaggle/working/cleaned_d2/moment_cms.npy")

with open(BASELINE_DIR / "pads_baseline_metrics.json") as f:
    baseline_results = json.load(f)

results = pd.DataFrame(baseline_results + [{
    "model":         "MOMENT (full fine-tune)",
    "macro_f1_mean": round(float(np.mean(f1s)), 3),
    "macro_f1_std":  round(float(np.std(f1s)), 3),
    "auroc_mean":    round(float(np.mean(aurocs)), 3),
    "auroc_std":     round(float(np.std(aurocs)), 3),
    "n_folds":       N_SPLITS,
}])

print("\n=== D2 Full Results ===")
print(results.to_string(index=False))
results.to_json("/kaggle/working/pads_all_metrics.json", orient="records", indent=2)

# %% Cell 7 — Confusion matrix + comparison bar chart
mean_cm = np.mean(cms, axis=0).astype(int)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.heatmap(mean_cm, annot=True, fmt="d", ax=axes[0], cmap="Blues",
            xticklabels=["HC", "PD"], yticklabels=["HC", "PD"])
axes[0].set_title(f"MOMENT full fine-tune (avg across folds)\n"
                  f"F1={np.mean(f1s):.3f}  AUROC={np.mean(aurocs):.3f}")
axes[0].set_xlabel("Predicted")
axes[0].set_ylabel("True")

f1_vals = results["macro_f1_mean"].tolist()
colors  = ["steelblue"] * (len(results) - 1) + ["darkorange"]
axes[1].bar(results["model"].tolist(), f1_vals, color=colors)
axes[1].axhline(max(f1_vals[:-1]), color="gray", linestyle="--",
                alpha=0.5, label="best baseline")
axes[1].set_ylabel("Macro-F1")
axes[1].set_title("D2 Model Comparison — PADS PD vs HC")
axes[1].set_ylim(0, 1.0)
for i, v in enumerate(f1_vals):
    axes[1].text(i, v + 0.01, str(v), ha="center", fontsize=10)

plt.tight_layout()
plt.show()
print("Done.")
