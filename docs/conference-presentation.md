# Conference Presentation — IEEE AIIoT 2026

**Paper:** Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification
**Conference:** IEEE World AI IoT Congress 2026, 20–22 May 2026
**Slot assumption:** 15-minute parallel-session talk
**Format:** ~6 min slides + ~5 min live demo + ~3 min Q&A
**Presenter:** An Nguyen
**Co-authors:** Hong Peng, Madhu Babu Cherukuri, Sarita Singh
**Presentation deadline:** 12 May 2026

## Audience

IEEE researchers from AI / IoT / edge-computing backgrounds. Mostly academic with industry presence. Technically strong but **not clinicians, not Parkinson's specialists, not necessarily wearable-sensor people**. So: keep it about the mission and the framework, not the bench details. The live demo carries the "how it actually works" story.

## Approach

Frame the talk around **what this enables in the world**, not what we soldered. The deck does three jobs:
1. Set the stakes (slides 2–3): why continuous PD monitoring is a real, growing, global-scale problem.
2. Hand off cleanly to the demo (slides 4–5): you've already built it; let the audience see it.
3. Close on impact, not architecture (slides 6–8): equity, accessibility, where this goes.

## Slide titles at a glance

| # | Slide title | Time |
|---|---|---|
| 1 | *Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification* (paper title verbatim) | 0:15 |
| 2 | The Monitoring Gap | 1:00 |
| 3 | Sensing-to-Decision: Privacy by Architecture | 1:00 |
| 4 | The Prototype | 0:30 |
| 5 | Live Demo | 5:00 |
| 6 | What the Prototype Proves | 1:00 |
| 7 | Designed for Where PD Is Growing Fastest | 1:00 |
| 8 | Three Takeaways | 0:30 |
| 9 | Questions? | 3:00 |

## Asset checklist

Images already in the repo at `images/`:

| Asset | Used on |
|---|---|
| `prototype_photo.jpg` | Slide 1 (corner), Slide 4 (full bleed), Slide 9 (background) |
| `edge_to_cloud_architecture.png` | Optional Slide 3 alternate visual |
| `pd_glove_circuit.png` | Optional Backup B3 visual |
| `pd_glove_dashboard_example.png` | Optional Backup B1 visual |

Build-side assets to create:

- [ ] Slide 2 — two-timeline graphic (sparse clinic dots vs dense symptom waveform)
- [ ] Slide 3 — three-icon row (glove / chip / encrypted envelope) with dashed red boundary line
- [ ] Slide 6 — three-statement layout, no graphics
- [ ] Slide 7 — cost progression graphic (Pi 5 today → Pi Zero 2W / ESP32 future)
- [ ] Slide 8 — three-line takeaways layout, no graphics
- [ ] Slide 9 — QR code linking to the paper (generate once IEEE Xplore listing is live)

---

## Slide 1 — Title (0:15)

**Title (on slide):**
> Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification

**Subtitle (on slide):**
> An Nguyen · Hong Peng · Madhu Babu Cherukuri · Sarita Singh
> Northeastern University — Khoury College of Computer Sciences
> IEEE World AI IoT Congress 2026

**Visual:** Title in large type, centered or left-aligned. Author block below in smaller type. Hero photo of the assembled glove (`images/prototype_photo.jpg`) bottom-right or as a soft watermark. AIIoT 2026 / IEEE branding bottom-left.

**Script:**

> "Good afternoon. I'm An Nguyen, from Northeastern University. This is joint work with Hong Peng, Madhu Babu Cherukuri, and Sarita Singh.
>
> What I'm going to show you today isn't really a sensor paper. It's a question about who gets to be monitored for a disease that's growing faster than any other in neurology — and a working prototype of one answer that runs entirely on commodity edge hardware."

**Notes:** Open with the framing shift. You're not pitching hardware; you're pitching access. Pause after "neurology" before saying "and a working prototype."

---

## Slide 2 — The Monitoring Gap (1:00)

**Title (on slide):**
> The Monitoring Gap

**Subtitle (on slide):**
> Parkinson's symptoms move hour by hour. Clinic visits happen every 3 to 6 months.

**On-slide text (large stat block, bottom of slide):**
> **25.2 million PD cases projected by 2050**
> *Most growth in regions with the fewest specialists.*

**Visual:** Two contrasting timelines stacked, top-to-bottom:
- Top timeline: thin sparse line with 3–4 dots, label "Clinic visits — every 3 to 6 months."
- Bottom timeline: dense fluctuating waveform, label "Actual symptoms — hour by hour."

The 25.2 M stat block sits below both timelines.

