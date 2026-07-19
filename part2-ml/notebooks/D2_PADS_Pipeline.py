# %% [markdown]
# # Deliverable 2 — PADS Dataset Pipeline
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Loads and cleans the PADS PhysioNet dataset (Parkinson's Disease Smartwatch Dataset).
# Extracts 42 features (7 features × 6 IMU channels) per window.
# Saves cleaned parquet + raw numpy arrays for downstream classifiers and Transformer.

# %% Cell 1 — Imports, path setup, locate_dir helper
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

PADS_ROOT      = locate_dir("pads*", "parkinsons*smartwatch*", "pads_dataset")
PATIENTS_DIR   = PADS_ROOT / "patients"
TIMESERIES_DIR = PADS_ROOT / "movement" / "timeseries"
print(f"PADS root : {PADS_ROOT}")
print(f"Output    : {OUT_DIR}")

# %% Cell 2 — Load subject labels from patients/*.json
PD_STRINGS = {"parkinson", "pd", "parkinson's", "parkinsons"}
HC_STRINGS = {"healthy"}

def load_labels():
    records = []
    for f in sorted(PATIENTS_DIR.glob("patient_*.json")):
        p = json.loads(f.read_text())
        sid       = int(p["id"])
        cond      = p.get("condition", "unknown")
        cond_lower = cond.lower().strip()
        if cond_lower in HC_STRINGS:
            label = 0
        elif any(cond_lower.startswith(s) for s in PD_STRINGS):
            label = 1
        else:
            label = -1  # DD / other — excluded from binary classification
        records.append({"subject_id": sid, "condition": cond, "label": label})
    df = pd.DataFrame(records).sort_values("subject_id").reset_index(drop=True)
    df_binary = df[df["label"] >= 0].copy()
    return df, df_binary

labels_all, labels_df = load_labels()
pd_count = (labels_df["label"] == 1).sum()
hc_count = (labels_df["label"] == 0).sum()
print(f"Subjects: PD={pd_count}  HC={hc_count}  Total={len(labels_df)}")

# %% Cell 3 — Feature extraction helpers
FS_PADS  = 100  # Hz
CHANNELS = ["Acc_X", "Acc_Y", "Acc_Z", "Gyro_X", "Gyro_Y", "Gyro_Z"]

def bandpass(sig, lo=0.5, hi=15.0, fs=FS_PADS, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lo / nyq, min(hi, nyq - 1e-3) / nyq], btype="band")
    return filtfilt(b, a, sig)

def window_feats(sig, fs=FS_PADS):
    """7 features from one channel signal (mirrors D1 feature extraction)."""
    sig   = bandpass(sig, fs=fs)
    spec  = np.abs(np.fft.rfft(sig - sig.mean()))
    freqs = np.fft.rfftfreq(len(sig), d=1.0 / fs)
    tremor_band = (freqs >= 4) & (freqs <= 6)
    low_band    = (freqs >= 0.5) & (freqs < 3.5)
    dom_band    = (freqs >= 3) & (freqs <= 8)
    pf = spec[tremor_band].sum() ** 2
    pl = spec[low_band].sum() ** 2 + 1e-9
    dom_idx = spec[dom_band].argmax() if dom_band.any() else 0
    return [
        float(sig.mean()),
        float(sig.std()),
        float(np.sqrt(np.mean(sig ** 2))),                              # RMS
        float(sig.max() - sig.min()),                                    # range
        float(freqs[dom_band][dom_idx]) if dom_band.any() else 0.0,     # dominant freq
        float(spec[tremor_band].sum() ** 2),                             # tremor band power
        float(pf / pl),                                                  # tremor index
    ]

FEAT_NAMES = ["mean", "std", "rms", "range", "dom_freq", "band_power", "tremor_index"]

# %% Cell 4 — Load windows and extract features
ARTEFACT_SAMPLES = 50  # drop first 0.5 s vibration artefact

