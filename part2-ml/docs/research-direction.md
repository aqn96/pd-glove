# Research Direction (post-coursework)

**An Nguyen · Northeastern University Khoury College · August 2026**

This is the research plan beyond CS 8674 Part II. The course timeline (D1 through D4)
lives in [`next-steps.md`](../next-steps.md); this document is about what the project
argues and how it gets there afterwards.

Status of every claim below is marked explicitly: **done**, **planned**, or **blocked**.
Clinical assertions are marked where they still need a clinician's sign-off.

---

## 1. The research claim

The project makes a **layered** claim (detail in §3.1, paper framing in §5). Layer 1 is a
multimodal low-cost home PD assessment system across motion, voice, gait, and tapping:
broad, deployable, and not novel by itself. Layer 2 is what makes Layer 1 credible outside
a curated cohort, and is where the contribution lives:

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

### 1.4 OPEN DECISION — which comparison group

**Not yet decided.** Recorded here so the options and their tradeoffs are not re-derived
later. Depends partly on what can be recruited (§7).

PADS' 114 differential-diagnosis subjects are not one thing:

| Group | n | Relationship to PD |
|---|---|---|
| Other Movement Disorders | 60 | Heterogeneous, unspecified |
| Essential Tremor | 28 | The classic diagnostic confusion |
| Atypical Parkinsonism | 15 | PSP / MSA / CBD — genuinely parkinsonian |
| Multiple Sclerosis | 11 | Not primarily a tremor disorder |

**Option A — PD vs ET (276 vs 28).** The mechanism, the citation [S1], and the real-world
misdiagnosis problem all line up here. Sharpest claim. Worst balance at roughly 10:1, and
5 to 6 ET subjects per fold under subject-level CV.

**Option B — PD vs all DD (276 vs 114).** Best balance at 2.4:1 and the most realistic
screening scenario, since a deployed device does not know in advance what the alternative
diagnosis is. But it is a *different, messier* question, not a better-powered version of
Option A:

- **The mechanism does not transfer.** [S1] establishes alternating-versus-synchronous for
  PD versus ET specifically. Nothing cited supports "PD alternating, all other disorders
  synchronous." Broadening the target costs the mechanistic grounding that makes the claim
  sharp.
- **Atypical parkinsonism is the wrong thing to call "not PD."** PSP, MSA, and CBD *are*
  parkinsonian, sharing rigidity, bradykinesia, and sometimes rest tremor. Separating them
  from PD with a hand sensor is a much harder problem than separating ET, and may not be
  solvable at all at the wrist or fingers. Clinically that distinction usually comes from
  disease course and non-motor signs, not tremor morphology. Including these 15 could
  depress results for reasons unrelated to the sensor.
- **MS tremor is a different mechanism** (intention / cerebellar).

**Option C — PD vs ET + atypical parkinsonism (276 vs 43).** Middle ground: keeps the arm
to parkinsonian-and-tremor conditions, drops MS and the unspecified grab bag, better
balanced than Option A. Still only 15 atypical subjects.

**Not recommended: multiclass.** At 15 and 11 subjects the small classes cannot support
anything reportable.

**Current leaning:** Option A as the primary claim, Option B reported alongside as the
realistic screening scenario. Two analyses, different purposes.

**Needs clinical input.** The grouping logic above, particularly the claim that atypical
parkinsonism is harder to separate from PD than ET is, comes from general clinical
knowledge rather than a source read for this project. It determines which subjects go in
which arm, so confirm with Prof. Singh or a neurologist before building the analysis.

### 1.5 If essential tremor patients cannot be recruited

A live concern. The important distinction: **the PADS analysis requires no recruitment at
all.** Those 28 ET subjects are already in staged data. Recruitment risk affects only the
glove cohort. Fallback ladder, strongest first:

1. **Recruit ET.** Full claim available: per-finger versus wrist-collapsed ablation on
   PD versus ET within one cohort.
2. **No ET, but PD patients available.** The discrimination claim is unavailable, but the
   *measurement* claim is not. Show that per-finger IMUs reliably extract the
   alternating-phase signature in PD patients, and report the PADS wrist-only PD-vs-ET
   result separately as a dataset analysis. Honest framing: "we demonstrate the glove
   recovers the phase signature the literature identifies as discriminating; validating
   discrimination against ET requires a cohort we were unable to recruit." Weaker, still a
   real contribution.
3. **Neither.** PADS PD-vs-ET and PD-vs-DD stand alone as a public-dataset result, and the
   glove study reverts to PD versus healthy controls. The per-finger claim becomes motivated
   future work rather than a tested one.

Decide which rung is acceptable *before* writing the introduction (§5.5).

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
| mPower (Synapse) access | **Not started** — gates three of five scoring channels |
| Patient data collection | **Blocked** — IRB pending |

Of the five scoring channels, one (glove tremor) is built and validated. Glove flex is
bench-characterised on the thumb only. The three phone channels are not started.

---

## 3. Architecture

### Diagram 1 — where each model comes from and how it is adapted

