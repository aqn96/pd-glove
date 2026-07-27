# %% [markdown]
# # Deliverable 2 — PADS Dataset Pipeline
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Loads the PADS (Parkinson's Disease Smartwatch) dataset, extracts features
# from raw wrist IMU signals, applies leakage-safe subject-level splits, runs
# EDA, and stages cleaned data for the D2 baseline classifiers.
#
# - Dataset: PADS (PhysioNet, 469 subjects, 100 Hz, bilateral wrist acc+gyro)
# - Task: PD vs Healthy Control binary classification
# - Sensor: Apple Watch Series 4 — Acc (g) + Gyro (rad/s), 6 channels
# - Label source: `patients/patient_XXX.json` → condition field
# - Companion: `D2_PADS_Baseline_Classifiers.py` (SVM / RF / 1D-CNN / Transformer)

# %% Cell 1 — Setup: portable paths (Kaggle and local) + locate_dir helper
import os, re, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

_here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd()

SEARCH_ROOTS = [
    Path("/kaggle/input"),
    _here.parents[1] / "data",
    Path("data"), Path("../data"),
]

_seen, _unique = set(), []
for _r in SEARCH_ROOTS:
    try:
        _rp = _r.resolve()
    except Exception:
        _rp = _r
    if _rp not in _seen:
        _seen.add(_rp)
        _unique.append(_r)
SEARCH_ROOTS = _unique

OUT_DIR = (
    Path("/kaggle/working/cleaned_d2")
    if Path("/kaggle/working").exists()
    else _here.parents[1] / "results" / "cleaned_d2"
    if "__file__" in globals() else Path("results/cleaned_d2")
)
OUT_DIR.mkdir(parents=True, exist_ok=True)
EDA_DIR = OUT_DIR.parent / "eda_d2"
EDA_DIR.mkdir(parents=True, exist_ok=True)

def locate_dir(*patterns, required=True):
    """Find first directory matching any pattern under search roots."""
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for pat in patterns:
            hits = sorted(root.rglob(pat))
            hits = [h for h in hits if h.is_dir()]
            if hits:
                return hits[0]
    if required:
        raise FileNotFoundError(
            f"Could not find directory matching {patterns}. "
            "Attach the PADS dataset on Kaggle via Add Input."
        )
    return None

# Find PADS root — works regardless of Kaggle dataset slug
PADS_ROOT      = locate_dir("pads*", "parkinsons*smartwatch*", "pads_dataset")
PATIENTS_DIR   = PADS_ROOT / "patients"
TIMESERIES_DIR = PADS_ROOT / "movement" / "timeseries"

print("PADS root   :", PADS_ROOT)
print("Patients    :", PATIENTS_DIR.exists(), "| files:", len(list(PATIENTS_DIR.glob("*.json"))))
print("Timeseries  :", TIMESERIES_DIR.exists(), "| files:", len(list(TIMESERIES_DIR.glob("*.txt"))))
print("Output dir  :", OUT_DIR)

# %% Cell 2 — Load PADS labels from patients/*.json
# PD condition strings vary slightly — print what we find and map all variants
PD_STRINGS = {"parkinson", "pd", "parkinson's", "parkinsons"}
HC_STRINGS = {"healthy"}

def load_labels():
    records = []
    for f in sorted(PATIENTS_DIR.glob("patient_*.json")):
        p = json.loads(f.read_text())
        sid   = int(p["id"])
        cond  = p.get("condition", "unknown")
        cond_lower = cond.lower().strip()

        if cond_lower in HC_STRINGS:
            label = 0
        elif any(cond_lower.startswith(s) for s in PD_STRINGS):
            label = 1
        else:
            label = -1  # DD — excluded from binary classification

        records.append({
            "subject_id": sid,
            "condition":  cond,
            "label":      label,
        })

    df = pd.DataFrame(records).sort_values("subject_id").reset_index(drop=True)
    print("=== All condition values found ===")
    print(df["condition"].value_counts().to_string())

    # Keep only PD and HC
    df_binary = df[df["label"] >= 0].copy()
    print(f"\nKept (PD=1, HC=0): {len(df_binary)} subjects")
    print(df_binary["label"].value_counts().rename({1: "PD", 0: "HC"}).to_string())
    return df, df_binary

labels_all, labels_df = load_labels()

# %% Cell 3 — Feature extraction — same 7 features as D1 Daphnet, adapted for 100 Hz
FS_PADS  = 100  # Hz
CHANNELS = ["Acc_X", "Acc_Y", "Acc_Z", "Gyro_X", "Gyro_Y", "Gyro_Z"]

def bandpass(sig, lo=0.5, hi=15.0, fs=FS_PADS, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lo / nyq, min(hi, nyq - 1e-3) / nyq], btype="band")
    return filtfilt(b, a, sig)

