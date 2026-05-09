# AIIoT 2026 Camera-Ready Edit Checklist

**Paper:** "Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification"
**Conference:** IEEE AIIoT 2026 (Accept with Major Revision)
**Status (2026-05-09):** Most camera-ready edits have landed in the manuscript. This file now tracks the **remaining** fixes only, with ready-to-paste blocks. See bottom for what is already done.

---

## How to use this doc

Each remaining fix has three blocks:

1. **Where** — section + a quoted snippet of the current text so you can find it
2. **Replace with** — the new text, copy-paste ready
3. **Why** — one line explaining the fix so you can defend the change

Fixes are ordered: critical (must fix) → recommended → cleanup.

---

## Critical fixes (must land before camera-ready submission)

### Fix 1 — §III-B-1 IMU Subsystem: remove "all five channels" over-claim

**Where.** §III-B-1, last sentence currently reads:

> "All five IMUs have been validated: the TCA9548A is detected at 0x70, and accelerometer data has been successfully read from all five channels via Python using the smbus2 library."

**Replace with:**

> "Four of the five channels (Ch0–Ch3, Thumb–Ring) are fully validated against the TCA9548A multiplexer (detected at 0x70) using the smbus2 library; Ch4 (Pinky) exhibits a suspected SDA/SCL crossover fault and is currently under investigation (see §V-A)."

**Why.** Direct contradiction with §V-A, which already discloses the CH4 fault. Reviewer R1 already flagged scope-overclaim once — leaving this in is the most likely path to a "this is misleading" comment in IEEE Xplore review.

---

### Fix 2 — Two broken cross-references (`§??`)

LaTeX did not resolve two references. Both need explicit section labels.

**2a. §I-B Contributions, first bullet.** Current:

> "five flex sensors (one validated at bench level, see §??)"

**Replace with:**

> "five flex sensors (one validated at bench level, see §V-D)"

**2b. §V-D, last paragraph, last sentence.** Current:

> "...supporting the cost-reduction roadmap described in Section ??."

**Replace with:**

> "...supporting the cost-reduction roadmap described in Section VIII."

**Why.** IEEE Xplore copy-edit will reject `??`. These are mechanical fixes — likely caused by `\ref{}` pointing to a label that was renamed.

---

### Fix 3 — §VIII Limitations and Future Work: numbering reset

**Where.** §VIII currently opens with one "First… Second…" enumeration (clinical cohort, MediaPipe), then immediately resets with another "First… Second… Third…" enumeration (lower-cost devices, longitudinal scoring, uncertainty-aware scoring, fairness auditing). Two competing enumerations in one section reads like a merge artifact.

**Replace the entire §VIII body with:**

> The current prototype has near-term limitations the next development cycle will address. Initial training relies exclusively on public datasets (mPower, PhysioNet) with a healthy volunteer cohort for hardware calibration; clinical validation against a diagnosed PD patient cohort remains future work [3]. Real-time MediaPipe compliance validation is a planned extension rather than a current implementation; the structured protocol currently provides temporal gating through app-controlled timestamps [9].
>
> Beyond these near-term gaps, four directions guide future work. **First**, lower-cost ARM-class edge devices will be evaluated as replacements for the Raspberry Pi 5, including the Raspberry Pi Zero 2W (~\$15) and ESP32-class microcontrollers (~\$5–10). Preliminary flex sensor characterization has been conducted on an Arduino Nano 33 BLE Sense Lite (~\$30), confirming separable raw-ADC response across 0°/30°/60° bench positions at ~33 Hz (serial-output limited at 9600 baud; the underlying SAADC supports substantially higher rates). The Nano's onboard 12-bit ADC and integrated IMU (BMI270 + BMM150) together demonstrate that both sensing modalities required by this framework are achievable on a single sub-\$35 device. Because the inference pipeline operates on compact INT8-quantized DSP feature vectors rather than raw waveforms, TFLite Micro deployment on these constrained devices is architecturally straightforward and consistent with prior work [10]. **Second**, longitudinal score accumulation will enable periodic model fine-tuning without transmitting raw biometric data in plaintext beyond the point of capture. **Third**, uncertainty-aware scoring will be incorporated so the system can flag predictions it is less confident about rather than producing a score in all cases without qualification. **Fourth**, fairness auditing across patient demographics will be introduced to ensure the model performs consistently across age groups, sex, and disease stage, rather than being implicitly optimized for a narrow population [11].

