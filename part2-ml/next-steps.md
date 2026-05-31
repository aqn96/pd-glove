# Part II: Next Steps and Timeline

**Course:** CS 8674 Part II — Intelligent IoT Frameworks for Chronic Disease Management (Summer 2026)
**Instructor:** Sarita Singh
**As of:** 2026-05-31 (end of Week 2 per syllabus)
**Companion doc:** [literature-review.md](literature-review.md)

This document translates the syllabus into a concrete week-by-week execution plan, calibrated to where the work actually stands today (the literature review just shipped; the technical pipeline has not started). It also gives an honest feasibility read against the existing PD-glove research base.

---

## 1. Current position (2026-05-31)

| Syllabus phase | Status |
|---|---|
| Pre-Planning P1 (Apr 26 – May 6) — Transformer/MDS-UPDRS reading | Likely covered by AIIoT 2026 paper preparation |
| Pre-Planning P2 (May 7 – May 13) — PPMI dictionary, mPower, Daphnet, VGRF, MediaPipe docs | Partially covered by the literature review (Bot, Bachlin, Güney) |
| Pre-Planning P3 (May 14 – May 18) — dataset downloads, AWS S3 + IAM, Kaggle env | **Not done** |
| Week 1 (May 19 – May 25) — PPMI + Roche joins, splits, Daphnet EDA | **Not done** |
| Week 2 (May 26 – Jun 1) — ALAMEDA alignment, unified schema, S3 upload | **In progress (today is the last weekend)** |

**Net position:** ~1.5 weeks of technical work has been deferred while the literature review was completed. D1 is in 16 days. This is recoverable but the gating risk is **dataset-access lead time** — LONI/PPMI and Synapse/mPower approvals can take days, and they have to start today.

---

## 2. Feasibility verdict

**Overall: Feasible, but tight on D1, with three named risks.**

**Why feasible:**
- The course is 100% software/cloud; no hardware blockers (the Pi 5 glove is back in the lab and the syllabus explicitly says no hardware access is required).
- D2–D3 architecture (per-finger Transformer encoder, INT8 TFLite, MQTT + MediaPipe compliance) is already the architecture targeted in the AIIoT 2026 paper, so no design pivot is needed.
- The literature review has already cited the canonical method paper for every D1–D3 component (see §3).

**Why tight:**
- **R1 — Dataset access lead time.** PPMI is gated by an LONI Data Use Agreement and per-collection approval; mPower (Synapse) requires a separate qualified-researcher application. These can take 3–10 days each. They have to start **today or Monday**. If either slips past Jun 7, the Week 3 baseline work compresses into Week 4.
- **R2 — Local validation cohort is small.** `tremor_validation_master.csv` is 9 sessions / 2 subjects. End-to-end Transformer training will not work on this base alone — D2 hinges on either PPMI/Roche IMU data being usable as supervised signal *or* the PRIMUS-style pretraining + fine-tune recipe (Das et al. 2024, entry 5 of the lit review). Plan for both.
- **R3 — AWS GPU quota.** School AWS accounts often cap GPU instances; `p3.2xlarge` may require a quota increase ticket. Verify in Pre-Planning catch-up.

**Mitigations are in §8.**

---

## 3. Alignment check: literature review ↔ Part II deliverables

The lit review is intentionally — and verifiably — aligned with the syllabus deliverables. Direct mapping:

