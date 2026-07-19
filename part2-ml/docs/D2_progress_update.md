# CS 8674 Part II — Progress Update & Amended Plan
**An Nguyen · Northeastern University Khoury College · July 19, 2026**

This document summarizes what was completed, what changed from the original syllabus, and why. It accompanies the D2 report submission.

---

## Deliverable 1 — Dataset Pipeline & Baseline Classifiers (complete)

**Original scope:** PPMI + ALAMEDA + Daphnet + Roche cleaned and uploaded to S3; SVM/RF/1D-CNN baselines for tremor and FOG; 3–5 page report.

**What was done:**
- PPMI Part III + Demographics + Roche PD App v2 downloaded, cleaned, and joined on PATNO (Roche has no EVENT_ID — flagged)
- ALAMEDA feature extraction reproduced; feature schema aligned to glove DSP output
- Daphnet FOG dataset loaded, windowed (4s, 50% overlap), 63 features extracted
- Baseline classifiers trained and evaluated (5-fold subject-grouped CV):

| Task | Model | Macro-F1 | AUROC |
|---|---|---|---|
| Tremor (ALAMEDA) | SVM | 0.510 ± 0.054 | 0.572 ± 0.082 |
| Tremor (ALAMEDA) | Random Forest | 0.453 ± 0.126 | 0.553 ± 0.067 |
| FOG (Daphnet) | SVM | 0.596 ± 0.118 | 0.875 ± 0.069 |
| FOG (Daphnet) | Random Forest | 0.570 ± 0.104 | 0.891 ± 0.070 |
| FOG (Daphnet) | 1D-CNN | 0.785 | 0.951 |

**What changed:**
- AWS S3 upload not completed — school account access was not available. All data and outputs stored on Kaggle instead.
- PPMI/Roche join used PATNO only (no EVENT_ID in actual Roche export).

**Key finding:** ALAMEDA tremor detection is near-chance cross-subject (AUROC ~0.57). This is because ALAMEDA provides pre-computed session-average features, not raw moment-to-moment signals. The model learns a patient's general movement profile rather than detecting tremor onset. This directly motivated the PADS dataset pivot in D2.

**Report:** `docs/D1_report.md`

---

## Deliverable 2 — Transformer Training & Evaluation (complete with modifications)

**Original scope:** Transformer encoder for tremor/bradykinesia trained on ALAMEDA + glove augmented data; separate FOG Transformer on Daphnet + mPower; ablation study (per-finger vs. single-wrist); TFLite INT8 quantization; uncertainty-aware scoring; 8–10 page report.

**What changed and why:**

| Original Plan | What Actually Happened | Reason |
|---|---|---|
| Fine-tune Transformer on augmented glove data (9 sessions → ~8k windows) | Not done | IRB approval pending — cannot collect labeled data from human subjects |
| Pretrain on ALAMEDA | Switched to PADS dataset | ALAMEDA has no raw signal — only pre-computed features, not usable for Transformer pre-training |
| Separate FOG Transformer on Daphnet + mPower | Not done | FOG uses ankle/thigh/hip sensors — irrelevant to glove hardware (hand/fingers) |
| mPower auxiliary gait input | Not done | mPower access requires Synapse application approval; not yet granted |
| Per-finger vs. single-wrist ablation | Not done | Requires labeled glove recordings — blocked by IRB |
| TFLite INT8 quantization | Moved to D3 | Logical to benchmark after final model is selected |
| Uncertainty-aware scoring | Deferred | Lower priority given IRB blocker |
| AWS EC2 + S3 artifact storage | Not done | School account access unavailable |

**What was done instead:**

The D2 work pivoted to the PADS dataset (Parkinson's Disease Smartwatch Dataset, PhysioNet) — 276 PD and 79 HC subjects, bilateral wrist accelerometer + gyroscope at 100 Hz, same sensor axes as the glove's MPU-6050 IMUs. This is the most sensor-compatible public dataset available and serves as the pre-training foundation for glove fine-tuning once IRB approval is granted.

**Stage 1 — PADS baselines (extended D1 on a better dataset):**

Same SVM/RF/CNN pipeline rerun on PADS for PD vs HC classification:

| Model | Macro-F1 | AUROC |
|---|---|---|
| SVM | **0.564 ± 0.023** | 0.693 ± 0.021 |
| Random Forest | 0.498 ± 0.011 | **0.726 ± 0.020** |
| 1D-CNN | 0.565 ± 0.022 | 0.702 ± 0.022 |

**Stage 2 — MOMENT Transformer fine-tuning (D2 core contribution):**

MOMENT-1-large (Yi et al., 2024 — CMU open-source time series foundation model) fine-tuned on PADS raw windows (974 samples, 6 channels, resampled to 512 for MOMENT's fixed sequence length).

- **V3 (linear probing, freeze_encoder=True):** F1=0.502 ± 0.012, AUROC=0.622 ± 0.012
- **V4 (full fine-tuning, freeze_encoder=False):** currently running on Kaggle T4 GPU

Linear probing result is below SVM, which is expected — a frozen encoder pre-trained on general time series cannot adapt to PD wrist kinematics without updating its weights. Full fine-tuning results will be added to the report once V4 completes.

**Notebooks:** `pd-glove-d2-pads-pipeline`, `pd-glove-d2-pads-baseline-classifiers`, `pd-glove-d2-pads-transformer-moment` (all on Kaggle, source in `part2-ml/notebooks/`)

**Report:** `docs/D2_report.md`

---

## Deliverable 3 — Edge Deployment & Pipeline Integration (due August 4)

**Original scope:** TFLite latency benchmark; MQTT with AES-256-GCM + TLS 1.3; MediaPipe Hand Landmarker compliance module; fairness audit across PPMI demographics.

**Current plan:**
- TFLite INT8 quantization of SVM or CNN — convert trained model, simulate latency on laptop (Pi not currently accessible)
- Explore merging additional public datasets (Oday, PD-BioStampRC21) into existing baselines
- Fairness audit using PPMI demographic splits (age, sex, disease stage, handedness)
- MQTT and MediaPipe modules deferred if time constrained — will note in D3 report

**What's blocked:**
- Pi hardware not currently accessible for live latency benchmark — will use software simulation
- AWS EC2 for MQTT broker not available

---

## Deliverable 4 — Final Report, Presentation & Demo (due August 16)

No changes to scope. Will incorporate D2 full fine-tuning results once V4 completes.

---

## Summary of blockers

| Blocker | Impact | Status |
|---|---|---|
| IRB approval pending | Cannot collect labeled glove recordings; glove fine-tuning and per-finger ablation blocked | Submitted, awaiting approval |
| mPower Synapse access | Could not incorporate mPower gait data | Application not yet approved |
| AWS school account unavailable | All compute on Kaggle; no S3 artifact storage | Using Kaggle private datasets as substitute |
| Pi hardware away | Cannot benchmark live latency on Pi | Will simulate on laptop for D3 |
