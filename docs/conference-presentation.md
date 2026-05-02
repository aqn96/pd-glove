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

## Deck overview (8 slides + Q&A)

| # | Slide | Time |
|---|---|---|
| 1 | Title | 0:15 |
| 2 | The mismatch we're solving | 1:00 |
| 3 | Our answer: sensing-to-decision, on the edge | 1:00 |
| 4 | What we built (demo handoff) | 0:30 |
| 5 | **[Live demo]** | 5:00 |
| 6 | What we've shown works | 1:00 |
| 7 | Why this matters at scale | 1:00 |
| 8 | Takeaways | 0:30 |
| 9 | Q&A | 3:00 |

---

## Slide 1 — Title (0:15)

**Visual:** Title in large type. Author block: An Nguyen, Hong Peng, Madhu Babu Cherukuri, Sarita Singh. Northeastern University / Khoury College of Computer Sciences. Hero photo of the assembled glove (`images/prototype_photo.jpg`) bottom-right. AIIoT 2026 / IEEE branding bottom-left.

**Script:**

> "Good afternoon. I'm An Nguyen, from Northeastern University. This is joint work with Hong Peng, Madhu Babu Cherukuri, and Sarita Singh.
>
> What I'm going to show you today isn't really a sensor paper. It's a question about who gets to be monitored for a disease that's growing faster than any other in neurology — and a working prototype of one answer that runs entirely on commodity edge hardware."

**Notes:** Open with the framing shift. You're not pitching hardware; you're pitching access. Pause after "neurology" before saying "and a working prototype."

---

## Slide 2 — The mismatch we're solving (1:00)

**Visual:** Two contrasting timelines stacked.
- Top: thin sparse line with 3–4 dots, labeled "Clinic visits — every 3 to 6 months."
- Bottom: dense fluctuating waveform, labeled "Actual symptoms — hour by hour."

Below, large stat: **"25.2 million PD cases projected by 2050."** Smaller line beneath: *"Most growth in regions with the fewest neurologists."*

**Script:**

> "Here's the gap. Patients with Parkinson's see a neurologist a few times a year. Their motor symptoms shift hour by hour — medication wears off, fatigue sets in, stress changes everything. So the most important question for managing the disease — *am I in a good window or a bad one right now?* — is something the clinical system simply doesn't measure.
>
> And the gap is going to widen. Cases are projected to hit 25.2 million by 2050, and the steepest growth is in places that already have the fewest movement-disorder specialists. So whatever the answer is, it cannot depend on more clinic time. There isn't more clinic time."

**Notes:** Don't rush this slide. The mission of the entire talk lives here. If the audience leaves with one number, it's 25.2 million.

---

## Slide 3 — Our answer: sensing-to-decision, on the edge (1:00)

**Visual:** Three icons in a horizontal row, each with a one-line label:
1. **Sense at home** — small glove icon
2. **Decide on-device** — small chip icon, with a red "raw data stays here" boundary line
3. **Share only what matters** — small encrypted-envelope icon, labeled "clinical summary"

Above the row: a single bold strapline — **"Privacy-by-design, by architecture — not by policy."**

**Script:**

> "Our framework is called sensing-to-decision, and it has three commitments.
>
> First, the measurement happens at home, continuously, on commodity hardware — no clinic visit required.
>
> Second, the decision happens on the device itself. Raw accelerometer streams and raw finger-curvature streams never leave the Pi. Session video is captured by the patient's phone and encrypted on-device before it ever crosses the network. The interpretation — the actual scoring — is local.
>
> Third, what *does* leave is only the clinical summary, encrypted, designed for a clinician to act on. Not a waveform, not a plaintext video, not a fingerprint of someone's nervous system. A score, with context.
>
> The key word here is *architecture.* Privacy isn't a setting we toggle — it's a property of where computation physically happens. If the raw data isn't there, it can't leak."

**Notes:** This is the slide that defines what the project *is*. Land it cleanly. The "by architecture, not by policy" line is the most quotable thing in the talk — pause before and after it.

---

## Slide 4 — What we built (0:30)

**Visual:** Single full-bleed photo of the assembled glove on the table next to the Pi 5 and the laptop running the demo dashboard. Small caption: *"Five-finger wearable. Raspberry Pi 5 edge gateway. Built on commodity hardware."*

**Script:**

> "I want to show you the prototype rather than describe it. So I'm going to step over to the demo here for the next few minutes — what you'll see is a real assessment, end-to-end, on the actual hardware. Then I'll come back and tell you what we've validated and where this is going."

**Notes:** Brief transition slide. Don't read the caption — the audience can. Walk to the demo setup as you finish speaking.

---

## Slide 5 — [Live demo placeholder] (5:00)

**Visual:** Either go dark, mirror the demo screen, or show a simple "Live Demo" title card — whatever's least distracting. If your laptop is doing the demo, mirror its screen here.

**Script:** *Demo runs from your existing 5-minute walkthrough. You already know this part.*

**Notes:**
- Have the demo loaded and warmed up *before* you begin Slide 1.
- If anything fails live, do not try to debug — pivot to "what you'd see is X" and continue.
- Time your demo. Five minutes goes fast on stage. Don't over-explain wiring.

---

## Slide 6 — What we've shown works (1:00)

**Visual:** Three short statements in large type, each with a tiny supporting line below.