| Syllabus item | Lit review entries supporting it |
|---|---|
| D1 baselines (SVM, RF, 1D-CNN) | Xing et al. 2022 (RF/XGBoost ceiling), Rodriguez et al. 2024 (SVM free-living), Atri et al. 2022 (1D-CNN canonical) |
| D1 Daphnet FOG baseline | Bachlin et al. 2010 (dataset paper + threshold baseline) |
| D2 Transformer architecture | Králik & Šuppa 2021 (WaveGlove — direct architecture donor) |
| D2 pretraining recipe (small labeled base) | Das et al. 2024 (PRIMUS) |
| D2 ordinal MDS-UPDRS severity | Liu et al. 2023 (video MDS-UPDRS ceiling), Duque-Quiceno et al. 2024 |
| D2 uncertainty / phenotype robustness fallback | Evers et al. 2025 (prototypical net) |
| D2 mPower auxiliary input | Bot et al. 2016 (mPower foundational paper) |
| D2 CARE-PD gait branch | Adeli et al. 2025 (CARE-PD release paper, MotionBERT baseline) |
| D2 differential PD-vs-ET / subclinical regime | Nanayakkara & Chan 2025, Xing et al. 2022 |
| D2 weak-label / session-level training | Papadopoulos et al. 2020 (MIL template) |
| D3 INT8 TFLite latency (gap claim) | Identified as the explicit research gap |
| D3 MediaPipe compliance module | Güney et al. 2022 (MediaPipe-vs-accelerometer validation) |
| D3 MQTT-only-derived-scores (gap claim) | Identified as the privacy-by-design gap |
| D3 fairness audit (PPMI + handedness) | Muhammad et al. 2026, Tumpa et al. 2025 |

Every syllabus deliverable has bibliographic backing. The Research Gap section's four claims (per-finger placement, calibrated MDS-UPDRS ordinal, INT8 TFLite latency on Pi 5, MQTT-only privacy) **are** D2–D3 reframed as contributions. The lit review is not a separate scholarly exercise — it is the framing document for the rest of the course.

---

## 4. Research synopsis: what the 20 papers actually tell you

The literature review is breadth-first, organized alphabetically by author. This section reorganizes it for action — what is settled, what is contested, which papers are templates, which are comparators, which are warnings, what to read first as each deliverable approaches, and how every finding maps back to the syllabus.

### 4.1 What the field has settled on

Findings that recur across multiple sources — treat as known good practice, not open questions.

- **Random Forest and XGBoost remain the strongest classical baselines on small-to-moderate tremor cohorts.** Xing et al. (2022) report >0.84 accuracy and >0.90 AUC for PD-vs-ET on 398 subjects; the CNN entry underperforms the gradient-boosted baselines. This is not a deep-learning failure — it is a cohort-size truth. *D1 implication: do not skip RF/XGBoost on the way to the Transformer.*
- **1D-CNN over wrist accelerometer is the canonical deep baseline.** Atri et al. (2022) defined the activity-gated 1D-CNN pattern that most subsequent wearable papers extend. *D1 implication: this is the third baseline the syllabus names — copy the architecture directly.*
- **Class rebalancing matters more than algorithm choice on small imbalanced data.** Rodriguez et al. (2024) reach 0.88 accuracy from a plain SVM by attending to rebalancing. *D1 implication: the single most actionable lesson for your cohort size; budget time for SMOTE / class-weight tuning before architecture tuning.*
- **MediaPipe-derived tremor frequency is accelerometer-grade for rest and postural tremor.** Güney et al. (2022) achieve 0.229 Hz mean absolute frequency error against simultaneous accelerometer ground truth. Kinetic-tremor regime degrades. *D3 implication: MediaPipe Hand Landmarker is validated for the compliance gating role; don't try to use it for primary scoring.*
- **The Daphnet freeze-band / locomotion-band ratio is a must-beat baseline for FOG.** Bachlin et al. (2010) reach ~73/82 sensitivity/specificity from a threshold rule. *D1 implication: any FOG model that does not exceed this on Daphnet has a defect somewhere in the pipeline.*
- **Subject-level splits are non-negotiable.** Multiple papers (Papadopoulos 2020, Paucar-Escalante 2025 survey) call out leakage from random splits in PD time-series. *D1 implication: subject-level splits are an explicit syllabus requirement; verify with a leakage assertion in the notebook.*

### 4.2 What the field is still arguing about

Open methodological questions where you have a real architectural choice.