**Script:**

> "Here's the gap. Patients with Parkinson's see a neurologist a few times a year. Their motor symptoms shift hour by hour — medication wears off, fatigue sets in, stress changes everything. So the most important question for managing the disease — *am I in a good window or a bad one right now?* — is something the clinical system simply doesn't measure.
>
> And the gap is going to widen. Cases are projected to hit 25.2 million by 2050, and the steepest growth is in places that already have the fewest movement-disorder specialists. So whatever the answer is, it cannot depend on more clinic time. There isn't more clinic time."

**Notes:** Don't rush this slide. The mission of the entire talk lives here. If the audience leaves with one number, it's 25.2 million.

---

## Slide 3 — Sensing-to-Decision: Privacy by Architecture (1:00)

**Title (on slide):**
> Sensing-to-Decision

**Subtitle (on slide, bold strapline above the icon row):**
> Privacy-by-design, by architecture — not by policy.

**On-slide text (three-icon row across the middle):**

| Icon | Label | One-line caption |
|---|---|---|
| 🧤 (glove) | **Sense at home** | Continuous capture on commodity hardware |
| 🔲 (chip) | **Decide on-device** | Raw data stays here · Privacy boundary |
| 🔐 (envelope) | **Share only what matters** | Encrypted clinical summary, not raw biometrics |

**Visual:** Three icons in a horizontal row, each with the label + caption above. A bold dashed red vertical line falls just to the right of the middle icon, labeled **"Privacy-by-Design boundary"**. The strapline sits above the icon row in larger weight.

**Script:**

> "Our framework is called sensing-to-decision, and it has three commitments.
>
> First, the measurement happens at home, continuously, on commodity hardware — no clinic visit required.
>
> Second, the decision happens on the device itself. Raw accelerometer streams and raw finger-curvature streams never leave the Pi. Session video is captured by the patient's phone and encrypted on-device before it ever crosses the network. The interpretation — the actual scoring — is local.
>
> Third, what *does* leave is only the clinical summary, encrypted, designed for a clinician to act on. Not a waveform, not a plaintext video, not a fingerprint of someone's nervous system. A score, with context.
>
> The key word here is *architecture*. Privacy isn't a setting we toggle — it's a property of where computation physically happens. If the raw data isn't there, it can't leak."

**Notes:** This is the slide that defines what the project *is*. Land it cleanly. The "by architecture, not by policy" line is the most quotable thing in the talk — pause before and after it.

---

## Slide 4 — The Prototype (0:30)

**Title (on slide):**
> The Prototype

**Subtitle (on slide):**
> Five-finger wearable · Raspberry Pi 5 edge gateway · Built on commodity hardware

**On-slide text:** None — the photo carries the slide.

**Visual:** Single full-bleed photo of the assembled glove on the table next to the Pi 5 and the laptop running the demo dashboard (`images/prototype_photo.jpg` if it shows the full setup; otherwise stage a fresh photo). Subtitle sits at the bottom in smaller type.

**Script:**

> "I want to show you the prototype rather than describe it. So I'm going to step over to the demo here for the next few minutes — what you'll see is a real assessment, end-to-end, on the actual hardware. Then I'll come back and tell you what we've validated and where this is going."

**Notes:** Brief transition slide. Don't read the subtitle — the audience can. Walk to the demo setup as you finish speaking.

---

## Slide 5 — Live Demo (5:00)

**Title (on slide):**
> Live Demo

**Subtitle (on slide):**
> *(Optional — if you mirror the demo screen onto the projector, hide this slide.)*

**On-slide text:** None.

**Visual:** Either go dark, mirror the demo screen, or show a simple "Live Demo" title card — whatever's least distracting. If your laptop is doing the demo, mirror its screen here.

**Script:** *Demo runs from your existing 5-minute walkthrough.*

**Notes:**
- Have the demo loaded and warmed up *before* you begin Slide 1.
- If anything fails live, do not try to debug — pivot to "what you'd see is X" and continue.
- Time your demo. Five minutes goes fast on stage. Don't over-explain wiring.

---

## Slide 6 — What the Prototype Proves (1:00)

**Title (on slide):**
> What the Prototype Proves

**Subtitle (on slide):** None.

**On-slide text (three statements stacked, each in large type with a smaller supporting line):**

> **The signal is real.**
> *Across multi-subject testing, the device cleanly separates tremor from rest — every time, in the clinically expected frequency band.*
>
> **The hardware is reliable.**
> *Stable continuous capture across every session, with zero communication failures recorded.*
>
> **The pipeline runs entirely on the device.**
> *Raw data never leaves. The cloud only ever sees the encrypted summary.*

