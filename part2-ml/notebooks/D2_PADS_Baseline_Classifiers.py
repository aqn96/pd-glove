# %% [markdown]
# # Deliverable 2 — PADS Baseline Classifiers
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Trains SVM, Random Forest, and 1D-CNN on PADS for PD vs HC classification.
# Uses 5-fold StratifiedGroupKFold (subject-level splits, no leakage).
# Reads cleaned data from the D2 PADS Pipeline notebook output.

# %% Cell 1 — Imports and data load
import warnings, json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
RANDOM_STATE = 42

DATA_DIR = Path("/kaggle/input/notebooks/aqn96kag/pd-glove-d2-pads-pipeline/cleaned_d2")
EDA_DIR  = Path("/kaggle/working/eda_d2")
EDA_DIR.mkdir(parents=True, exist_ok=True)
DEVICE   = "cuda" if torch.cuda.is_available() else "cpu"
N_SPLITS = 5
print(f"Device: {DEVICE}")

feat_df  = pd.read_parquet(DATA_DIR / "pads_all.parquet")
raw      = np.load(DATA_DIR / "pads_raw_windows.npz")
X_raw    = raw["X"]       # (7810, 974, 6)
y_raw    = raw["y"]
subj_raw = raw["subject"]

feat_cols = [c for c in feat_df.columns
             if any(c.endswith(f) for f in
                    ["mean", "std", "rms", "range", "dom_freq", "band_power", "tremor_index"])]
X      = feat_df[feat_cols].values.astype(np.float32)
y      = feat_df["label"].values
groups = feat_df["subject_id"].values

print(f"Feature matrix : {X.shape}")
print(f"Raw windows    : {X_raw.shape}")
print(f"PD rate        : {y.mean():.3f}")

# %% Cell 2 — Cross-validation helper (SVM / RF)
def groupkfold_eval(X, y, groups, model, model_name, n_splits=N_SPLITS):
    gkf = StratifiedGroupKFold(n_splits=n_splits)
    f1s, aurocs, cms = [], [], []
    for fold, (tr, te) in enumerate(gkf.split(X, y, groups)):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[tr])
        X_te = scaler.transform(X[te])
        model.fit(X_tr, y[tr])
        y_pred  = model.predict(X_te)
        y_score = model.predict_proba(X_te)[:, 1]
        f1s.append(f1_score(y[te], y_pred, average="macro"))
        aurocs.append(roc_auc_score(y[te], y_score))
        cms.append(confusion_matrix(y[te], y_pred))
        print(f"  Fold {fold+1} — F1={f1s[-1]:.3f}  AUROC={aurocs[-1]:.3f}")
    mean_cm = np.mean(cms, axis=0).astype(int)
    print(f"{model_name} — macro-F1: {np.mean(f1s):.3f} ± {np.std(f1s):.3f}"
          f"   AUROC: {np.mean(aurocs):.3f} ± {np.std(aurocs):.3f}\n")
    return {
        "model":         model_name,
        "macro_f1_mean": round(float(np.mean(f1s)), 3),
        "macro_f1_std":  round(float(np.std(f1s)), 3),
        "auroc_mean":    round(float(np.mean(aurocs)), 3),
        "auroc_std":     round(float(np.std(aurocs)), 3),
        "n_folds":       n_splits,
        "confusion_matrix": mean_cm.tolist(),
    }

# %% Cell 3 — SVM
print("=== SVM ===")
svm = SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=RANDOM_STATE)
svm_res = groupkfold_eval(X, y, groups, svm, "SVM")

# %% Cell 4 — Random Forest
print("=== Random Forest ===")
rf = RandomForestClassifier(n_estimators=400, class_weight="balanced",
                            random_state=RANDOM_STATE, n_jobs=-1)
rf_res = groupkfold_eval(X, y, groups, rf, "RandomForest")

