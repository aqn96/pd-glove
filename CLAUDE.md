# PD-Glove — repo orientation

Wearable glove for objective Parkinson's disease motor assessment, plus the ML pipeline
behind it. Two largely separate bodies of work live here.

## The two halves

| Path | What it is |
|---|---|
| Repo root (`app.py`, `scripts/`, `docs/`) | **Hardware + demo.** Raspberry Pi 5 glove: 5x MPU6050 IMUs via TCA9548A mux, 5x flex sensors via MCP3008. DSP pipeline (Butterworth 3–15 Hz + FFT), Flask demo app. Backs the AIIoT 2026 paper. |
| `part2-ml/` | **ML pipeline.** CS 8674 Part II coursework: public-dataset training, baselines, transformer fine-tuning, edge quantization, fairness auditing. Self-contained. |

Start at `README.md` (hardware) or `part2-ml/README.md` (ML).

## Current state

- **AIIoT 2026 paper:** accepted with revision, camera-ready. Hardware + DSP + architecture.
  Contains **no trained ML classifier** — every ML/inference element is marked pending.
- **CS 8674 D1, D2, D3:** complete. D4 due Aug 16.
- **Hardware:** 4 of 5 IMU channels working (CH4 fault). Flex sensors bench-validated on
  thumb only, off-platform on an Arduino; Pi 5 + MCP3008 integration pending.
- **IRB:** pending. Blocks all patient data collection.
- **Pi 5:** not currently physically accessible. The D3 latency number is a laptop ARM proxy.

## Headline results

| Where | Result |
|---|---|
| D2 (`part2-ml/docs/D2_report.md`) | MOMENT-1-large full fine-tune on PADS: macro-F1 0.626 / AUROC 0.731, beats SVM 0.564, RF 0.498, CNN1D 0.565. Linear probe (frozen encoder) underperformed at 0.502. |
| D3 (`part2-ml/docs/D3_report.md`) | CNN quantized to INT8 TFLite, 19.6 KB, small accuracy cost. Fairness gaps across gender/handedness/age turned out to be explained by subgroup class balance, not model bias. Latency 0.066 ms on M3 Pro (proxy, not Pi). AES-256-GCM + MQTT v5 message expiry implemented and tested. |

**Deployment split:** SVM/CNN run on the Pi. MOMENT (1.4 GB) is cloud-only and serves as an
accuracy ceiling, not a deployable model.

## Research direction

Read `part2-ml/docs/research-direction.md` before proposing anything about future work.
It has diagrams, sourcing, and open decisions. Summary:

The claim is **layered**. Layer 1 is a multimodal low-cost home PD assessment system:
deployable, not novel by itself. Layer 2 is what makes Layer 1 credible and is where the
contribution lives: **per-finger inertial sensing captures inter-digit phase relationships
that discriminate PD from essential tremor, as an EMG-free alternative to the established
alternating-versus-synchronous sign.**

The mechanism is specific. PD rest tremor is *alternating* (antagonist muscles out of
phase), ET is *synchronous*; one study reports no overlap. Classically measured with EMG.
A wrist sensor averages away inter-digit timing; five per-finger IMUs can resolve it.

**This space is occupied — do not claim novelty carelessly.** IMU-based PD/ET
discrimination exists in the literature, including thumb/index placement. Per-finger
placement alone is not a contribution. See §1.2 for what actually remains open.

**Framing note:** ET is not a bonus feature. Essential tremor is more common than PD, so a
home system that calls all tremor Parkinson's would misclassify much of its real user base.
ET is the validity check on the detection claim.

**Five scoring channels, two-level late fusion** (never early — §3 has the six reasons):
glove tremor (PADS), glove flex bradykinesia (engineered features; no *flex* dataset
exists, but mPower tapping becomes one once the feature space is sensor-agnostic),
phone tapping (mPower, and the head-to-head baseline the glove must beat), phone voice
(mPower), phone gait (mPower, in-pocket accelerometry not camera pose).

**Fusion grouping rule:** a channel goes in level 1 if mPower observed it *paired* with the
other level-1 channels on the same person; everything else goes in level 2. So voice, gait,
and tapping form level 1 (pretrained on ~9.5k subjects), and glove tremor + glove flex +
the level-1 phone score form level 2 (fitted on the cohort). Four parameters each. This
means the two bradykinesia measures land at different levels, which looks wrong until you
know the rule: grouping follows data pairing, not clinical construct. Flat vs two-level is
still an open empirical question — settle it with LOSO.

**Two datasets:** **PADS** (only source of essential tremor anywhere) and **mPower** (only
source of *paired* modalities, so the fusion head can be pretrained rather than fitted at
n=20). mPower labels are self-reported — weak supervision at scale, not a clinical result.

**Deployment:** Path A is fully on-device, every encoder small enough for the Pi, nothing
raw leaves. That is the headline claim, not a tiered compromise. Path B is an opt-in cloud
second opinion using MOMENT, which sends raw IMU but never raw audio.

**Adaptation method depends on model size:** LoRA above 100M params (MOMENT),
freeze-most-train-last-block at 1M–100M (voice), freeze-extractor-train-head below 1M
(CNN, tapping, gait). Never full fine-tune at n=20. Never train the `.tflite` — keep the
float32 master, fine-tune that, re-quantize.

**Blocking dependencies:** IRB (all patient work), Synapse access (three of five channels),
and an unresolved question about whether mPower can legally be hosted on Kaggle at all.

## Conventions that matter

- **Notebook source of truth is `.py`** (jupytext percent format) in `part2-ml/notebooks/`.
  The `.ipynb` files are Kaggle copies and can drift. When editing, check whether the user's
  live Kaggle notebook has diverged from the repo `.py` before assuming they match.
- **Deliverable prefixes:** `D1_`, `D2_`, `D3_` on notebooks and reports.
- **Splits are always subject-level**, never window- or session-level. `GroupShuffleSplit`
  with a hard leakage assertion, or `StratifiedGroupKFold`. This is load-bearing: the
  literature's most common failure is subject leakage inflating accuracy.
- **Fairness metrics are pooled out-of-fold**, not single-split. A single small test split
  produced confident-looking disparities in D3 that dissolved when pooled across folds.
- `part2-ml/results/` and `part2-ml/data/` are gitignored. Reports and figures under
  `docs/` are tracked.
- All compute runs on Kaggle (no AWS access). `/kaggle/working` is wiped between notebook
  versions — a checkpoint only survives if uploaded as its own Kaggle Dataset and attached
  as an input.

## Writing style for this repo

Plain language. No em dashes. Report what was actually measured, including when a result
contradicts an earlier one. Every reported number should say what it is a proxy for if it
is not the real thing (for example, the latency benchmark is an M3 Pro stand-in for a Pi 5
and is labelled as such everywhere it appears).

Claims are marked **done**, **planned**, or **blocked**. Clinical assertions are marked
where they still need a clinician's sign-off.
