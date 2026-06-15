# Part II: Plan & Timeline (plain-English)

**Course:** CS 8674 Part II — Intelligent IoT Frameworks for Chronic Disease Management (Summer 2026)
**Instructor:** Sarita Singh
**As of:** 2026-06-14 (Week 4) — **Deliverable 1 complete. D2 starts June 17.**
**Companion docs:** [literature-review.md](literature-review.md) · [README.md](README.md) · [docs/D1_report.md](docs/D1_report.md)

This is the plain-English version of the plan: what the project is, where it stands today,
and what happens next. The detailed annotated bibliography lives in `literature-review.md`.

---

## 1. The big picture (in plain English)

### What the research says
Across the 20 papers we reviewed, the pattern is simple: **medical AI is good at the easy
version of Parkinson's tracking and falls apart on the hard version.**

- **The easy version** — a smartwatch on the wrist answering "is the patient shaking, yes or
  no?" Standard models do this well.
- **The hard version** — measuring *how severe* a tremor is on the clinical 0–4 scale,
  running that model *fast and locally* on a cheap device (a Raspberry Pi) instead of the
  cloud, and staying accurate across different hardware and patient groups (e.g. left- vs
  right-handed). Here, accuracy collapses.

### The four blind spots (the gaps we exploit)
1. **Single-wrist blindness** — almost every study straps one sensor to the wrist (or uses a
   phone) and is blind to what individual fingers do.
2. **No real-time speed tests** — researchers train big models in the cloud but rarely
   measure how fast they actually run on a wearable.
3. **Privacy by data-shipping** — most systems send raw patient movement to the cloud to do
   the math, a real privacy risk for medical data.
4. **Hidden subgroup bias** — average accuracy scores hide big drops for minority groups
   (one study: 38–70% accuracy loss for left-handed patients).

### The glove's answers (our contribution surface)
1. **Per-finger sensing** — IMUs on each finger (4 of 5 channels working today; flex sensors
   for stiffness bench-validated on the thumb) capture the rotating "pill-rolling" finger
   motion a wristband misses.
2. **Measured edge speed** — D3 reports actual INT8 inference latency on edge hardware, the
   number the literature keeps omitting.
3. **Privacy-by-design** — the model runs *on the device*; only the final safe severity
   score is sent over MQTT. Raw data never leaves the glove.
4. **The ablation test (D2 Week 6)** — we deliberately "blindfold" the model by turning off
   the finger channels and running it as a simulated single-wrist sensor. The drop in score
   is the empirical proof that per-finger hardware beats a smartwatch.

These four are exactly the four deliverable contributions — see §4.

---

## 2. Where we are right now (2026-06-14)

**Deliverable 1 is complete.**

| Piece | Status |
|---|---|
| Datasets downloaded, organized, verified | ✅ ALAMEDA, Daphnet (17 sessions), PPMI Part III (5,157 patients), Demographics, Roche |
| `Dataset_Pipeline.ipynb` — clean, leakage-safe subject splits, unified schema, EDA | ✅ verified on Kaggle |
| `Unimodal_Classifiers.ipynb` — SVM / RF / 1D-CNN, subject-grouped CV | ✅ verified on Kaggle GPU T4 |
| D1 report | ✅ written — `docs/D1_report.md` (PDF export ready) |
| AWS S3 upload | ⏳ optional — skip if school account not available |

### D1 results summary
- **FOG (Daphnet):** 1D-CNN AUROC **0.95**, RF AUROC **0.90** — both beat the Bächlin floor.
- **Tremor (ALAMEDA):** all models AUROC **~0.45–0.54 (chance)**. Expected — pre-extracted tabular features capture subject identity, not tremor state. This is the argument for D2's raw-signal Transformer.
- **Roche discrepancy:** no `EVENT_ID` in the actual export, only 32 patients. Handled as per-patient feature table on `PATNO` only. Flagged for Prof. Singh.

### D2 starts June 17. Key addition: glove data augmentation.
The glove has 9 sessions from 2 subjects — not enough to fine-tune a Transformer from scratch.
D2 adds a data augmentation step before fine-tuning (Gaussian noise, amplitude scaling,
time-shift, channel dropout, left/right mirror) to expand the 9 sessions into ~8,000 windows
for training. Augmented windows are excluded from validation. This is standard practice for
small medical cohorts and is distinct from synthetic data generation (which would require
a much larger base dataset to produce genuinely new patient profiles).