- **Best path to a usable Transformer when labels are scarce.** Three competing recipes are in play: PRIMUS-style multimodal pretraining + fine-tune (Das et al. 2024), prototypical networks with clinical phenotype priors (Evers et al. 2025), or Multiple Instance Learning over session-level labels (Papadopoulos et al. 2020). PRIMUS is the syllabus-aligned default; Evers is the fallback if the n=2-subject validation cohort proves too thin.
- **Whether IMU + video fusion materially helps.** Hemmerling et al. (2026) report only ~0.01 AUC gain from adding head IMU on top of speech. *D2 implication: do not over-invest in fusion architectures; the per-finger IMU signal should carry the load and video serves the separate compliance role.*
- **Subclinical (low-amplitude) regime.** Nanayakkara & Chan (2025) argue STFT + LSTM is needed because frequency-domain peaks blur at low amplitude. The current 4–6 Hz Butterworth + FFT pipeline is most vulnerable here. *D2 implication: worth flagging in the error-analysis section.*
- **Cross-site / cross-device generalization is brittle.** Adeli et al. (2025) show MotionBERT dropping from 0.49 to 0.25 across CARE-PD sites; Timmermans et al. (2025) report 0.61 sensitivity on real-life cross-device data. *D2/D3 implication: any single-cohort number requires an external-validation caveat in the report.*

### 4.3 Architecture templates (papers to copy from)

Whose pipeline you should pattern your own work after, with the syllabus deliverable it feeds.

| Source | What to copy | Where it lands |
|---|---|---|
| Králik & Šuppa 2021 (WaveGlove) | Per-finger IMU patch-embed Transformer; multi-sensor ablation methodology | D2 main model, D2 Week 6 ablation |
| Das et al. 2024 (PRIMUS) | Pretrain-on-generic-motion → fine-tune-on-PD recipe; open-source weights from Nokia Bell Labs | D2 Week 5 |
| Atri et al. 2022 | Activity-gated 1D-CNN; aggregation absorbs per-segment uncertainty | D1 baseline + D3 compliance-gating concept |
| Bachlin et al. 2010 | Daphnet dataset + freeze-index baseline | D1 FOG track |
| Papadopoulos et al. 2020 | MIL attention pooling over session-level labels | D2 fallback if per-window labels prove unreliable |
| Evers et al. 2025 | Prototypical RBF network when end-to-end Transformer underperforms | D2 fallback architecture |
| Adeli et al. 2025 (CARE-PD) | MotionBERT / POTR backbone for gait branch | D2 Week 7 |

### 4.4 Performance numbers to beat or match

Concrete comparator numbers from the lit review. D2/D3 reported numbers should be presented in this context.

| Task | Best reported | Source | Caveat |
|---|---|---|---|
| Video MDS-UPDRS hand tremor (4-class) | 90.6% accuracy | Liu et al. 2023 (GTSN) | Single-center, not released, raw pixels |
| Video tremor severity, multi-cohort | "Robust concordance" with clinical ratings | Duque-Quiceno et al. 2024 | Dataset not released |
| PD-vs-ET differential (classical ML) | >0.84 accuracy, >0.90 AUC | Xing et al. 2022 | In-clinic, posture-prompted |
| Free-living tremor (SVM) | 0.88 accuracy, 0.90 sensitivity | Rodriguez et al. 2024 | 24 subjects, per-subject calibration |
| Free-living tremor (logistic regression, cross-device) | 0.61 sensitivity / 0.97 specificity | Timmermans et al. 2025 (Paradigma) | External cohort lacks labels |
| Subclinical PD-vs-ET (LSTM on STFT) | 0.95 binary, 0.93 three-class | Nanayakkara & Chan 2025 | Single-center, imbalanced cohorts |
| FOG (federated stacking ensemble) | ~99% | Paneru 2025 | Single-author preprint; cite skeptically |
| FOG (classical threshold) | 73/82 sens/spec | Bachlin et al. 2010 | The must-beat floor on Daphnet |
| PD detection multimodal (speech + head IMU) | AUC 0.875 | Hemmerling et al. 2026 | Gated early fusion; modest IMU lift |

### 4.5 Cautionary patterns — do not replicate