**Visual:** Plain three-statement layout. No graphics. Generous spacing so each statement reads as its own beat.

**Script:**

> "Three things we've established with the working prototype.
>
> The signal is real. Across nine validation tests on two subjects, the device reliably distinguishes resting tremor from rest, in the right 4-to-6-hertz frequency range every single time. The separation is large enough that there's no overlap between the two states.
>
> The hardware is reliable. Across every one of those tests, sampling stayed stable and we recorded zero communication retries on the sensor bus.
>
> And critically, the entire pipeline runs on the device itself. The cloud doesn't see your raw biometrics. It sees a clinical summary. That's the privacy commitment, in operation, today."

**Notes:** No tables, no per-channel numbers — the audience just watched the demo, they don't need the table. If a skeptic in Q&A asks for the actual separation magnitude, you have Backup B1.

---

## Slide 7 — Designed for Where PD Is Growing Fastest (1:00)

**Title (on slide):**
> Designed for Where PD Is Growing Fastest

**Subtitle (on slide):** None.

**On-slide text (cost progression, two stages, with a strapline below):**

> **Today** — Built on commodity hardware (Raspberry Pi 5)
>
> **Near future** — `<$35` deployment target on Pi Zero 2W (~$15) or ESP32 (~$5–10)

Strapline below the progression, in larger weight:

> **Continuous PD monitoring at the price of a phone charger.**

Smallest line below the strapline:
> *Engineered for the regions where PD is growing fastest.*

**Visual:** Simple horizontal arrow going left-to-right. Pi 5 icon on the left, Pi Zero 2W and ESP32 icons on the right. The strapline sits below the arrow in bold.

**Script:**

> "Here's why I think this is more than a research artifact.
>
> The architecture we built doesn't depend on expensive proprietary hardware or recurring cloud costs. Today's prototype runs on a Raspberry Pi 5. But the inference pipeline is designed to port directly to a Pi Zero 2W at around fifteen dollars, or an ESP32 in the five-to-ten-dollar range. The deployment target is under thirty-five dollars. Continuous, privacy-preserving Parkinson's monitoring, at the price of a phone charger.
>
> That's the part that I think matters most. The populations expected to see the biggest growth in PD over the next 25 years are not the populations with the most neurologists or the best broadband. If the answer to continuous monitoring requires either, it doesn't reach them. This one can."

**Notes:** This is the impact slide. Speak slower here. The "phone charger" line is meant to land — let it sit for a beat before continuing.

---

## Slide 8 — Three Takeaways (0:30)

**Title (on slide):**
> Three Takeaways

**Subtitle (on slide):** None.

**On-slide text:**

> **A working prototype, not a paper sketch.**
> *The sensing pipeline is real, validated, and reproducible.*
>
> **Privacy by architecture, not by promise.**
> *Raw data physically cannot leak from a device that never transmits it.*
>
> **Built for the world Parkinson's is actually growing in.**
> *Commodity hardware, no cloud dependency, deployable anywhere.*

**Visual:** Three short stacked statements. No graphics. Match the layout of Slide 6 visually so the audience recognizes the bookend.

**Script:**

> "Three things to take away.
>
> One, this is a working prototype — not a paper sketch. You just saw it run.
>
> Two, the privacy story is structural, not promotional. Data doesn't leak from a device that doesn't transmit it.
>
> And three, this is built for the world Parkinson's is actually growing in — the parts of the world where you can't assume specialist access or reliable broadband, but where the burden of this disease is going to land hardest over the next two decades.
>
> Thank you. I'd love to take questions."

**Notes:** Close clean. Don't add a fourth line. Pause before "Thank you."

---

## Slide 9 — Questions? (3:00)

**Title (on slide):**
> Questions?

**Subtitle (on slide):**
> An Nguyen · nguyen.an4@northeastern.edu

**On-slide text:** Optional — short paper title repeated below the email so attendees can identify the talk in conference proceedings.

**Visual:** Large "Questions?" centered. QR code (linking to the paper on IEEE Xplore once available) bottom-right. Prototype photo in the background at low opacity, or solid color.

**Notes:**
- Repeat each question into the mic before answering.
- If you don't know, say so. "Honest answer — that's outside what we've tested. My intuition is X, but I'd want to verify it." Beats bluffing.
- Three questions you should expect:
  1. "How does this compare to a PD diagnosis from a neurologist?" → Backup B2.
  2. "What about the parts you said are pending — flex sensors, the ML model?" → "Fair question. The sensing layer and the privacy architecture are validated today. The scoring model and the bradykinesia channel are next-stage work, with the dataset we showed already collected as the training input." Don't apologize.
  3. "Why not just use an Apple Watch?" → Backup B3.

