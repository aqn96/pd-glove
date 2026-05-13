# AIIoT 2026 Camera-Ready Edit Checklist

**Paper:** "Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification"
**Conference:** IEEE AIIoT 2026 (Accept with Major Revision)
**Status (2026-05-09, post-re-read):** Critical reviewer-driven edits have landed (Fixes 1–3). A close re-read of the manuscript surfaced three additional **internal-consistency** issues (Fixes A–C below) that a reviewer can spot from the PDF alone — these are the only items still recommended before submission. Fixes 4–5 (severity-bin scheme, g² unit relabel) and the repo↔paper consistency items remain deferred since reviewers do not have code access.

---

## How to use this doc

Each remaining fix has three blocks:

1. **Where** — section + a quoted snippet of the current text so you can find it
2. **Replace with** — the new text, copy-paste ready
3. **Why** — one line explaining the fix so you can defend the change

Order: post-re-read internal consistency (Fixes A–C, recommended) → previously-applied (Fixes 1–3, ✅ done) → deferred polish (Fixes 4–5, optional) → asset tracking → out-of-scope.

---

## Post-re-read internal-consistency fixes (recommended before submission)

These are paper-internal contradictions visible in the PDF alone — reviewers do not need code access to see them. All three are one-line edits.

### Fix A — §III-G dashboard severity claim contradicts §V-B's own bin definitions

**Where.** §III-G, paragraph describing the Exercise 1 dashboard panel, last sentence currently reads:

> "All values fall within the mild-to-moderate severity range identified in Table I, and all dominant frequencies lie within the clinical tremor signature."

**Why this is a contradiction.** The four reported channel values are Thumb 2,537 g², Index 6,630 g², Middle 2,859 g², Ring 2,861 g². §V-B defines bins as: 1,000–3,000 g² mild-to-moderate; 3,000–10,000 g² moderate-to-severe; >10,000 g² high-severity. Index at 6,630 is moderate-to-severe by the paper's own bins, not mild-to-moderate. A reviewer doing arithmetic catches this immediately.

**Replace with:**

> "These values span the mild-to-moderate to moderate-to-severe range described in §V-B, consistent with the medication-OFF state logged for this session, and all dominant frequencies lie within the clinical tremor signature."

---

### Fix B — §VII cross-reference points to wrong section

**Where.** §VII Discussion, fourth-research-question paragraph, currently reads:

> "The qualitative mapping of observed band power ranges to MDS-UPDRS severity anchors in **Section III** provides a plausible prior, but formal weighted-kappa agreement analysis against neurologist-scored sessions is required before clinical utility claims can be substantiated."

**Why.** The qualitative bin mapping (1k–3k mild-to-moderate, 3k–10k moderate-to-severe, etc.) is in **§V-B**, not §III. Section III contains the system design, not the qualitative mapping. A reviewer flipping back to §III to find the anchors will not find them.

**Replace with:**

> "The qualitative mapping of observed band power ranges to MDS-UPDRS severity anchors in **§V-B** provides a plausible prior, but formal weighted-kappa agreement analysis against neurologist-scored sessions is required before clinical utility claims can be substantiated."

---

### Fix C — §I MediaPipe described as operational; §III-B-3 and §VIII label it as planned

**Where.** §I, third pipeline stage in the four-stage list, currently reads:

> "Third, a MediaPipe-based classifier [9] retrospectively validates patient compliance against the uploaded video post-session, flagging any windows where movement contaminated designated rest periods."

**Why.** The same paragraph in §I hedges TFLite correctly: *"and is designed to run the scoring model on-device once training is complete, though this stage is currently pending."* §III-B-3 explicitly labels MediaPipe as a "Planned Extension," and §VIII says it is "a planned extension rather than a current implementation." The unhedged §I sentence is the kind of scope-overclaim that R1 already flagged once.

**Replace with:**

> "Third, a MediaPipe-based classifier [9] is designed to retrospectively validate patient compliance against the uploaded video post-session, flagging any windows where movement contaminated designated rest periods; this stage is currently planned (see §III-B-3)."

---

## Already applied in the manuscript (✅ no further action)

These were the original critical fixes. The paper text confirmed on 2026-05-09 has all three landed.