- **Atri's 100% per-day accuracy** is best read as aggregation hiding per-segment uncertainty. When aggregating in D2, report both per-window and per-session numbers.
- **mPower's voluntary self-enrollment** produced large self-selection and weak-diagnosis biases. The PD-glove protocol's structured in-app tasks avoid this; do not drift toward unconstrained at-home capture in any extension.
- **Liu's pixel-only GTSN** inherits clothing/lighting confounders. Reinforces the MediaPipe-landmarks-over-raw-pixels choice for the compliance module.
- **Adeli's MotionBERT cross-site drop** (0.49 → 0.25) is a warning that held-out site results matter more than aggregate cross-validation. The D2 ablation should hold out at least one cohort.
- **Paneru's ~99% FOG accuracy** is a sole-author preprint with sparse validation detail; cite it as conceptual precedent for federation, not as a performance claim.
- **PPMI's relative cohort homogeneity** (Muhammad et al. 2026) means demographic-generalization claims drawn from PPMI alone need external-validation language in the D3 report.

### 4.6 Fairness obligations the lit review surfaces

Two papers (Muhammad 2026, Tumpa 2025) push these into the D3 protocol:

- **Subgroup metrics, not aggregates.** Adversarial perturbations and platform-specific biases surface as subgroup disparities, not aggregate accuracy.
- **Handedness is a real bias axis.** Tumpa et al. (2025) document 38–70% diagnostic disparity by handedness on remote PD assessment. The current validation cohort is right-dominant; D3 needs an explicit handedness section even with synthetic mirroring.
- **Hardware-platform bias.** Less of an issue here because the Pi 5 + MPU6050 stack is fixed, but worth a sentence in the D3 report describing why this risk is bounded.
- **Fairness preprocessing trades absolute accuracy for parity.** Be ready to report both the unconstrained and fairness-aware numbers.

### 4.7 The PD-glove research gap (your contribution surface)

The lit review's Research Gap section is the contribution thesis for the entire D2–D3 stack. Four claims, each defensible against the surveyed corpus:

1. **Five-finger IMU placement captures pill-rolling spatial signature.** WaveGlove demonstrates multi-sensor ablation lift but only for gesture recognition; no published PD-scoring paper extends per-finger to MDS-UPDRS. *Filled by:* D2 Week 6 per-finger vs. single-wrist ablation.
2. **Calibrated ordinal MDS-UPDRS prediction with uncertainty.** The reviewed corpus is dominated by binary detection; only three papers target severity at all, and none from wearables. *Filled by:* D2 Week 7 uncertainty-aware regression head.
3. **Documented INT8 TFLite latency on Pi 5.** Across 20 papers, this number is conspicuously absent. *Filled by:* D3 Week 11 latency benchmark.
4. **MQTT-only-derived-scores privacy boundary.** Paneru offers federation; Tumpa surfaces fairness; nobody combines on-device inference with a strict raw-data-never-leaves-device guarantee. *Filled by:* D3 Week 9 MQTT publisher with AES-256-GCM + TLS 1.3.

These four are not a survey of the field — they are the four contributions D2–D3 must demonstrate. The lit review has already framed the argument; the deliverables produce the evidence.

### 4.8 Reading priority by syllabus phase

If reading time is scarce, prioritize papers in the week before they become load-bearing. The lit review entry numbers below match the order in `literature-review.md`.

