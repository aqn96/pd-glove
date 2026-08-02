# Research Direction (post-coursework)

**An Nguyen · Northeastern University Khoury College · August 2026**

This is the research plan beyond CS 8674 Part II. The course timeline (D1 through D4)
lives in [`next-steps.md`](../next-steps.md); this document is about what the project
argues and how it gets there afterwards.

Status of every claim below is marked explicitly: **done**, **planned**, or **blocked**.
Clinical assertions are marked where they still need a clinician's sign-off.

---

## 1. The research claim

The project makes a **layered** claim (detail in §3.1). Layer 1 is a multimodal PD
detection and severity system across motion, voice, and gait: broad, deployable, and not
novel by itself. Layer 2 is the contribution:

**Per-finger inertial sensing captures inter-digit phase relationships that discriminate
Parkinsonian tremor from essential tremor, providing an EMG-free alternative to the
established alternating-versus-synchronous sign, in a deployable low-cost device.**

### The mechanism, and where it comes from

The strongest published discriminator between PD rest tremor and ET is **not** frequency
or amplitude — those overlap heavily, with both conditions sitting roughly in the 4–8 Hz
band [S1, S3]. It is the **phase relationship between antagonist muscle pairs**:

- **PD rest tremor: alternating pattern** (antagonist muscles contract out of phase)
- **ET rest tremor: synchronous pattern** (antagonist muscles contract together)

Nisticò et al. [S1] report **no overlap between the two diseases** on this feature: every
ET patient in their sample showed the synchronous pattern, every PD patient the
alternating one. It is classically measured with surface EMG [S2], which requires
electrodes and clinical setup.

The hypothesis this project tests is that **inter-digit phase, measured with per-finger
IMUs, is a usable proxy for that sign without EMG.** A wrist-mounted sensor measures
aggregate hand acceleration and spatially averages away the relative timing between
digits; five per-finger IMUs can resolve it directly. This is a narrower and better
grounded claim than "pill-rolling looks different," and it is the version that survives
the objection that IMU tremor classification has already been done (see §1.2).

Secondary discriminators reported in the literature, useful as additional features rather
than as the core claim: PD rest tremor amplitude is significantly higher than ET's [S1],
and ET shows higher burst duration and frequency [S2].

**Needs clinical verification.** The alternating/synchronous distinction is well
documented in the sources above, but two things should be confirmed with Prof. Singh or a
neurologist before the design depends on them: (a) how cleanly that separation holds in
unselected real-world patients rather than in a curated study sample, and (b) whether
inter-digit phase measured at the fingertips is a physiologically sound proxy for
antagonist-muscle phase measured at the forearm. Point (b) is an assumption this project
is making, not something the cited sources establish.

### Why this framing rather than "multimodal PD detection"

Multimodal fusion for PD detection is a crowded space and is not a contribution on its
own. Nor is edge deployment, nor methodological rigour (both matter, neither is novel).
The per-finger claim is narrower and considerably harder to dismiss because:

