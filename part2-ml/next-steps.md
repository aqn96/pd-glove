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
| Pre-Planning P3 (May 14 – May 18) — dataset downloads, AWS S3 + IAM, Kaggle env | **Partially done.** Open-access datasets downloaded (Daphnet, ALAMEDA); AWS S3 + IAM and Kaggle env still pending — blocked on the professor meeting and PPMI/Synapse approval requests. |
| Week 1 (May 19 – May 25) — PPMI + Roche joins, splits, Daphnet EDA | **Daphnet EDA starting today on Colab** (see §5 item 8); PPMI/Roche join blocked on DUA approval. |
| Week 2 (May 26 – Jun 1) — ALAMEDA alignment, unified schema, S3 upload | **In progress.** ALAMEDA columns mapped onto glove DSP schema in `data/alameda/README.md`; full schema notebook starts on Colab this weekend; S3 upload waits on AWS. |

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

The literature review is organized alphabetically — useful for citing but not for acting. This section reorganizes the same 20 papers around one question: *what do they tell me to do?*

**Read in 30 seconds.** Wearable PD-tremor ML is mature on the easy version of the problem (tremor-vs-no-tremor on a wrist accelerometer) and brittle on every harder version (severity scoring, cross-site generalization, edge deployment, fairness). The PD-glove framework targets the harder version on every axis at once: per-finger placement instead of wrist, ordinal MDS-UPDRS severity instead of binary, INT8 TFLite on a Pi 5 instead of a server, and a privacy boundary that almost no published wearable system enforces. The four "research gap" claims in the lit review *are* the contribution surface D2–D3 will produce evidence for — everything else in the timeline is execution.

**Read in 5 minutes.** Skim §4.1 (the 20-paper cheatsheet — who's who), §4.8 (your contribution surface), and §4.10 (this week's action paragraph). That's the minimum.

**Read in 15 minutes.** All of §4.1 through §4.10 — the full action-reorganization.

### 4.1 Paper-by-paper at a glance (the 20-source cheatsheet)

Before §4.2 through §4.10 start naming papers in different contexts (templates, comparators, warnings, fairness, gap), this subsection gives you the **one-line "what it does + why you care"** for each of the 20 entries in `literature-review.md`. Entry numbers match the lit-review order, so you can jump straight to the full annotated bibliography for any paper.

