# %% [markdown]
# # Deliverable 3 — INT8 TFLite Quantization + Fairness Audit
# **CS 8674 Part II · Intelligent IoT Frameworks for Chronic Disease Management**
#
# Trains one deployable CNN on the D2 pipeline's subject-level train/test
# split, quantizes it to INT8 TFLite, and audits the quantized model's
# fairness across PADS' own patient demographics (age, gender, handedness).
#
# The D2 baseline classifiers notebook's 5-fold CV already reports the
# unbiased benchmark numbers in the D2 report — this notebook is D3-specific
# and deliberately kept separate so re-running it never touches those
# already-final numbers.
#
# Inputs required (Add Input on Kaggle):
# - `pd-glove-d2-pads-pipeline` notebook output (cleaned PADS parquet + npz)
# - The raw PADS dataset (for `patients/*.json` demographics — the cleaned
#   pipeline output doesn't carry demographics forward)

# %% Cell 1 — Imports and paths
import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import f1_score, roc_auc_score

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)

DATA_DIR = Path("/kaggle/input/notebooks/aqn96kag/pd-glove-d2-pads-pipeline/cleaned_d2")
OUT_DIR  = Path("/kaggle/working")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def locate_pads_root():
    """Find the raw PADS dataset dir (for patients/*.json) under /kaggle/input."""
    for pat in ("pads*", "parkinsons*smartwatch*"):
        hits = sorted(p for p in Path("/kaggle/input").rglob(pat) if p.is_dir())
        if hits:
            return hits[0]
    raise FileNotFoundError(
        "PADS raw dataset not found under /kaggle/input — attach it as an "
        "input to this notebook (same dataset the pipeline notebook uses)."
    )

print("Data dir :", DATA_DIR)

# %% Cell 2 — Load cleaned PADS raw windows + subject-level train/test split
raw      = np.load(DATA_DIR / "pads_raw_windows.npz")
X_raw    = raw["X"]        # (7810, 974, 6) — channels-last, no transpose needed for Keras
y_raw    = raw["y"]
subj_raw = raw["subject"]
split_of = raw["split"]    # "train" / "val" / "test", subject-level, leakage-safe

train_mask = split_of == "train"
test_mask  = split_of == "test"

X_tr_raw, y_tr_raw, subj_tr = X_raw[train_mask], y_raw[train_mask], subj_raw[train_mask]
X_te_raw, y_te_raw, subj_te = X_raw[test_mask],  y_raw[test_mask],  subj_raw[test_mask]

print(f"Train windows : {len(y_tr_raw)}   Subjects: {len(np.unique(subj_tr))}")
print(f"Test windows  : {len(y_te_raw)}   Subjects: {len(np.unique(subj_te))}")

# %% Cell 3 — Deployable CNN (Keras) — same architecture as D2's PyTorch CNN1D
#
# Reimplemented directly in tf.keras rather than converted from the PyTorch
# model — TFLite's converter handles native Keras ops far more reliably
# than a PyTorch -> ONNX -> TensorFlow path for a model this small.