> **The signal is real.** Across multi-subject testing, the device cleanly separates tremor from rest — every time, in the clinically expected frequency band.
>
> **The hardware is reliable.** Stable continuous capture across every session, with zero communication failures recorded.
>
> **The pipeline runs entirely on the device.** Raw data never leaves. The cloud only ever sees the encrypted summary.

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

## Slide 7 — Why this matters at scale (1:00)

**Visual:** A simple cost progression graphic.
- Today: "Built on commodity hardware (Raspberry Pi 5)" with Pi 5 icon.
- Near future: **"<$35 deployment target"** with Pi Zero 2W (~$15) / ESP32 (~$5–10) icons.
- Below, large bold line: **"Continuous PD monitoring at the price of a phone charger."**

Smaller line below that: *"Engineered for the regions where PD is growing fastest."*

**Script:**

> "Here's why I think this is more than a research artifact.
>
> The architecture we built doesn't depend on expensive proprietary hardware or recurring cloud costs. Today's prototype runs on a Raspberry Pi 5. But the inference pipeline is designed to port directly to a Pi Zero 2W at around fifteen dollars, or an ESP32 in the five-to-ten-dollar range. The deployment target is under thirty-five dollars. Continuous, privacy-preserving Parkinson's monitoring, at the price of a phone charger.
>
> That's the part that I think matters most. The populations expected to see the biggest growth in PD over the next 25 years are not the populations with the most neurologists or the best broadband. If the answer to continuous monitoring requires either, it doesn't reach them. This one can."

**Notes:** This is the impact slide. Speak slower here. The "phone charger" line is meant to land — let it sit for a beat before continuing.

---

## Slide 8 — Takeaways (0:30)

**Visual:** Three short lines.

> **A working prototype, not a paper sketch.** The sensing pipeline is real, validated, and reproducible.
>
> **Privacy by architecture, not by promise.** Raw data physically cannot leak from a device that never transmits it.
>
> **Built for the world Parkinson's is actually growing in.** Commodity hardware, no cloud dependency, deployable anywhere.

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

## Slide 9 — Q&A (3:00)

**Visual:** "Questions?" with paper QR code (link to IEEE Xplore listing once available) + presenter email + the prototype photo.

**Notes:**
- Repeat each question into the mic before answering.
- If you don't know, say so. "Honest answer — that's outside what we've tested. My intuition is X, but I'd want to verify it." Beats bluffing.
- Three questions you should expect:
  1. "How does this compare to a PD diagnosis from a neurologist?" → Backup B2.
  2. "What about the parts you said are pending — flex sensors, the ML model?" → "Fair question. The sensing layer and the privacy architecture are validated today. The scoring model and the bradykinesia channel are next-stage work, with the dataset we showed already collected as the training input." Don't apologize.
  3. "Why not just use an Apple Watch?" → Backup B3.

---

## Backup slides (have ready, don't show by default)

### B1 — The actual numbers, if asked

**Visual:** Table I from the paper (Person A and B, tremor vs rest, min/max/median band power) plus a line: **"30× to 895× rest-to-tremor separation across all channels and subjects."**

**Talking points:**
- Nine validation tests across two subjects, 72 per-finger feature vectors total.
- All tremor captures landed in the 4–6 Hz Parkinsonian band.
- Rest band power stayed below 70 across every channel and subject; tremor band power ranged from ~670 up to ~26,000.
- Healthy volunteers performing simulated tremor — clinical PD-cohort validation is the next stage (Section VIII of the paper).

### B2 — Clinical validation status

**Talking points:**
- The current dataset is healthy volunteers — we're transparent about that in the paper and in the talk.
- Formal clinical agreement (weighted-kappa against neurologist-scored sessions in a diagnosed PD cohort) is the next study, and the architecture is built to support it without changing the privacy contract.
- The signal quality demonstrated so far establishes that the device *can* discriminate — the open question is whether the learned model's scores agree with clinician scores, and that's empirically open.

### B3 — Why not an Apple Watch?

**Talking points:**
- Wrist sensors measure aggregate hand motion. Parkinsonian resting tremor has a specific thumb-index opposition pattern that a wrist sensor averages out.
- Per-finger sensing also captures asymmetry — Parkinson's often presents one hand or specific fingers worse than others — which is clinically meaningful and invisible to wrist data.
- And cost — a $400 watch is not a global-deployment story.

---

## Pre-talk checklist

- [ ] Confirm talk length and AV format with session chair
- [ ] Demo laptop charged, glove + Pi powered, network ready, demo loaded *before* Slide 1
- [ ] Backup: bring slides on a USB stick in PDF format in case AV fails on your laptop
- [ ] Time the slides-only run (target ~6 min) and a full run with demo (target ~11 min)
- [ ] Practice Slide 3 (privacy by architecture) and Slide 7 (scale) until you can deliver them without notes — these are the two slides that carry the talk
- [ ] If the demo fails live, pivot to "what you'd see is…" and keep moving — do not debug on stage

## Tone reminders

- This is a story about access and privacy at global scale, illustrated by a working device. The device is the evidence; the mission is the message.
- Don't apologize for what's pending. Reviewers accepted the work knowing the scope. The audience will follow your lead — if you treat it as a strength, they will too.
- Speak slowly. Pause after the "phone charger" line on Slide 7 and the "by architecture, not by policy" line on Slide 3. Both are designed to land.