# %% Cell 5 — 1D-CNN (raw windows)
class CNN1D(nn.Module):
    def __init__(self, n_channels=6, n_classes=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(n_channels, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64), nn.ReLU(), nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Linear(64, n_classes)

    def forward(self, x):
        return self.head(self.net(x).squeeze(-1))

def train_eval_cnn(X_raw, y_raw, subj_raw, n_splits=N_SPLITS,
                   epochs=40, batch=64, lr=1e-3):
    X_t = torch.tensor(X_raw.transpose(0, 2, 1), dtype=torch.float32)  # (N, C, T)
    y_t = torch.tensor(y_raw, dtype=torch.long)
    counts  = np.bincount(y_raw)
    weights = torch.tensor(len(y_raw) / (len(counts) * counts),
                           dtype=torch.float32).to(DEVICE)
    gkf = StratifiedGroupKFold(n_splits=n_splits)
    f1s, aurocs, cms = [], [], []

    for fold, (tr, te) in enumerate(gkf.split(X_t, y_t, subj_raw)):
        model     = CNN1D(n_channels=X_t.shape[1]).to(DEVICE)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss(weight=weights)
        train_dl  = DataLoader(TensorDataset(X_t[tr], y_t[tr]),
                               batch_size=batch, shuffle=True)
        model.train()
        for epoch in range(epochs):
            for xb, yb in train_dl:
                optimizer.zero_grad()
                loss = criterion(model(xb.to(DEVICE)), yb.to(DEVICE))
                loss.backward()
                optimizer.step()

        model.eval()
        all_preds, all_probs, all_labels = [], [], []
        with torch.no_grad():
            for xb, yb in DataLoader(TensorDataset(X_t[te], y_t[te]), batch_size=batch):
                logits = model(xb.to(DEVICE))
                all_probs.extend(torch.softmax(logits, 1)[:, 1].cpu().numpy())
                all_preds.extend(logits.argmax(1).cpu().numpy())
                all_labels.extend(yb.numpy())
        f1s.append(f1_score(all_labels, all_preds, average="macro"))
        aurocs.append(roc_auc_score(all_labels, all_probs))
        cms.append(confusion_matrix(all_labels, all_preds))
        print(f"  Fold {fold+1} — F1={f1s[-1]:.3f}  AUROC={aurocs[-1]:.3f}")

    print(f"CNN1D — macro-F1: {np.mean(f1s):.3f} ± {np.std(f1s):.3f}"
          f"   AUROC: {np.mean(aurocs):.3f} ± {np.std(aurocs):.3f}\n")
    return {
        "model":         "CNN1D",
        "macro_f1_mean": round(float(np.mean(f1s)), 3),
        "macro_f1_std":  round(float(np.std(f1s)), 3),
        "auroc_mean":    round(float(np.mean(aurocs)), 3),
        "auroc_std":     round(float(np.std(aurocs)), 3),
        "n_folds":       n_splits,
        "confusion_matrix": np.mean(cms, axis=0).astype(int).tolist(),
    }

print("=== 1D-CNN ===")
cnn_res = train_eval_cnn(X_raw, y_raw, subj_raw)

# %% Cell 6 — Save results and figures
all_results = [svm_res, rf_res, cnn_res]
out_path = Path("/kaggle/working/pads_baseline_metrics.json")
with open(out_path, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"Saved → {out_path}")

results_df = pd.DataFrame([{k: v for k, v in r.items() if k != "confusion_matrix"}
                            for r in all_results])
print("\n=== D2 Baseline Results ===")
print(results_df.to_string(index=False))

# Confusion matrix grid
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, res in zip(axes, all_results):
    cm = np.array(res["confusion_matrix"])
    sns.heatmap(cm, annot=True, fmt="d", ax=ax, cmap="Blues",
                xticklabels=["HC", "PD"], yticklabels=["HC", "PD"])
    ax.set_title(f"{res['model']}\nF1={res['macro_f1_mean']}  AUROC={res['auroc_mean']}")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_confusion_matrices.png", dpi=120, bbox_inches="tight")
plt.close()
print("Saved → pads_confusion_matrices.png")

# %% Cell 7 — RF feature importance
scaler_full = StandardScaler()
rf_full = RandomForestClassifier(n_estimators=400, class_weight="balanced",
                                  random_state=RANDOM_STATE, n_jobs=-1)
rf_full.fit(scaler_full.fit_transform(X), y)
importances = rf_full.feature_importances_
top_idx = np.argsort(importances)[::-1][:20]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh([feat_cols[i] for i in top_idx][::-1],
        importances[top_idx][::-1], color="steelblue")
ax.set_xlabel("Feature importance")
ax.set_title("Top 20 RF features — PADS PD vs HC")
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_rf_feature_importance.png", dpi=120, bbox_inches="tight")
plt.close()
print("Saved → pads_rf_feature_importance.png")