**Why.** Resolves the duplicate "First/Second" enumerations into one section opener (near-term limitations) plus one cleanly numbered four-item future-work list. No content lost.

---

## Recommended fix (low effort, high readability)

### Fix 4 — §V-B severity bins: align with the validated dataset

**Where.** §V-B (Tremor Discrimination Results), the paragraph after Table I, currently reads:

> "Across all tremor captures, the observed severity range maps qualitatively to the MDS-UPDRS 0–4 clinical scale [1]: band power in the range 1,000–3,000 g² corresponds approximately to mild-to-moderate severity (scores 1–2), 3,000–10,000 g² to moderate-to-severe (scores 2–3), and values exceeding 10,000 g² to high-severity endpoints (scores 3–4), consistent with the exaggerated tremor protocol used in test one. This qualitative mapping will be formalized through Transformer-based scoring once the TFLite model is trained on the validated dataset."

**Replace with:**

> "Across all tremor captures, the observed severity range maps qualitatively to the MDS-UPDRS 0–4 clinical scale [1]: relative band power in the range 1.4–2.5 K corresponds to score 1 (slight), 2.5–7 K to score 2 (mild), 7–15 K to score 3 (moderate), and 15–26 K to score 4 (marked) — the latter consistent with the exaggerated tremor protocol used in test one. This qualitative mapping will be formalized through Transformer-based scoring once the TFLite model is trained on the validated dataset."

**Why.** The paper's previous 3-bin scheme (1–3 K / 3–10 K / >10 K) does not match either `app.py::classify_severity` (5-bin, boundaries at 1 K / 2.5 K / 7 K / 15 K) or `docs/validation-results.md` (4 MDS-UPDRS scores at 2.5 K / 7 K / 15 K boundaries). Fig. 4 in the paper is rendered against the code's bins. The replacement aligns the prose with both the dashboard image a reviewer would compare against and the validation-results document linked from the repo. It also drops "g²" in favor of "relative band power" — see Fix 5.

---

## Cleanup fix (small but visible)

### Fix 5 — Relabel `g²` as relative band power, add one footnote

**Why.** The paper labels band power as `g²` throughout, but `dsp_pipeline.py` operates on raw int16 ACCEL_XOUT registers without scaling to `g`, so the actual unit is "filtered ADC magnitude squared, summed over the 4–6 Hz bins." `docs/mobile-web-data-contract.md:246` already documents this as "unitless relative DSP outputs unless calibrated later." The cleanest fix is to relabel uniformly and add one footnote at first use.

The fix is mechanical — three locations:

**5a. Table I header.** Current row: `Band Power (g²)`. **Replace with:** `Band Power (a.u.)¹`

**5b. First mention in §V-B body.** Current opening of the post-table paragraph mentions "70 g² across all channels":

> "Rest windows consistently exhibited band power below 70 g² across all channels and subjects, providing a clear empirical boundary between pathological and baseline states."

**Replace with:**

> "Rest windows consistently exhibited band power below 70 a.u. across all channels and subjects, providing a clear empirical boundary between pathological and baseline states.¹"

Then add this footnote (1) at the bottom of the column or as a `\footnotetext`:

> "¹ Band power is reported in arbitrary units (a.u.) corresponding to filtered raw int16 accelerometer magnitude squared, summed over the 4–6 Hz bins. Values are not calibrated to physical units (g²) at this stage; calibration is planned alongside Transformer model training."

**5c. All remaining `g²` instances.** Three more places to swap `g²` → `a.u.`:
- §III-G dashboard description: "Thumb (2,537 g²,..." → "Thumb (2,537 a.u., ..." (and the three other channel values in the same sentence)
- §VII Discussion: "rest windows remained consistently below 70 g²" → "below 70 a.u."
- Any caption text referring to `g²` in Fig. 4

After these swaps, do a final find-and-replace for `g²` to confirm zero remaining occurrences.