1. **Adeli et al. 2025 (CARE-PD).** Released the largest multi-site 3D-mesh PD gait dataset (9 cohorts) and benchmarked motion-encoder baselines; MotionBERT scores drop from 0.49 to 0.25 across sites. **Why you care:** D2 Week 7 gait-branch backbone candidate + the canonical example of why cross-site drift forces external-validation caveats.
2. **Atri et al. 2022 (1D-CNN canonical pattern).** Activity-gated 1D-CNN over wrist Verily Watch data; ~90% per-segment accuracy and 100% per-day after aggregation, 11 subjects. **Why you care:** defines the third D1 baseline architecture you copy directly; the activity-gating idea is the conceptual ancestor of your D3 compliance gate.
3. **Bachlin et al. 2010 (Daphnet + freeze-index).** Foundational FOG dataset and a threshold rule on freeze-band / locomotion-band power ratio reaching ~73/82 sens/spec. **Why you care:** the dataset itself is your D1 FOG track; the threshold is the must-beat floor for any FOG model.
4. **Bot et al. 2016 (mPower foundational).** First iPhone-based PD study (9,000+ enrollees) with finger-tapping, gait, voice, and memory tasks; self-selection and weak-diagnosis biases are well-documented. **Why you care:** syllabus-listed auxiliary corpus for the D2 gait branch — and a cautionary template not to replicate when extending the protocol.
5. **Das et al. 2024 (PRIMUS pretraining).** Multimodal self-supervised pretraining recipe for IMU encoders; up to +15% on low-label downstream tasks; open-source weights from Nokia Bell Labs. **Why you care:** D2 Week 5 — your pretrain-then-fine-tune path on a generic motion corpus before specialising on the small PD-glove labeled cohort.
6. **Duque-Quiceno et al. 2024 (pixel video severity).** Deep pixel model on 2,742 videos predicts MDS-UPDRS tremor sub-scores; cross-cohort, recovers dose-response signal. **Why you care:** sets a video-only severity ceiling; reinforces your structured-landmark-over-raw-pixel design choice.
7. **Evers et al. 2025 (prototypical RBF network).** Tremor encoded as a mixture over 7 sub-prototypes; designed for low-label, phenotype-robust deployment; 66% sens / 95% spec. **Why you care:** D2 fallback architecture if end-to-end Transformer fine-tune underperforms on the n=2-subject labeled base.
8. **Güney et al. 2022 (MediaPipe validation).** 240 fps video + MediaPipe Hand Landmarker; tremor frequency recovered within 0.229 Hz MAE against simultaneous accelerometer. **Why you care:** the strongest direct evidence that the D3 MediaPipe compliance module is kinematically valid for rest and postural tremor.
9. **Hemmerling et al. 2026 (multimodal fusion).** HoloLens 2 captures speech + head IMU on 165 subjects; gated early fusion adds only ~0.01 AUC over speech alone. **Why you care:** quantitative argument against over-investing in IMU+video fusion in D2 — let the per-finger IMU carry the scoring load.
10. **Králik & Šuppa 2021 (WaveGlove).** Five-finger IMU Transformer for hand gestures; multi-sensor ablation shows clear lift over single-wrist; >11,000 samples. **Why you care:** your direct architecture donor for the D2 main model; their ablation methodology is exactly what you replicate in Week 6.
11. **Liu et al. 2023 (GTSN video MDS-UPDRS).** Pixel model + temporal-difference module on Eulerian-magnified video; 90.6% on 4-class rest hand tremor severity. **Why you care:** the video-only MDS-UPDRS performance ceiling your IMU-plus-video architecture should be positioned to match or exceed.
12. **Muhammad et al. 2026 (trustworthy AI / fairness).** Adversarial-robust and fairness-aware ML on PPMI; subgroup disparities surface under both attack and aggregation. **Why you care:** the fairness preprocessing recipes apply directly to D3 Week 11; surfaces the rule that subgroup metrics must be reported alongside aggregates.
13. **Nanayakkara & Chan 2025 (subclinical LSTM).** LSTM over STFT features handles low-amplitude PD-vs-ET classification; 95% binary, 93% three-class. **Why you care:** explains why your Butterworth + FFT pipeline is weakest in the subclinical regime — flag this in D2 error analysis.
14. **Paneru 2025 (federated FOG).** Federated learning across wearable clients with stacking ensemble; ~99% accuracy on FOG. **Why you care:** single-author preprint — treat the accuracy claim skeptically; useful only as conceptual precedent if a future phase scales the deployment to multiple devices.
15. **Papadopoulos et al. 2020 (MIL for in-the-wild tremor).** Multiple Instance Learning over smartphone IMU bags with session-level labels; 45 subjects, real-world deployment. **Why you care:** D2 fallback when per-window labels prove unreliable; also names subject-level splits as a non-negotiable.
16. **Paucar-Escalante et al. 2025 (survey).** Survey of wearable PD-tremor ML methods; explicitly names methodological pitfalls — leakage, weak external validation, inconsistent label conventions. **Why you care:** justifies your D1 baseline-trio choice (SVM/RF/1D-CNN) and is the most useful single citation for the D1 report's "method-choice" framing.
17. **Rodriguez et al. 2024 (SVM + class rebalance).** SVM on 67-hour free-living IMU corpus (24 subjects); 0.88 accuracy, 0.90 sensitivity; class rebalancing was the critical engineering choice. **Why you care:** the closest small-cohort analog in the field; the rebalancing-first lesson is the single most actionable D1 takeaway.
18. **Timmermans et al. 2025 (Paradigma cross-device).** Logistic regression on wrist gyroscope cepstral features, cross-device validated on 565+ subjects; open-source Paradigma toolbox. **Why you care:** the most useful comparator for D3 cross-device generalization — and an external reference implementation against which to sanity-check your DSP pipeline.
19. **Tumpa et al. 2025 (handedness bias).** Audits a remote PD assessment across handedness and device platform on 251 subjects; 38–70% diagnostic disparity by handedness. **Why you care:** motivates the handedness section in your D3 fairness audit — even with synthetic mirroring, the audit cannot skip this axis.
20. **Xing et al. 2022 (RF/XGBoost ceiling).** Seven classifiers on 398 PD/ET subjects with accel + surface EMG; RF and XGBoost reach >0.84 accuracy and >0.90 AUC; the CNN entry underperforms. **Why you care:** the classical-ML performance ceiling for D1; concrete evidence that RF/XGBoost benchmarks must come *before* any Transformer claim.

### 4.2 What the field has settled on (ground rules)

Six findings recur across multiple sources in the lit review. Treat them as ground rules and let them shape D1 from the start rather than re-deriving them later. Each one ends with the practical consequence in italics.