def build_cnn1d(seq_len, n_channels=6, n_classes=2):
    inputs = tf.keras.Input(shape=(seq_len, n_channels))
    x = tf.keras.layers.Conv1D(32, 5, padding="same")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.MaxPooling1D(2)(x)
    x = tf.keras.layers.Conv1D(64, 5, padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    outputs = tf.keras.layers.Dense(n_classes)(x)
    return tf.keras.Model(inputs, outputs)

counts = np.bincount(y_tr_raw)
class_weight = {0: len(y_tr_raw) / (2 * counts[0]), 1: len(y_tr_raw) / (2 * counts[1])}
print(f"Class weights: HC={class_weight[0]:.2f}  PD={class_weight[1]:.2f}")

keras_cnn = build_cnn1d(seq_len=X_tr_raw.shape[1])
keras_cnn.compile(optimizer="adam",
                   loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                   metrics=["accuracy"])
keras_cnn.fit(X_tr_raw, y_tr_raw, epochs=40, batch_size=64,
              class_weight=class_weight, verbose=2)

test_logits = keras_cnn.predict(X_te_raw, verbose=0)
test_probs  = tf.nn.softmax(test_logits, axis=1).numpy()[:, 1]
test_preds  = test_logits.argmax(axis=1)
float_f1    = f1_score(y_te_raw, test_preds, average="macro")
float_auroc = roc_auc_score(y_te_raw, test_probs)
print(f"Float32 Keras CNN — test F1={float_f1:.3f}  AUROC={float_auroc:.3f}")

# %% Cell 4 — INT8 TFLite quantization + accuracy delta
def representative_dataset():
    rng = np.random.default_rng(RANDOM_STATE)
    idx = rng.choice(len(X_tr_raw), size=min(200, len(X_tr_raw)), replace=False)
    for i in idx:
        yield [X_tr_raw[i:i + 1].astype(np.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(keras_cnn)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
                                        tf.lite.OpsSet.TFLITE_BUILTINS]
tflite_model = converter.convert()

TFLITE_PATH = OUT_DIR / "pads_cnn1d_int8.tflite"
TFLITE_PATH.write_bytes(tflite_model)
print(f"Saved {TFLITE_PATH}  ({TFLITE_PATH.stat().st_size / 1024:.1f} KB)")

# Evaluate the quantized model on the same held-out test split
interpreter = tf.lite.Interpreter(model_path=str(TFLITE_PATH))
interpreter.allocate_tensors()
in_detail  = interpreter.get_input_details()[0]
out_detail = interpreter.get_output_details()[0]

tflite_preds, tflite_probs = [], []
for i in range(len(X_te_raw)):
    x = X_te_raw[i:i + 1].astype(np.float32)
    interpreter.set_tensor(in_detail["index"], x)
    interpreter.invoke()
    logits = interpreter.get_tensor(out_detail["index"])[0]
    probs  = tf.nn.softmax(logits).numpy()
    tflite_preds.append(int(np.argmax(probs)))
    tflite_probs.append(float(probs[1]))

int8_f1    = f1_score(y_te_raw, tflite_preds, average="macro")
int8_auroc = roc_auc_score(y_te_raw, tflite_probs)
print(f"INT8 TFLite CNN  — test F1={int8_f1:.3f}  AUROC={int8_auroc:.3f}")
print(f"Accuracy delta from quantization: F1 {float_f1:.3f} -> {int8_f1:.3f}"
      f"  ({int8_f1 - float_f1:+.3f})")

# %% Cell 5 — Fairness audit (PADS demographics, on the deployed INT8 model)
#
# Audits the INT8 model specifically since that's the artifact that would
# actually deploy, not the float32 training-time model.

PATIENTS_DIR = locate_pads_root() / "patients"

demo_rows = []
for f in sorted(PATIENTS_DIR.glob("patient_*.json")):
    p = json.loads(f.read_text())
    demo_rows.append({
        "subject_id": int(p["id"]),
        "age":        p.get("age"),
        "gender":     p.get("gender"),
        "handedness": p.get("handedness"),
    })
demo_df = pd.DataFrame(demo_rows)
print(f"Loaded demographics for {len(demo_df)} subjects")

# Window-level audit, consistent with how every other D2/D3 metric is computed
test_df = pd.DataFrame({
    "subject_id": subj_te,
    "y_true":     y_te_raw,
    "y_pred":     tflite_preds,
    "y_prob":     tflite_probs,
}).merge(demo_df, on="subject_id", how="left")

test_df["age_group"] = pd.cut(test_df["age"], bins=[0, 55, 70, 200],
                              labels=["<55", "55-70", "70+"])

def subgroup_report(df, col):
    print(f"\n=== Fairness by {col} ===")
    rows = []
    for val, g in df.groupby(col):
        pd_rate = g["y_true"].mean()  # class balance within this subgroup —
                                       # a skewed rate here can explain an
                                       # F1/AUROC gap without the model
                                       # actually treating the group worse
        if len(g) < 10 or g["y_true"].nunique() < 2:
            f1 = f1_score(g["y_true"], g["y_pred"], average="macro")
            print(f"  {val}: n={len(g)}  PD rate={pd_rate:.2f} — too few / single-class, "
                  f"AUROC skipped (F1={f1:.3f})")
            rows.append({"group": str(val), "n": len(g), "pd_rate": round(pd_rate, 3),
                        "f1": round(f1, 3), "auroc": None})
            continue
        f1    = f1_score(g["y_true"], g["y_pred"], average="macro")
        auroc = roc_auc_score(g["y_true"], g["y_prob"])
        print(f"  {val}: n={len(g)}  PD rate={pd_rate:.2f}  F1={f1:.3f}  AUROC={auroc:.3f}")
        rows.append({"group": str(val), "n": len(g), "pd_rate": round(pd_rate, 3),
                    "f1": round(f1, 3), "auroc": round(auroc, 3)})
    return pd.DataFrame(rows)

fairness_results = {col: subgroup_report(test_df, col)
                    for col in ["gender", "handedness", "age_group"]}

# %% Cell 6 — Robust fairness audit via 5-fold pooled out-of-fold predictions
#
# The audit above uses only the one held-out test split (54 subjects) --
# small enough that a subgroup like left-handed can end up single-class by
# chance (as it did). Pooling out-of-fold predictions across a 5-fold
# StratifiedGroupKFold gives fairness statistics over the *entire* dataset
# (every subject evaluated exactly once) instead of one small slice.
#
# Uses float32 predictions per fold rather than re-quantizing 5 separate
# INT8 models -- quantization cost was already shown to be small (-0.010
# F1 above), so this is a reasonable proxy for what the deployed model
# would do across the full population.
from sklearn.model_selection import StratifiedGroupKFold

gkf = StratifiedGroupKFold(n_splits=5)
oof_subj, oof_true, oof_pred, oof_prob = [], [], [], []

for fold, (tr, te) in enumerate(gkf.split(X_raw, y_raw, subj_raw)):
    fold_counts = np.bincount(y_raw[tr])
    fold_class_weight = {0: len(y_raw[tr]) / (2 * fold_counts[0]),
                         1: len(y_raw[tr]) / (2 * fold_counts[1])}

    fold_model = build_cnn1d(seq_len=X_raw.shape[1])
    fold_model.compile(optimizer="adam",
                       loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                       metrics=["accuracy"])
    fold_model.fit(X_raw[tr], y_raw[tr], epochs=40, batch_size=64,
                   class_weight=fold_class_weight, verbose=0)

    fold_logits = fold_model.predict(X_raw[te], verbose=0)
    fold_probs  = tf.nn.softmax(fold_logits, axis=1).numpy()[:, 1]
    fold_preds  = fold_logits.argmax(axis=1)

    fold_f1 = f1_score(y_raw[te], fold_preds, average="macro")
    print(f"Fold {fold + 1}/5 — F1={fold_f1:.3f}")

    oof_subj.extend(subj_raw[te])
    oof_true.extend(y_raw[te])
    oof_pred.extend(fold_preds)
    oof_prob.extend(fold_probs)

pooled_df = pd.DataFrame({
    "subject_id": oof_subj,
    "y_true":     oof_true,
    "y_pred":     oof_pred,
    "y_prob":     oof_prob,
}).merge(demo_df, on="subject_id", how="left")

pooled_df["age_group"] = pd.cut(pooled_df["age"], bins=[0, 55, 70, 200],
                                labels=["<55", "55-70", "70+"])

print(f"\nPooled out-of-fold predictions: {len(pooled_df)} windows, "
      f"{pooled_df['subject_id'].nunique()} subjects")

pooled_fairness_results = {col: subgroup_report(pooled_df, col)
                           for col in ["gender", "handedness", "age_group"]}

# %% Cell 7 — Save results
summary = {
    "float32": {"f1": round(float_f1, 3), "auroc": round(float_auroc, 3)},
    "int8":    {"f1": round(int8_f1, 3), "auroc": round(int8_auroc, 3)},
    "tflite_size_kb": round(TFLITE_PATH.stat().st_size / 1024, 1),
    "fairness_single_split":     {k: v.to_dict("records") for k, v in fairness_results.items()},
    "fairness_pooled_5fold_oof": {k: v.to_dict("records") for k, v in pooled_fairness_results.items()},
}
summary_path = OUT_DIR / "d3_tflite_fairness_summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved -> {summary_path}")
print(f"Saved -> {TFLITE_PATH}  (download this for the local latency benchmark)")
