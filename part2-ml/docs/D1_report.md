# Deliverable 1: Dataset Pipeline & Baseline Classifiers
**CS 8674 Part II — Intelligent IoT Frameworks for Chronic Disease Management**
An Nguyen · Northeastern University Khoury College · June 2026

---

## 1. Introduction

This report documents the dataset pipeline and baseline classifier benchmarks for
Deliverable 1 of the PD-Glove ML project. Four Parkinson's disease datasets were
cleaned, split, and analyzed: ALAMEDA tremor, Daphnet FOG, PPMI Part III with
Demographics, and the Roche PD Monitoring App v2. Three baseline models — SVM,
Random Forest (RF), and 1D-CNN — were evaluated on tremor/bradykinesia detection and
freezing of gait (FOG) detection. These baselines set the performance floor that the
Deliverable 2 Transformer must exceed. All code is reproducible on Kaggle and
committed to `github.com/aqn96/pd-glove` under `part2-ml/notebooks/`.

---

## 2. Datasets and Pipeline

**Table 1: Dataset summary**

| Dataset | Task role | Size | Group key |
|---|---|---|---|
| ALAMEDA | Feature source + tremor labels | 4,151 windows / 11 subjects | `subject_id` |
| Daphnet | Feature source + FOG labels | 8,895 windows / 10 subjects | `subject` |
| PPMI Part III + Demographics | Clinical anchor / fairness cohort | 36,050 visits / 5,157 patients | `PATNO` |
| Roche PD App v2 | Digital sub-study features | 32 patients / 130 features | `PATNO` |

All datasets are split 70/15/15 at the **subject level** using `GroupShuffleSplit` —
no patient appears in more than one partition. A runtime assertion in
`Dataset_Pipeline.ipynb` verifies zero subject overlap across splits. PPMI splits
are 3,609 / 774 / 774 patients.

Daphnet raw recordings (64 Hz, 9-axis) were segmented into 4-second windows (256
samples, 50% overlap) and 54 time- and frequency-domain features were extracted per
window, including the Bächlin freeze index (power ratio 3–8 Hz / 0.5–3 Hz) per
channel [1]. ALAMEDA provides 92 pre-extracted accelerometer features per window,
labeled with four binary tremor scores. Both feature sets were aligned to the glove's
unified DSP schema (`dominant_freq_hz`, `dominant_amp`, `band_power` per channel).

> ⚠️ **Roche join-key discrepancy:** the syllabus specifies joining Part III and
> Roche on `PATNO`+`EVENT_ID`, but the actual Roche v2 export has no `EVENT_ID`
> column and covers only 32 patients in a long-format digital sub-study. It was
> handled as a per-patient feature table (32 × 130) joined on `PATNO` only and saved
> separately. This has been flagged for instructor clarification.

---

## 3. Exploratory Data Analysis

---
> 📊 **[INSERT FIGURE HERE]**
> File: `results/eda/alameda_label_balance.png`
> Caption: **Figure 1.** ALAMEDA tremor label positive rates across 4,151 windows.
> `Constancy_of_rest` (76%) and `Rest_tremor` (38%) are the most frequent; `Kinetic_tremor`
> (4%) is severely imbalanced, motivating macro-F1 rather than accuracy as the primary metric.
---

---
> 📊 **[INSERT FIGURE HERE]**
> File: `results/eda/daphnet_fog_per_subject.png`
> Caption: **Figure 2.** Per-subject FOG window rate in Daphnet. Freeze prevalence
> varies widely across subjects, motivating subject-grouped cross-validation.
---

ALAMEDA label rates: `Constancy_of_rest` 76%, `Rest_tremor` 38%, `Postural_tremor`
21%, `Kinetic_tremor` 4%. The `alameda_dom_freq.png` EDA figure confirms tremor-positive
windows cluster in the 4–6 Hz Parkinsonian band, validating the FFT feature design.
Daphnet FOG positive rate is 9.6% overall, with high subject-level variance (Figure 2).
PPMI Hoehn & Yahr distribution: stage 1 = 4,841 visits, stage 2 = 14,837, stage 3 = 1,302,
stage 4 = 285 — providing a broad severity range for the D3 fairness audit.

---

