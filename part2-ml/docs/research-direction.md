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

**Per-finger inertial sensing improves differential diagnosis of Parkinsonian tremor
versus essential tremor, relative to wrist-worn sensing.**

The mechanism is specific rather than general. The clinical sign that distinguishes PD
rest tremor from essential tremor is pill-rolling, a thumb-index opposition pattern.
That is a finger-level phenomenon. A wrist-mounted sensor measures aggregate hand
acceleration and spatially averages away which digits are moving. Five per-finger IMUs
can, in principle, resolve thumb-index relative motion directly.

**Needs clinical verification:** the pill-rolling and rest-versus-action distinctions are
well established, but how cleanly they separate in real patients (as opposed to in a
textbook table) should be confirmed with Prof. Singh or a neurologist before this becomes
load-bearing.

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

### Why the PD/ET distinction is worth solving

Different first-line medications with no overlap (levodopa for PD; propranolol or
primidone for ET), different prognosis (progressive neurodegeneration versus a generally
slower course), and a real misdiagnosis rate in both directions. When the distinction
cannot be resolved clinically, the current tiebreaker is DaTscan imaging, which needs a
radioactive tracer, specialised facilities, and significant cost. A low-cost wearable
that gives meaningful signal on this question matters most exactly where that imaging is
unavailable, which sharpens the accessibility argument already in the AIIoT paper.

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
| Patient data collection | **Blocked** — IRB pending |

Roughly one of the three proposed modalities is built.

---

## 3. Architecture

### Three unimodal encoders, late fusion

```
[Glove: 5x per-finger IMU + flex]  -> tremor/bradykinesia encoder -> score_motion
[Phone mic: voice recording]       -> dysarthria encoder          -> score_voice
[Phone camera: gait/posture video] -> pose-based encoder          -> score_gait
                                                                        |
                                             late fusion (small, LOSO-validated)
                                                                        |
                                                                  final output
```

### Why late fusion, and why the fusion head is the constrained part

PADS, MDVR-KCL, and REMAP Open share no subjects. No person in any public dataset has all
three modalities. So the public data can fine-tune three encoders independently, but it
**cannot** train a fusion layer at all. The fusion layer can only be trained on paired
patient data, which means it is the component running at n = 15 to 20.

Consequences:

- Fusion must be small. Logistic regression over three scores is roughly four parameters
  and is fittable at that scale under LOSO. A learned cross-attention fusion module is not.
- Describe it as **late fusion of independently adapted unimodal encoders**, not "learned
  multimodal fusion."
- Do **not** validate fusion by stitching PADS/MDVR-KCL/REMAP subjects together by
  diagnosis label. That is precisely the confound that makes existing tri-modal papers
  unconvincing, and doing it forfeits the main methodological differentiator.
- Design for **missing modalities** from the start. At n = 20 a participant cannot be
  dropped because one recording failed or because they use a mobility aid and could not do
  the gait task. A fusion rule that renormalises over available modalities costs nothing
  now and prevents losing subjects later.

### Transfer sequence per modality

```
general pretrained model  ->  large public PD dataset  ->  paired patient data
      (MOMENT, etc.)            (full fine-tune)          (frozen / LoRA / head-only)
```

**Stage 3 must not be a full fine-tune.** At n around 30, full fine-tuning will overwrite
the public-dataset representations. Head-only, LoRA, or linear probing.

### Datasets per modality

| Modality | Public dataset | Access | Contains ET? | Notes |
|---|---|---|---|---|
| Motion | PADS | Already staged | **Yes, 28** | 276 PD, 79 HC, 114 DD, wrist acc+gyro @ 100 Hz |
| Voice | MDVR-KCL | Public (Zenodo) | No | 16 PD, 21 HC, raw `.wav`, recorded on a Motorola Moto G4 smartphone |
| Gait | REMAP Open | Public download, no request form | No | 12 PD, 12 HC, 2D/3D skeleton pose, sit-to-stand and gait turns, medication state labels |

**Only PADS has essential tremor.** This constrains the research claim materially: the
PD-versus-ET signal can be pretrained on public data for the motion modality only. For
voice and gait, the public encoders can only learn PD-versus-healthy, and any ET
discrimination in those modalities has to be learned at the paired-patient stage where
n is 15 to 20. See §3.1.

### Capture format, and what each modality needs from a phone

**Voice: clean fit.** MDVR-KCL was itself recorded on a Motorola Moto G4 smartphone, so the
public training data and the eventual deployment device are the same class of hardware.
No domain gap worth worrying about. A phone microphone is sufficient.

**Gait: there is a real domain gap, and it is easy to miss.** REMAP Open does **not**
contain video. The released data is derived 2D/3D skeleton coordinates in CSV, coarsened
for anonymisation — the raw RGB footage is withheld precisely because faces are
identifying. Consequences:

- You cannot run your own pose estimator over REMAP. There are no frames to process.
- You would train on their skeleton coordinates, then at inference run a pose model
  (MediaPipe Pose or similar) over phone video to produce skeletons, then feed those in.
- **The two skeleton formats will not match.** Joint sets, ordering, and coordinate
  conventions differ between pose estimators. A harmonisation layer mapping MediaPipe
  output onto REMAP's joint schema is required work, not a detail.
- **Viewpoint differs too.** REMAP used fixed wall-mounted cameras in a home. A handheld
  or tripod phone is a different distance, height, and angle. Skeleton coordinates are
  sensitive to this unless normalised (scale, translation, and rotation invariance need to
  be handled explicitly).

This is the main reason gait is staged last: it is the only modality where the public data
and the deployment sensor are not the same kind of signal.

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

| Modality | Expected in PD | Expected in ET |
|---|---|---|
| Motion (glove) | Rest tremor, pill-rolling, bradykinesia | Action/postural tremor, no pill-rolling |
| Gait / posture | Postural instability, shuffling, reduced arm swing | Largely unaffected |
| Voice | Hypophonia, monotone (hypokinetic dysarthria) | Vocal tremor in some patients |

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

The wider public-dataset survey (PD-BioStampRC21, Daphnet, Oday, MJFF, mPower, REMAP) was
reviewed and deprioritised for merging into PADS: every candidate is missing at least one
of wrist placement, both accelerometer and gyroscope, a real PD/HC comparison, or open
access. More importantly, none of them have per-finger placement or flex sensors, so none
of them can substitute for glove data on the core research question.

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

**Stage 0 — now, no IRB, no new data.**
Reframe PADS from PD-vs-HC to PD-vs-ET (28 ET subjects currently discarded in
`load_labels()`). This establishes the wrist-only baseline the glove must beat and
measures how much harder the differential-diagnosis question is. If wrist-only PD-vs-ET
lands well below PD-vs-HC, that gap is the motivation section.

**Stage 1 — finish the glove.**
Flex sensors integrated on the Pi 5, CH4 fault resolved, real Pi latency measured. Plus an
IRB'd patient study, this is a complete paper on its own: per-finger sensing against the
single-IMU baseline.

**Stage 2 — add voice.**
Cheapest modality: phone microphone, no new hardware, best-supported in the literature,
public dataset with raw audio and a PD/HC split already identified.

**Stage 3 — add gait.**
Most work (pose estimation, framing, the baggy-clothing and mobility-aid failure modes)
and most likely to be cut for time. REMAP Open is downloadable now if it happens.

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
| Scope: three modalities, one built | Unfinished trimodal paper | Stage so each modality is publishable alone |

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
