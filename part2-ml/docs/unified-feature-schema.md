# Unified Feature Schema — Deliverable 1

The D1 datasets come from different sensors at different sampling rates and label
granularities. This document defines the **one schema** the baseline classifiers (and
the D2 Transformer) read against, and records exactly **which dataset contributes
features vs. labels for each task**. This is the deliverable's "unified feature schema
documented + EDA" requirement.

## The core asymmetry (read this first)

PPMI provides the **clinical 0–4 MDS-UPDRS labels but no raw waveforms** — it is tabular
scores per visit. So PPMI cannot teach a classifier "what a tremor looks like at 100 Hz."
The sensor-feature → label mapping lives in **ALAMEDA**, **Daphnet**, and the **glove**.

| Role | Datasets |
|---|---|
| **Feature source** (sensor → features) | ALAMEDA, Daphnet, glove DSP |
| **Label / clinical anchor** | PPMI (ordinal 0–4 + Hoehn-Yahr stage), ALAMEDA (binary tremor), Daphnet (freeze) |
| **Fairness cohort** (D3) | PPMI Demographics (age, sex) + NHY stage |

## Tasks

| Task | Feature source | Label | Label type | Group key | Eval |
|---|---|---|---|---|---|
| Tremor / bradykinesia | ALAMEDA 92 feats (glove DSP-aligned) | `Rest/Postural/Kinetic_tremor`, `Constancy_of_rest` | binary | `subject_id` | GroupKFold CV |
| Freezing of gait | Daphnet 9-ch windowed feats | `fog` (annotation 2 vs 1) | binary | `subject` | GroupKFold CV |
| (D2) Ordinal severity | per-finger glove IMU | PPMI NP3* | 0–4 ordinal | `PATNO` | subject split |

## Naming convention

`<sensor>_<domain>_<stat>` — e.g. `ankle_x_dom_freq`, `Magnitude_fft_energy`,
`ch0_band_power`. ALAMEDA already follows this; Daphnet features were named to match;
the glove columns are mapped below.

## Feature-family alignment

The glove DSP (`scripts/dsp_pipeline.py`: 4th-order Butterworth 3–15 Hz + FFT, 4–6 Hz
tremor band) produces three core descriptors per channel. Every dataset exposes an
analog, so the same feature *family* spans all sources:

| Glove DSP output | ALAMEDA analog | Daphnet analog (engineered) |
|---|---|---|
| `dominant_freq_hz` (4–6 Hz FFT peak) | `Magnitude_fft_dom_freq`, `PC1_fft_dom_freq` | `<ch>_dom_freq` |
| `dominant_amp` | `Magnitude_fft_pw_ar_dom_freq` | (peak magnitude in `<ch>_band_power`) |
| `band_power` (4–6 Hz power) | `Magnitude_fft_energy`, `PC1_fft_energy` | `<ch>_band_power`, `<ch>_freeze_index` |

## Per-dataset specifics

### ALAMEDA (tremor)
- 99 cols = `start_timestamp`, `end_timestamp`, `subject_id` + **92 features** + 4 labels.
- Band-pass [2.5–12.5 Hz], 2048-sample (20.48 s) windows, 50 % overlap, magnitude + PC1.
- Timestamps are `MM:SS.f` **relative offsets**, not clock times → dropped from features.
- Labels are **binary** (MDS-UPDRS score collapsed: 0 → absent, >0 → present).
- 11 subjects; per-subject label is near-constant → **GroupKFold CV**, not a single split.

### Daphnet (FOG)
- Raw: `time_ms` + 9 accel channels (ankle/thigh/trunk × xyz, milli-g) + `annotation`, 64 Hz.
- `annotation` 0 = outside protocol (**dropped**), 1 = no freeze, 2 = freeze.
- Engineered to **4 s windows (256 samples), 50 % overlap**; per-channel features:
  `mean, std, rms, range, dom_freq, band_power, freeze_index` (= 3–8 Hz / 0.5–3 Hz power,
  the Bächlin freeze index). 63 features total.
- Window label = freeze if >50 % of samples are annotation 2 (majority).
- Raw windows `(N, 256, 9)` also saved for the 1D-CNN.
- FOG positive rate ≈ **9.6 %** → heavy imbalance; report macro-F1, not accuracy.

### PPMI Part III + Demographics (clinical anchor)
- Part III = per-visit motor exam, 38,226 rows / **5,157 patients**, keyed `PATNO`+`EVENT_ID`.
- Demographics joins on **`PATNO` only** (screening row, `EVENT_ID=TRANS`, broadcast across
  visits) → `SEX`, `BIRTHDT`, `HANDED`.
- Labels: 11 NP3* tremor/bradykinesia items (0–4) auto-detected by prefix
  (`NP3PTRMR/L`, `NP3KTRMR/L`, `NP3RTA*`, `NP3RTCON`, `NP3BRADY`); `NHY` Hoehn-Yahr stage
  (note `NHY=101` = not-assessed code).
- `PDSTATE` (ON/OFF medication) kept — scores swing by medication state.
- Age derived from `BIRTHDT` vs visit `INFODT` (month-year only → ±1 yr, fine for bins).
- Split by **`PATNO`** (no longitudinal leakage): 3609/774/774 patients train/val/test.

### Roche PD Monitoring App v2 (digital sub-study) — ⚠ syllabus join discrepancy
- The real export is **CDISC/SDTM long format**: 108,901 rows, 22 cols
  (`PATNO`, `QRSTEST`, `QRSRESN`, `QRSDTM`, `QRSLAT`, …), **no `EVENT_ID`**, only **32
  patients**. Tests span voice MFCCs, hand-turn speed, drawing Hausdorff distances, sway,
  turn speed, and questionnaires (HADS, sleep/symptom diaries).
- The syllabus's "join Part III + Roche on `PATNO` and `EVENT_ID`" is therefore **not
  literally possible**. Handling: pivot long→wide to **per-patient features** (mean
  `QRSRESN` per `QRSTEST`×`QRSLAT`) → `ppmi_roche_features.parquet` (32 × ~131), joinable
  to Part III on **`PATNO` only**. Too few patients (32) to train baselines; documents the
  digital-biomarker modality and is flagged for the instructor.

### Glove (schema reference)
- `tremor_validation_master.csv`: 8 rows/test (4 channels × {rest, tremor}); per-channel
  `dominant_freq_hz`, `dominant_amp`, `band_power`. Pivoted to one row per (test,
  condition) with `ch{0-3}_*` columns. Too small to train (9 tests / 2 subjects) — used to
  *demonstrate* the unified schema and as a rest-vs-tremor sanity target.

## Leakage rule (non-negotiable)

Every split/CV fold is grouped by subject (`subject_id` / `subject` / `PATNO`). The
pipeline asserts zero subject overlap across train/val/test; the baselines use
`GroupKFold`. A random row split would leak longitudinal information and inflate metrics.
