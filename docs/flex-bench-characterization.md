# Flex Sensor Bench Characterization

**Status:** Data collected 2026-05-07. Pending paper §V-D integration.
**Scope:** Single-finger (thumb) bench validation, off-platform on Arduino Nano 33 BLE Sense Lite
**Raw data:** `data/flex_bench_thumb_2026-05-07.csv` (40 measurements: 10 trials × 4 angles)
**Source of truth for:** Paper §V-D and §VIII flex-sensor claims (AIIoT 2026 camera-ready)

This document captures the bench-level characterization of the flex sensor channel for the PD-glove framework. It is intentionally separate from `validation-results.md`, which covers the Pi 5 + MCP3008 + IMU integration path. The flex characterization here is **off-platform**: a portable Arduino Nano 33 BLE Sense Lite is used in place of the Pi 5 / MCP3008 path so the subsystem can be validated independently of the host glove and so the test setup also informs the cost-reduction roadmap (§VIII).

## Why off-platform

- The Pi 5 + MCP3008 SPI path is the deployment target (see `images/pd_glove_circuit.png` and paper §III-B-2). It is not yet integrated.
- The Arduino Nano 33 BLE Sense Lite (~$30) has both an onboard 12-bit ADC and an integrated IMU (BMI270 + BMM150 in current revisions; LSM9DS1 in older revisions), making it a single-MCU stand-in for both sensing modalities. Confirming both modalities work on a sub-$35 device strengthens the cost-reduction claim in §VIII (and is consistent with the Raspberry Pi Zero 2W / ESP32 deployment targets named there).
- Bench scope is **thumb only**. Multi-finger integration with the Pi 5 host is deferred to subsequent work.

## Hardware