**Why.** A reviewer who reads §III-B-1 (raw `accel_x_high`/`accel_x_low` register reads, no scaling) and then reads `g²` in §V-B will notice the gap. One footnote at first use defuses this without bloating the text.

---

## Asset tracking (not a paper edit, but needed before submission)

| Item | Status | Action |
|---|---|---|
| `images/flex_bench_scatter.png` | ✅ in repo | None — already referenced from §V-D |
| Fig. 5 left panel: thumb-on-jig photo | ⏳ pending | Need Vatsalya's photo. Paper's Fig. 5 currently references `flex_bench_combined.png` — either generate the combined left+right figure, or update the LaTeX to use the existing `flex_bench_scatter.png` and add the photo as a separate sub-figure. |
| Fig. 5 filename in LaTeX | ⚠️ inconsistent | Paper `\includegraphics` references `flex_bench_combined.png`; repo has `flex_bench_scatter.png`. Reconcile when the photo lands. |
| Author block: add Vatsalya Cherukuri | ⏳ pending | Add to manuscript author list, position after An Nguyen. |
| EDAS / manuscript author reconciliation | ⏳ pending | EDAS lists Madhu Babu Cherukuri; manuscript does not. Confirm with chair before camera-ready. |

---

## Already landed (no action required)

These were on the original checklist and are now in the manuscript text the user pasted on 2026-05-09:

- ✅ **Abstract** — softened to "Each finger position is designed to host an IMU and a resistive flex sensor"
- ✅ **§III-B-2** — added off-platform bench note: "Bench characterization of the flex channel was conducted off-platform on an Arduino Nano 33 BLE Sense Lite (see §V-D and §VIII)"
- ✅ **§V-C** — replaced broken forward-ref to "Section V.E pending trial completion" with "Section V-D"
- ✅ **§V-D** — new subsection landed with Table II, Fig. 5 caption, scoping language, raw-ADC framing, and the "component- and MCU-level rather than full subsystem integration" disclosure
- ✅ **§VIII** — bench paragraph includes Nano IMU naming (BMI270 + BMM150) and the 33 Hz / 9600-baud serial-limit disclosure
- ✅ **Fig. 4 caption** — "simulated bradykinesia metrics as placeholder targets pending full five-finger flex sensor integration" preserved

The `§III-E` simulation-disclosure sentence was intentionally not added in this edit pass — Fig. 4 caption + §III-G dashboard discussion already cover the simulation framing, and adding another disclosure in §III-E would have double-flagged the same point. This is a defensible judgment call and is not on the punch list.

---

## Honest-disclosure final check (run before submitting)

After applying Fixes 1–5, verify each statement is true of the manuscript:

- [ ] No claim of "integrated flex-sensor subsystem" in the Pi 5 / MCP3008 sense — only off-platform bench characterization
- [ ] All flex numbers in the paper are raw ADC, not degrees
- [ ] SD at each angle is disclosed in Table II, including the worst angle (60°)
- [ ] ADC bit-depth (12-bit) and sample rate (~33 Hz) are stated, not just inferred
- [ ] The IMU on the Nano 33 BLE Sense Lite is named (BMI270 + BMM150) when the "both modalities on one $35 device" claim is made
- [ ] §III-B-1 acknowledges the CH4 fault (after Fix 1)
- [ ] §V-A reports four-channel IMU validation only
- [ ] §VII Discussion does not retroactively claim flex results that §V-D did not produce
- [ ] No remaining `§??` or `Section ??` cross-references
- [ ] No remaining `g²` units (after Fix 5)
- [ ] Severity bins in §V-B match `app.py` / `docs/validation-results.md` (after Fix 4)

---

## Out of scope for this camera-ready

These were debated but agreed not in scope. Do not let scope creep pull them back in:

- **R1 #2 (TFLite latency benchmark on Pi 5).** Separate workstream. If An decides to address this, it adds a new subsection — not covered here.
- **R1 #3 (clinical cohort weighted-kappa).** Reframed as Study II in the paper's future-work language; do not attempt for camera-ready.
- **R1 #4 (close 88.9–89.3 Hz vs 100 Hz gap).** §V-C already attributes the gap to Python-layer polling overhead and notes future C-extension/firmware optimization. No change needed.
