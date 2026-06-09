# Deliverable 1 — Technical Report (3–5 pages) · Outline + Results

Drop-in skeleton for the D1 report. Numbers below are the **actual** outputs from the
notebooks on ALAMEDA + Daphnet (PPMI section fills in once those CSVs are staged).
Figures are in `results/figures/` and `results/eda/`.

---

## 1. Introduction (½ page)
- Goal: curate/join D1 datasets, build a unified schema, benchmark SVM/RF/1D-CNN on two
  tasks (tremor/bradykinesia, FOG) as the baseline the D2 Transformer must beat.
- One-paragraph framing from `next-steps.md` §4.10 (class rebalancing matters; RF/SVM are
  strong on small cohorts; subject-level splits are non-negotiable).

## 2. Datasets & pipeline (1 page)
- Table: the four datasets, roles (feature vs label vs fairness), sizes, group keys —
  copy from `docs/unified-feature-schema.md`.
- The clinical-anchor asymmetry: PPMI = labels, no waveforms; ALAMEDA/Daphnet/glove =
  features. State it explicitly (graders look for this).
- Joins: PPMI Part III ⋈ Roche on `PATNO`+`EVENT_ID`; Demographics on `PATNO`.
- **Leakage-safe splits:** subject-grouped; assertion in `Dataset_Pipeline.ipynb`.
  Explain why CV (GroupKFold) is used for ALAMEDA (11 subjects, near-constant per-subject
  labels → single 2-subject test fold is unstable).

## 3. EDA (½–1 page) — figures
- `results/eda/alameda_label_balance.png` — label positive rates:
  Constancy_of_rest 0.76, Rest_tremor 0.38, Postural 0.21, Kinetic 0.04 (imbalanced →
  macro-F1, not accuracy).
- `results/eda/alameda_dom_freq.png` — dominant frequency clusters in the 4–6 Hz PD band
  (sanity check that the band-pass/FFT features are physiologically meaningful).
- `results/eda/daphnet_fog_per_subject.png` — FOG rate varies widely by subject
  (some subjects barely freeze) → motivates subject-grouped evaluation.
- Counts: ALAMEDA 4151 windows / 11 subjects; Daphnet 8895 windows / 10 subjects,
  FOG positive rate 9.6 %.

## 4. Baseline classifiers (1–1.5 pages)
Subject-grouped 5-fold CV (mean ± std); 1D-CNN on held-out test split.

### Tremor / bradykinesia (ALAMEDA)
| Label | Model | macro-F1 | AUROC |
|---|---|---|---|
| Rest_tremor | SVM | 0.44 ± 0.09 | 0.52 |
| Rest_tremor | RandomForest | 0.39 ± 0.11 | 0.45 |
| Postural_tremor | RandomForest | 0.45 ± 0.05 | 0.45 |
| Kinetic_tremor | RandomForest | 0.62 ± 0.22 | n/a (rare class) |
| Constancy_of_rest | SVM | 0.43 ± 0.04 | 0.54 |

### Freezing of gait (Daphnet)
| Model | macro-F1 | AUROC |
|---|---|---|
| SVM | 0.60 ± 0.12 | 0.88 ± 0.07 |
| **RandomForest** | **0.61 ± 0.08** | **0.90 ± 0.06** |
| 1D-CNN (raw windows) | *(run on Kaggle GPU — torch)* | |

- Confusion matrices: `results/figures/cm_*`.
- Feature importance: `results/figures/fi_fog_FOG.png` (Bächlin freeze-index features
  dominate — physiologically sensible) and `fi_tremor_Rest_tremor.png`.

## 5. Discussion / error analysis (½–1 page)
- **FOG is learnable cross-subject** (AUROC 0.90 ≥ Bächlin 73/82 floor); freeze-index
  features carry the signal — validates the engineered-feature design.
- **ALAMEDA tremor does *not* generalize across subjects** (AUROC ≈ 0.45–0.54, near
  chance). This is the key finding: with 11 subjects and near-constant per-subject labels,
  pre-extracted features capture subject identity more than tremor state. Matches
  Rodriguez 2024 (per-subject calibration / rebalancing is decisive) and motivates D2:
  per-finger raw-signal Transformer + PRIMUS-style pretraining rather than tabular feats.
- Imbalance handling (`class_weight="balanced"`) and macro-F1 reporting; note Kinetic
  tremor (4 % positive) is too rare for stable AUROC.
- Limitations: ALAMEDA 1D-CNN runs on a feature vector (not raw signal) — unconventional,
  flagged.

## 6. Conclusion + next steps (¼ page)
- Best baselines (the D2 bar to beat): **FOG = RF, macro-F1 0.61 / AUROC 0.90**;
  **tremor = essentially chance cross-subject** → D2 must add raw-signal modeling.
- All cleaned datasets in S3 (`deliverable1/cleaned/`); notebooks reproducible on Kaggle.

## Citations to include
Xing 2022 (RF ceiling), Rodriguez 2024 (SVM + rebalancing), Atri 2022 (1D-CNN),
Bächlin 2010 (Daphnet + freeze-index floor), Paucar-Escalante 2025 (baseline-choice /
leakage). See `literature-review.md`.