- **Random Forest and XGBoost are still the strongest classical baselines on small clinical cohorts.** Xing et al. (2022) report >0.84 accuracy and >0.90 AUC for PD-vs-essential-tremor on 398 subjects — and their CNN underperformed both gradient-boosted methods. This is the rule whenever cohort sizes are small to moderate: classical ensembles are competitive, sometimes dominant, against deep nets. *Do not skip RF/XGBoost on the way to the Transformer in D1.*
- **1D-CNN over wrist accelerometer is the canonical deep baseline.** Atri et al. (2022) defined the activity-gated 1D-CNN pattern most subsequent wearable papers extend. *The syllabus names this as the third D1 baseline. Copy the architecture directly — there is no point innovating on a baseline.*
- **Class rebalancing matters more than algorithm choice when the dataset is small and imbalanced.** Rodriguez et al. (2024) reach 0.88 accuracy from a plain SVM by attending carefully to rebalancing. *For your local cohort (n=2 subjects, 9 sessions) this is the single most actionable lesson — budget time for SMOTE / class-weight tuning before architecture tuning.*
- **MediaPipe-derived tremor frequency is accelerometer-grade on rest and postural tremor.** Güney et al. (2022) achieve 0.229 Hz mean absolute frequency error against simultaneous accelerometer ground truth. It degrades on kinetic tremor when the hand occludes itself. *MediaPipe Hand Landmarker is the right tool for D3 compliance gating — don't try to make it a primary scoring channel.*
- **The Daphnet freeze-band / locomotion-band ratio is a must-beat baseline for FOG.** Bachlin et al. (2010) hit ~73% sensitivity / ~82% specificity from a threshold rule on a hand-engineered power ratio. *Any FOG model in D1 or D2 that does not exceed this on Daphnet has a defect somewhere in the pipeline, not a real result.*
- **Subject-level splits are non-negotiable.** Papadopoulos (2020) and the Paucar-Escalante (2025) survey both call out leakage when PD time-series gets randomly split. The syllabus also names this explicitly. *Verify with a one-line assertion at the top of `Dataset_Pipeline.ipynb` — don't rely on it being implicit.*

### 4.3 What the field is still arguing about (your forks in the road)

Four design questions are still open. You don't have to resolve them, but you do have to pick a fork in each and document why. The fork you take in D2 should be defensible against the alternative — that is the actual cost of these being unresolved.

- **Fork 1: best path to a Transformer when labels are scarce.** Three recipes compete: PRIMUS-style multimodal pretraining + fine-tune (Das et al. 2024), prototypical networks with clinical phenotype priors (Evers et al. 2025), or Multiple Instance Learning over session-level labels (Papadopoulos et al. 2020). PRIMUS is the syllabus-aligned default; Evers is the fallback if the n=2-subject cohort proves too thin for fine-tuning.
- **Fork 2: does adding video to IMU actually help?** Hemmerling et al. (2026) report only ~0.01 AUC gain from adding head IMU on top of speech. Translation for D2: don't over-invest in IMU+video fusion. The per-finger IMU should carry the scoring load; video has a separate job (D3 compliance gating).
- **Fork 3: subclinical (low-amplitude) regime is harder.** Nanayakkara & Chan (2025) argue STFT + LSTM is needed because frequency-domain peaks blur at low amplitude. The current Butterworth + FFT pipeline is most vulnerable here. You don't need to fix this for D1/D2, but the D2 error-analysis section should flag subclinical performance as a known weakness.
- **Fork 4: cross-site / cross-device generalization is brittle.** Adeli et al. (2025) report MotionBERT dropping from 0.49 to 0.25 across CARE-PD sites; Timmermans et al. (2025) get 0.61 sensitivity in real-life cross-device evaluation. Translation: any single-cohort number in D2/D3 ships with an external-validation caveat, not as a stand-alone claim.

### 4.4 Architecture templates (papers to copy from)

You don't need to invent the encoder. Seven papers in the lit review provide proven templates, and each maps cleanly to a syllabus deliverable. Start each week by reading the corresponding row before writing code.