- **This weekend → Week 3 (D1 prep):** #3 Bachlin 2010 (Daphnet methodology), #2 Atri 2022 (1D-CNN canonical), #20 Xing 2022 (RF ceiling), #17 Rodriguez 2024 (SVM + class-rebalance lesson), #16 Paucar-Escalante 2025 (survey for baseline-choice justification).
- **Late Week 4 → Week 5 (D2 prep):** #10 Králik & Šuppa 2021 (WaveGlove — architecture donor), #5 Das 2024 (PRIMUS pretraining recipe), #15 Papadopoulos 2020 (MIL fallback).
- **Week 6 → Week 7 (D2 advanced):** #1 Adeli 2025 (CARE-PD + MotionBERT for gait branch), #11 Liu 2023 (video MDS-UPDRS ceiling), #7 Evers 2025 (prototypical-net fallback), #6 Duque-Quiceno 2024 (video-only ceiling).
- **Week 8 → Week 9 (D2 → D3):** #18 Timmermans 2025 (Paradigma cross-device comparator + open-source reference), #8 Güney 2022 (MediaPipe validation).
- **Week 10 → Week 11 (D3 fairness):** #19 Tumpa 2025 (handedness audit motivation), #12 Muhammad 2026 (fairness preprocessing on PPMI).
- **Skim only, conceptual context:** #4 Bot 2016 (mPower foundational), #9 Hemmerling 2026 (fusion ceiling), #13 Nanayakkara 2025 (subclinical regime), #14 Paneru 2025 (federation conceptual).

### 4.9 One-paragraph synthesis

Wearable PD-tremor ML is mature on the binary-detection axis (wrist accelerometer + 1D-CNN or SVM with class rebalancing) and brittle on the cross-site axis (Adeli's MotionBERT site drop, Timmermans' cross-device sensitivity numbers). MDS-UPDRS ordinal severity prediction from wearables — with uncertainty, with edge deployment, with privacy guarantees, and with handedness-aware fairness — is collectively under-served. The PD-glove framework's per-finger Transformer + INT8 TFLite + MQTT-only-derived-scores stack is positioned exactly in that gap, and the lit review's four named claims are the contribution surface this course's deliverables produce evidence for. Everything else in the timeline is execution.

---

## 5. Immediate next steps (May 31 – Jun 1, this weekend)

These are not in the syllabus week-grid because the syllabus assumed Pre-Planning was already done. They are blockers — start today.

| # | Action | Why it's blocking | Time estimate |
|---|---|---|---|
| 1 | Confirm LONI/PPMI account active and request the **Part III motor exam** and **Roche PD App v2** collections | Without approval, D1 dataset join cannot start. Approvals take 3–10 days. | 30 min today, then wait |
| 2 | Submit Synapse mPower access application (`syn4993293`) | Required for D2 walking-task auxiliary input. Approval is a separate qualified-researcher review. | 30 min today, then wait |
| 3 | Verify AWS school account access; create `pd-glove-data` S3 bucket; document IAM policy in `aws_setup.md` | Required by D1, D2, D3 (artifact storage). Also surfaces any GPU quota issue early. | 1–2 hours |
| 4 | Set up Kaggle account, enable GPU, verify pandas/scipy/torch/tflite versions match what notebooks will need | Free GPU is the prototyping environment per syllabus. | 30 min |
| 5 | Download Daphnet (UCI, immediate, no approval) | Smallest dataset, gets Week 1 EDA unblocked today. | 30 min download + unzip |
| 6 | Download ALAMEDA (Zenodo, CC BY 4.0, immediate, no approval) | Required for Week 2 feature alignment. | 30 min |
| 7 | Confirm `tremor_validation_master.csv` schema is documented (units, sampling rate, channel order) — this is the schema other datasets get aligned **to** | Week 2 unified-schema task depends on this. | Already documented in repo README; just verify. |

**Day-of-Jun-1 milestone:** Daphnet and ALAMEDA on local disk and in S3; PPMI and Synapse approvals pending; AWS bucket live; Kaggle ready. That puts you formally caught up to the end of Week 2 by Monday night.

---

## 6. Week-by-week plan (Jun 2 → Aug 16)

Each row names the deliverable artifact in the repo at end of week. Filenames follow the syllabus repo-requirements list.

### D1 phase (Jun 2 – Jun 16) — **20% of grade**

