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

The claim is **layered**. Layer 1 is multimodal PD detection (motion, voice, gait, tapping)
— deployable but not novel. Layer 2 is the contribution: **per-finger inertial sensing
improves PD versus essential tremor discrimination**, because pill-rolling is a finger-level
sign that wrist sensors spatially average away. iTex (the closest prior system) named this
exact gap in their Background and then built one IMU per glove; this project has five.

Two public datasets drive it: **PADS** (only source of essential tremor) and **mPower**
(only source of paired multimodal data, so the fusion head can be pretrained there).

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