## 4. Baseline Classifiers

Subject-grouped 5-fold CV (`GroupKFold`) was used for SVM and RF: every subject is
held out exactly once, and mean ± std macro-F1 / AUROC are reported. The 1D-CNN is
evaluated on the held-out test split. Class imbalance is handled with
`class_weight="balanced"` (SVM/RF) and inverse-frequency weighted loss (CNN).

### Task 1 — Tremor and bradykinesia (ALAMEDA)

**Table 2: ALAMEDA tremor baselines**

| Label | Model | macro-F1 | AUROC |
|---|---|---|---|
| Rest_tremor | SVM | 0.44 ± 0.09 | 0.52 ± 0.09 |
| Rest_tremor | RandomForest | 0.39 ± 0.11 | 0.45 ± 0.10 |
| Postural_tremor | SVM | 0.43 ± 0.02 | 0.44 ± 0.05 |
| Postural_tremor | RandomForest | 0.45 ± 0.05 | 0.45 ± 0.03 |
| Constancy_of_rest | SVM | 0.43 ± 0.04 | 0.54 ± 0.10 |
| Constancy_of_rest | RandomForest | 0.41 ± 0.10 | 0.49 ± 0.07 |
| Constancy_of_rest | 1D-CNN | 0.43 | 0.39 |

### Task 2 — Freezing of gait (Daphnet)

**Table 3: Daphnet FOG baselines**

| Model | macro-F1 | AUROC |
|---|---|---|
| SVM | 0.60 ± 0.12 | 0.88 ± 0.07 |
| RandomForest | **0.61 ± 0.08** | **0.90 ± 0.06** |
| 1D-CNN (raw windows) | **0.79** | **0.95** |

---
> 📊 **[INSERT FIGURE HERE]**
> File: `results/figures/fi_fog_FOG.png`
> Caption: **Figure 3.** RF feature importance for FOG detection (top 20 features).
> Freeze-index features dominate, confirming Bächlin's frequency-based heuristic
> captures the true freeze signal.
---

---
> 📊 **[INSERT FIGURE HERE]**
> File: `results/figures/cm_fog_FOG_RandomForest.png`
> Caption: **Figure 4.** Out-of-fold confusion matrix for RF on Daphnet FOG.
---

---

## 5. Discussion and Conclusion

**FOG is learnable cross-subject.** RF achieves AUROC = 0.90, clearing the Bächlin
73/82 floor [1]. The 1D-CNN on raw 9-channel windows reaches AUROC = 0.95,
demonstrating that raw-signal models outperform hand-engineered features on this task.
Feature importance confirms the freeze index is the dominant signal.

**Tremor does not generalize cross-subject with tabular features.** All ALAMEDA AUROC
values fall at 0.39–0.54 — indistinguishable from chance. With only 11 subjects whose
tremor labels are near-constant per person, pre-extracted features capture *subject
identity* rather than *tremor state*, matching Rodriguez et al. [4]. This is the
primary finding of D1 and directly motivates D2: a per-finger raw-signal Transformer
with PRIMUS-style pretraining [3] will learn the within-subject temporal dynamics
that tabular features cannot represent.

**Baselines to beat in D2:**

| Task | Best baseline | macro-F1 | AUROC |
|---|---|---|---|
| FOG (Daphnet) | 1D-CNN raw | 0.79 | 0.95 |
| Tremor (ALAMEDA) | SVM | 0.44 | 0.52 (≈ chance) |

---

## References

[1] Bächlin et al. (2010). Wearable assistant for PD patients with freezing of gait.
*IEEE Trans. Information Technology in Biomedicine*, 14(2), 436–446.

[2] Atri et al. (2022). 1D-CNN based deep learning for IoT sensor classification.
*IEEE ISCC*.

[3] Das et al. (2024). PRIMUS: Pretraining IMU encoders with multimodal
self-supervision. *arXiv:2411.15127*.

[4] Rodriguez et al. (2024). Cross-subject tremor classification.
*IEEE J. Biomedical and Health Informatics*.

[5] Xing et al. (2022). Distinguishing PD from essential tremor using wrist
accelerometry. *IEEE Trans. Neural Systems and Rehabilitation Engineering*.