| Week | Dates | Primary work | Artifact at end of week |
|---|---|---|---|
| 3 | Jun 2 – Jun 8 | If PPMI not yet approved: full Daphnet + ALAMEDA EDA, unified-schema draft, baseline SVM/RF/1D-CNN on Daphnet FOG. If PPMI approved by Jun 4: PPMI Part III + Roche join, subject-level splits with no longitudinal leakage. | `Dataset_Pipeline.ipynb` (EDA + schema), `Unimodal_Classifiers.ipynb` (FOG baselines committed) |
| 4 | Jun 9 – Jun 16 | Tremor/bradykinesia baselines (SVM/RF/1D-CNN) on PPMI + Roche features. Feature-importance analysis. Write the 3–5 page technical report. | `D1_report.pdf`, completed notebooks, S3 datasets uploaded, **D1 submission Jun 16** |

**D1 success criterion:** All four datasets in S3 under a documented schema; baselines benchmarked on both tasks; subject-level splits verified leakage-free; report cites Xing 2022, Rodriguez 2024, Bachlin 2010 as comparators.

### D2 phase (Jun 17 – Jul 14) — **35% of grade**

| Week | Dates | Primary work | Artifact at end of week |
|---|---|---|---|
| 5 | Jun 17 – Jun 23 | Transformer encoder for tremor/brady on Kaggle. Patch embedding from per-finger IMU. Optional: PRIMUS-style mPower pretrain run. Hyperparameter search. | `Transformer_Training.ipynb` (initial training curves) |
| 6 | Jun 24 – Jun 30 | Full training on AWS EC2 GPU. Per-finger vs. simulated single-wrist ablation (this directly validates the WaveGlove design rationale cited in the AIIoT paper). | Trained `.pt` checkpoint in S3, ablation table |
| 7 | Jul 1 – Jul 7 | CARE-PD gait model (MotionBERT or POTR backbone) on UPDRS gait labels. Daphnet FOG features as auxiliary input. Uncertainty-aware scoring head (predictive intervals on MDS-UPDRS 0–4). | Gait model checkpoint, uncertainty calibration plot |
| 8 | Jul 8 – Jul 14 | INT8 TFLite quantization for both models; report accuracy delta vs. float32. MediaPipe Pose → h36m skeleton mapping for phone inference bridge. 8–10 page technical report. | `TFLite_Deployment.ipynb` (quantization section), `.tflite` artifacts in S3, **D2 submission Jul 14** |

**D2 success criterion:** Two Transformer encoders (tremor, FOG/gait) with INT8 quantization, calibration plots, uncertainty intervals, and per-finger ablation showing measurable lift over single-wrist — this is the empirical version of the lit review's first Research Gap claim.

### D3 phase (Jul 15 – Aug 4) — **25% of grade**

| Week | Dates | Primary work | Artifact at end of week |
|---|---|---|---|
| 9 | Jul 15 – Jul 21 | MQTT publisher on AWS EC2. AES-256-GCM payload encryption. TLS 1.3 transport. Test against the schema in `docs/mobile-web-data-contract.md`. | `mqtt_publisher.py`, security test log |
| 10 | Jul 22 – Jul 28 | `mediapipe_compliance.py` on pre-recorded video. Hand Landmarker for compliance gating; Pose for gait pipeline. Session-flagging logic + failure handling. | `mediapipe_compliance.py`, integration test results |
| 11 | Jul 29 – Aug 4 | TFLite latency benchmark on available hardware (Pi 5 if accessible by then; otherwise EC2 c-class proxy). Fairness audit across PPMI age/sex/disease-stage **and** handedness (the handedness axis is the explicit add per Tumpa et al. 2025). 3–5 page report. | Latency table, fairness subgroup metrics, **D3 submission Aug 4** |