def window_feats(sig, fs=FS_PADS):
    """7 features from one channel signal (mirrors D1 _window_feats)."""
    sig  = bandpass(sig, fs=fs)
    spec = np.abs(np.fft.rfft(sig - sig.mean()))
    freqs = np.fft.rfftfreq(len(sig), d=1.0 / fs)

    # tremor band 4–6 Hz (Parkinsonian rest tremor) vs low-freq locomotion
    tremor_band = (freqs >= 4) & (freqs <= 6)
    low_band    = (freqs >= 0.5) & (freqs < 3.5)
    pf = spec[tremor_band].sum() ** 2
    pl = spec[low_band].sum()    ** 2 + 1e-9

    dom_band = (freqs >= 3) & (freqs <= 8)
    dom_idx  = spec[dom_band].argmax() if dom_band.any() else 0

    return [
        float(sig.mean()),
        float(sig.std()),
        float(np.sqrt(np.mean(sig ** 2))),          # RMS
        float(sig.max() - sig.min()),               # range
        float(freqs[dom_band][dom_idx]) if dom_band.any() else 0.0,  # dominant freq
        float(spec[tremor_band].sum() ** 2),        # tremor band power
        float(pf / pl),                             # tremor index (replaces Freeze Index)
    ]

FEAT_NAMES = ["mean", "std", "rms", "range", "dom_freq", "band_power", "tremor_index"]

# %% Cell 4 — Load all PADS timeseries windows + extract features
#
# Each .txt file = one task recording for one subject on one wrist
# Shape: (1024, 6) — 10.24 s at 100 Hz, 6 channels (Acc xyz + Gyro xyz)
# No sliding window needed — each file IS already one window.
# Usage note from dataset: cut first ~50 samples (0.5 s vibration artefact).

ARTEFACT_SAMPLES = 50  # vibration from watch at task start

def load_pads_features(labels_df):
    rows        = []
    subject_ids = []
    raw_windows = []
    raw_labels  = []
    raw_subjs   = []

    sid_set = set(labels_df["subject_id"])

    txt_files = sorted(TIMESERIES_DIR.glob("*.txt"))
    print(f"Total .txt files in timeseries/: {len(txt_files)}")

    skipped = 0
    for fpath in txt_files:
        # filename pattern: 001_CrossArms_LeftWrist.txt
        parts = fpath.stem.split("_")
        if len(parts) < 3:
            skipped += 1
            continue

        try:
            sid = int(parts[0])
        except ValueError:
            skipped += 1
            continue

        if sid not in sid_set:
            continue  # DD subject — excluded

        task  = "_".join(parts[1:-1])   # e.g. CrossArms, DrinkGlas
        wrist = parts[-1]               # LeftWrist / RightWrist

        label = labels_df.loc[labels_df["subject_id"] == sid, "label"].values[0]

        try:
            data = np.loadtxt(fpath, delimiter=",")  # (1024, 7) — col 0 is timestamp
        except Exception:
            skipped += 1
            continue

        if data.ndim != 2 or data.shape[1] != 7:
            skipped += 1
            continue

        data = data[:, 1:]  # drop timestamp → (1024, 6): AccX AccY AccZ GyroX GyroY GyroZ

        # Drop vibration artefact at start
        data = data[ARTEFACT_SAMPLES:]

        if data.shape[0] < 256:
            skipped += 1
            continue

        # Extract features: 7 features × 6 channels = 42 features
        feats = []
        for ch in range(6):
            feats.extend(window_feats(data[:, ch]))

        row = {f"{CHANNELS[ch]}_{feat}": feats[ch * 7 + fi]
               for ch in range(6)
               for fi, feat in enumerate(FEAT_NAMES)}
        row.update({"subject_id": sid, "label": label, "task": task, "wrist": wrist})

        rows.append(row)
        subject_ids.append(sid)
        raw_windows.append(data[:1024 - ARTEFACT_SAMPLES])
        raw_labels.append(label)
        raw_subjs.append(sid)

    feat_df = pd.DataFrame(rows)
    print(f"\nLoaded windows : {len(feat_df)}")
    print(f"Skipped files  : {skipped}")
    print(f"Subjects       : {feat_df['subject_id'].nunique()}")
    print(f"\nLabel balance:")
    print(feat_df["label"].value_counts().rename({1: "PD", 0: "HC"}).to_string())
    print(f"\nWindows per task:")
    print(feat_df["task"].value_counts().to_string())

    # Pad raw windows to uniform length for CNN
    min_len = min(w.shape[0] for w in raw_windows)
    raw_arr = np.stack([w[:min_len] for w in raw_windows]).astype(np.float32)

    return feat_df, raw_arr, np.array(raw_labels), np.array(raw_subjs)