1. **iTex named this exact gap and did not fill it.** Verified against the paper directly
   (Ravichandran, Sadhu, Convey, Guerrier, Chomal, Mankodiya et al., *iTex Gloves: Design
   and In-Home Evaluation of an E-Textile Glove System for Tele-Assessment of Parkinson's
   Disease*, 2023, [PMC10054833](https://pmc.ncbi.nlm.nih.gov/articles/PMC10054833)). Their
   Background states:

   > "However, this approach has lower precision while measuring fine-grained movement
   > within fingers, unless individual IMU sensors are used for each finger for analysis of
   > specific MDS-UPDRS-III exercises such as finger tapping and hand open-close."

   iTex then built **one 6-DoF IMU per glove** plus three flex sensors (index, middle,
   thumb). This project has five IMUs and five flex sensors, one per finger. The closest
   prior system identified the limitation and did not address it.

   **Also worth citing from the same paper:** iTex targeted 128 Hz and achieved 82–87 Hz
   effective, traced to MQTT inter-payload interval averaging 364 ± 23 ms rather than any
   hardware ceiling. This glove sustains 88.9–89.3 Hz, which is *higher than the closest
   prior system actually achieved*. The repo currently frames 89 Hz as a shortfall against
   a 100 Hz target; it should be reframed as comfortably within the range the literature
   treats as sufficient, with a citation to what comparable systems deliver in practice.
2. **It has a built-in ablation.** Collapse the five per-finger channels to a single
   wrist-equivalent signal and measure what is lost. This is testable within a single
   cohort, no cross-dataset comparison needed.
3. **The clinical question is the hard one.** PD versus healthy controls is essentially
   tremor-versus-no-tremor. PD versus ET means classifying tremor *type*, which is the
   question a neurologist actually faces and where misdiagnosis genuinely happens.

### 1.2 Prior work on PD versus ET with wearables — this space is occupied

**Read this before claiming novelty.** IMU-based PD/ET discrimination is an active area,
not virgin territory. Thumb and index sensor placement has already been used. "We put IMUs
on fingers" is not by itself a contribution.

| Approach | Sensors | Reported performance | Cohort | Source |
|---|---|---|---|---|
| Balance and gait characteristics | Body-worn IMU | Best **F1 0.61** (neural net); 0.59 gradient boosting, 0.56 random forest | — | [S4] |
| Postural maneuver (stretched vs hanging) | **One IMU per hand**, 50 Hz | Sens **83%** / spec **75%** | 12 PD vs 12 ET | [S5] |
| Temporal fluctuations of tremor signal | Inertial | Preliminary | — | [S6] |
| Phase displacement, wearable validated against EMG | Wearable + EMG comparison | — | PD and ET | [S2, S7] |
| Multi-location hand accelerometry | Thumb, index, metacarpal, wrist | Severity assessment, not PD/ET classification | — | [S7] |
| Gait analysis, early PD vs ET | Wearable | — | — | [S8] |

**What remains open, and is therefore where the contribution has to live:**

1. **Five per-finger channels**, versus the one-to-four sensor sites used in the work
   above. [S5] used a single IMU per hand; [S7] used four locations but for severity, not
   differential diagnosis.
2. **Inter-digit phase as the explicit discriminating feature**, framed as an EMG-free
   proxy for the alternating/synchronous sign. Prior wearable work on phase displacement
   exists [S7] but validated against EMG rather than using per-finger resolution.
3. **Flex sensors** adding finger flexion (rigidity), which none of the above have.
4. **Edge deployment.** The work above is offline lab analysis. This project runs INT8
   inference on-device with raw data never leaving the glove.

**Note on the gait result.** Best F1 of 0.61 for PD versus ET from gait [S4] is weak. This
retroactively supports the decision in §3 to drop camera-based gait: gait is a poor
discriminator for this specific question, whatever sensor captures it.

### 1.3 Why the PD/ET distinction is worth solving

Different first-line medications with no overlap (levodopa for PD; propranolol or
primidone for ET), different prognosis (progressive neurodegeneration versus a generally
slower course), and a real misdiagnosis rate in both directions. When the distinction
cannot be resolved clinically, the current tiebreaker is DaTscan imaging, which needs a
radioactive tracer, specialised facilities, and significant cost. A low-cost wearable
that gives meaningful signal on this question matters most exactly where that imaging is
unavailable, which sharpens the accessibility argument already in the AIIoT paper.

**Sourcing status:** the medication, prognosis, and DaTscan claims in this paragraph are
general clinical knowledge stated without a citation read for this project. They are
uncontroversial but should be given proper references before appearing in a paper, and the
misdiagnosis rate in particular should be cited with an actual figure rather than
described as "real." Flagged rather than silently asserted.

**Scope honestly:** the device provides clinical decision support, not diagnosis. This is
already stated in the paper's Intended Use section and should stay there.

---

## 2. Where things actually stand

| Component | Status |
|---|---|
| PADS pipeline, subject-level splits, 42-feature extraction | **Done** (D2) |
| SVM / RF / CNN1D baselines on PADS PD-vs-HC | **Done** (D2) |
| MOMENT-1-large full fine-tune, F1 0.626 / AUROC 0.731 | **Done** (D2) |
| INT8 TFLite quantization, 19.6 KB, small accuracy cost | **Done** (D3) |
| Fairness audit (pooled 5-fold, class-balance explained) | **Done** (D3) |
| Latency benchmark on M3 Pro as ARM proxy | **Done** (D3) |
| AES-256-GCM payload encryption + MQTT v5 message expiry | **Done** (D3) |
| Real Pi 5 latency measurement | **Blocked** — hardware not currently accessible |
| Glove hardware: 4 of 5 IMU channels | **Done**; CH4 fault outstanding |
| Flex sensors on Pi 5 + MCP3008 | **Blocked** — thumb-only bench validation on Arduino so far |
| Voice modality | **Not started** |
| Gait modality | **Not started** |
| Tapping modality | **Not started** |
| mPower (Synapse) access | **Not started** — gates three of four modalities |
| Patient data collection | **Blocked** — IRB pending |

One of the four proposed modalities is built.

---

## 3. Architecture

### Full picture

```
PUBLIC PRETRAINING                     ADAPTATION                  DEPLOYMENT
(weak/clinical labels, large n)        (n = 15-20, clinical)       (edge)

┌─ PADS ──────────────────┐
│ 276 PD / 79 HC / 114 DD │
│ incl. 28 ESSENTIAL      │──> motion encoder ──┐
│ TREMOR  (only source)   │    (MOMENT -> PADS) │
│ wrist acc+gyro @100Hz   │                     │
└─────────────────────────┘                     │
                                                │  freeze / LoRA
┌─ mPower ────────────────┐                     │  (never full FT)
│ ~9.5k subjects, PAIRED  │                     v
│ self-reported labels    │              ┌──────────────┐        ┌─────────────┐
│                         │              │ paired glove │        │ Raspberry   │
│  voice  (sustained /a/) │──> voice ────│ + phone data │───────>│ Pi 5        │
│  walking (in pocket)    │──> gait  ────│ from own     │        │ INT8 TFLite │
│  tapping (screen)       │──> tapping ──│ PD/ET/HC     │        │ 19.6 KB     │
│                         │              │ cohort       │        │ local infer │
│  (+ fusion head can be  │──> fusion ───│              │        └──────┬──────┘
│   PRETRAINED here, all  │    head      └──────────────┘               │
│   3 from same person)   │                                      AES-256-GCM
└─────────────────────────┘                                      + MQTT expiry
                                                                        │
                                                                        v
                                                                   cloud: score
                                                                   only, never
                                                                   raw signal
```

**The one thing to understand from this diagram:** PADS is the only source of essential
tremor, so the differential-diagnosis claim rests on the glove path. mPower is the only
source of *paired* modalities, so the fusion head can be pretrained there rather than fit
from scratch at n = 20. Those two facts drive the whole design.

### Two public datasets, four modalities, late fusion

```
[Glove: 5x per-finger IMU + flex]  -> tremor/bradykinesia encoder -> score_motion   (PADS)
[Phone mic: sustained /a/]         -> dysarthria encoder          -> score_voice    (mPower)
[Phone in pocket: walk + stand]    -> gait/postural encoder       -> score_gait     (mPower)
[Phone screen: tapping]            -> bradykinesia encoder        -> score_tapping  (mPower)
                                                                        |
                                             late fusion (small, LOSO-validated)
                                                                        |
                                                                  final output
```

**PADS owns the hand, tremor, and ET question. mPower owns the phone-based multimodal
system.** That split keeps harmonisation work to two datasets rather than four, and every
mPower modality is phone-native, so the pretraining sensor and the deployment sensor are
identical.

### Why late fusion, and where the fusion head can actually be trained

**Correction to an earlier version of this document:** it claimed no public dataset carries
multiple modalities from the same person, and concluded the fusion head could only be
trained on patient data. That is wrong. **mPower is paired** — voice, walking, and tapping
all come from the same participants — so the fusion head *can* be pretrained there and then
adapted on the patient cohort.

The fusion head should still stay small:

- Logistic regression over the modality scores is roughly four or five parameters and is
  fittable under LOSO at n = 15 to 20 even without mPower pretraining. A learned
  cross-attention fusion module is not.
- Describe it as **late fusion of independently adapted unimodal encoders**, not "learned
  multimodal fusion."
- Do **not** stitch PADS and mPower subjects together by diagnosis label to fake a paired
  set. Fusion pretraining uses mPower's genuinely paired modalities only; the glove enters
  the fusion at the patient stage. Faking pairing is the confound that makes existing
  tri-modal papers unconvincing.
- Design for **missing modalities** from the start. At n = 20 a participant cannot be
  dropped because one recording failed or because they could not complete the walk. A
  fusion rule that renormalises over available modalities costs nothing now and prevents
  losing subjects later.

### Tapping is a baseline, not redundancy

Screen tapping overlaps the glove in body region and symptom (hand bradykinesia), but that
is the point. Screen tapping is precisely what a **phone-only** system would use to measure
bradykinesia, and it is the cheap alternative the glove has to justify itself against.
Running both gives a direct head-to-head: does per-finger IMU sensing beat a capacitive
touchscreen at the same clinical task? That supports the core claim rather than duplicating
another modality.

### Transfer sequence per modality

```
general pretrained model  ->  large public PD dataset  ->  paired patient data
      (MOMENT, etc.)            (full fine-tune)          (frozen / LoRA / head-only)
```

**Stage 3 must not be a full fine-tune.** At n around 30, full fine-tuning will overwrite
the public-dataset representations. Head-only, LoRA, or linear probing.

### Datasets

| Dataset | Covers | Access | Contains ET? | Label quality |
|---|---|---|---|---|
| **PADS** | Glove / tremor modality | Already staged | **Yes, 28** | Clinical diagnosis |
| **mPower** | Voice, gait, tapping, fusion pretraining | Synapse: register, certify, validate profile, submit data use statement | No | **Self-reported, no clinician confirmation** |
| MDVR-KCL *(fallback)* | Voice only | Zenodo, immediate download, no gate | No | Clinical, with H&Y and UPDRS scores |

**Only PADS has essential tremor.** The PD-versus-ET signal can therefore only be
pretrained for the motion modality. For voice, gait, and tapping the public encoders learn
PD-versus-healthy, and any ET discrimination in those modalities has to be learned at the
paired-patient stage where n is 15 to 20. See §3.1.

**mPower's labels are self-reported.** That is its main weakness and it should be stated
plainly: pretraining is weak supervision at scale, and the clinician-confirmed patient
cohort provides the strong supervision. That sequence is defensible; presenting mPower
accuracy as a clinical result is not.

### Why phone-in-pocket gait rather than camera pose

An earlier version of this plan used REMAP Open for gait. Switching to mPower's
phone-in-pocket walking module removes a substantial amount of work and risk:

- **REMAP Open ships no video.** It releases derived 2D/3D skeleton coordinates, coarsened
  for anonymisation, because the raw RGB footage is identifying. You cannot run your own
  pose estimator over it.
- Training on REMAP skeletons and inferring on MediaPipe output would require mapping
  between two different joint schemas, plus normalising for the fact that REMAP used fixed
  wall-mounted home cameras while deployment would be a handheld phone at a different
  height, distance, and angle.
- mPower's walking module has none of that. Phone in pocket during pretraining, phone in
  pocket at deployment. Same sensor, same placement, same signal. No CV pipeline at all.

REMAP remains a reasonable option if camera-based postural analysis ever becomes a
priority, but it should not be the default path.

### Voice task: decide this before writing the study protocol

mPower's voice module is a 10-second sustained "aaah". MDVR-KCL is passage reading plus
spontaneous dialogue. These are different tasks producing different acoustic features, and
**the patient protocol must record whichever task the encoder was pretrained on**.

- **Sustained phonation (mPower):** easier to administer, classic PD voice task, captures
  jitter/shimmer/HNR-type features. Gives up prosody, speech rate, and pausing.
- **Connected speech (MDVR-KCL):** richer, captures hypokinetic dysarthria more fully,
  harder to standardise across participants.

Default to sustained phonation for protocol simplicity, keeping MDVR-KCL on disk as a
fallback.

### Access concentration risk

Three of the four modalities plus the fusion pretraining all sit behind a single Synapse
gate. If that access is slow or denied, most of the phone-side system disappears at once.
Mitigations: start the Synapse process immediately, in parallel with IRB rather than after
it, and download MDVR-KCL now (free, ungated) so voice has an independent path.

### 3.1 The layered claim: detection and differentiation are different questions

The two framings are compatible, and stacking them is stronger than either alone, provided
they are kept clearly separate:

**Layer 1 (all three modalities): multimodal PD detection and severity.** Each modality
contributes an independent symptom domain, trained on public PD-versus-HC data. This is
the broad, deployable capability. It is not novel on its own.

**Layer 2 (glove-led): PD versus essential tremor.** This is the contribution. Only PADS
has ET subjects, so this is the only modality where the discriminator can be pretrained.

The reason multimodality is *more* justified under Layer 2, not less, is that the three
modalities plausibly carry different PD-versus-ET information:

| Modality | Expected in PD | Expected in ET | Sourcing |
|---|---|---|---|
| Motion (glove) | Rest tremor, **alternating** antagonist phase, higher amplitude | Action/postural tremor, **synchronous** phase, lower amplitude | [S1], [S2] |
| Gait / posture | Postural instability, shuffling, reduced arm swing | Largely unaffected | Partially supported: [S4] and [S8] attempt gait-based PD/ET discrimination, but [S4] reports only F1 0.61, so the separation is weaker than this row implies |
| Voice | Hypophonia, monotone (hypokinetic dysarthria) | Vocal tremor in some patients | **Unsourced.** Clinical description only |

If that holds, the *pattern across modalities* discriminates even where any single one is
ambiguous: PD elevates all three, whereas ET elevates the tremor channel while leaving
gait comparatively intact. That is a genuine multimodal argument rather than a
score-averaging exercise.

**Needs clinical verification.** The table above is drawn from general clinical
description, not from a source read for this project. Gait sparing in ET and postural
instability being PD-characteristic are the load-bearing assumptions and should be
confirmed with a neurologist before the design depends on them.

**The honest limitation:** because no public voice or gait dataset contains ET subjects,
Layer 2's multimodal component cannot be pretrained. It can only be learned and tested on
paired patient data at n = 15 to 20. So Layer 2 should be reported as: wrist/finger motion
evidence (trainable on PADS today, strongest arm), plus a smaller, exploratory multimodal
result from the patient cohort framed with effect sizes rather than accuracy.

Parkinsons Telemonitoring was considered for voice and rejected: it ships pre-extracted
acoustic features rather than raw audio (nothing for a pretrained audio model to consume),
has no healthy controls, and targets UPDRS regression rather than classification.

The wider public-dataset survey (PD-BioStampRC21, Daphnet, Oday, MJFF, REMAP) was reviewed
and deprioritised **for merging into PADS on the motion modality**: every candidate is
missing at least one of wrist placement, both accelerometer and gyroscope, a real PD/HC
comparison, or open access. More importantly, none of them have per-finger placement or
flex sensors, so none can substitute for glove data on the core research question. mPower
is the exception, but it earns its place for the *phone* modalities and fusion pretraining,
not as extra motion data.

Two other third-modality candidates were considered and set aside:

- **Spiral / handwriting** (UCI digitised tablet dataset, 62 PD / 15 HC). Strong clinical
  fit, since digitised drawing analysis is used specifically to characterise tremor across
  PD, ET, and dystonia, and micrographia is PD-specific. Touchscreen-capturable, no privacy
  exposure. Set aside because it shares a body region with the glove and would not be
  paired with the other modalities the way mPower is. **Worth revisiting** if a fourth
  phone-based modality is wanted later, particularly for the ET question.
- **Face / hypomimia.** Clinically PD-specific and largely absent in ET, so it would
  discriminate, and public data exists (~1,800 videos, 604 people, via parktest.net).
  Rejected on two grounds: face is identifying biometric data, which cuts against the
  project's privacy-by-design posture, and the highest-profile paper in the subfield
  ([npj Digital Medicine, 2021](https://www.nature.com/articles/s41746-021-00502-8)) has
  been retracted.

---

## 4. Study design (post-IRB)

### Cohort

- **PD and ET are the primary arms.** The ablation (five channels versus wrist-collapsed)
  runs within tremor-positive participants; healthy controls do not participate in it.
- **Healthy controls are cheap insurance**, not a requirement: easiest arm to recruit,
  they rule out the model learning age instead of pathology, and they preserve a
  publishable result if the ET arm under-recruits.
- **Age-match the controls.** D3 demonstrated that subgroup composition alone can drive
  apparent metric differences; mismatched controls would let the model learn age
  invisibly.
- Target 15 to 20 participants total, weighted toward PD and ET.

### Sessions

Two to three per participant. Sessions multiply data but **do not** increase n for
cross-subject generalisation. LOSO folds equal participants, not sessions. Split by
subject, never by session (this is the error behind iTex's 80/20 split on four
participants).

What sessions do buy: more encoder training data, a better-conditioned fusion head,
session-level robustness (glove re-donned, different day), and test-retest reliability
(ICC), which is a legitimate publishable result that small-n studies are well suited to
produce.

**Make at least one session a contrast, not a replicate.** On-medication versus
off-medication gives a within-person design where each subject is their own control. That
is better powered than the cross-sectional comparison and needs no healthy controls at
all. It is also the right first test of whether the instrument can detect within-person
change, since levodopa response is large and well characterised.

### Task protocol: include the postural maneuver contrast

[S5] found that the **direction of tremor change between two arm postures** discriminates
PD from ET, independent of any sensor sophistication:

| Posture | PD | ET |
|---|---|---|
| Hands completely stretched (CS), arms outstretched | baseline | baseline |
| Hands hanging down (HD), arms at shoulder height, hands relaxed downward | tremor **increases** (83% of patients) | tremor **decreases** (75% of patients) |

They reported 83% sensitivity and 75% specificity from this contrast alone, using one IMU
per hand at 50 Hz, on 12 PD versus 12 ET. That is a **task-design** discriminator, not a
sensor one, which means it costs nothing to adopt and composes with the per-finger
approach rather than competing with it.

**PADS supports only half of it.** Checked against the 11 PADS task labels
(`CrossArms`, `DrinkGlas`, `Entrainment`, `HoldWeight`, `LiftHold`, `PointFinger`,
`Relaxed`, `RelaxedTask`, `StretchHold`, `TouchIndex`, `TouchNose`):

- **Stretched condition: present.** `StretchHold` and `LiftHold` approximate CS.
- **Hanging condition: absent.** No PADS task places the arms at shoulder height with the
  hands relaxed downward. `Relaxed` and `RelaxedTask` are seated rest, which is a
  different posture.

So the CS/HD contrast **cannot be evaluated on PADS** and must be added to the patient
protocol. Worth doing: it is two extra postures, roughly 20 seconds, and it is an
independent discriminator that does not depend on the per-finger hypothesis being correct.
If the per-finger phase claim underperforms, this maneuver still produces a result.

### Pairing requirements

All three modalities from the same person, **same session, same medication state**,
linked by a shared session ID. Recording voice on-medication and gait off-medication means
the modalities describe different neurological states and the fusion head learns noise.
The existing exercise-centric data contract extends naturally to carry a session ID.

### What gets reported

Feasibility study, effect sizes, LOSO-validated, test-retest reliability. Not a headline
accuracy number. At this n, "94% detection accuracy" is the claim that draws fire;
"system validated on 18 participants, effect sizes reported" is standard and publishable.

### Known tension worth stating in the paper

Cases with clinically unambiguous diagnoses are exactly the cases where the device adds
least value. Participants whose diagnosis is genuinely difficult are the ones who would
benefit, and are also the ones whose ground-truth label is least reliable. This cannot be
fully escaped at small n. Note any DaTscan-confirmed participants separately, since those
labels are stronger.

---

## 5. Staging

Each stage should stand alone as a result, so that a later stage failing does not leave an
unfinished paper.

```
                     NO BLOCKERS                    GATED
                     (start today)                  (waiting on others)

  Stage 0   PADS PD-vs-ET reframe  ────────────────────────────┐
            one line in load_labels() + rerun                  │
                                                               │
  Stage 0b  Synapse access request ─────> [Synapse approval]   │
            Download MDVR-KCL (ungated)                 │      │
                                                        │      │
  Stage 1   Flex on Pi 5                                │      │
            CH4 fault fix           ────> [IRB] ──> patient cohort
            Real Pi latency                     │      │      │
                                                v      v      v
  Stage 2   Voice encoder  <──────────────────────────────┐   │
                                                          │   │
  Stage 3   Gait + tapping encoders  <────────────────────┤   │
            Fusion head pretraining  <────────────────────┘   │
                                                              │
            ============ PAPER ============  <────────────────┘
            Layer 1: multimodal PD detection
            Layer 2: per-finger PD vs ET   <-- the contribution
```

**Only Stage 0 is unblocked and free.** Stage 0b costs calendar time but no effort, and it
should start immediately because Synapse gates three modalities. Everything in Stages 1
through 3 that touches patients waits on IRB.

**Stage 0 — now, no IRB, no new data.**
Reframe PADS from PD-vs-HC to PD-vs-ET (28 ET subjects currently discarded in
`load_labels()`). This establishes the wrist-only baseline the glove must beat and
measures how much harder the differential-diagnosis question is. If wrist-only PD-vs-ET
lands well below PD-vs-HC, that gap is the motivation section.

**Stage 0b — start in parallel, calendar time only.**
Begin the Synapse access process for mPower (registration, certification, profile
validation, data use statement) and download MDVR-KCL. Neither depends on IRB, both take
elapsed time rather than effort, and mPower gates three of the four modalities.

**Stage 1 — finish the glove.**
Flex sensors integrated on the Pi 5, CH4 fault resolved, real Pi latency measured. Plus an
IRB'd patient study, this is a complete paper on its own: per-finger sensing against the
single-IMU baseline, with screen tapping as the phone-only comparison.

**Stage 2 — add voice.**
Cheapest modality: phone microphone, no new hardware, best-supported in the literature.
Sustained phonation from mPower, with MDVR-KCL as the ungated fallback.

**Stage 3 — add gait and tapping.**
Both come from the same mPower access, both are phone-native, and neither needs a CV
pipeline now that gait is phone-in-pocket rather than camera pose. This is also the point
at which the fusion head can be pretrained on mPower's paired modalities rather than fit
from scratch on the patient cohort.

---

## 6. Risks and dependencies

| Risk | Impact | Mitigation |
|---|---|---|
| IRB not yet cleared | Blocks every patient-facing stage | Critical path; nothing downstream has a timeline until it moves |
| ET arm cannot be recruited | Removes the core research claim | Ask Prof. Singh early whether the clinical contact reaches ET patients at all. If not, reframe before building the study |
| No clinical rater available | Cannot train toward MDS-UPDRS 0-4 | Within-person medication contrast needs no absolute severity labels |
| Full fine-tune at stage 3 | Silently destroys public-dataset representations | Freeze encoder; head-only or LoRA |
| Splitting by session not subject | Inflated accuracy, invalid result | Group on subject ID, as D1 through D3 already do |
| MQTT throughput ceiling | Sampling rate collapse when streaming | iTex hit this at 128 Hz and traced it to inter-payload interval. Current design publishes per-exercise summaries, not raw streams, so should be clear. Revisit if raw windows are ever streamed for cloud inference |
| Scope: four modalities, one built | Unfinished multimodal paper | Stage so each modality is publishable alone |
| **Synapse access concentration** | mPower gates voice, gait, tapping, *and* fusion pretraining. One denial removes most of the phone-side system | Start the access process immediately, in parallel with IRB. Keep MDVR-KCL (ungated) on disk as an independent voice path |
| **mPower labels are self-reported** | Pretraining on unconfirmed diagnoses | Frame as weak supervision at scale; the clinician-confirmed patient cohort provides strong supervision. Never report mPower accuracy as a clinical result |
| Voice task mismatch | Encoder pretrained on sustained vowels will not transfer to connected speech, or vice versa | Fix the task before writing the study protocol; record whichever task the encoder was pretrained on |

---

## 7. What is explicitly not a contribution

Worth being clear-eyed, since these all appear in the project and none of them are the
reason someone would cite it:

- **Multimodal fusion** on its own. Crowded, and the generic framing of this entire space.
- **Edge deployment / INT8 quantization.** Well trodden; the project's own citation list
  includes prior work establishing the latency and footprint benefits.
- **Methodological rigour.** Subject-level splits, pooled out-of-fold fairness auditing,
  and honest reporting make the paper trustworthy rather than novel. Good reviewers treat
  this as table stakes. It belongs in the methods section, not the contributions list.

---

## 8. Sources

Every claim in this document that rests on outside literature is tagged with an `[Sn]`
marker. Claims **without** a marker are either (a) facts about this project's own repo and
results, verifiable in the reports under `docs/`, or (b) general clinical knowledge stated
without a citation read for this project, in which case they are explicitly flagged as
needing sourcing at the point they appear.

| Tag | Source |
|---|---|
| **[S1]** | Nisticò et al., *Synchronous pattern distinguishes resting tremor associated with essential tremor from rest tremor of Parkinson's disease.* Parkinsonism & Related Disorders. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1353802010002531) — source of the **no-overlap** alternating vs synchronous finding, and of PD rest tremor amplitude being higher than ET's. |
| **[S2]** | Zhang et al. (2017), *Differential Diagnosis of Parkinson Disease, Essential Tremor, and Enhanced Physiological Tremor with the Tremor Analysis of EMG.* Parkinson's Disease (Wiley). [Wiley](https://onlinelibrary.wiley.com/doi/10.1155/2017/1597907) · [PMC5573102](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5573102/) — EMG as the classical measurement route; burst duration and frequency higher in ET. |
| **[S3]** | *Distinguishing Essential Tremor From Parkinson's Disease.* Practical Neurology. [link](https://practicalneurology.com/diseases-diagnoses/imaging-testing/distinguishing-essential-tremor-from-parkinsons-disease/30751/) — clinical overview, frequency band overlap. |
| **[S4]** | *Classification of Parkinson's disease and essential tremor based on balance and gait characteristics from wearable motion sensors via machine learning techniques.* J NeuroEngineering and Rehabilitation (2020). [Springer](https://link.springer.com/article/10.1186/s12984-020-00756-5) · [PMC7488406](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7488406/) — best F1 0.61 for gait-based PD vs ET. |
| **[S5]** | *Differentiation of Parkinson's disease tremor and essential tremor based on a novel hand posture.* [PMC9136132](https://pmc.ncbi.nlm.nih.gov/articles/PMC9136132/) · [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2590112522000172) — the CS/HD postural maneuver. One ReSense IMU per hand, 50 Hz, 12 PD vs 12 ET (4 excluded for missing data). Sens 83% / spec 75%. |
| **[S6]** | *Temporal fluctuations of tremor signals from inertial sensor: a preliminary study in differentiating Parkinson's disease from essential tremor.* [PMC4632333](https://pmc.ncbi.nlm.nih.gov/articles/PMC4632333/) |
| **[S7]** | *Development and Validation of a New Wearable Mobile Device for the Automated Detection of Resting Tremor in Parkinson's Disease and Essential Tremor.* [PMC7911899](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7911899/) — wearable phase displacement compared against classical EMG; multi-location hand accelerometry (thumb, index, metacarpal, wrist). |
| **[S8]** | *Wearable sensor-based gait analysis to discriminate early Parkinson's disease from essential tremor.* [PMC10025195](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10025195/) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/36725698/) |
| **[S9]** | Ravichandran, Sadhu, Convey, Guerrier, Chomal, Mankodiya et al. (2023), *iTex Gloves: Design and In-Home Evaluation of an E-Textile Glove System for Tele-Assessment of Parkinson's Disease.* [PMC10054833](https://pmc.ncbi.nlm.nih.gov/articles/PMC10054833) — the per-finger gap quote; one IMU + three flex sensors per glove; 128 Hz target vs 82–87 Hz achieved; MQTT inter-payload interval 364 ± 23 ms. |
| **[S10]** | PADS: Varghese et al. (2024), *Machine Learning in the Parkinson's disease smartwatch (PADS) dataset.* npj Parkinsons Dis. 10, 9. [PhysioNet](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) — 276 PD / 79 HC / 114 DD (of which 28 essential tremor), bilateral wrist acc+gyro @ 100 Hz, 11 tasks. |
| **[S11]** | mPower: Bot et al. (2016), *The mPower study, Parkinson disease mobile data collected using ResearchKit.* Sci Data 3, 160011. [Synapse portal](https://www.synapse.org/Synapse:syn4993293/wiki/247859) — paired voice / walking / tapping modules; self-reported diagnosis. |
| **[S12]** | MDVR-KCL: Jaeger, Trivedi & Stadtschnitzer (2019). [Zenodo](https://doi.org/10.5281/zenodo.2867216) — 16 PD / 21 HC, raw `.wav`, recorded on a Motorola Moto G4. |
| **[S13]** | REMAP Open. [data.bris](https://data.bris.ac.uk/data/dataset/21h9f9e30v9cl2fapjggz4q1x7) — skeleton pose only, no video; sister to the access-controlled REMAP dataset. Considered and set aside, see §3. |
| **[S14]** | UCI Parkinson Disease Spiral Drawings (digitised graphics tablet), 62 PD / 15 HC. [UCI](https://archive.ics.uci.edu/dataset/395/parkinson+disease+spiral+drawings+using+digitized+graphics+tablet) — considered and set aside, see §3. |
| **[S15]** | *Facial expressions can detect Parkinson's disease: preliminary evidence from videos collected online.* npj Digital Medicine (2021) — **RETRACTED**. [Nature](https://www.nature.com/articles/s41746-021-00502-8) · [preprint](https://arxiv.org/abs/2012.05373) — basis for rejecting the face modality, see §3. |

### Claims in this document that are NOT yet sourced

Listed so they are not mistaken for verified:

1. **Inter-digit phase as a proxy for antagonist-muscle phase.** This is the project's core
   hypothesis, not an established result. [S1] and [S2] establish the muscle-level sign;
   nothing cited establishes that fingertip IMUs capture it. This is what the work would
   demonstrate.
2. **PD/ET medication, prognosis, and DaTscan claims** (§1.3) — general clinical knowledge,
   uncontroversial, but needs proper references before publication. The misdiagnosis rate
   should be cited with a figure.
3. **The PD-versus-ET expectations per modality** (§3.1 table: gait sparing in ET, vocal
   tremor in ET versus hypophonia in PD) — clinical description, flagged in place, needs a
   neurologist's confirmation.
4. **"50 Hz is sufficient for PD assessment"** — appears in project notes attributed to
   Shawen et al. via [S9]'s citation list. Not read directly. Verify before relying on it
   to justify the 89 Hz sampling rate.