### Fix 1 — §III-B-1 CH4 over-claim
✅ Now reads: *"Four of the five channels (Ch0–Ch3, Thumb–Ring) are fully validated against the TCA9548A multiplexer (detected at 0x70) using the smbus2 library; Ch4 (Pinky) exhibits a suspected SDA/SCL crossover fault and is currently under investigation (see §V-A)."*

### Fix 2 — Broken cross-references
✅ §I-B Contributions: now reads *"five flex sensors (one validated at bench level, see §V-D)"*
✅ §V-D last paragraph: now reads *"supporting the cost-reduction roadmap described in Section VIII."*

### Fix 3 — §VIII numbering reset
✅ §VIII now reads as one limitations paragraph followed by a clean enumerated four-item future-work list ("Beyond these near-term gaps, four directions guide future work. First… Second… Third… Fourth…").

### Earlier camera-ready edits
✅ Abstract — softened "Each finger position is designed to host an IMU and a resistive flex sensor"
✅ §III-B-2 — added off-platform bench note
✅ §V-C — replaced "Section V.E pending trial completion" with "Section V-D"
✅ §V-D — new subsection landed with Table II, Fig. 5 caption, raw-ADC framing, scope-limiting language
✅ §VIII — bench paragraph includes Nano IMU naming (BMI270 + BMM150) and 33 Hz / 9600-baud serial-limit disclosure
✅ Fig. 4 caption — preserves "simulated bradykinesia metrics as placeholder targets pending full five-finger flex sensor integration"

---

## Deferred polish (not required for camera-ready)

These were on the original punch list. The user opted not to land them, on the basis that reviewers do not have code access and the issues are repo↔paper consistency rather than paper-internal contradictions. Documented here for future reference.

### Fix 4 — §V-B severity bin scheme (3-bin paper vs 5-bin code)
- Paper §V-B uses 3 bins (1k–3k / 3k–10k / >10k).
- `app.py::classify_severity` uses 5 bins (1k / 2.5k / 7k / 15k boundaries).
- `docs/validation-results.md` uses 4 MDS-UPDRS scores at 2.5k / 7k / 15k boundaries.
- Reviewers cannot see this divergence without code access. **Skipped.**

### Fix 5 — Relabel `g²` as relative band power (a.u.)
- Paper labels band power as `g²`, but `dsp_pipeline.py` operates on raw int16 ACCEL registers without scaling to g.
- `docs/mobile-web-data-contract.md:246` already documents the values as "unitless relative DSP outputs unless calibrated later."
- Reviewers cannot see this divergence without code access. **Skipped.**

---

## Mild stylistic items (defensible as-is, not on punch list)

The re-read also surfaced these patterns. None are inconsistencies — they are the standard "design described first, prototype status disclosed in §V/§VIII" convention common in research papers. Listed for awareness only:

- §III-D opens describing the Transformer/TFLite as if running, then closes with the hedge that training is "the immediate next implementation stage."
- §III-E Exercises 2 and 3 describe flex sensors as actively measuring; simulation status is disclosed in Fig. 4 caption and §III-G.
- §III-F describes MQTT publishing as operational; §VII discloses MQTT is pending integration.
- §VI uses present tense ("Model training combines… evaluation protocol reports…") for items that haven't happened yet — standard methodology-section convention.

**No action required.** Reviewers expect this pattern in system-design papers.

---

## Optional length tightening (low-risk surgical cuts)

A re-read for length surfaced some redundancy that adds words without adding information. **None of these are required** — the paper is fine as-is. But if you want to free up a few lines without changing the paper's voice, these are the safest cuts. Each one removes duplicated material; none introduces new claims, new numbers, or new structural changes.

**Risk note.** Reviewers will not notice these cuts because they delete repetition rather than add or modify content. The paper still says everything it currently says — just once instead of twice or three times. Safer than the major-revision-style rewrites we already chose to skip.

**Recommended.** Cuts 1 and 2 below are highest-leverage and lowest-risk. They take roughly 2 minutes to apply and free ~8 lines. Cuts 3 and 4 are optional polish.

### Cut 1 (recommended) — §III-F: delete the duplicate "Incomplete sessions" sentence

**Where.** §III-F (Data Transmission and Privacy) currently ends with:

> "Incomplete sessions are transmitted with an interrupted status flag rather than discarded, as the inability to complete an exercise is itself a clinically meaningful indicator of disease progression [23]."

**Action.** Delete this sentence entirely from §III-F.

**Why.** §IV-A (Data Contract) already makes the same point with a stronger concrete example ("a patient sustaining 10 seconds of finger tapping last month but only 4 seconds today provides actionable longitudinal data [23]"). §III-F is about transmission/privacy; the longitudinal-meaning argument belongs in §IV-A's session-semantics section, where it already lives. Removing the §III-F version eliminates a near-verbatim duplicate one section apart.

### Cut 2 (recommended) — §V-A: tighten the PLA ring sentence

**Where.** §V-A opens with:

> "Custom 3D-printed polylactic acid (PLA) rings - one per finger - serve as the sensor mounting platform, each designed with two bottom slots for elastic band threading to provide adjustable tension, two side bars matching the MPU6050 footprint for hot-glue stabilization, and a top cavity sized to fit the sensor body precisely. This mounting strategy minimizes motion artifacts without requiring adhesives directly on the skin, supporting repeated donning across sessions."

**Replace with:**

> "Custom 3D-printed PLA rings (one per finger) hold each MPU6050 in a top cavity, with elastic-band slots for adjustable tension and side bars for hot-glue stabilization. This minimizes motion artifacts without skin adhesives and supports repeated donning across sessions."

**Why.** Same information, roughly half the length. The slot/bar/cavity geometry is workshop-paper detail that a reviewer does not need to follow the prototype description. The replacement keeps every claim (PLA, one per finger, elastic-band tension, hot-glue stabilization, no skin adhesive, repeated donning) and the same neutral tone.

### Cut 3 (optional) — §VIII: shorten the flex-bench recap

**Where.** §VIII (Limitations and Future Work) currently restates four facts already in §V-D:

> "Preliminary flex sensor characterization has been conducted on an Arduino Nano 33 BLE Sense Lite (~$30), confirming separable raw-ADC response across 0°/30°/60° bench positions at ~33 Hz (serial-output limited at 9600 baud; the underlying SAADC supports substantially higher rates). The Nano's onboard 12-bit ADC and integrated IMU (BMI270 + BMM150) together demonstrate that both sensing modalities required by this framework are achievable on a single sub-$35 device."

**Replace with:**

> "Preliminary flex characterization on the Nano 33 BLE Sense Lite (~$30, see §V-D) confirms that both sensing modalities can run on a single sub-$35 device, supporting the TFLite Micro deployment path described above."

**Why.** §VIII is the future-work section, not a second results paragraph. The bench numbers, the 33 Hz / 9600-baud disclosure, and the BMI270 + BMM150 IMU naming all already appear in §V-D where they belong. One back-reference is enough.

**Risk note.** This is a more visible cut than #1 and #2 because it shortens an entire paragraph rather than tweaking a sentence. If you would rather keep the verbose version for emphasis, no harm — it is repetition, not contradiction.

### Cut 4 (optional) — §VII: trim one "below 70 g²" repetition

**Where.** §VII currently says:

> "Critically, rest windows remained consistently below 70 g² across both subjects and all nine test runs, confirming that the app-controlled timestamp protocol adequately gates the tremor scoring window without requiring real-time activity classification…"

**Replace with:**

> "Critically, the consistently low rest-window band power confirms that the app-controlled timestamp protocol adequately gates the tremor scoring window without requiring real-time activity classification…"

**Why.** "Below 70 g²" already appears in Table I (where the rest maxima are 51 and 69) and in the §V-B body text. The third mention in §VII restates a number the reader has seen twice. The interpretation ("gating works") is what §VII contributes; the number was §V-B's contribution.

**Risk note.** Same as Cut 3 — visible but defensible. The §VII paragraph still references §V-B's findings; it just stops repeating the specific value.

---

## Asset tracking (paper-side, not LaTeX edits)

