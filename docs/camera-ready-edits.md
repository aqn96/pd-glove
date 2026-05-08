# AIIoT 2026 Camera-Ready Edit Checklist

**Paper:** "Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification"
**Conference:** IEEE AIIoT 2026 (Accept with Major Revision)
**Reviewer ask this list addresses:** R1 contingency #1 (empirical data for the integrated flex-sensor subsystem) and the convergent R1/R3 critique that too much of the framework reads as "planned."

This document is the persistent reference for what changes between the accepted manuscript and the camera-ready version. Items are grouped by section. Each item names the change and the rationale so co-authors can fix things without re-deriving the reasoning.

## Reviewer-driven priorities

1. **R1 #1 — flex-sensor empirical data.** Addressed via off-platform thumb bench characterization on Arduino Nano 33 BLE Sense Lite. See `docs/flex-bench-characterization.md`.
2. **R1 #2 — TFLite latency benchmark on Pi 5.** Separate workstream. Not covered by this checklist.
3. **R1 #3 / R3 — clinical cohort weighted-kappa.** Out of scope for camera-ready; reframe as Study II.
4. **R1 #4 — close 88.9–89.3 Hz vs 100 Hz gap.** Out of scope for camera-ready.

## Scope of "in progress" language

Only the **flex** subsystem moves out of "pending" — and only at the bench level. Do NOT strip "pending" / "planned" hedges from:

- TFLite inference (still not deployed)
- MQTT publishing (still not implemented)
- MediaPipe compliance validation (still planned)
- CH4 (Pinky) IMU hardware fault (real, unresolved)
- Clinical cohort weighted-kappa (deferred)

Stripping these other hedges turns the over-claim risk reviewers already noted in §III-B-1 into a much bigger problem.

## Required paper edits

### Abstract

- **Soften the "each finger has a flex sensor" claim.** Current text reads "Each finger is equipped with an inertial measurement unit (IMU) and a resistive flex sensor." With thumb-only flex bench data, this overstates validation. Replace with:
  > "Each finger position is designed to host an IMU and a resistive flex sensor; preliminary characterization in this paper covers four IMU channels and a single-finger flex bench validation, with full integration deferred to subsequent work."

### §I-B Contributions

- **Optional softening:** "5×flex sensors" → "5 flex sensor channels (one validated at bench level, see §V-D)." Defensive; not strictly required.

### §III-B-2 Flex Sensor Subsystem

- **Add one sentence acknowledging the off-platform validation,** so §III-B-2 (which describes the Pi 5 + MCP3008 target) does not contradict §V-D (which reports Arduino bench data):
  > "Bench characterization of the flex channel was conducted off-platform on an Arduino Nano 33 BLE Sense Lite (see §V-D and §VIII); MCP3008 integration with the Pi 5 host is pending."
- No Fig. 2 redraw required — the schematic still represents the deployment target.

### §III-E Patient Exercise Protocol

- The previous version had a closing line stating "Exercises 2–4 are currently validated using the IMU subsystem; full flex sensor integration will be completed upon hardware arrival." This was removed in the latest draft. **Add it back in a softer form** so Exercises 2 and 3 do not read as if flex sensors are already capturing tap rate, ROM, and decrement:
  > "Bradykinesia metrics from flex sensors are reported as simulated placeholders in the dashboard examples in this paper; bench-level flex characterization is presented in §V-D."

### §V-C Sampling Stability and I2C Reliability

- The current draft contains a forward reference: "Flex sensor preliminary characterization results are presented in Section V.E pending trial completion." **Two fixes needed:**
  1. Change "Section V.E" to "Section V-D" — the prior §V-D ("Current Implementation Scope") was deleted in the latest draft, so the new flex section naturally takes that slot.
  2. Drop "pending trial completion" since trials are now complete (data collected 2026-05-07; results in §V-D).
  Suggested replacement:
  > "Flex sensor preliminary characterization results are presented in Section V-D."

### §V-D Flex Sensor Bench Characterization (NEW)

**Add a new subsection** after §V-C (the prior §V-D "Current Implementation Scope" was deleted in the latest draft, so the new flex section takes that slot). Numbers below are computed from `data/flex_bench_thumb_2026-05-07.csv` and documented in `docs/flex-bench-characterization.md`.

**Ready-to-paste draft:**

