# PD-Glove · Part II — ML Pipeline (CS 8674)

Model-training, validation, and system-integration work for **Part II** of the
Sensing-to-Decision framework. This folder is self-contained: code, data, docs, and
generated results all live under `part2-ml/`.

> **Status (2026-07-19):** Deliverable 2 **complete** — three D2 notebooks verified on Kaggle
> (GPU T4), report written at `docs/D2_report.md`. Key results: SVM macro-F1 0.564 / AUROC 0.693
> on PADS (best baseline); MOMENT linear probe F1 0.502 (frozen encoder insufficient, expected).
> **D3 starts next** — on-device latency + fairness audit.

## Layout

```
part2-ml/
├── notebooks/
│   ├── Dataset_Pipeline.ipynb              # D1: load · clean · subject-split · EDA
│   ├── Unimodal_Classifiers.ipynb          # D1: SVM · RF · 1D-CNN baselines
│   ├── D2_PADS_Pipeline.py                 # D2: PADS cleaning + feature extraction
│   ├── D2_PADS_Baseline_Classifiers.py     # D2: SVM · RF · CNN on PADS
│   ├── D2_PADS_Transformer_MOMENT.py       # D2: MOMENT fine-tuning on PADS
│   └── *.py                                # jupytext source (version-controlled)
├── scripts/
│   └── organize_data.py              # verify/unzip/organize a pasted data folder
├── data/                             # datasets (gitignored; READMEs tracked) — see data/README.md
│   ├── alameda/  daphnet/  ppmi/  pad/  glove/
├── results/                          # generated: cleaned/ eda/ figures/ metrics/ (gitignored)
├── docs/
│   ├── unified-feature-schema.md     # the one schema; feature/label roles per task
│   ├── D1_report_outline.md          # report skeleton with the actual baseline numbers
│   ├── D1_report.md                  # final D1 report (figures embedded)
│   ├── D2_report.md                  # final D2 report — PADS pipeline + MOMENT results
│   └── figures/                      # report figures committed here (results/ is gitignored)
├── aws_setup.md                      # S3 bucket layout, IAM policy, EC2 config
├── requirements.txt
├── literature-review.md              # 20-paper annotated review (done)
├── next-steps.md                     # plain-English plan + week-by-week timeline
└── professor-meeting.md
```

## Deliverable 2 — PADS + MOMENT (complete)

Three notebooks, all run on Kaggle (GPU T4):

1. **`D2_PADS_Pipeline.py`** — loads PADS PhysioNet dataset (469 subjects, wrist acc+gyro 100 Hz), excludes DD group, extracts 42 features (7 × 6 channels), subject-level splits. Saves `pads_all.parquet`, `pads_raw_windows.npz`, train/val/test splits.
2. **`D2_PADS_Baseline_Classifiers.py`** — SVM, Random Forest, 1D-CNN on PADS for PD vs HC classification (5-fold subject-grouped CV). Saves `pads_baseline_metrics.json`.
3. **`D2_PADS_Transformer_MOMENT.py`** — fine-tunes MOMENT-1-large (CMU time series foundation model) on PADS raw windows. Linear probing (freeze_encoder=True). Resample 1024→512 samples via F.interpolate.

### D2 Results (PADS, 276 PD / 79 HC, 10,318 windows)

| Model | Macro-F1 | AUROC |
|---|---|---|
| SVM | **0.564 ± 0.023** | 0.693 ± 0.018 |
| Random Forest | 0.498 ± 0.011 | **0.726 ± 0.014** |
| 1D-CNN | 0.562 ± 0.039 | 0.700 ± 0.031 |
| MOMENT (linear probe) | 0.502 ± 0.012 | 0.622 ± 0.012 |

SVM is the strongest classifier for fixed-threshold deployment (Pi). Random Forest has the best AUROC for risk ranking. MOMENT linear probing does not improve over SVM — frozen encoder representations do not adapt to PD wrist kinematics without full fine-tuning.

Full write-up at `docs/D2_report.md`.

---

## Deliverable 1 — what it produces

Two notebooks, both reproducible on Kaggle (free GPU) or locally:

1. **`Dataset_Pipeline.ipynb`** — loads ALAMEDA, Daphnet, PPMI Part III + Demographics
   (+ Roche), and the glove DSP data; cleans; makes **leakage-safe subject-level splits**
   (with an assertion); documents the unified feature schema; runs EDA (figures →
   `results/eda/`); writes cleaned parquet → `results/cleaned/`; optional S3 upload.