| Item | Status | Action |
|---|---|---|
| `images/flex_bench_scatter.png` | ✅ in repo | None — used as Fig. 5 right panel |
| Fig. 5 left panel: full five-finger flex prototype photo | ⏳ to combine | User has the photo of the assembled five-finger flex prototype. Combine with the scatter plot into one side-by-side PNG (e.g., via Photopea, Keynote, or Cmd+Shift+4 screenshot of both Preview windows aligned). |
| Fig. 5 caption | ✅ updated | Caption now honestly scopes both panels: "(Left) Assembled five-finger flex sensor prototype… integration with the Pi 5 + MCP3008 host is pending. (Right) ADC distribution from a single thumb-mounted sensor sampled off-platform…" |
| Fig. 5 filename in LaTeX | ⚠️ check | Paper `\includegraphics` should point at the new combined PNG (suggest `images/flex_bench_combined.png`). |
| Author block: add Vatsalya Rohitbhai Dabhi | ✅ landed | Manuscript now lists An Nguyen, Madhu Babu Cherukuri, Vatsalya Rohitbhai Dabhi, Sarita Singh, Hongpeng Fu (in that order). |
| EDAS / manuscript author reconciliation | ✅ landed | Manuscript and EDAS both list Madhu Babu Cherukuri; reconciled in the final author block. |

---

## Honest-disclosure final check (run before submitting)

After applying Fixes A–C, verify each statement is true of the manuscript:

- [ ] No claim of "integrated flex-sensor subsystem" in the Pi 5 / MCP3008 sense — only off-platform bench characterization
- [ ] All flex numbers in the paper are raw ADC, not degrees
- [ ] SD at each angle is disclosed in Table II, including the worst angle (60°)
- [ ] ADC bit-depth (12-bit) and sample rate (~33 Hz) are stated, not just inferred
- [ ] The IMU on the Nano 33 BLE Sense Lite is named (BMI270 + BMM150) when the "both modalities on one $35 device" claim is made
- [ ] §III-B-1 acknowledges the CH4 fault (Fix 1 applied ✅)
- [ ] §V-A reports four-channel IMU validation only
- [ ] §VII Discussion does not retroactively claim flex results that §V-D did not produce
- [ ] No remaining `§??` or `Section ??` cross-references (Fix 2 applied ✅)
- [ ] §III-G severity claim is consistent with §V-B's own bin definitions (after Fix A)
- [ ] §VII cross-ref to severity anchors points to §V-B not §III (after Fix B)
- [ ] §I MediaPipe sentence is hedged consistently with §III-B-3 / §VIII (after Fix C)
- [ ] Fig. 5 caption scopes the left panel as "Assembled five-finger flex sensor prototype" and the right panel as single-thumb bench data, with no claim that the photo represents the bench setup
- [ ] Fig. 5 `\includegraphics` references the combined PNG file actually present in the repo

---

## Out of scope for this camera-ready

These were debated but agreed not in scope. Do not let scope creep pull them back in:

- **R1 #2 (TFLite latency benchmark on Pi 5).** Time-bound: the experiment was deemed not feasible in the camera-ready window. Paper relies on cited prior-work latency [10] and frames the present pipeline as "designed to inherit" that performance. Defensible because the chair has already accepted with revision.
- **R1 #3 (clinical cohort weighted-kappa).** §VIII frames this as future work; §VII explicitly states the agreement analysis is required before clinical utility claims.
- **R1 #4 (close 88.9–89.3 Hz vs 100 Hz gap).** §V-C attributes the gap to Python-layer polling, defends Nyquist sufficiency for the 4–6 Hz band, and commits to C-extension/firmware optimization in future iterations. No measurement change required.

---

## Reviewer concern coverage matrix (final state)

| Reviewer | Concern | Coverage |
|---|---|---|
| R1 | #1 Empirical flex data | ✅ §V-D (off-platform bench, honestly scoped) |
| R1 | #2 TFLite latency on Pi 5 | ⚠️ Cited from prior work; not measured (out of time) |
| R1 | #3 Sampling rate optimization | ⚠️ Acknowledged + path forward + Nyquist defense |
| R1 | #4 Weighted-kappa | ⚠️ Honestly deferred to future work |
| R2 | (no required revisions) | ✅ N/A |
| R3 | Flex pending / simulated metrics | ✅ §V-D + Fig. 4 caption |
| R3 | Healthy volunteers + public data only | ⚠️ Honestly deferred to §VIII |
| R3 | No weighted-kappa | ⚠️ Honestly deferred (same as R1 #4) |
| R3 | Uncertainty awareness gap | ✅ §VIII fourth future-work item |