| Component | Detail |
|---|---|
| Flex sensor | SparkFun SEN-10264 (2.2") — single unit, mounted on thumb |
| MCU | Arduino Nano 33 BLE Sense Lite |
| ADC | 12-bit, confirmed by mean of 1036 at 0° (exceeds 10-bit ceiling of 1023) |
| Divider | 10 kΩ pull-down, sensor on supply side, 3.3 V rail |
| Mounting | (describe how the sensor is fixed to the bench jig — adhesive, taped, clamped) |

### Sample rate (~33 Hz)

The bench sketch sampled at approximately 33 Hz. This is **serial-output limited**, not an ADC capability limit: at the default 9600 baud, printing one multi-value line (~26 chars) yields ~37 lines/sec before loop overhead, which lands on the observed ~33 Hz. The Nano's onboard SAADC supports much higher rates (a tight `analogRead()` loop reaches ~2 kHz; the peripheral itself is rated to ~200 ksps). The 33 Hz figure is reported honestly in the paper with a one-line caveat to that effect — it is the rate of the bench characterization sketch, not a hardware ceiling. Raising the baud to 115200 would push the same sketch to several hundred Hz; for clinical tapping at 4–5 Hz, 33 Hz already exceeds Nyquist by a wide margin.

## Protocol

- **Angles:** 0°, 30°, 60° (bench-jig discrete positions)
- **Trials per angle:** 10
- **Total measurements:** 30 (1 sensor × 3 angles × 10 trials)
- **Order:** Randomized across angles to mitigate drift / hysteresis effects from a single sweep direction
- **Hold time:** Each trial is a static read with the sensor held at the target angle for at least N seconds before the sample is logged (specify N once finalized — recommend 3 s settle).
- **Why 60° cap:** SparkFun SEN-10264 exhibits documented resistive-ink hysteresis above ~70°. 60° spans the linear operating range and the clinically meaningful curvature region for finger tapping (Item 3.4) and partial hand open/close (Item 3.5).
- **Why thumb:** The thumb is the dominant joint for the thumb-index interaction characteristic of Parkinsonian pill-rolling tremor (paper §II-B) and is the most accessible finger for jig mounting.

## Results

Computed from `data/flex_bench_thumb_2026-05-07.csv` (sample SD, N-1 denominator).

### Reported in the paper (0°, 30°, 60°)

| Angle (°) | Mean ADC | SD ADC | N | Min | Max |
|---|---|---|---|---|---|
| 0 | 1036.08 | 35.78 | 10 | 968.5 | 1074.0 |
| 30 | 961.89 | 43.04 | 10 | 905.4 | 1015.5 |
| 60 | 924.91 | 63.67 | 10 | 841.9 | 1022.9 |

### Excluded from the paper but retained in the CSV (90°)

| Angle (°) | Mean ADC | SD ADC | N | Min | Max |
|---|---|---|---|---|---|
| 90 | 784.52 | 144.95 | 10 | 575.1 | 1001.4 |

The 90° condition is excluded from the paper's reported analysis because the SD (±145 ADC) and an individual reading of 1001.4 ADC at nominal full bend (within the 0° distribution) indicate the sensor enters the SEN-10264's documented hysteresis regime above ~70°. Raw 90° readings are preserved in the CSV for reproducibility.

### Separability (Cohen's d) for the reported angles

| Pair | Δ Mean | Pooled SD | Cohen's d | Interpretation |
|---|---|---|---|---|
| 0° vs 30° | 74.19 | 39.58 | **1.87** | Large — well separated |
| 30° vs 60° | 36.98 | 54.34 | **0.68** | Medium — 1σ envelopes overlap |
| 0° vs 60° | 111.17 | 51.64 | **2.15** | Large — cleanly separated |

The 0° / 60° pair is cleanly separable. 0° / 30° is well separated. 30° / 60° is only marginally separated — the channel cannot reliably distinguish 30° from 60° at the individual-trial level on this rig.

### What the data supports

- **Monotonicity:** Mean decreases 1036 → 962 → 925 across 0° → 30° → 60° as expected (sensor R increases with bend → divider voltage drops → ADC drops).
- **Flat-vs-bent discrimination:** Yes, with a large effect size (d = 2.15 between 0° and 60°).
- **Graded angular resolution across 0/30/60:** No — the 30° / 60° overlap means the channel does not reliably support fine-grained graded angle reporting on this rig.

## What we do NOT claim

- **No degrees conversion.** All paper-facing numbers are reported in raw ADC. No calibration curve fit. Three points are insufficient to support one and the noise budget at ≥60° on this sensor family does not justify the false precision.
- **No clinical metric (tap rate, decrement, ROM).** This is a sensor-channel characterization, not a bradykinesia validation.
- **No multi-finger generalization.** Thumb only. Other fingers and the Pi 5 / MCP3008 integration path remain pending.

## Reproducibility

- **Raw data:** `data/flex_bench_thumb_2026-05-07.csv` — 40 rows (10 trials × 4 angles), columns `trial, angle_deg, adc_value, capture_date`.
- **Plot script:** `scripts/flex_bench/plot_bench.py` — regenerates `images/flex_bench_scatter.png` from the CSV. Requires matplotlib + numpy in the local venv (not in `requirements.txt`; figure-generation only).
- **Figure output:** `images/flex_bench_scatter.png` — box-plus-strip plot of the 0°/30°/60° measurements; intended as the right panel of paper Fig. 5.
- **Arduino sketch:** to be committed under `scripts/flex_bench/` once Vatsalya shares the code used for capture.
- **Bench-setup photo:** to be added at `images/flex_thumb_bench.jpg` (left panel of paper Fig. 5).

## Limitations and forward path

- Single sensor, single finger, single mounting jig — no inter-sensor or inter-finger variability captured.
- Off-platform: the Pi 5 / MCP3008 path described in §III-B-2 of the paper is **not exercised** by this characterization. Subsystem-level integration data (R1's contingency #1 in its strict reading) remains future work.
- 0–60° range omits the high-bend regime needed for full hand open/close (Item 3.5). Replacement with higher-grade flex sensors that retain linearity to ≥90° is a planned next step before clinical bradykinesia claims can be made.

## Cross-references

- Paper §III-B-2 — flex subsystem hardware description (Pi 5 + MCP3008 deployment target)
- Paper §V-D — bench characterization results (this document is the source)
- Paper §VIII — cost-reduction story (Arduino Nano 33 BLE Sense Lite as candidate target)
- `docs/validation-results.md` — IMU / Pi 5 validation (separate scope)
- `docs/camera-ready-edits.md` — full list of paper edits this work feeds