| Source | What to copy from it | Where it lands |
|---|---|---|
| Králik & Šuppa 2021 (WaveGlove) | Per-finger IMU patch-embed Transformer; multi-sensor ablation methodology | D2 main model, D2 Week 6 ablation |
| Das et al. 2024 (PRIMUS) | Pretrain-on-generic-motion → fine-tune-on-PD recipe; open-source weights from Nokia Bell Labs | D2 Week 5 |
| Atri et al. 2022 | Activity-gated 1D-CNN; aggregation pattern that absorbs per-segment uncertainty | D1 baseline + D3 compliance-gating concept |
| Bachlin et al. 2010 | Daphnet dataset + freeze-index baseline | D1 FOG track |
| Papadopoulos et al. 2020 | MIL attention pooling over weak (session-level) labels | D2 fallback if per-window labels prove unreliable |
| Evers et al. 2025 | Prototypical RBF network when end-to-end Transformer underperforms | D2 fallback architecture |
| Adeli et al. 2025 (CARE-PD) | MotionBERT / POTR backbone for gait branch | D2 Week 7 |

### 4.5 Performance numbers to beat or match

These are the published numbers your D2/D3 results will be read against. Two caveats before reading the table:

1. **You are not competing with every row.** Some are different problems entirely — video vs. IMU, in-clinic vs. free-living, binary vs. ordinal. Your job is to be defensible in context, not to dominate every cell.
2. **Some numbers should be discounted.** Single-center, dataset-not-released, single-author preprint — these flags are real. Treat the flagged rows as informational, not as targets.

| Task | Best reported | Source | Caveat |
|---|---|---|---|
| Video MDS-UPDRS hand tremor (4-class) | 90.6% accuracy | Liu et al. 2023 (GTSN) | Single-center, not released, raw pixels |
| Video tremor severity, multi-cohort | "Robust concordance" with clinical ratings | Duque-Quiceno et al. 2024 | Dataset not released |
| PD-vs-ET differential (classical ML) | >0.84 accuracy, >0.90 AUC | Xing et al. 2022 | In-clinic, posture-prompted |
| Free-living tremor (SVM) | 0.88 accuracy, 0.90 sensitivity | Rodriguez et al. 2024 | 24 subjects, per-subject calibration |
| Free-living tremor, cross-device | 0.61 sensitivity / 0.97 specificity | Timmermans et al. 2025 (Paradigma) | External cohort lacks labels |
| Subclinical PD-vs-ET (LSTM on STFT) | 0.95 binary, 0.93 three-class | Nanayakkara & Chan 2025 | Single-center, imbalanced cohorts |
| FOG (federated stacking ensemble) | ~99% | Paneru 2025 | Single-author preprint; cite skeptically |
| FOG (classical threshold) | 73/82 sens/spec | Bachlin et al. 2010 | The must-beat floor on Daphnet |
| Multimodal PD detection (speech + head IMU) | AUC 0.875 | Hemmerling et al. 2026 | Gated early fusion; modest IMU lift |

### 4.6 Cautionary patterns — do not replicate

Six published patterns look attractive on the surface but will hurt your work if copied uncritically. Reading them once now will save a self-inflicted bug in D2 or D3.

- **Atri's 100% per-day accuracy.** Looks impressive, but it's aggregation hiding per-segment uncertainty. When you aggregate in D2, report both per-window and per-session numbers — the gap between them is part of the story.
- **mPower's voluntary self-enrollment.** Looks like a huge dataset, but the self-selection and weak-diagnosis biases are well-documented. Your structured in-app assessment protocol avoids this — do not drift toward unconstrained at-home capture in any "extension" idea.
- **Liu's pixel-only GTSN.** Strong headline accuracy, but inherits clothing and lighting confounders. Your MediaPipe-landmarks pipeline is more transferable; don't switch to raw pixels because the GTSN numbers look better.
- **Adeli's MotionBERT cross-site drop (0.49 → 0.25).** A warning, not a method to copy. Lesson: held-out *site* results matter more than aggregate cross-validation. The D2 ablation should hold out at least one cohort.
- **Paneru's ~99% FOG accuracy.** Sole-author preprint, sparse validation detail. Cite as conceptual precedent for federation if you discuss federation, but never as a performance target.
- **PPMI's relative cohort homogeneity.** PPMI is recruited from specialty clinics and is less diverse than its size suggests (Muhammad et al. 2026). Any demographic-generalization claim drawn from PPMI alone needs an external-validation hedge in the D3 fairness report.

### 4.7 Fairness obligations the lit review forces into D3

Two papers — Muhammad et al. (2026) and Tumpa et al. (2025) — push the following into the D3 protocol whether or not the syllabus names them explicitly. Skip these and the D3 audit is incomplete.

