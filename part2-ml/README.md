# PD-Glove · Part II — ML Pipeline (CS 8674)

Model-training, validation, and system-integration work for **Part II** of the
Sensing-to-Decision framework. This folder is self-contained: code, data, docs, and
generated results all live under `part2-ml/`.

> **Status (2026-06-08):** Deliverable 1 (Dataset Pipeline & Baseline Classifiers, due
> **Jun 16**) — code **complete and verified end-to-end on all four datasets**
> (ALAMEDA, Daphnet, PPMI Part III, Roche). All data staged and verified under
> `part2-ml/data/`. Remaining for D1: run on Kaggle, optional S3 upload, write the report.

## Layout

```
part2-ml/
├── notebooks/
│   ├── Dataset_Pipeline.ipynb        # load · clean · subject-split · unified schema · EDA · S3
│   ├── Unimodal_Classifiers.ipynb    # SVM · RF · 1D-CNN baselines (subject-grouped CV)
│   └── *.py                          # jupytext source of the notebooks (version-controlled)
├── scripts/
│   └── organize_data.py              # verify/unzip/organize a pasted data folder
├── data/                             # datasets (gitignored; READMEs tracked) — see data/README.md
│   ├── alameda/  daphnet/  ppmi/  glove/
├── results/                          # generated: cleaned/ eda/ figures/ metrics/ (gitignored)
├── docs/
│   ├── unified-feature-schema.md     # the one schema; feature/label roles per task
│   └── D1_report_outline.md          # report skeleton with the actual baseline numbers
├── aws_setup.md                      # S3 bucket layout, IAM policy, EC2 config
├── requirements.txt
├── literature-review.md              # 20-paper annotated review (done)
├── next-steps.md                     # plain-English plan + week-by-week timeline
└── professor-meeting.md
```

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

`next-steps.md` has the full week-by-week plan. In short: D2 = per-finger Transformer
encoder + INT8 TFLite + uncertainty; D3 = MQTT (AES-256-GCM/TLS 1.3) + MediaPipe
compliance + fairness audit; D4 = final report + demo.