> **V-D. Flex Sensor Bench Characterization**
>
> To validate flex-channel behavior independently of the Pi 5 host, a single SparkFun SEN-10264 flex sensor was characterized off-platform on an Arduino Nano 33 BLE Sense Lite. The sensor was configured as a voltage divider with a 10 kΩ pull-down on a 3.3 V rail and sampled at 12-bit resolution by the Nano's onboard ADC. The sensor was mounted on a thumb-jig holding it at three discrete bench positions: 0° (flat), 30°, and 60°. The 60° upper bound was selected because the SEN-10264 exhibits documented resistive-ink hysteresis above ~70°; 0–60° spans the linear operating range and the curvature region clinically relevant for finger tapping (Item 3.4) and partial hand open/close (Item 3.5).
>
> Across N=10 trials per angle, the channel produced a monotonically decreasing mean ADC response (Table II, Fig. 5), consistent with the expected increase in sensor resistance with bend. Separability between the 0° and 60° conditions is large (Cohen's d = 2.15); 0° is well separated from 30° (d = 1.87) but 30° and 60° are only marginally separated (d = 0.68), with 1σ envelopes partially overlapping. The bench data therefore supports a flat-vs-bent discrimination claim at the channel level but does not yet support fine-grained graded angular reporting on this rig; the latter is contingent on higher-grade flex sensors and subsystem-level integration with the Pi 5 host.
>
> This characterization is component-and-MCU level rather than full subsystem integration: the Pi 5 + MCP3008 SPI path described in §III-B-2 remains pending. The Nano's onboard 12-bit ADC and integrated IMU (BMI270 + BMM150) together demonstrate that both sensing modalities required by this framework are achievable on a single sub-$35 device, supporting the cost-reduction roadmap in §VIII.

**Table II — Flex-Channel Bench Characterization (Thumb, Arduino Nano 33 BLE Sense Lite)**

| Angle (°) | Mean ADC | SD ADC | N |
|---|---|---|---|
| 0 | 1036.08 | 35.78 | 10 |
| 30 | 961.89 | 43.04 | 10 |
| 60 | 924.91 | 63.67 | 10 |

**Fig. 5:** Two-panel — left: Vatsalya's thumb photo with the flex sensor mounted (target path `images/flex_thumb_bench.jpg`, pending); right: box-plus-strip plot of the 30 measurements at `images/flex_bench_scatter.png` (already generated, regenerable via `scripts/flex_bench/plot_bench.py`).

Suggested figure caption:

> **Fig. 5.** Flex-channel bench characterization on the thumb. (Left) Sensor mounting on the bench jig. (Right) ADC distribution across 0°, 30°, and 60° jig positions over 10 trials per angle on an Arduino Nano 33 BLE Sense Lite at 12-bit resolution. Diamonds mark per-angle means; horizontal lines mark medians. The 0° / 60° pair is cleanly separable (Cohen's d = 2.15); 30° / 60° envelopes partially overlap. Raw values from `data/flex_bench_thumb_2026-05-07.csv`.

### §VIII Limitations and Future Work

The current draft includes a flex-bench sentence that needs two fixes. Both are folded into a single ready-to-paste replacement below:

- **Replace "real-time angle acquisition at 33 Hz across clinically relevant curvature positions"** with raw-ADC framing consistent with §V-D, plus the IMU chip name (BMI270 + BMM150). The 33 Hz figure is **serial-output limited at 9600 baud, not an ADC ceiling** — disclose that in one short clause so a reviewer doesn't ask "why so slow?"

  Suggested replacement (the full sentence around the flex bench claim):
  > "Preliminary flex sensor characterization has been conducted on an Arduino Nano 33 BLE Sense Lite (~$30), confirming separable raw-ADC response across 0°/30°/60° bench positions at ~33 Hz (serial-output limited at 9600 baud; the underlying SAADC supports substantially higher rates). The Nano's onboard 12-bit ADC and integrated IMU (BMI270 + BMM150) together demonstrate that both sensing modalities required by this framework are achievable on a single sub-$35 device."

### Fig. 4 (dashboard)

- The caption was already updated in the latest draft to "pending full five-finger flex sensor integration" — keep as is.

## Author block

- **Add Vatsalya Cherukuri** to the manuscript author block, position after An Nguyen.
- **Reconcile EDAS:** the AIIoT 2026 review notification listed Madhu Babu Cherukuri on EDAS, but he was not in the prior manuscript block. With Vatsalya added, both the manuscript and EDAS author lists need to be brought into agreement. Confirm conference policy on author-list changes after acceptance and email the chair if required.

## Repo sync (when bench data lands)

These keep the repo and paper consistent — reviewers may consult the linked GitHub.

1. **`docs/flex-bench-characterization.md`** — fill in the placeholder results table from the actual CSV, lock the ADC bit-depth and sample rate.
2. **`docs/validation-results.md:16`** — change scope line from "Tremor only (flex/bradykinesia pending)" to "Tremor (Pi 5, 4 IMU channels) + flex bench characterization (Arduino Nano 33 BLE Sense Lite, single thumb channel, off-platform)."
3. **`README.md`** — flex sensor row in the hardware table: change status from "⏳ Pending" to "✅ Bench validated (thumb only, off-platform)." Update the Validated checklist (~line 110) similarly. Keep the MCP3008 + Pi 5 integration items unchecked — they are not validated.
4. **`images/flex_thumb_bench.jpg`** — add Vatsalya's thumb-on-jig photo. Reference it from paper Fig. 5 and from `docs/flex-bench-characterization.md`.
5. **`data/flex_bench_thumb_<DATE>.csv`** — add the raw 30-measurement dataset with columns specified in `flex-bench-characterization.md`.
6. **`scripts/flex_bench/`** — commit the Arduino sketch used for capture so the bench setup is reproducible.
7. **`docs/README.md`** — add `flex-bench-characterization.md` and this file to the index.

## Honest-disclosure checklist

Before submitting, verify the following are accurate as written:

- [ ] No claim of "integrated flex-sensor subsystem" in the Pi 5 / MCP3008 sense — only off-platform bench characterization.
- [ ] All flex numbers in the paper are raw ADC, not degrees.
- [ ] SD at each angle is disclosed, including the worst angle.
- [ ] ADC bit-depth and sample rate are stated (not just inferred).
- [ ] The IMU on the Nano 33 BLE Sense Lite is named when the "both modalities on one $35 device" claim is made.
- [ ] §III-B-1 still acknowledges CH4 fault.
- [ ] §V-A still reports four-channel IMU validation only.
- [ ] §VII Discussion does not retroactively claim flex results that §V-D did not produce.