feat_df, raw_arr, raw_y, raw_subjs = load_pads_features(labels_df)

# %% Cell 5 — Subject-level splits
from sklearn.model_selection import GroupShuffleSplit

def subject_split(df, group_col, test_size=0.15, val_size=0.15, seed=42):
    df = df.reset_index(drop=True)
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    trainval_idx, test_idx = next(gss.split(df, groups=df[group_col]))
    trainval, test = df.iloc[trainval_idx], df.iloc[test_idx]
    rel_val = val_size / (1.0 - test_size)
    gss2 = GroupShuffleSplit(n_splits=1, test_size=rel_val, random_state=seed)
    tr_idx, val_idx = next(gss2.split(trainval, groups=trainval[group_col]))
    train, val = trainval.iloc[tr_idx], trainval.iloc[val_idx]
    s_tr, s_va, s_te = (set(d[group_col]) for d in (train, val, test))
    assert not (s_tr & s_va), "LEAKAGE: subject overlap train/val"
    assert not (s_tr & s_te), "LEAKAGE: subject overlap train/test"
    assert not (s_va & s_te), "LEAKAGE: subject overlap val/test"
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)

def report_split(name, train, val, test, group_col):
    print(f"[{name}] rows  train/val/test = {len(train)}/{len(val)}/{len(test)}")
    print(f"[{name}] subjects train/val/test = "
          f"{train[group_col].nunique()}/{val[group_col].nunique()}/{test[group_col].nunique()}")

def save_splits(prefix, train, val, test):
    for name, d in [("train", train), ("val", val), ("test", test)]:
        d.to_parquet(OUT_DIR / f"{prefix}_{name}.parquet", index=False)
    print(f"  saved -> {prefix}_(train|val|test).parquet")

pads_tr, pads_va, pads_te = subject_split(feat_df, "subject_id")
report_split("PADS", pads_tr, pads_va, pads_te, "subject_id")
save_splits("pads", pads_tr, pads_va, pads_te)

feat_df.to_parquet(OUT_DIR / "pads_all.parquet", index=False)

test_sids = set(pads_te["subject_id"])
val_sids  = set(pads_va["subject_id"])
split_of  = np.where(np.isin(raw_subjs, list(test_sids)), "test",
            np.where(np.isin(raw_subjs, list(val_sids)), "val", "train"))

np.savez_compressed(
    OUT_DIR / "pads_raw_windows.npz",
    X=raw_arr, y=raw_y, subject=raw_subjs,
    split=split_of, channels=np.array(CHANNELS),
)
print(f"  saved -> pads_raw_windows.npz {raw_arr.shape}")