---

## 3. The four deliverables, in plain English

| # | Due | Weight | What it is |
|---|---|---|---|
| **D1** | Jun 16 | 20% | **Get the data ready and set the bar.** Clean four datasets, document one shared feature format, and benchmark simple models (SVM / Random Forest / 1D-CNN) so the fancy model in D2 has something to beat. |
| **D2** | Jul 14 | 35% | **Build the real model.** A Transformer that reads per-finger motion and predicts MDS-UPDRS severity, shrunk to INT8 for the edge, with the per-finger-vs-wrist ablation that proves the hardware's worth. |
| **D3** | Aug 4 | 25% | **Make it a system.** Measure on-device speed, send only scores over encrypted MQTT, add a camera-based compliance check, and audit fairness across age/sex/stage/handedness. |
| **D4** | Aug 16 | 20% | **Tell the story.** Final report, clean repo, 15-min talk, and a live demo. |

---

## 4. Week-by-week timeline (Jun 2 → Aug 16)

Each row names the file that should exist in the repo at the end of the week.

### D1 — Dataset & baselines (Jun 2 – 16) · 20%
| Week | Dates | Work | Artifact |
|---|---|---|---|
| 3 | Jun 2–8 | Clean + split all datasets, unified schema, EDA, baseline SVM/RF/1D-CNN | `Dataset_Pipeline.ipynb`, `Unimodal_Classifiers.ipynb` ✅ |
| 4 | Jun 9–16 | Kaggle run, S3 upload, feature-importance, write report | `D1_report.pdf`, S3 datasets, **submit Jun 16** |

### D2 — Transformer + augmentation + fine-tuning (Jun 17 – Jul 14) · 35%
| Week | Dates | Work | Artifact |
|---|---|---|---|
| 5 | Jun 17–23 | **Glove data augmentation** (noise, scaling, time-shift, channel dropout, mirror) on 9 sessions → ~8k windows; Transformer encoder architecture; pretrain on ALAMEDA raw features | `Augmentation.ipynb`, `Transformer_Training.ipynb` |
| 6 | Jun 24–30 | **Fine-tune on augmented glove sessions** with leave-session-out validation; pretrained-only vs. fine-tuned comparison; **per-finger vs. single-wrist ablation** | `.pt` checkpoint, fine-tune validation table, ablation table |
| 7 | Jul 1–7 | Full GPU training on EC2/Kaggle; uncertainty-aware scoring; gait model (CARE-PD / MotionBERT) if time allows | final checkpoint, calibration plot |
| 8 | Jul 8–14 | INT8 TFLite (report accuracy delta); D2 report (augmentation + fine-tuning + ablation) | `TFLite_Deployment.ipynb`, `.tflite`, **submit Jul 14** |

**Augmentation strategy (Week 5):**
Apply 5 transforms to each raw glove IMU window independently:
1. Gaussian noise (sigma = 0.01 × channel std)
2. Amplitude scaling (random factor 0.8–1.2×)
3. Time shift (±10 samples)
4. Channel dropout (zero out one IMU channel at random)
5. Left/right mirror (swap symmetric finger channel pairs)

Each original window produces 5 augmented copies → 9 sessions × ~150 windows × 5 = ~6,750
augmented training windows (plus the ~1,350 originals = ~8,100 total).
Augmented windows are **never used in validation** — held-out sessions use original recordings only.

**Fine-tuning validation (Week 6):**
Leave-session-out cross-validation on the 9 original sessions:
- Hold out 2-3 sessions for testing (original only, no augmentation)
- Fine-tune on the remaining 6-7 sessions (with augmentation)
- Compare: pretrained-only vs. fine-tuned on held-out sessions
- Report the improvement as evidence that fine-tuning helps even on a 2-subject cohort
- Honest caveat: cross-subject generalization requires a larger future clinical study

### D3 — Edge + integration (Jul 15 – Aug 4) · 25%
| Week | Dates | Work | Artifact |
|---|---|---|---|
| 9 | Jul 15–21 | MQTT publisher with AES-256-GCM + TLS 1.3 | `mqtt_publisher.py`, security log |
| 10 | Jul 22–28 | MediaPipe Hand Landmarker compliance on pre-recorded video; session flagging | `mediapipe_compliance.py` |
| 11 | Jul 29–Aug 4 | INT8 latency benchmark; fairness audit (age/sex/stage **+ handedness**) | latency table, fairness metrics, **submit Aug 4** |