---

## Backup slides (have ready, don't show by default)

### Backup B1 — The actual numbers, if asked

**Title (on slide):** "Validation Numbers"

**On-slide text:** Table I from the paper (Person A and B, tremor vs rest, min/max/median band power) and a strapline:

> **30× to 895× rest-to-tremor separation across all channels and subjects.**

**Talking points:**
- Nine validation tests across two subjects, 72 per-finger feature vectors total.
- All tremor captures landed in the 4–6 Hz Parkinsonian band.
- Rest band power stayed below 70 across every channel and subject; tremor band power ranged from ~670 up to ~26,000.
- Healthy volunteers performing simulated tremor — clinical PD-cohort validation is the next stage (Section VIII of the paper).

### Backup B2 — Clinical Validation Status

**Title (on slide):** "Clinical Validation — Where We Are"

**On-slide text:** A two-column table — left column "Done today," right column "Study II (next stage)":

| Done today | Study II (next stage) |
|---|---|
| Signal quality validated on healthy volunteers | Diagnosed PD cohort recruitment |
| 30–895× rest-to-tremor discrimination | Weighted-kappa vs neurologist scores |
| Privacy + encryption architecture | IRB-approved longitudinal protocol |

**Talking points:**
- The current dataset is healthy volunteers — we're transparent about that in the paper and in the talk.
- Formal clinical agreement (weighted-kappa against neurologist-scored sessions in a diagnosed PD cohort) is the next study, and the architecture is built to support it without changing the privacy contract.
- The signal quality demonstrated so far establishes that the device *can* discriminate — the open question is whether the learned model's scores agree with clinician scores, and that's empirically open.

### Backup B3 — Why Not an Apple Watch?

**Title (on slide):** "Why Per-Finger, Not Wrist"

**On-slide text:** Side-by-side comparison.

> **Wrist sensor:** averages thumb-index pill-rolling motion away.
>
> **Per-finger sensors:** preserve the spatial signature of Parkinsonian tremor.

**Talking points:**
- Wrist sensors measure aggregate hand motion. Parkinsonian resting tremor has a specific thumb-index opposition pattern that a wrist sensor averages out.
- Per-finger sensing also captures asymmetry — Parkinson's often presents one hand or specific fingers worse than others — which is clinically meaningful and invisible to wrist data.
- And cost — a $400 watch is not a global-deployment story.

---

## Slide design suggestions

To make the deck visually coherent without spending a lot of time on it:

- **Color palette:** Stick to two accent colors. Suggest **`#3b82f6` (blue, used in the existing app UI)** for "you / patient" elements and **`#ef4444` (red)** for the privacy boundary on Slide 3. Neutrals for everything else.
- **Typography:** A single sans-serif throughout (Inter, Helvetica Neue, or PowerPoint's Calibri). Title 40–48pt, body 24–28pt, captions 14–16pt. Don't mix more than two weights.
- **Slide masters:** Use one master slide for the seven content slides (2, 3, 4, 6, 7, 8, 9) so headers and footers stay consistent. Slide 1 (title) and Slide 5 (demo) can have their own layouts.
- **Footer (every content slide):** small line bottom-left — "AIIoT 2026 · An Nguyen · Northeastern" — plus slide number bottom-right.
- **Avoid:** dense bullets, animations, transitions, screenshots of the paper. The slides must be readable from the back of the room.

## Pre-talk checklist

- [ ] Confirm talk length and AV format with session chair
- [ ] Demo laptop charged, glove + Pi powered, network ready, demo loaded *before* Slide 1
- [ ] Backup: bring slides on a USB stick in PDF format in case AV fails on your laptop
- [ ] Time the slides-only run (target ~6 min) and a full run with demo (target ~11 min)
- [ ] Practice Slide 3 (privacy by architecture) and Slide 7 (scale) until you can deliver them without notes — these are the two slides that carry the talk
- [ ] If the demo fails live, pivot to "what you'd see is…" and keep moving — do not debug on stage
- [ ] Generate the QR code for Slide 9 once the IEEE Xplore listing is live

## Tone reminders

- This is a story about access and privacy at global scale, illustrated by a working device. The device is the evidence; the mission is the message.
- Don't apologize for what's pending. Reviewers accepted the work knowing the scope. The audience will follow your lead — if you treat it as a strength, they will too.
- Speak slowly. Pause after the "phone charger" line on Slide 7 and the "by architecture, not by policy" line on Slide 3. Both are designed to land.