# %% Cell 6 — EDA figures for the D2 report
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

feat_cols = [c for c in feat_df.columns
             if any(c.endswith(f) for f in FEAT_NAMES)]

# (a) Label balance
fig, ax = plt.subplots(figsize=(5, 4))
feat_df["label"].value_counts().rename({1: "PD", 0: "HC"}).plot.bar(
    ax=ax, color=["steelblue", "indianred"])
ax.set_ylabel("Windows")
ax.set_title("PADS class balance (PD vs HC)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_label_balance.png", dpi=120)
plt.close()

# (b) Windows per subject
fig, ax = plt.subplots(figsize=(10, 4))
feat_df.groupby("subject_id").size().plot.bar(ax=ax, color="steelblue", width=0.8)
ax.set_xlabel("Subject ID")
ax.set_ylabel("Windows")
ax.set_title("PADS windows per subject")
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_windows_per_subject.png", dpi=120)
plt.close()

# (c) Dominant frequency by label (tremor band sanity check)
dom_col = "Acc_X_dom_freq"
fig, ax = plt.subplots(figsize=(6, 4))
for lbl, color, name in [(1, "darkorange", "PD"), (0, "gray", "HC")]:
    vals = feat_df.loc[feat_df["label"] == lbl, dom_col]
    ax.hist(vals, bins=40, alpha=0.6, color=color, label=name)
ax.axvspan(4, 6, color="green", alpha=0.12, label="4–6 Hz PD tremor band")
ax.set_xlabel("Dominant frequency (Hz)")
ax.set_ylabel("Count")
ax.set_title("PADS Acc_X dominant frequency — PD vs HC")
ax.legend()
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_dom_freq.png", dpi=120)
plt.close()

# (d) Windows per task
fig, ax = plt.subplots(figsize=(8, 4))
feat_df["task"].value_counts().plot.bar(ax=ax, color="steelblue")
ax.set_ylabel("Windows")
ax.set_title("PADS windows per assessment task")
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_windows_per_task.png", dpi=120)
plt.close()

print("EDA figures written to:", EDA_DIR)
for p in sorted(EDA_DIR.glob("*.png")):
    print("  -", p.name)

# Text summary
with open(OUT_DIR.parent / "eda_summary_d2.txt", "w") as fh:
    fh.write("=== PADS label distribution ===\n")
    fh.write(feat_df["label"].value_counts().rename({1: "PD", 0: "HC"}).to_string() + "\n\n")
    fh.write(f"PADS windows : {len(feat_df)}\n")
    fh.write(f"Subjects     : {feat_df['subject_id'].nunique()}\n")
    fh.write(f"Tasks        : {feat_df['task'].nunique()}\n")
    fh.write(f"Features/win : {len(feat_cols)}\n")
    fh.write(f"PD rate      : {feat_df['label'].mean():.4f}\n")
print("Wrote eda_summary_d2.txt")

# %% Cell 7 — Summary
print("\n=== Pipeline complete ===")
print(f"Feature windows : {len(feat_df)}")
print(f"Raw windows     : {raw_arr.shape}  (N, samples, channels)")
print(f"Features/window : {len(feat_cols)}  (7 features × 6 channels)")
print(f"Subjects        : {feat_df['subject_id'].nunique()}")
print(f"\nOutput files:")
for p in sorted(OUT_DIR.glob("*")):
    print(f"  - {p.name}")
print(f"\nEDA figures:")
for p in sorted(EDA_DIR.glob("*.png")):
    print(f"  - {p.name}")

# AWS S3 upload (uncomment when bucket is configured)
# def upload_dir_to_s3(local_dir, bucket, prefix="deliverable2/cleaned"):
#     import boto3
#     s3 = boto3.client("s3")
#     for p in sorted(Path(local_dir).glob("*")):
#         if p.is_file():
#             key = f"{prefix}/{p.name}"
#             s3.upload_file(str(p), bucket, key)
#             print(f"uploaded s3://{bucket}/{key}")
# BUCKET = "pd-glove-data"
# upload_dir_to_s3(OUT_DIR, BUCKET)