```
PUBLIC PRETRAINING (large n)                 PATIENT ADAPTATION (n = 15-20, clinician-labelled)
──────────────────────────────               ──────────────────────────────────────────────────

┌─ PADS ─────────────────────┐
│ 276 PD / 79 HC             │  full
│ 114 DD, incl. 28 ET        │  fine-tune    ┌─ CNN1D ~11.6K params ─┐  freeze convs,
│ ← ONLY ET SOURCE ANYWHERE  │──────┬───────>│ on-device motion model│──train final layer──> tremor
│ 1 wrist IMU, 6ch @ 100 Hz  │      │        └───────────────────────┘                       score
└────────────────────────────┘      │
                                    │        ┌─ MOMENT ~350M params ─┐
                                    └───────>│ cloud-only, 1.4 GB    │──LoRA───────────────> tremor
                                             └───────────────────────┘                    score (B)

┌─ mPower ───────────────────┐
│ ~9.5k subjects             │
│ PAIRED: one person does    │
│ all three tasks            │
│ self-reported labels (weak)│
│                            │
│  voice: sustained /a/      │────────────>  small audio model ──freeze most, train last──> voice
│  walking: phone in pocket  │────────────>  small accel model ──freeze, train head──────> gait
│  tapping: screen           │────────────>  engineered features ──recalibrate───────────> tap
│                            │
│  all 3 from same person ───│────────────>  PHONE FUSION (level 1) ─────────────────> phone
└────────────────────────────┘               3 inputs + bias = 4 params                 score
                                             pretrained on thousands of subjects

┌─ no public dataset exists ─┐
│ glove flex sensors         │────────────>  engineered features ──fit on cohort─────────> brady
│ (finger bend angle)        │               rate / decrement / irregularity                score
└────────────────────────────┘


                    LEVEL 2 FUSION, fitted on the patient cohort (n = 15-20)
                    ────────────────────────────────────────────────────────
                        tremor score  ─┐
                        brady score   ─┼──> 3 inputs + bias = 4 params ──> FINAL
                        phone score   ─┘
```

**Three things this diagram encodes:**

1. **PADS pretrains two different motion models**, not one. The CNN goes on the device;
   MOMENT is the cloud second opinion. Same pretraining data, different sizes, therefore
   different adaptation methods.
2. **PADS is the only source of essential tremor anywhere**, so the differential-diagnosis
   claim rests entirely on the glove path.
3. **mPower is the only source of paired modalities**, so the fusion head can be pretrained
   on thousands of subjects instead of fitted from scratch on twenty.

Note that two channels use **engineered features rather than learned encoders**: glove flex
and phone tapping. Both measure bradykinesia, which has an explicit clinical definition
(MDS-UPDRS 3.4: speed, amplitude, decrement, hesitations) that is directly computable. No
encoder needed, and no public flex dataset exists to pretrain one on.

### Diagram 2 — the five channels, and the head-to-head hiding in them

```
GLOVE                                                    PHONE
─────                                                    ─────
5x per-finger IMU  -> tremor score          ┌── same ──> screen tapping -> bradykinesia score
5x flex sensor     -> bradykinesia score  ──┘ construct                    (comparison baseline)
                                                         microphone     -> voice score
                                                         in-pocket accel-> gait score
                                                    |
                              late fusion (~5 weights, LOSO-validated)
                                                    |
                                              final output
```

Glove flex and phone tapping measure **the same construct by different means**. That is not
redundancy, it is the head-to-head: screen tapping is what a phone-only system would use for
bradykinesia, and it is the cheap alternative the glove has to beat. Report both.

### Diagram 3 — two deployment paths

```
PATH A — routine, fully on-device (the default, and the headline claim)

  phone mic     ──> small audio model ──┐
  phone pocket  ──> small accel model ──┼─> LEVEL 1 phone fusion ──> phone_score ─┐
  phone screen  ──> engineered features ┘   (4 params, mPower-pretrained)         │
                                                                                  │
  glove IMU     ──> CNN, 19.6 KB, 0.066 ms ────────────> tremor_score ────────────┤
  glove flex    ──> engineered features ───────────────> brady_score  ────────────┤
                                                                                  v
                                                       LEVEL 2 fusion A (4 params)
  EVERYTHING RUNS ON THE PI.                                        │
  No raw signal of any kind leaves.                                 v
                                                     AES-256-GCM + MQTT expiry
                                                                    │
                                                                    v
                                                        cloud receives score only


PATH B — optional second opinion (explicit consent required)

  phone mic     ──> audio model  (local) ─┐
  phone pocket  ──> accel model  (local) ─┼─> LEVEL 1 phone fusion (local, UNCHANGED)
  phone screen  ──> features     (local) ─┘                    │
                                                               └──> phone_score ──┐
  glove flex    ──> features     (local) ──────────────────────────> brady_score ─┤
                                                                                  │
  glove IMU     ══> RAW IMU LEAVES DEVICE ══> MOMENT (cloud) ──────> tremor_score ┤
                                                                                  v
                                                       LEVEL 2 fusion B (4 params,
  Only raw IMU crosses the boundary. Voice, gait, tapping,          SEPARATE weights)
  and flex all stay local and travel as plain numbers.                  │
  Raw AUDIO never leaves. Level 1 is untouched.                         v
                                                                      score
```

**Design Path B this way deliberately.** Only the motion encoder needs swapping, so only raw
IMU has to go up. Voice is the most sensitive modality — it is identifying and carries
speech content — and there is no reason for it to leave the device even in the cloud path.

**Path A is the claim.** Because every encoder can be small, the whole system runs locally.
This is not a tiered compromise where privacy is traded for accuracy on the routine path; it
is a complete on-device system, with Path B as an opt-in extra.

**The two paths need separate level-2 fusion heads.** Fusion weights are fitted to the
distribution of scores they saw during training. MOMENT and the CNN are confident in
different ways and their outputs are not interchangeable. Swapping the motion encoder under
a head trained on the other one degrades performance in a way that is hard to diagnose.
Only level 2 needs duplicating — the level-1 phone fusion is unaffected, since Path B
changes nothing about the phone channels. Each level-2 head is four parameters, so fitting
two is cheap, but it must be done knowingly.

**Preferred: make Path B unnecessary.** Distillation (train the CNN to imitate MOMENT's
soft outputs during training) recovers part of the accuracy gap while keeping everything
local. If it works well enough, the privacy claim covers the entire system with no
exceptions.

### Dataset ownership

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

#### The grouping rule: follow data pairing, not clinical construct

This is the counterintuitive part and the thing most likely to be re-derived later, so it
is stated plainly:

> **A channel goes in level 1 if mPower observed it alongside the other level-1 channels
> on the same person. Everything else goes in level 2.**

| Channel | Source | Paired with others in mPower? | Level |
|---|---|---|---|
| Voice | mPower | Yes | **1** |
| Gait | mPower | Yes | **1** |
| Tapping | mPower | Yes | **1** |
| Tremor | PADS, then cohort | No — PADS has no phone data | **2** |
| Flex bradykinesia | No public dataset exists | No | **2** |

A fusion head learns *weights*, and weights require joint observations. mPower recorded
voice, gait, and tapping on the same people, so those three relationships are learnable from
thousands of subjects. Nothing anywhere pairs glove channels with phone channels, so that
relationship can only come from the patient cohort.

**Two consequences that look wrong until you know the rule:**

1. **The two bradykinesia measures sit at different levels.** Phone tapping is inside
   level 1; glove flex enters at level 2. Clinically they are the same construct, which
   makes this look misplaced. But grouping follows pairing, not clinical category. Tapping's
   placement is determined by mPower having recorded it next to voice and gait, not by what
   it measures.
2. **Tapping is engineered features, yet still level 1.** Where the features came from is
   irrelevant. What matters is that mPower observed tapping on the same subjects as the
   other two.

**A useful side effect:** burying tapping inside `phone_score` *reduces* the
multicollinearity problem. As a standalone level-2 input it would sit beside `flex_brady`
measuring the same construct, and the two weights would fight. Mixed with voice and gait,
what reaches level 2 correlates more weakly with `flex_brady`.

**Keep the two bradykinesia scores separate rather than merging them.** The head-to-head —
does per-finger flex beat a capacitive touchscreen on the same clinical task — requires two
separately evaluated scores. Report it as an ablation result; it does not need to be encoded
in the fusion topology.

#### Two-level fusion, and why it is not one flat head

A flat head over all five channels would be 5 weights plus a bias = **6 parameters**, all
fitted on 15 to 20 patients. Worse, the mPower pretraining would not transfer into it: a
head pretrained on mPower has **three** inputs (voice, gait, tapping), the deployed head
needs five, and the two channels with no pretrained weight at all are the glove channels —
exactly the ones carrying the contribution.

Two levels fix that by respecting where the data actually lives:

```
LEVEL 1 — pretrained on mPower (thousands of paired subjects)
  voice   ─┐
  gait    ─┼──> phone fusion:  3 inputs + bias = 4 params  ──> phone_score
  tapping ─┘

LEVEL 2 — fitted on the patient cohort (n = 15-20)
  glove_tremor ─┐
  glove_flex   ─┼──> final fusion: 3 inputs + bias = 4 params ──> FINAL
  phone_score  ─┘
```

Level 1 is learned where there are thousands of subjects. Level 2 has only **four**
parameters to fit on twenty patients rather than six, because the three phone channels
arrive pre-combined. The mPower pretraining is used as a self-contained module rather than
as partial initialisation of something with the wrong input shape.

**Parameter count summary**

| Head | Inputs | Params | Fitted on |
|---|---|---|---|
| Phone fusion (level 1) | voice, gait, tapping | 4 | mPower, ~9.5k subjects |
| Final fusion (level 2), Path A | glove tremor, glove flex, phone score | 4 | Patient cohort, n = 15-20 |
| Final fusion (level 2), Path B | same, but tremor from MOMENT | 4 | Patient cohort, separate weights |

#### Implementation details that follow from this structure

**Feed logits between levels, not probabilities.** A sigmoid output is squashed toward 0
and 1 at the extremes, discarding information exactly where a model is most confident. Pass
the level-1 logit into level 2, and likewise for the other channel scores.

**`phone_score` is a feature, not a calibrated probability.** Level 1 was optimised to
predict *self-reported* PD in mPower's population; level 2 predicts *clinician-confirmed*
diagnosis in this cohort. Different targets, different populations, different label quality.
Level 2 consumes `phone_score` as an input signal, and the weights absorb any systematic
scale difference. Do not interpret or report it as "probability of PD."

**Watch for a near-zero weight on `phone_score`.** If level 2 learns to ignore it, that is
evidence mPower's population differs enough from the patient cohort that the pretraining did
not transfer. Report that honestly rather than quietly dropping the channel.

**Encoder drift after adaptation.** Level 1's weights are fitted to mPower's encoder
outputs. Adapting those encoders on the cohort shifts their score distributions, so a frozen
level 1 becomes somewhat miscalibrated. Level 2's weight on `phone_score` absorbs overall
scaling but cannot fix *relative* drift inside level 1. Three options, in order of
defensibility at n = 15-20:

1. **Freeze the phone encoders entirely.** Level 1 stays exactly valid. Gives up cohort
   adaptation on channels that are not the contribution anyway, and leaves very few degrees
   of freedom fitted on the small cohort — which is easy to defend in a paper.
2. **Adapt the encoders, keep level 1, let level 2 absorb the scaling.** Probably fine.
   Worth testing.
3. **Adapt the encoders and refit level 1 on the cohort.** Defeats the purpose of
   pretraining it.

#### OPEN — flat versus two-level is an empirical question

Everything above is a reasoned argument, not a result. Both variants fit in seconds at this
parameter count.

| | Flat (5 inputs, 6 params) | Two-level (4 + 4) |
|---|---|---|
| Fitted on n = 15-20 | All 6 params | Only level 2's 4 |
| mPower fusion pretraining | Cannot transfer cleanly — a 3-weight model does not slot into a 5-weight one, since logistic weights are meaningful only relative to each other and the bias | Level 1 used whole, as a module |
| Flexibility | Can learn that voice matters more than gait *for this cohort* | Level 1's internal balance is frozen from mPower's population |
| Overfitting risk | Higher | Lower |