### D4 — Final (Aug 5 – 16) · 20%
| Week | Dates | Work | Artifact |
|---|---|---|---|
| 12 | Aug 5–11 | Final report (10–12 pp); repo cleanup | `final_report.pdf` |
| 13 | Aug 12–16 | Slides, live demo, Q&A prep | deck + demo, **submit Aug 16** |

---

## 5. The 20 papers, on one screen

Full annotated detail is in [`literature-review.md`](literature-review.md). The short version:

**Copy these (templates).** WaveGlove (Králik & Šuppa 2021) → the per-finger Transformer +
ablation. PRIMUS (Das 2024) → pretrain-then-fine-tune when labels are scarce. Atri (2022) →
the 1D-CNN baseline. Bächlin (2010) → Daphnet FOG + the must-beat threshold. CARE-PD (Adeli
2025) → gait backbone.

**Beat or match these (numbers).** RF/XGBoost reach >0.84 acc on PD-vs-ET (Xing 2022) — so
classical models must come *before* the Transformer. SVM hits 0.88 with good rebalancing
(Rodriguez 2024). FOG floor is 73/82 (Bächlin). MediaPipe recovers tremor frequency to within
0.23 Hz (Güney 2022) — good enough for compliance gating, not primary scoring.

**Don't be fooled by these (cautions).** "100% per-day" accuracy is aggregation hiding
per-window error (Atri). mPower's huge size hides self-selection bias. Cross-site accuracy
craters (MotionBERT 0.49→0.25, Adeli) — every single-cohort number needs an
external-validation caveat. PPMI is less diverse than its size suggests.

**Fairness obligations (Muhammad 2026, Tumpa 2025).** Report subgroup metrics, not just
averages. Handedness is a real bias axis (38–70% disparity) and needs its own section in D3.

---

## 6. Risks & backup plans

| Risk | Backup plan |
|---|---|
| **Small labeled glove cohort** (9 sessions / 2 subjects) — too thin to train a Transformer end-to-end | Augment 9 sessions to ~8k windows (noise/scale/shift/dropout/mirror) for fine-tuning; pretrain on ALAMEDA first; validate with leave-session-out CV. Frame as proof-of-concept; full cross-subject validation is future work. |
| **AWS GPU quota** too small for `p3.2xlarge` | Use `g4dn.xlarge` (usually available); the encoder is small (<10M params). |
| **INT8 quantization** drops accuracy >3% | Per-channel quantization with calibration; report INT8 *and* FP16. |
| **Pi 5 unavailable** for the D3 latency benchmark | Benchmark on an EC2 low-CPU instance as a proxy; note Pi numbers added when hardware returns (~89 Hz / 4-channel already documented in the AIIoT paper). |
| **ALAMEDA tremor ≈ chance cross-subject** (already observed) | Expected; it's the argument for D2's raw-signal model. Report it honestly as the baseline floor. |

---

## 7. Open questions to resolve

1. **Roche/`EVENT_ID` discrepancy** — confirm with Prof. Singh how to present the Roche
   sub-study, since the syllabus's join key doesn't exist in the data.
2. **AWS school account** — is it usable now? (console login + a `boto3` smoke-test.)
3. **mPower (Synapse) access** — application filed? Needed for D2 Week 5.
4. **Pi 5 availability** for the D3 latency benchmark by Jul 29 — if not, lock the EC2 proxy.
5. **Co-author sync** — are D2/D3 results headed toward a follow-on paper or coursework only?
   (Affects how the ablation is framed.)

---

## 8. Bottom line

D1 is done. The data is clean, the baselines are run, and the report is written. The key
finding — tremor is near-chance with tabular features, FOG works well — directly motivates
D2's raw-signal Transformer approach.

D2 starts June 17 with one important addition: a data augmentation step that expands the
9 glove sessions into ~8,000 training windows before fine-tuning. This is the practical
solution to the small cohort problem. The Transformer pretrains on ALAMEDA, fine-tunes on
the augmented glove data, and is validated with leave-session-out CV. The ablation test
(per-finger vs. single-wrist) remains the core research contribution that justifies the
hardware design.