def load_pads_features(labels_df):
    rows, raw_windows, raw_labels, raw_subjs = [], [], [], []
    sid_set   = set(labels_df["subject_id"])
    txt_files = sorted(TIMESERIES_DIR.glob("*.txt"))

    for fpath in txt_files:
        parts = fpath.stem.split("_")
        if len(parts) < 3:
            continue
        try:
            sid = int(parts[0])
        except ValueError:
            continue
        if sid not in sid_set:
            continue

        task  = "_".join(parts[1:-1])
        wrist = parts[-1]
        label = labels_df.loc[labels_df["subject_id"] == sid, "label"].values[0]

        try:
            data = np.loadtxt(fpath, delimiter=",")  # (1024, 7)
        except Exception:
            continue
        if data.ndim != 2 or data.shape[1] != 7:
            continue

        data = data[:, 1:]           # drop timestamp → (1024, 6)
        data = data[ARTEFACT_SAMPLES:]
        if data.shape[0] < 256:
            continue

        feats = []
        for ch in range(6):
            feats.extend(window_feats(data[:, ch]))

        row = {f"{CHANNELS[ch]}_{feat}": feats[ch * 7 + fi]
               for ch in range(6) for fi, feat in enumerate(FEAT_NAMES)}
        row.update({"subject_id": sid, "label": label, "task": task, "wrist": wrist})
        rows.append(row)
        raw_windows.append(data[:1024 - ARTEFACT_SAMPLES])
        raw_labels.append(label)
        raw_subjs.append(sid)

    feat_df = pd.DataFrame(rows)
    min_len = min(w.shape[0] for w in raw_windows)
    raw_arr = np.stack([w[:min_len] for w in raw_windows]).astype(np.float32)
    return feat_df, raw_arr, np.array(raw_labels), np.array(raw_subjs)

feat_df, raw_arr, raw_y, raw_subjs = load_pads_features(labels_df)
print(f"Windows : {len(feat_df)}   Shape: {raw_arr.shape}")

# %% Cell 5 — Subject-level splits and save
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
    assert not (s_tr & s_va), "Train/val subject overlap!"
    assert not (s_tr & s_te), "Train/test subject overlap!"
    assert not (s_va & s_te), "Val/test subject overlap!"
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)

pads_tr, pads_va, pads_te = subject_split(feat_df, "subject_id")
for name, d in [("train", pads_tr), ("val", pads_va), ("test", pads_te)]:
    d.to_parquet(OUT_DIR / f"pads_{name}.parquet", index=False)
feat_df.to_parquet(OUT_DIR / "pads_all.parquet", index=False)

test_sids = set(pads_te["subject_id"])
val_sids  = set(pads_va["subject_id"])
split_of  = np.where(np.isin(raw_subjs, list(test_sids)), "test",
            np.where(np.isin(raw_subjs, list(val_sids)),  "val", "train"))

np.savez_compressed(
    OUT_DIR / "pads_raw_windows.npz",
    X=raw_arr, y=raw_y, subject=raw_subjs,
    split=split_of, channels=np.array(CHANNELS),
)
print(f"Splits — Train: {len(pads_tr)}  Val: {len(pads_va)}  Test: {len(pads_te)}")
print("Leakage check passed.")

# %% Cell 6 — EDA figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Label balance
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(["HC (0)", "PD (1)"], [(raw_y == 0).sum(), (raw_y == 1).sum()],
       color=["steelblue", "darkorange"])
ax.set_ylabel("Windows")
ax.set_title("PADS — Label Balance")
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_label_balance.png", dpi=120)
plt.close()

# Dominant frequency by label
feat_cols = [c for c in feat_df.columns if c.endswith("dom_freq")]
dom_freq_mean = feat_df[feat_cols].mean(axis=1)
fig, ax = plt.subplots(figsize=(7, 4))
for lbl, name, color in [(0, "HC", "steelblue"), (1, "PD", "darkorange")]:
    ax.hist(dom_freq_mean[feat_df["label"] == lbl], bins=40, alpha=0.6,
            label=name, color=color, density=True)
ax.axvspan(4, 6, alpha=0.15, color="red", label="Tremor band (4–6 Hz)")
ax.set_xlabel("Mean dominant frequency (Hz)")
ax.set_title("PADS — Dominant Frequency by Diagnosis")
ax.legend()
plt.tight_layout()
plt.savefig(EDA_DIR / "pads_dom_freq.png", dpi=120)
plt.close()

print("EDA figures saved.")

# %% Cell 7 — Summary
print(f"\nPADS pipeline complete")
print(f"  Windows : {len(raw_y):,}  (PD={(raw_y==1).sum()}, HC={(raw_y==0).sum()})")
print(f"  Subjects: {len(np.unique(raw_subjs))}")
print(f"  Features: {feat_df.shape[1] - 3} (7 × 6 channels)")
counts = np.bincount(raw_y)
print(f"  Class weights: HC={len(raw_y)/(2*counts[0]):.2f}  PD={len(raw_y)/(2*counts[1]):.2f}")
print(f"\nOutputs in {OUT_DIR}:")
for f in sorted(OUT_DIR.iterdir()):
    print(f"  {f.name}  ({f.stat().st_size/1e6:.1f} MB)")