**Resolve it with LOSO, then report what happened.** "We evaluated flat and hierarchical
late fusion under leave-one-subject-out; the hierarchical variant generalised better,
plausibly because it fits fewer parameters on the small cohort" is a stronger sentence than
asserting either is correct.

Note also that if mPower access falls through entirely, flat fusion fitted on the cohort is
the natural fallback: 6 parameters on 20 subjects, no pretraining, still workable.

#### Late fusion, not early — and this is not a close call

**Late fusion** means each encoder produces its own score first, then those scores are
combined:

```
score = w1·channel1 + w2·channel2 + ... + bias     (one weight per input, plus a bias)
```

**Early fusion** would combine the raw signals before encoding, learning one joint
representation. Six reasons that is the wrong choice here, roughly in order of how
decisive they are:

1. **The pretraining data makes it nearly impossible.** Early fusion must be trained on
   examples where all modalities are present together. PADS and mPower share no subjects,
   so there is nothing to pretrain a joint representation on. Late fusion lets each encoder
   train on whatever dataset covers it.
2. **Parameter count versus cohort size.** Five numbers is fittable at n = 15 to 20. A
   joint model is not.
3. **Missing modalities.** A participant whose gait recording failed cannot be dropped at
   this n. Late fusion renormalises over whatever scores exist; early fusion generally
   breaks when an input is absent.
4. **The signals are not commensurable.** Glove is 100 Hz over 10 s, voice is 44.1 kHz,
   gait is variable-rate accelerometry over 20 to 30 s, tapping is discrete touch events
   with no fixed rate. Early fusion requires aligning all of that; late fusion does not.
5. **Staging requires it.** Adding a modality means adding one input and refitting five
   weights, rather than retraining a joint model from scratch.
6. **Interpretability.** Per-modality scores let a clinician see which channel flagged a
   patient, and make the ablations readable. Early fusion is one number from a black box.

*When to reconsider:* early fusion's genuine advantage is capturing cross-modal
interactions that separate scoring misses. Reaching that ceiling needs hundreds of paired
subjects. If the cohort ever grows that far, the natural intermediate step is
**intermediate fusion** — concatenating encoder *embeddings* rather than final scores,
then training a small classifier on the concatenation.

- Describe it in the paper as **late fusion of independently adapted unimodal encoders**,
  not "learned multimodal fusion."
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

### Pretraining and adaptation strategy

Every model follows the same three-step shape, but the **adaptation step differs by model
size**, and that is the part most easily got wrong.

```
general pretrained model  ->  large public PD dataset  ->  paired patient data
                                (full fine-tune, n is        (adaptation — method
                                 large enough to support it)   depends on size, below)
```

**Step 2 can be a full fine-tune.** PADS has 355 subjects and mPower has thousands. That is
enough data to move all the weights safely. D2 already demonstrated this: MOMENT full
fine-tuned on PADS reached F1 0.626, while the frozen-encoder linear probe managed only
0.502.

**Step 3 must not be.** At 15 to 20 patients, full fine-tuning has far more parameters than
data points. The model memorises the cohort and overwrites what it learned from the public
data. This is the single easiest way to silently invalidate the pipeline.

#### Choosing the adaptation method

Rule of thumb, by trainable parameter count of the pretrained model:

| Model size | Method | Why |
|---|---|---|
| **> 100M params** (MOMENT-1-large, ~350M) | **LoRA** | Full FT overfits badly; freezing entirely is too rigid to pick up cohort-specific patterns. LoRA trains small adapter matrices alongside the frozen weights, typically under 1% of parameters |
| **1M – 100M params** (likely the voice model) | **Freeze most layers, train the last block plus head** | Enough capacity to adapt, few enough trainable weights to survive small n |
| **< 1M params** (the CNN, tapping, probably gait) | **Freeze the feature extractor, train the final layer only** | A few hundred trainable parameters. LoRA here would add complexity for no benefit — it exists to make *large* models cheap to adapt |

**LoRA is for MOMENT, not for the CNN.** The CNN is roughly 50 thousand parameters. Freeze
its convolutional layers, retrain the final Dense layer, done.

#### Quantization is a packaging step, not a training step

Do **not** fine-tune the `.tflite` file. INT8 weights are discrete and the TFLite artifact
is inference-only. Keep the float32 model as the master copy:

```
float32 CNN  --fine-tune on patients-->  float32 CNN v2  --quantize-->  .tflite  --> Pi
```

(Quantization-aware training exists, which simulates INT8 during training so the model
learns to tolerate it. Worth knowing the term; not worth the complexity at this scale.)

### The two motion models, side by side

Easy to conflate. **Both pretrain on PADS** (Diagram 1), then diverge:

| | On-device motion model | Cloud second-opinion model |
|---|---|---|
| Model | CNN1D | MOMENT-1-large |
| Trainable params | ~11,600 | ~350M (Flan-T5-large encoder, 24 layers, d_model 1024) |
| Size | 19.6 KB quantized | 1.4 GB |
| Pretrain on PADS | Full fine-tune | Full fine-tune (done, D2: F1 0.626) |
| Adapt to patients | Freeze convs, retrain final Dense (~130 params) | LoRA |
| Runs where | Raspberry Pi 5, 0.066 ms | Cloud only, cannot fit a Pi |
| Raw data leaves device? | **No** | **Yes** |
| Used in | Path A (routine) | Path B (opt-in) |

**Open item — a smaller MOMENT might collapse this distinction.** Now **confirmed**: the
MOMENT repo announces small and base variants alongside the large one used here.