- **Report subgroup metrics, not aggregates.** Adversarial perturbations and platform-specific biases surface as subgroup disparities, not as drops in overall accuracy. A model that looks fine on average can be quietly bleeding accuracy on minority strata. The D3 audit must stratify.
- **Handedness is a real bias axis.** Tumpa et al. (2025) document 38–70% diagnostic disparity by handedness on a remote PD assessment. Your validation cohort is right-dominant. The D3 report needs an explicit handedness section — even if the audit is done synthetically (channel-mirrored) rather than with new subjects.
- **Hardware-platform bias is bounded but worth a sentence.** The Pi 5 + MPU6050 stack is fixed across the deployment, so platform drift is a smaller concern than in Tumpa's mouse/keyboard study. Note this explicitly in the D3 report rather than ignoring the question.
- **Fairness preprocessing trades absolute accuracy for parity.** Muhammad et al. document this directly. Report both the unconstrained and fairness-aware numbers — the comparison is the point, not just the parity number.

### 4.8 The PD-glove research gap (your contribution surface)

**This is the most important subsection.** The lit review's Research Gap section is not a scholarly exercise — it *is* the contribution thesis for D2 and D3, in four claims, each defensible against the surveyed corpus and each tied to a specific week's work. If a week ships on time, the corresponding contribution is supported; if a week slips, the contribution shrinks. That is the entire purpose of the timeline.

1. **Five-finger IMU placement captures the pill-rolling spatial signature.** WaveGlove (Králik & Šuppa 2021) showed multi-sensor ablation lifts accuracy on hand-motion tasks, but only for gesture recognition. No published PD-scoring paper extends per-finger placement to MDS-UPDRS. **Evidence produced by:** D2 Week 6 per-finger vs. single-wrist ablation.
2. **Calibrated ordinal MDS-UPDRS prediction with uncertainty.** The reviewed corpus is dominated by binary tremor-vs-no-tremor detection; only three papers target severity at all, and none from wearables. **Evidence produced by:** D2 Week 7 uncertainty-aware regression head.
3. **Documented INT8 TFLite latency on Pi 5.** Across all 20 papers, this number is conspicuously absent — every paper either runs in the cloud or skips the latency measurement entirely. **Evidence produced by:** D3 Week 11 latency benchmark.
4. **MQTT-only-derived-scores privacy boundary.** Paneru (2025) offers federation; Tumpa (2025) surfaces fairness; nobody in the lit review combines on-device inference with a strict raw-data-never-leaves-device guarantee. **Evidence produced by:** D3 Week 9 MQTT publisher with AES-256-GCM + TLS 1.3.

The lit review has framed the argument — the rest of the course produces the evidence.

### 4.9 Reading priority (what to read, and when)

If reading time is scarce, prioritize papers the week before they become load-bearing rather than reading the whole bibliography up-front. Entry numbers below match the order in `literature-review.md`.

- **This weekend → Week 3 (D1 prep):** #3 Bachlin 2010 (Daphnet methodology), #2 Atri 2022 (1D-CNN canonical), #20 Xing 2022 (RF ceiling), #17 Rodriguez 2024 (SVM + class-rebalance lesson), #16 Paucar-Escalante 2025 (survey for baseline-choice justification).
- **Late Week 4 → Week 5 (D2 prep):** #10 Králik & Šuppa 2021 (WaveGlove — your architecture donor), #5 Das 2024 (PRIMUS pretraining recipe), #15 Papadopoulos 2020 (MIL fallback).
- **Week 6 → Week 7 (D2 advanced):** #1 Adeli 2025 (CARE-PD + MotionBERT for gait branch), #11 Liu 2023 (video MDS-UPDRS ceiling), #7 Evers 2025 (prototypical-net fallback), #6 Duque-Quiceno 2024 (video-only ceiling).
- **Week 8 → Week 9 (D2 → D3):** #18 Timmermans 2025 (Paradigma cross-device comparator + open-source reference), #8 Güney 2022 (MediaPipe validation).
- **Week 10 → Week 11 (D3 fairness):** #19 Tumpa 2025 (handedness audit motivation), #12 Muhammad 2026 (fairness preprocessing on PPMI).
- **Skim only, conceptual context:** #4 Bot 2016 (mPower foundational), #9 Hemmerling 2026 (fusion ceiling), #13 Nanayakkara 2025 (subclinical regime), #14 Paneru 2025 (federation conceptual).

### 4.10 What to do this week, in one paragraph