**D3 success criterion:** Documented INT8 inference latency on edge-class hardware (this is the lit review's third Research Gap claim — INT8 numbers are conspicuously absent across the surveyed papers), fairness audit reports subgroup metrics not just aggregates, MQTT encryption end-to-end-validated.

### D4 phase (Aug 5 – Aug 16) — **20% of grade**

| Week | Dates | Primary work | Artifact |
|---|---|---|---|
| 12 | Aug 5 – Aug 11 | Final report (10–12 pages). Repo cleanup: README, `requirements.txt`, all four notebooks, `aws_setup.md`, sample data. | `final_report.pdf`, polished repo |
| 13 | Aug 12 – Aug 16 | 15-min presentation, live inference demo, MQTT publisher demo. Q&A prep. | Slide deck, demo recording, **D4 submission Aug 16** |

---

## 7. Concrete repo artifacts (final state by Aug 16)

Required by syllabus repo-requirements list (current presence in this repo noted):

- [ ] `README.md` — exists, needs Part II addendum
- [ ] `requirements.txt` — exists, needs ML deps added
- [ ] `Dataset_Pipeline.ipynb` — to create (D1)
- [ ] `Unimodal_Classifiers.ipynb` — to create (D1)
- [ ] `Transformer_Training.ipynb` — to create (D2)
- [ ] `TFLite_Deployment.ipynb` — to create (D2)
- [ ] `mqtt_publisher.py` — to create (D3)
- [ ] `mediapipe_compliance.py` — to create (D3)
- [ ] `aws_setup.md` — to create (Pre-Planning catch-up this weekend)
- [ ] `part2-ml/literature-review.md` — **done** (8f183a0)
- [ ] `part2-ml/next-steps.md` — **this file**

---

## 8. Risks and contingencies

**R1 — PPMI or Synapse approval slips past Jun 7.**
*Contingency:* Do all of D1 Week 3 on Daphnet + ALAMEDA + local glove data. Daphnet alone supports the FOG baseline track end-to-end. PPMI tremor work compresses into Week 4 but is doable because the join is straightforward (PATNO + EVENT_ID).

**R2 — End-to-end Transformer training fails on the small labeled base.**
*Contingency (named in the lit review):* fall back to (a) PRIMUS-style mPower pretrain → fine-tune on the labeled cohort, or (b) Evers et al. 2025 prototypical-network architecture, which is explicitly designed for the low-label regime. Either is defensible in the D2 report.

**R3 — AWS GPU quota too small for `p3.2xlarge`.**
*Contingency:* Drop to `g4dn.xlarge` (usually default-available) and use longer training time. The Transformer encoder is small enough (<10M params for the per-finger config) that this is acceptable.

**R4 — TFLite INT8 quantization causes more than ~3% accuracy drop.**
*Contingency:* Per-channel quantization with calibration on a held-out subject batch; report both INT8 and FP16 numbers if INT8 alone is unacceptable.

**R5 — Pi 5 unavailable for D3 latency benchmark.**
*Contingency:* Benchmark on an EC2 `t3.medium` or similar low-CPU instance and report it as a proxy; flag in the report that on-device Pi 5 numbers will be added when hardware access resumes. The AIIoT 2026 paper already documents ~89 Hz / 4-channel performance, which sets the latency budget context.

---

## 9. Open questions to resolve this weekend

1. **Is PPMI access fully provisioned, or only the LONI login?** Account creation is one step; per-collection DUA approval is another.
2. **Is the AWS school account currently usable?** Check console login + a `boto3` smoke-test in Kaggle.
3. **Is the Roche PD App v2 collection still listed under the PPMI portal?** It was at the time the syllabus was written; verify before counting on it for D1.
4. **Glove hardware status for the D3 latency benchmark.** Will the Pi 5 be in reach by Jul 29? If not, lock in the EC2-proxy contingency now.
5. **Co-author / advisor sync.** The AIIoT 2026 paper has co-authors (Hong Peng, Sarita Singh, Madhu Babu Cherukuri, Vatsalya Dabhi). Confirm whether D2/D3 results will be drafted toward a follow-on paper or remain coursework-only — that decision affects how D2 ablations are framed.

---

## 10. Bottom line

The literature review is the single best preparation artifact for the rest of this course — it has the bibliography, the gap statement, and the contribution framing already in shape. The work that remains is execution against a clear plan, with the main 2026-05-31 priority being **today's dataset-access requests** so that the approval clock starts now rather than at the end of Week 3.

If PPMI/Synapse approvals come back on time and AWS GPU quota is available, the syllabus is feasible at the current pace. If R1 hits, D1 compresses but is still achievable on Daphnet + ALAMEDA + local data alone.