| Variant | Backbone | Approx. params | HuggingFace |
|---|---|---|---|
| MOMENT-1-small | `flan-t5-small` | ~38–40 M | [AutonLab/MOMENT-1-small](https://huggingface.co/AutonLab/MOMENT-1-small) |
| MOMENT-1-base | `flan-t5-base` | ~113 M | [AutonLab/MOMENT-1-base](https://huggingface.co/AutonLab/MOMENT-1-base) |
| MOMENT-1-large *(used in D2)* | `flan-t5-large` | ~350 M | [AutonLab/MOMENT-1-large](https://huggingface.co/AutonLab/MOMENT-1-large) |

Parameter counts for small and base are from secondary sources, not verified against a
downloaded config the way the large variant was (§ D2 report). At ~38–40 M, small quantized
to INT8 would be roughly 40 MB, which a Pi 5 with 8 GB RAM can certainly hold. **Memory is
not the blocker; inference speed is what needs measuring**, and that measurement needs the
actual Pi.

Worth checking early. If a usable variant runs on-device at acceptable latency, Path B stops
being necessary and the privacy claim covers the whole system with no exceptions. It would
also change the adaptation strategy: at ~38 M, small falls in the freeze-most-train-last-block
band rather than needing LoRA.

**Related, and relevant to reproducibility:** the MOMENT changelog records a fix for
classification being *unable to handle multi-channel inputs*. This project runs
`n_channels=6`, so it is directly affected. The notebook installs from GitHub `main` rather
than pinning a release, so the fixed code was used. Pinning a version for reproducibility
would be sensible, but pin a version *after* that fix.

### Handling the glove's channel count

PADS is one wrist IMU: **6 channels**. The glove is five IMUs plus five flex sensors:
**35 channels**. A PADS-pretrained encoder cannot accept that input directly.

**This is less of an obstacle than it first appears**, because each finger IMU produces
exactly the same 6-channel shape PADS trained on. The problem is not incompatible input, it
is how to combine five compatible inputs.

| Option | How | Trade-off |
|---|---|---|
| **1. Per-finger encoding** | Run the encoder 5x, once per finger, combine the 5 embeddings | No mismatch at all, uses pretrained weights as intended. 5x compute (trivial for the CNN at 0.066 ms, expensive for MOMENT). **But the encoder cannot see between fingers**, so inter-digit phase must be reintroduced elsewhere |
| **2. Expand the input embedding** | Keep pretrained weights for the original 6 channels, randomly initialise the other 29, train those | Standard practice, but new channels start from nothing and need data. Thin at n = 20 |
| **3. Projection layer** | Learn a 35→6 linear map, feed the frozen encoder | **Don't.** Compresses away exactly the per-finger information that is the contribution |
| **4. Aggregate + explicit phase features** | Wrist-equivalent aggregate (6ch) into the PADS encoder, plus separately computed inter-digit phase features | **Recommended** — see below |

**Why option 4 is preferred.** It maps directly onto the experiment:

```
5 finger IMUs ──┬──> aggregate to wrist-equivalent (6ch) ──> PADS encoder ──> baseline score
                │                                                                (CONTROL ARM)
                └──> inter-digit phase features ──────────────────────────────> phase score
                     (cross-spectral phase, thumb-index etc.)                    (TREATMENT)
```

The aggregate path **is** the wrist-equivalent baseline, which is the control arm of the
ablation. The phase features **are** the treatment. The comparison is the whole experiment,
built into the architecture rather than bolted on afterwards.

Second advantage, and it matters for a clinical paper: an explicit phase measurement (say
the phase difference between thumb and index in the tremor band) is **interpretable and
directly comparable to the EMG literature** [S1, S2]. A learned embedding is not. Being
able to put a measured phase difference next to the published alternating-versus-synchronous
finding is far stronger than reporting that a black box separated the classes.

The DSP infrastructure for this already exists in the repo. Cross-spectral phase between two
finger channels is a modest extension of the Butterworth-plus-FFT pipeline in
`scripts/dsp_pipeline.py`.

### The flex channel: engineered features, and a synthesised pretraining set

**Correction to an earlier version of this document.** It said the flex channel has "no
public dataset." That is true at the **sensor** level and misleading at the **construct**
level. No PD dataset carries finger-flexion data, but if the feature space is defined to be
sensor-agnostic, **mPower's tapping module becomes a bradykinesia dataset in that space**,
with roughly 9,500 subjects. The pretraining set is synthesised rather than found, but it is
real. See the transfer subsection below.

Start from the fact that **bradykinesia already has an explicit clinical definition**.
MDS-UPDRS item 3.4 scores finger tapping on speed, amplitude, decrement across the sequence,
and hesitations. Every one of those is directly computable:

| Feature | Computation |
|---|---|
| Tap rate | Peaks per second in the flexion signal |
| Amplitude | Flexion range per tap |
| **Decrement** | Slope of amplitude across the 10 s sequence |
| Hesitations | Irregularity or gaps in inter-tap interval |
| Velocity | Peak flexion rate per tap |

Five or six numbers feeding a logistic regression is roughly seven parameters, trainable on
twenty patients with no pretraining at all. The AIIoT paper already specifies exactly these
metrics for Exercise 2, so the design was right; only the Pi integration is outstanding.

**Decrement is also a PD-versus-ET discriminator.** Progressive amplitude reduction during
repetitive movement is specifically parkinsonian; ET does not produce it. So the flex
channel contributes to the differential-diagnosis claim through a *completely different
mechanism* than the phase argument. Two independent lines of evidence for the same
conclusion are worth considerably more than two correlated ones. Flag for clinical
confirmation.

**The flex channel does not block on Synapse access.** With a small feature set and a small
model, it is not data-starved. This is the one channel with a working zero-dependency
fallback.

#### Build order: cohort-only first, mPower as an enhancement

Not either/or. Sequential:

**1. Cohort-only (unblocked, do this first).** Fit the ~6-parameter model on the patient
cohort's own flex data. Twenty subjects supports six parameters. No Synapse dependency, no
transfer assumptions to defend. This is the floor, and it survives every failure mode
upstream.

**2. mPower-pretrained (enhancement, if access arrives).** What this buys is *not* mostly
"more data for a six-parameter model" — at that size the channel is not data-starved. It
buys three other things:

- **Feature-set validation at n ≈ 9,500.** If these features do not separate PD from
  controls on thousands of people, they will not on twenty. Much better to learn that before
  collecting patient data.
- **Population reference ranges.** What is a normal tap rate, what decrement ratio is
  abnormal. Twenty people cannot establish this.
- **The same-model-two-sensors comparison** (below), which is the clean version of the
  glove-versus-phone head-to-head.

**If both exist, report the comparison.** "Cohort-fitted achieved X; mPower-pretrained
achieved Y" is itself a result about whether the transfer works.

### Feature-level transfer from mPower tapping

mPower's tapping module measures **the same construct with a different sensor**: screen taps
rather than flexion angle. The construct transfers even when the signal does not. Write one
feature extractor and two thin adapters:

```
bradykinesia_features(tap_times, tap_amplitudes) -> features
    tap_rate                    taps per second
    inter_tap_interval_cv       coefficient of variation = irregularity
    rate_decrement_ratio        rate in last third / first third
    amplitude_decrement_ratio   amplitude in last third / first third
    n_hesitations               gaps beyond threshold

  flex adapter:   peak detection on flexion signal -> (times, bend amplitudes)
  mPower adapter: tap timestamps + position deltas -> (times, spatial amplitudes)
```

**Be precise about what transfers:**

- **Timing features transfer cleanly.** Rate, inter-tap variability, rate decrement. Same
  construct regardless of how the tap was detected.
- **Absolute amplitude does not transfer at all.** mPower measures touch position in screen
  units; flex measures bend angle via ADC. Different physical quantities, no meaningful
  mapping.
- **Amplitude decrement transfers, but only normalised.** Express as a ratio (last third
  over first third), not an absolute drop. This matters because decrement is the clinically
  important, PD-specific signal, so it needs to be in the transferable set.

**Rule: normalise every feature within subject and within session.** Then the feature space
is sensor-agnostic and the comparison is legitimate.

**Verify the mPower tapping protocol on access.** It is believed to be two fingers
alternating between on-screen targets, whereas MDS-UPDRS 3.4 and this project's protocol are
index-tapping-thumb. Different biomechanics for the same construct. Rate and decrement
should still be comparable, but confirm, because a large enough difference weakens the
transfer argument.

**What mPower is actually for here.** Not weight transfer, and not rescuing an underpowered
model:

1. **Validating the feature set.** Do these five features separate PD from HC at n = 5,000?
   If not, they will not at n = 20 — and it is much better to learn that before collecting
   patient data.
2. **Population reference ranges.** What is a normal tap rate? What decrement ratio is
   abnormal? Twenty people cannot establish that; thousands can.
3. **Effect size expectations.** Knowing the separation to expect tells you whether a glove
   result is plausible or whether the pipeline is broken.

#### Train the mPower model deliberately handicapped

The transferable feature subset is smaller than what mPower alone could support. Absolute
amplitude in particular is screen position in one case and bend angle in the other, with no
meaningful mapping between them.

**So train the mPower bradykinesia model using only the sensor-agnostic normalised features,
even where an mPower-specific feature would improve its standalone accuracy.** A model that
scores better on mPower but breaks on flex input is worthless here. Cripple it on purpose so
it transfers.

#### The payoff: one model, two sensors, a clean controlled comparison

If a single bradykinesia model serves both sensors, the glove-versus-phone head-to-head
becomes a properly controlled experiment:

> One bradykinesia model, trained on mPower tapping features. Applied to two sensors on the
> same patients: phone screen tapping and glove flex. **The only variable is the sensor.**

That is considerably stronger than training two separate models and comparing their outputs,
where any difference could come from the models rather than the hardware. This isolates
exactly what the paper claims: that per-finger flex sensing beats a capacitive touchscreen at
the same clinical task.

**Consequence for fusion.** Sharing a model makes `flex_brady` and the tapping component
inside `phone_score` *more* correlated than previously noted. That reinforces treating the
head-to-head as a reported ablation rather than relying on both as independent fusion inputs.

**And it does not move flex to level 1.** Good test of the grouping rule: grouping follows
*pairing*, not where a model was pretrained. mPower's tapping is paired with mPower's voice
and gait. The cohort's flex readings are paired with the cohort's phone readings, not with
mPower's. Flex stays at level 2.

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

### mPower data governance — resolve before downloading anything

Synapse registration includes a pledge covering inclusion and respect, legal compliance,
ethical conduct, **security measures for the content**, open-access practice, crediting
sources, no marketing use, and 2-business-day incident reporting. Nothing in this project's
intended use conflicts with any of that in spirit. But the pledge is not the binding
document — the **mPower-specific conditions of use**, agreed at the data request step, are.
Two questions must be answered before committing to the mPower plan.

**1. Can mPower data be hosted on Kaggle? This is the one that could break the workflow.**

The security item commits the account holder to appropriate technical and administrative
measures. This project's entire compute pattern is: download dataset, upload to a *private
Kaggle dataset*, train there. That is fine for PADS (PhysioNet, open licence). It may not
be permitted for mPower.

Governed datasets commonly prohibit redistribution and require the data remain under the
qualified recipient's control. A private Kaggle dataset is still third-party hosted, and
"private" means private from other Kaggle users, not from Kaggle itself. **If mPower's
conditions restrict re-hosting, the standard workflow is non-compliant** and an alternative
compute path is needed — which is a serious constraint given there is no AWS access and
Kaggle is where everything currently runs.

Ask `act@sagebionetworks.org` directly, in writing, before downloading.

**2. Does secondary use need institutional review?**

Secondary analysis of an existing de-identified dataset is often exempt or classed as
not-human-subjects-research, but **the institution decides, not the researcher**.
Northeastern research compliance should confirm. This is separate from the IRB covering
this project's own patient collection.

**Get the data use statement right.** It should describe the actual intended work, not a
narrower version: training and fine-tuning across the voice, walking, and tapping modules;
later combination of derived model outputs with a separately-consented clinical cohort;
and publication of results. Also ask explicitly whether **model weights trained on mPower
count as derived data** with their own restrictions — this matters if a checkpoint is ever
released, and agreements differ on it.

**Status: not yet asked.** Owner: An. Do this in parallel with registration, not after.

### Access concentration risk

Three of the five scoring channels plus the fusion pretraining all sit behind a single Synapse
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

## 5. Paper framing and narrative

Decided direction: the paper is a **multimodal low-cost home PD assessment system**, with
PD-versus-ET as an integrated part of the argument rather than a separate contribution.
This section records how to frame that so it does not collapse into the generic
"we fused modalities and got X%" paper.

### 5.1 ET is the validity check, not a bonus feature

The instinct is to present differential diagnosis as an extra. Framed that way, a reviewer
reads it as underpowered scope creep. Reframe it:

**Essential tremor is more common than Parkinson's.** A home system that detects "tremor"
and reports PD will misclassify a substantial fraction of the people who would actually
use it. So the ET evaluation is not a bonus, it is what makes the detection claim credible
outside a curated cohort where everyone already has a diagnosis.

That single move puts ET in the spine of the argument. The paper is not "we detect PD, and
also ET." It is **"we detect PD in a way that survives the population the device would
actually meet."**

### 5.2 The four gaps, and what fills each

The gap is not that nobody does multimodal. It is that the field reports accuracy and
almost nothing else. Four specific failures, each matched to something this project has:

| Gap in the field | What this project has |
|---|---|
| **Single-modality.** PD is not one symptom; systems measuring one domain miss the others | Tremor and bradykinesia (glove), voice, gait, tapping |
| **Data shipping.** Most home systems send raw biometrics to the cloud | On-device inference, score-only publishing, AES-256-GCM, MQTT message expiry — all implemented and tested (D3) |
| **No deployment accounting.** Everyone trains in the cloud, few report what it costs on target hardware | Model size, quantization cost, latency, cold start, peak memory (D3) |
| **The easy comparison.** Nearly everything benchmarks PD against healthy controls | Benchmarked against essential tremor, the question a clinician actually faces |

The first is the system, the middle two are the engineering, the fourth is the clinical
credibility. Together they are the paper.

### 5.3 Structure

1. **Motivation.** Clinic visits are sparse, symptoms fluctuate hourly, specialist access
   is limited globally. Cheap home assessment matters most where DaTscan and neurologists
   are unavailable.
2. **System.** Commodity hardware: per-finger glove plus a phone. State the cost explicitly.
3. **Pipeline.** Pretrain on public data (PADS, mPower), adapt on a small
   clinician-confirmed cohort, deploy quantized to the Pi.
4. **Evaluation — this is the differentiating section.** Subject-level splits throughout,
   pooled out-of-fold subgroup fairness, full deployment cost accounting, and the
   PD-versus-ET comparison.
5. **Limitations.** Small cohort, self-reported labels in mPower, laptop-proxy latency
   until the Pi is accessible again.

### 5.4 Title

Working title:

> **Not All Tremor Is Parkinson's: A Low-Cost Multimodal Edge System for Home Assessment
> and Differential Diagnosis**

The first clause states the problem in six words, is memorable, and signals immediately
that this is not the crowded PD-versus-healthy paper. The subtitle carries the keywords a
reviewer scans for.

Alternatives by emphasis:

- *Conventional, safer:* "A Low-Cost Multimodal Edge System for Home Parkinson's Assessment
  and Differential Diagnosis from Essential Tremor"
- *Most combative, leads with the methodological complaint:* "Beyond Accuracy: Deployment
  Cost, Subgroup Fairness, and Differential Diagnosis in a Low-Cost Parkinson's Monitor"
- *Continues the existing brand:* "Sensing-to-Decision at Home: Multimodal Edge Assessment
  and Parkinsonian versus Essential Tremor Discrimination"

On the last option: the AIIoT paper is *"Sensing-to-Decision: A Low-Cost, Privacy-Centric
Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification."*
Reusing the prefix builds a recognisable line of work, which is worth something if several
papers come off this hardware. The cost is that it reads as incremental rather than
distinct. Only do it if the series is deliberate.

**Avoid in the title:** the phrase "multimodal fusion" (files the paper into the crowded
bucket, and fusion is not the contribution), and any number — no accuracy figure, no
subject count. At this cohort size a number in the title invites exactly the scrutiny the
feasibility framing is meant to avoid.

### 5.5 Two cautions

**Do not let "multimodal" carry the novelty.** If a reviewer can summarise the paper as
"they fused three modalities and got X%," it lands in the crowded bucket. The sentence they
should be able to write is *"they built a complete low-cost home system and reported what
it actually costs to run and where it fails."* Multimodality is how the system is complete,
not why it is new.

**Decide the ET fallback before writing the introduction.** If ET recruitment fails
(§7 risk table), the fallback is to run PD-versus-ET on PADS' 28 ET subjects as a
wrist-only offline analysis, reported as a dataset result rather than a claim about the
glove. That is weaker but publishable. Knowing this in advance prevents building an
introduction that cannot be supported.

### 5.6 Venue fit

This framing suits venues like UEMCON and AIIoT, where a working system with honest
engineering accounting is valued above a novel ML claim. Since the existing accepted paper
is in that family, this reads as a coherent continuation rather than a pivot. Both venues
tend toward colon-subtitle titles with keyword-dense second halves, which is why every
option in §5.4 keeps that shape.

---

## 6. Staging

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

**Stage 0 — now, no IRB, no new data, and independent of mPower.**

Add the PADS differential-diagnosis groups back in. `load_labels()` currently assigns
`label = -1` to everything that is not PD or Healthy, discarding all 114 DD subjects
including the 28 with essential tremor. This establishes the wrist-only baseline the glove
must beat, and measures how much harder differential diagnosis is than PD-vs-HC. If
wrist-only PD-vs-ET lands well below PD-vs-HC, that gap *is* the motivation section.

**This is not a contingency for mPower failing.** The two are orthogonal: mPower supplies
the phone modalities, PADS supplies the differential-diagnosis question. Stage 0 should
happen regardless of how the Synapse process goes, and it happens to also be the thing that
keeps the paper alive if both mPower access and ET recruitment fall through.

Four practical points:

1. **This is a new task, not a replacement.** Do not overwrite the PD-vs-HC results in the
   D2 and D3 reports — those remain valid as reported. Add PD-vs-ET as a parallel analysis
   with its own label mapping and its own numbers.
2. **Expect a worse F1 than PD-vs-HC, partly for uninteresting reasons.** PD-vs-ET is
   276 vs 28 subjects, roughly a 10:1 imbalance, against 3.5:1 for PD-vs-HC. D3 established
   that subgroup class balance alone shifts macro-F1 substantially, so some of the drop will
   be imbalance rather than task difficulty. Report AUROC prominently (prevalence-invariant)
   and state the class ratio explicitly. Consider a PD-subsampled variant matched to the ET
   arm as a sanity check.
3. **Run PD-vs-all-DD as well.** 276 vs 114 is far better balanced than 276 vs 28, and
   "PD versus other movement disorders" is a legitimate clinical question in its own right.
   Two analyses: the specific one (ET, small, clinically sharp) and the better-powered
   broader one (all DD).
4. **28 ET subjects across 5-fold subject-level CV is 5 to 6 per fold.** Thin. Treat the
   output as effect sizes with wide intervals, not a headline accuracy.

**Stage 0b — start in parallel, calendar time only.**
Begin the Synapse access process for mPower (registration, certification, profile
validation, data use statement) and download MDVR-KCL. Neither depends on IRB, both take
elapsed time rather than effort, and mPower gates three of the five scoring channels.

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

## 7. Risks and dependencies

| Risk | Impact | Mitigation |
|---|---|---|
| IRB not yet cleared | Blocks every patient-facing stage | Critical path; nothing downstream has a timeline until it moves |
| ET arm cannot be recruited | Removes the *glove* discrimination claim, but **not** the PADS analysis, which needs no recruitment | Ask Prof. Singh early whether the clinical contact reaches ET patients at all. Fallback ladder in §1.5 — the measurement claim survives even without an ET cohort. Decide which rung is acceptable before writing the introduction |
| Comparison group not yet decided | Determines the mechanism, the balance, and the achievable claim | §1.4 records the options. Needs clinical input on whether atypical parkinsonism belongs in the "not PD" arm |
| No clinical rater available | Cannot train toward MDS-UPDRS 0-4 | Within-person medication contrast needs no absolute severity labels |
| Full fine-tune at stage 3 | Silently destroys public-dataset representations | Freeze encoder; head-only or LoRA |
| Splitting by session not subject | Inflated accuracy, invalid result | Group on subject ID, as D1 through D3 already do |
| MQTT throughput ceiling | Sampling rate collapse when streaming | iTex hit this at 128 Hz and traced it to inter-payload interval. Current design publishes per-exercise summaries, not raw streams, so should be clear. Revisit if raw windows are ever streamed for cloud inference |
| Scope: five channels, one built | Unfinished multimodal paper | Stage so each channel is publishable alone |
| **Synapse access concentration** | mPower gates voice, gait, tapping, *and* fusion pretraining. One denial removes most of the phone-side system | Start the access process immediately, in parallel with IRB. Keep MDVR-KCL (ungated) on disk as an independent voice path |
| **mPower may not be hostable on Kaggle** | Would break the only available compute workflow, not just delay it | Email `act@sagebionetworks.org` before downloading. See §3 governance subsection. If re-hosting is prohibited, either find a compliant compute path or drop mPower and fall back to MDVR-KCL for voice, accepting the loss of paired fusion pretraining |
| **mPower labels are self-reported** | Pretraining on unconfirmed diagnoses | Frame as weak supervision at scale; the clinician-confirmed patient cohort provides strong supervision. Never report mPower accuracy as a clinical result |
| Voice task mismatch | Encoder pretrained on sustained vowels will not transfer to connected speech, or vice versa | Fix the task before writing the study protocol; record whichever task the encoder was pretrained on |

---

## 8. What is explicitly not a contribution

Worth being clear-eyed. These all appear in the project and all belong in the paper, but
none of them is the reason someone would cite it. Compare with §5.2, which lists what each
of them *does* contribute when combined.

- **Multimodal fusion** on its own. Crowded, and the generic framing of this entire space.
  Per §5.5: multimodality is how the system is complete, not why it is new.
- **Edge deployment / INT8 quantization.** Well trodden; the project's own citation list
  includes prior work establishing the latency and footprint benefits. What is less common
  is *reporting the full deployment cost* rather than asserting the technique works.
- **Methodological rigour.** Subject-level splits, pooled out-of-fold fairness auditing,
  and honest reporting make the paper trustworthy rather than novel. Good reviewers treat
  this as table stakes. It belongs in the methods section, not the contributions list.
- **Per-finger IMU placement by itself.** Per §1.2, thumb and index placement is already in
  the literature. The contribution has to be inter-digit *phase* as an EMG-free proxy, plus
  five channels, plus flex, plus deployment — not the fact of putting sensors on fingers.

The honest summary: no single element here is novel. The argument is that the *combination*
is a complete, deployable, honestly-measured system evaluated against the hard clinical
comparison, and that no existing system is all four of those at once.

---

## 9. Sources

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