2. **`Unimodal_Classifiers.ipynb`** — **SVM, Random Forest, 1D-CNN** for the
   tremor/bradykinesia task (ALAMEDA) and the FOG task (Daphnet). **Subject-grouped K-fold
   CV** (mean ± std macro-F1 / AUROC), confusion matrices, RF feature importance →
   `results/figures/`, `results/metrics/`.

### Verified results (full local run, all four datasets)

| Item | Result |
|---|---|
| FOG (Daphnet) — best baseline | **RandomForest, macro-F1 0.61 ± 0.08, AUROC 0.90 ± 0.06** (clears Bächlin 73/82 floor) |
| Tremor presence (ALAMEDA) — best baseline | RF/SVM macro-F1 ~0.4–0.6, **AUROC ~0.45–0.54 ≈ chance cross-subject** |
| PPMI Part III | 38,226 rows / 5,157 patients → leakage-safe `PATNO` split 3609/774/774 |
| Roche v2 | long-format, **32 patients, no `EVENT_ID`** → pivoted to 32×131 per-patient features ⚠ |

ALAMEDA tremor does **not** generalize across its 11 subjects with pre-extracted features
— a real finding that motivates D2's raw-signal per-finger Transformer (see
`docs/D1_report_outline.md` §5).

> ⚠ **Roche/`EVENT_ID` discrepancy:** the syllabus says join Part III + Roche on
> `PATNO`+`EVENT_ID`, but the real Roche v2 export has no `EVENT_ID` and only 32 patients.
> Handled as a separate per-patient digital-feature table joined on `PATNO`; flagged for
> the instructor. Details in `docs/unified-feature-schema.md`.

---

## How to run on Kaggle (recommended path)

1. **Stage data as a Kaggle Dataset.** Create a *private* Kaggle Dataset and upload the
   contents of `part2-ml/data/` (ALAMEDA csv, the Daphnet `dataset/` folder, and the PPMI
   CSVs). Keep it **private** — PPMI is DUA-restricted.
2. **New Kaggle Notebook** → *Add Input* → attach that dataset. Upload
   `Dataset_Pipeline.ipynb`. Accelerator = **None** for the pipeline; **GPU T4** when you
   run the 1D-CNN in the classifiers notebook.
3. **Run `Dataset_Pipeline.ipynb`.** Paths auto-detect under `/kaggle/input` — no edits
   needed. Cleaned files land in `/kaggle/working/cleaned`. Confirm the leakage assertion
   passes and the EDA figures look right.
4. **Run `Unimodal_Classifiers.ipynb`** in the same session (it reads
   `/kaggle/working/cleaned`). Torch is preinstalled, so the 1D-CNN runs here.
5. **(Optional) S3 upload.** Add AWS keys as Kaggle *Secrets* and uncomment the upload
   cell — see `aws_setup.md`.
6. **Commit notebooks** to GitHub (`aqn96/pd-glove`) and write the report from
   `docs/D1_report_outline.md`.

## How to run locally

```bash
cd part2-ml
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) stage data (paste a folder/zip anywhere, then organize it)
python scripts/organize_data.py /path/to/pasted_folder    # or --verify

# 2) run the pipeline, then the baselines
python notebooks/Dataset_Pipeline.py
python notebooks/Unimodal_Classifiers.py

# results in results/{cleaned,eda,figures,metrics}/
```

The `.py` files are the canonical source (jupytext "percent" format); regenerate the
`.ipynb` with `jupytext --to ipynb notebooks/*.py`.

## Datasets

All four are staged and verified under `part2-ml/data/` — see
[`data/README.md`](data/README.md) for layout and the `organize_data.py` stager/verifier.
ALAMEDA (Zenodo) and Daphnet (UCI) are open; **PPMI Part III / Demographics / Roche are
DUA-restricted** (LONI IDA) and gitignored. Run `python scripts/organize_data.py --verify`
to confirm integrity (ALAMEDA md5 matches Zenodo; 17 Daphnet sessions; PPMI present).

## Where this is going (D2–D4)

`next-steps.md` has the full week-by-week plan. In short:

- **D2 (complete):** PADS pipeline + SVM/RF/CNN/MOMENT baselines on PD vs HC. Best: SVM F1=0.564. Full fine-tuning of MOMENT (freeze_encoder=False) in progress.
- **D3 (due Aug 4):** On-device latency benchmark (TFLite INT8 on Pi) + fairness audit (handedness, severity subgroups using PPMI).
- **D4 (due Aug 16):** Final report + clean repo + 15-min talk + live demo.