The literature review is done; the next 16 days belong to D1. The five papers worth your reading time before Week 3 starts are the D1-prep entries in §4.9 (Bachlin, Atri, Xing, Rodriguez, Paucar-Escalante). The two most actionable lessons from those five are *use class rebalancing aggressively* (Rodriguez) and *RF/XGBoost will likely beat a small CNN on your cohort* (Xing). The single most important defensive measure in the D1 notebooks is **subject-level splits with an explicit leakage assertion**. Everything else in §4 either supports those choices or sets up D2/D3 work that doesn't start until late June.

---

## 5. Immediate next steps (May 31 – Jun 1, this weekend)

These are not in the syllabus week-grid because the syllabus assumed Pre-Planning was already done. They are blockers — start today.

| # | Action | Why it's blocking | Time estimate | Status |
|---|---|---|---|---|
| 1 | Confirm LONI/PPMI account active and request the **Part III motor exam** and **Roche PD App v2** collections | Without approval, D1 dataset join cannot start. Approvals take 3–10 days. | 30 min today, then wait | ⏳ |
| 2 | Submit Synapse mPower access application (`syn4993293`) | Required for D2 walking-task auxiliary input. Approval is a separate qualified-researcher review. | 30 min today, then wait | ⏳ |
| 3 | Verify AWS school account access; create `pd-glove-data` S3 bucket; document IAM policy in `aws_setup.md` | Required by D1, D2, D3 (artifact storage). Also surfaces any GPU quota issue early. | 1–2 hours | ⏳ blocked on professor meeting (see [professor-meeting.md](professor-meeting.md) §1) |
| 4 | Set up Kaggle account, enable GPU, verify pandas/scipy/torch/tflite versions match what notebooks will need | Free GPU is the prototyping environment per syllabus. Needed before D2 (Week 5). | 30 min | ⏳ |
| 5 | Download Daphnet (UCI, immediate, no approval) | Smallest dataset, gets Week 1 EDA unblocked today. | 30 min download + unzip | ✅ Done 2026-05-31 (commit `5d06ec8`) |
| 6 | Download ALAMEDA (Zenodo, CC BY 4.0, immediate, no approval) | Required for Week 2 feature alignment. | 30 min | ✅ Done 2026-05-31 (commit `439ef39`) |
| 7 | Confirm `tremor_validation_master.csv` schema is documented (units, sampling rate, channel order) — this is the schema other datasets get aligned **to** | Week 2 unified-schema task depends on this. | Already documented in repo README; just verify. | ✅ Done (verified in `data/README.md`) |
| 8 | **Start Daphnet + ALAMEDA EDA on Google Colab.** Open colab.research.google.com → new notebook (T4 GPU runtime). Upload Daphnet zip + ALAMEDA CSV. Run the Quick-load snippets from each dataset's README. Per-subject freeze-event counts (Daphnet), per-subject window distributions and label-column structure (ALAMEDA). | Unblocks Week 2 syllabus work today without waiting on AWS or Kaggle setup. | 2–3 hours | ⏳ Ready to start |

### Compute environment: where to work this week

The syllabus names Kaggle as the prototyping environment (chosen for its no-session-timeout policy) and AWS EC2 for full training. Neither is set up yet, and PPMI/AWS access is blocked on the professor meeting. **Use Google Colab in the gap.**

- **This week (May 31 – Jun 7):** Colab free tier — Daphnet + ALAMEDA EDA, schema-alignment notebook, any toy baseline runs. Daphnet ≈ 86 MB and ALAMEDA ≈ 6 MB both upload trivially.
- **Week 3 – Week 4 (D1 baselines, Jun 2 – Jun 16):** Migrate to Kaggle once the account is set up. SVM/RF/1D-CNN baselines run fine on Kaggle's free T4/P100 — keep notebooks here for the no-timeout property.
- **Week 5+ (D2 Transformer training, Jun 17+):** AWS EC2 (`g4dn.xlarge` or `p3.2xlarge`) for full training runs; Kaggle still useful for hyperparameter prototyping.
- **Storage from the start:** all final notebooks live in `aqn96/pd-glove` regardless of environment (Colab has File → Save a copy in GitHub). Raw datasets land in the S3 bucket once AWS is on; until then, local disk + Colab uploads are fine.

**Day-of-Jun-1 milestone:** Daphnet + ALAMEDA EDA notebook drafted in Colab and committed to GitHub as `Dataset_Pipeline.ipynb` (initial version); PPMI and Synapse access requests filed; AWS and Kaggle accounts queued behind the professor meeting. That puts you operationally back on the syllabus week-grid by Monday night, even though the AWS-dependent items still sit in the holding pattern.

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
