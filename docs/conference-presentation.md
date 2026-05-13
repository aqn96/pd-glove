# Conference Presentation — IEEE AIIoT 2026

**Paper:** Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification
**Conference:** IEEE World AI IoT Congress 2026, 20–22 May 2026
**Slot assumption:** 15-minute parallel-session talk
**Format:** ~7 min slides + ~5 min live demo + ~3 min Q&A
**Presenter:** An Nguyen
**Co-authors:** Madhu Babu Cherukuri, Vatsalya Rohitbhai Dabhi, Sarita Singh, Hongpeng Fu
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
| 3 | Sensing-to-Decision | 1:00 |
| 4 | The Prototype | 0:30 |
| 5 | Live Demo | 5:00 |
| 6 | What the Prototype Proves | 1:00 |
| 7 | Accessible by Design | 1:00 |
| 8 | Limitations & Future Work | 0:50 |
| 9 | Conclusion | 0:30 |
| 10 | Questions? | 3:00 |

## Asset checklist

Images already in the repo at `images/`:

| Asset | Used on |
|---|---|
| `prototype_photo.jpg` | Slide 1 (corner), Slide 4 (full bleed), Slide 10 (background) |
| `edge_to_cloud_architecture.png` | Optional Slide 3 alternate visual |
| `pd_glove_circuit.png` | Optional Backup B3 visual |
| `pd_glove_dashboard_example.png` | Optional Backup B1 visual |
| `flex_bench_scatter.png` | Optional Backup B1 sub-panel — flex thumb 0°/30°/60° distribution |

Build-side assets to create:

- [ ] Slide 2 — two-timeline graphic (sparse clinic dots vs dense symptom waveform)
- [ ] Slide 3 — three-icon row (glove / chip / encrypted envelope) with dashed red boundary line
- [ ] Slide 6 — three-statement layout + small `flex_bench_scatter.png` inset on the right
- [ ] Slide 7 — cost progression graphic (Pi 5 today → Pi Zero 2W / ESP32 future)
- [ ] Slide 8 — two-column layout (Limitations | Future Work), no graphics
- [ ] Slide 9 — conclusion layout, three stacked statements, no graphics
- [ ] Slide 10 — QR code linking to the paper (generate once IEEE Xplore listing is live)

---

## Slide 1 — Title (0:15)

**Title (on slide):**
> Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification

**Subtitle (on slide):**
> An Nguyen · Madhu Babu Cherukuri · Vatsalya Rohitbhai Dabhi · Sarita Singh · Hongpeng Fu
> Northeastern University — Khoury College of Computer Sciences
> IEEE World AI IoT Congress 2026

**Visual:** Title in large type, centered or left-aligned. Author block below in smaller type. Hero photo of the assembled glove (`images/prototype_photo.jpg`) bottom-right or as a soft watermark. AIIoT 2026 / IEEE branding bottom-left.

**Script:**

> "Good afternoon. I'm An Nguyen, from Northeastern University. This is joint work with Madhu Babu Cherukuri, Vatsalya Rohitbhai Dabhi, Sarita Singh, and Hongpeng Fu.
>
> What I'm going to show you today isn't really a sensor paper. It's an architectural argument — that continuous, privacy-preserving monitoring of Parkinson's disease, the fastest-growing neurological disorder in the world, can be done entirely on low-cost commodity edge hardware. And we built a working prototype to back it up."

**Notes:** Open with the framing shift. You're not pitching hardware; you're pitching a design philosophy — privacy-centric, low-cost, edge-first. Pause briefly before "And we built a working prototype to back it up" — that's the line that turns the thesis from claim into evidence.

---

## Slide 2 — The Monitoring Gap (1:00)

**Title (on slide):**
> The Monitoring Gap

**Subtitle (on slide):**
> Parkinson's symptoms shift hour by hour. Clinical assessments don't.

**On-slide text (three impact lines stacked beneath the timeline visual):**

> **Symptoms shift hour by hour** — medication windows, fatigue, stress
> **Direct costs rise as PD progresses** — more clinic visits is not a scalable answer
> **Steepest growth in regions with the fewest specialists**

**Headline stat block (bottom of slide, large bold type):**

> **25.2 million PD cases projected by 2050**
> *The fastest-growing neurological disorder by prevalence, disability, and mortality.*

**Visual (top half of slide):** Two stacked timelines spanning a 6-month window, drawn with intent:
- Top timeline (label *"Clinic visits"*): a thin neutral-blue line with 3 dots, evenly spaced.
- Bottom timeline (label *"Actual symptoms"*): a dense jagged waveform in amber/red, with two of the troughs annotated *"medication wearing off."*
- Thin downward arrows from each clinic dot into the waveform, each labeled *"snapshot."* The arrows hit only 3 of the dozens of fluctuations — visually demonstrating the *snapshot effect* the paper names.

The three impact lines sit in the middle band; the 25.2 M stat block anchors the bottom.

**Script:**

> "Here's the gap. Patients with Parkinson's see a neurologist a few times a year. Their symptoms shift hour by hour — medication wears off, fatigue sets in, stress changes everything. So the most important clinical question — *am I in a good window or a bad one right now?* — is something the current system simply doesn't measure. The paper calls this the *snapshot effect* — every clinical assessment captures a single moment in a disease that's never standing still.
>
> And it's getting harder, not easier. Direct costs of Parkinson's care rise substantially as the disease progresses, and more frequent clinic visits is simply not a scalable answer to that. There isn't more clinic time, and the populations expected to see the steepest growth in PD are the ones with the fewest movement-disorder specialists to begin with.
>
> By 2050, we're looking at 25.2 million cases worldwide — Parkinson's is the fastest-growing neurological disorder on Earth. So whatever the answer to continuous monitoring is, it has to work outside the clinic, on hardware people can actually afford. That's the constraint this paper is built around."

**Notes:**
- Mission slide. Speak slowly. Don't rush past the cost beat — that's the line the audience will internalize as *"more visits won't fix this."*
- Pause briefly before "25.2 million" — that's the headline number, let it land.
- The closing line ("hardware people can actually afford") is the bridge into Slide 3 — deliver it with intention; it sets up the privacy + low-cost framework directly.

---

## Slide 3 — Sensing-to-Decision (1:00)

**Title (on slide):**
> Sensing-to-Decision

**Subtitle (on slide, bold strapline):**
> Privacy by architecture, not by promise.
> A four-layer edge framework: sense at home · decide on-device · share only the encrypted summary.

**On-slide text — three-icon row across the upper-middle band:**

| Icon | Label | One-line caption |
|---|---|---|
| 🧤 (glove) | **Sense at home** | Continuous capture on commodity hardware |
| 🔲 (chip) | **Decide on-device** | DSP + inference local · Privacy boundary |
| 🔐 (envelope) | **Share only what matters** | Encrypted clinical summary, not raw biometrics |

**On-slide text — boundary-check panel below the icons (two columns):**

> **Stays on-device by architecture**
> Raw accelerometer streams · Raw flex streams · DSP intermediate state · Severity classification
>
> **Crosses the wire — encrypted by architecture**
> Per-exercise clinical JSON · Session video (post-session compliance audit only)
>
> *Encryption profile per paper §IV-B: AES-256-GCM payload · MQTT over TLS 1.3 · Mutual cert auth. MQTT publisher is identified in §VIII as next-stage integration work.*

**Visual:** Three icons in a horizontal row, each with the label + caption above. A bold dashed red vertical line falls just to the right of the middle icon, labeled **"Privacy-by-Design boundary."** Strapline above the icon row in larger weight. Below the icons: a clean two-column boundary-check panel — left column with a small lock-and-Pi icon (stays inside), right column with a small encrypted-envelope icon (crosses the wire). The encryption-profile line sits in smaller italic at the bottom.

**Script:**

> "Our framework is called sensing-to-decision, and it has three architectural commitments.
>
> First, the measurement happens at home, continuously, on commodity hardware. The current prototype demonstrates this — DSP and severity classification run entirely on the Pi today.
>
> Second, the decision happens on the device itself. Raw accelerometer streams, raw flex streams — by architecture, none of it crosses the network. The interpretation, the clinical scoring, is local.
>
> Third, only the clinical summary leaves the device, and it crosses the wire encrypted. The framework specifies AES-256-GCM at the application layer, MQTT over TLS 1.3 with mutual certificate authentication at transport. That publisher is identified in the paper as the next integration stage.
>
> The key word here is *architecture*. Most systems that call themselves privacy-preserving are running cryptography on top of cloud surveillance. This framework doesn't transmit the raw data at all. Privacy isn't a setting we toggle — it's a property of where computation physically happens. If the raw data isn't there, it can't leak."

**Notes:**
- This is the slide that defines what the project *is*. Land it cleanly.
- The "by architecture, not by promise" line is the most quotable thing in the talk — pause before and after it.
- The "cryptography on top of cloud surveillance" line is the sharpener — it directly contrasts the framework against the typical "secure cloud" pitch the audience hears constantly.
- Be honest about the MQTT publisher being next-stage. Reviewers know; the audience deserves the same honesty. Frame it as scope clarity, not weakness.

---

## Slide 4 — The Prototype (0:30)

**Title (on slide):**
> The Prototype

**Subtitle (on slide):**
> Five-finger wearable · Raspberry Pi 5 edge gateway · Built on commodity hardware

**On-slide text — single spec strip across the bottom of the photo:**

> **5 IMU mounts** (4 operational; CH4 hardware fault under investigation) · **TCA9548A** I²C mux · **MCP3008** SPI ADC ready · **Flex sensor channels validated** · **All processing local on Pi 5**

**Visual:** Full-bleed photo of the assembled glove on the table next to the Pi 5 and the laptop running the demo dashboard (`images/prototype_photo.jpg`, or stage a fresh photo if the existing one doesn't show the full setup). Subtitle sits at the top in smaller type. The spec strip overlays the bottom edge of the photo in a translucent dark band — readable but doesn't fight the image.

**Script:**

> "I want to show you the prototype rather than describe it. Five IMU mounts, one per finger — four operational today, with the fifth-channel hardware fault still under investigation. Five SparkFun flex sensors are mounted on the same PLA rings; the thumb channel is bench-validated off-platform on an Arduino Nano 33 BLE Sense Lite, and the Pi 5 plus MCP3008 path described in the paper is the target host integration. All capture, filtering, and feature extraction runs on a single Raspberry Pi 5. Every component is off the commodity supply chain — no proprietary parts.
>
> So instead of walking through the architecture diagram, I'm going to step over to the demo here for the next few minutes — what you'll see is a real assessment, end-to-end, on the actual hardware. Then I'll come back and tell you what we've validated and where this is going."

**Notes:**
- Brief transition slide. Don't read the spec strip — the audience can.
- Walk to the demo setup as you finish speaking.
- The "no proprietary parts" line is intentional — it sets up the equity argument on Slide 7 ahead of time, so when you say "accessible by design," the audience already knows the parts are commodity.
- Flex scope on stage matches paper §V-D exactly: five sensors mounted on PLA rings, single thumb bench characterization, Pi 5 + MCP3008 host integration pending. Do **not** quote angles or Cohen's d in the live script — those numbers are in Backup B1 if asked. Naming the Arduino Nano early also seeds Slide 7's cost-reduction story without pre-empting it.
- Honesty on CH4 disarms the obvious "where's the fifth channel" question before someone asks it in Q&A.

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

**Subtitle (on slide):**
> From architecture to evidence — three things we've validated on real hardware.

**On-slide text — three statements stacked, each anchored by a paper-supported number and a "what it means" line:**

> **1. The signal is real — on both modalities.**
> **Tremor (IMU):** 30× to 895× rest-to-tremor separation across all four channels, every capture inside the 4–6 Hz Parkinsonian band.
> **Flex (thumb, bench):** Cohen's d = 2.15 between 0° and 60° on Arduino Nano off-platform (paper §V-D, Table II).
>
> **2. The hardware is reliable.**
> **0 I²C retries** across **9 validation runs**. **88.9–89.3 Hz** sustained sampling.
> *Stable enough to trust the data, against a 100 Hz design target.*
>
> **3. The pipeline runs entirely on-device.**
> **Raw biometric data never leaves the Pi.** By architecture, only encrypted clinical summaries cross the wire (publisher integration is next-stage).
> *Privacy commitment, demonstrable in the prototype today.*

**Visual:** Two-column layout. **Left two-thirds:** the three statements stacked, bold numeric callouts in accent color (suggested: blue `#3b82f6`). **Right one-third:** small inset of `images/flex_bench_scatter.png` (the 0°/30°/60° box-plus-strip plot) with a one-line caption *"Flex (thumb, bench): 0°/60° cleanly separated, d=2.15."* No tremor chart — the dashboard from the demo carries that visually.

**Script:**

> "Three things we've established with the working prototype.
>
> First, the signal is real on both sensing modalities. On the tremor side, across nine validation tests on two subjects, we measured tremor-to-rest band power separation between thirty times and eight hundred and ninety-five times — every single tremor capture landed in the four-to-six hertz Parkinsonian band. The separation is large enough that there's no overlap between the two states. On the flex side, we bench-characterized a single thumb sensor off-platform on an Arduino Nano — ten trials at each of three bench-jig angles. The chart on the right shows the result: flat versus bent is cleanly separated, Cohen's d of two-point-one-five between zero and sixty degrees. That's a flat-versus-bent claim at the channel level — graded angle reporting isn't supported on this rig yet, and the Pi 5 plus MCP3008 multi-finger integration is the next step.
>
> Second, the hardware is reliable. Across every one of those nine tests, sampling stayed stable in the 89-hertz range, and we recorded zero communication retries on the sensor bus. That stability matters — it means the data is trustworthy enough to feed into a model.
>
> And third, critically, the entire pipeline runs on the device itself. Raw biometric data never leaves the Pi. By architecture, only encrypted clinical summaries cross the wire — that publisher is the immediate next integration step. But the privacy commitment from Slide 3 is structural, and it's demonstrable in the prototype today."

**Notes:**
- This is the "we built it and it works" slide. Confidence, not modesty.
- The "30× to 895×" is the strongest number in the talk — speak it slowly.
- Flex scope on this slide matches paper §V-D exactly: thumb only, off-platform on Arduino Nano, **flat-vs-bent** discrimination only (d = 2.15 between 0° and 60°). Do **not** claim graded angle reporting — the 30°/60° envelopes overlap (d = 0.68), and §V-D explicitly does not claim it.
- If a reviewer pushes on "what about the other four flex channels," the honest framing is "five sensors are mounted on the glove; the Pi 5 + MCP3008 multi-finger host pipeline is the next integration step" (paper Fig. 5 caption, §VIII).
- If asked in Q&A for raw numbers per IMU channel or per subject, you have Backup B1; Backup B1 also carries the flex Table II values.
- Closing line ties back to Slide 3 — the privacy commitment isn't just a diagram, it's measurable in this prototype right now.

---

## Slide 7 — Accessible by Design (1:00)

**Title (on slide):**
> Accessible by Design

**Subtitle (on slide):**
> Continuous clinical monitoring at the price of a phone charger.

**On-slide text — cost progression, two stages:**

> **Today** — Built on commodity hardware (Raspberry Pi 5)
>
> **Near future** — `<$35` deployment target
> Pi Zero 2W (~$15) · ESP32 (~$5–10) · Arduino Nano 33 BLE Sense (~$30)

**On-slide text — three impact bullets below the progression:**

> **No proprietary hardware.** Off-the-shelf components, accessible supply chain.
> **No cloud dependency.** Processing stays local — no recurring cloud costs by architecture.
> **Built for resource-constrained settings.** Where chronic-disease burden is projected to grow fastest.

**Visual:** Simple horizontal arrow going left-to-right. Pi 5 icon on the left under "Today." Pi Zero 2W, ESP32, and Arduino icons on the right under "Near future." The `<$35` figure rendered large in your accent color. The strapline ("phone charger") sits in the subtitle slot at the top of the slide. The three impact bullets sit below the cost progression, each anchored by a bold lead phrase.

**Script:**

> "Here's why I think this is more than a research artifact.
>
> Just like privacy on Slide 3, accessibility here is a design principle — not a feature we layered on. The architecture doesn't depend on expensive proprietary hardware. It doesn't depend on recurring cloud costs. It doesn't depend on always-on broadband. Today's prototype runs on a Raspberry Pi 5. Because the pipeline operates on compact INT8-quantized DSP feature vectors rather than raw waveforms, it ports directly to a Pi Zero 2W at around fifteen dollars, an ESP32 in the five-to-ten-dollar range, or an Arduino Nano 33 BLE Sense at around thirty dollars — a single board that carries both an ADC and an IMU, covering both sensing modalities. The framework's deployment target is under thirty-five dollars per device — continuous, privacy-preserving clinical monitoring, at the price of a phone charger.
>
> And that's the part that I think matters most. The populations expected to see the biggest growth in chronic-disease burden over the next 25 years are not the populations with the most specialists, or the best broadband, or the budget for proprietary clinical devices. If the answer to continuous monitoring depends on any of those, it doesn't reach the people who need it most. This framework was designed so it can."

**Notes:**
- This is the impact slide. Speak slower here.
- "Accessible by Design" intentionally parallels "Privacy by architecture, not by promise" on Slide 3 — the talk argues for *two* design principles, privacy and accessibility, both as architectural properties rather than features. Lean into the parallel verbally; the structural pun is the deck's strongest rhetorical move.
- The "phone charger" line is the punchline — let it sit for a beat before continuing.
- The closing line ("the people who need it most") is the moral case of the entire talk. Don't rush past it.
- If asked about latency or model size: TFLite INT8 quantization reduces footprint by 70–85% and gets sub-5 ms inference on comparable ARM (cited in paper §II-D, ref [10]). On-device benchmark on the Pi 5 is forthcoming.

---

## Slide 8 — Limitations & Future Work (0:50)

**Title (on slide):**
> Limitations & Future Work

**Subtitle (on slide):**
> Honest scope — and what's next.

**On-slide text — two-column layout (left: limitations today; right: future work next):**

| **Limitations (today)** | **Future Work (next)** |
|---|---|
| Healthy volunteers; public-dataset pre-training (mPower / PhysioNet) | Train TFLite Transformer scoring model on the validated tremor dataset |
| TFLite scoring model + MQTT publisher: architecture defined, integration pending | Multi-finger flex on Pi 5 + MCP3008 (off-platform bench complete) |
| Multi-finger flex on Pi 5 pending (thumb bench-validated off-platform on Arduino Nano) | Diagnosed PD cohort + weighted-kappa agreement vs. neurologist scores |
| MediaPipe compliance validation: planned extension (app-timestamp gating today) | Port runtime to sub-$35 devices · longitudinal fine-tuning · uncertainty-aware scoring · fairness audit |

**Visual:** Two-column text layout. No graphics. Column headers in bold accent color; body in plain weight. Generous white space between rows so each item reads as a discrete beat. A thin vertical divider between the columns helps the eye separate "today" from "next."

**Script:**

> "Before I close, the honest scope.
>
> On the limitations side: today's signal validation is on healthy volunteers performing simulated tremor — clinical PD-cohort validation is the next study, not this paper. The TFLite scoring model and the MQTT publisher are architecturally specified but not yet integrated. The flex bench is single-thumb off-platform on the Arduino Nano; multi-finger flex on the Pi 5 with the MCP3008 is ahead of us. And MediaPipe-based compliance validation is a planned extension — today, gating is handled by app-controlled timestamps rather than real-time computer vision.
>
> On the future-work side: four directions guide what's next. Train the scoring model on the validation dataset we showed. Finish the Pi 5 multi-finger flex pipeline so bradykinesia metrics are live. Recruit a diagnosed PD cohort to run weighted-kappa agreement against neurologist scores. And port the runtime to sub-thirty-five-dollar devices — Pi Zero 2W and ESP32 — with longitudinal model fine-tuning, uncertainty-aware scoring, and fairness auditing as the longer arc.
>
> Every one of these is grounded in what the prototype already demonstrates. None of them require rebuilding the architecture."

**Notes:**
- Speak this slide briskly — it's information-dense but you don't want to dwell on caveats.
- Every item on this slide maps to a specific paper section: §V-B (healthy volunteers), §III-D (TFLite), §III-F (MQTT), §V-D (flex), §III-B-3 (MediaPipe), §VIII (four future-work directions). No new claims.
- Honesty here disarms Q&A — reviewers who came in with "what's pending?" questions get the answer pre-emptively.
- The closing line ("None of them require rebuilding the architecture") is the bridge to Slide 9's conclusion: the work that's pending is integration work, not redesign work. That's the message reviewers should leave with.
- Do **not** apologize. State the scope, state the path, move on.

---

## Slide 9 — Conclusion (0:30)

**Title (on slide):**
> Conclusion

**Subtitle (on slide):** None.

**On-slide text — three stacked statements, each broadening from prototype to pattern:**

> **A working prototype — and a generalizable framework.**
> *Dual-modality validation on real hardware today (Tremor: 9 tests · 2 subjects · 30–895× discrimination. Flex: thumb bench-validated, d = 2.15). The sense-locally · decide-on-device · share-only-encrypted-summary pattern isn't PD-specific.*
>
> **Privacy by architecture, not by promise.**
> *Raw biometric data physically cannot leak from a device that never transmits it.*
>
> **A path to continuous healthcare monitoring at global scale.**
> *Phone-guided sessions · edge inference · encrypted summary out. Commodity hardware, no cloud dependency, `<$35` deployment target — for any chronic condition, anywhere broadband isn't a given.*

**Visual:** Three short stacked statements with the bold lead line in larger type and the supporting line in smaller italic. Match the layout of Slide 6 visually so the audience recognizes the bookend. No graphics — let the words carry it. Optional: a small closing strapline at the bottom in italic: *"Parkinson's is the first instance. The framework is the contribution."*

**Script:**

> "To close, three things.
>
> One, we built a working prototype — both sensing modalities validated on real hardware today. But the larger point is that the architecture behind it isn't PD-specific. *Sense locally · decide on the device · share only the encrypted summary.* That pattern works for any chronic condition where continuous motor or physiological monitoring is clinically useful — stroke recovery, multiple sclerosis, post-surgical rehab. The glove is one instance; the framework generalizes.
>
> Two, the privacy story is structural, not promotional. Raw biometric data physically cannot leak from a device that doesn't transmit it. That's not a setting we toggle — it's a property of where computation physically happens.
>
> And three, this is a path to accessible, continuous healthcare monitoring at global scale. A phone-guided exercise app, an edge gateway running locally, an encrypted clinical summary on the wire — on commodity hardware that costs less than a phone charger. The populations expected to see the steepest growth in chronic-disease burden over the next 25 years are the same populations with the fewest specialists and the least reliable broadband. If continuous clinical monitoring is going to reach them, it has to look like this — not like cloud-tethered, proprietary, premium devices.
>
> Parkinson's is the first instance. The framework is the contribution.
>
> Thank you. I'd love to take questions."

**Notes:**
- Close clean. The "Parkinson's is the first instance. The framework is the contribution." line is your landing — pause before and after.
- This is the bookend to Slide 6 — same three-statement layout — but here each statement *broadens* from the prototype's specific evidence to the IoT pattern it instantiates. Audience leaves with the framework, not just the device.
- The chronic-condition examples (stroke, MS, rehab) are illustrative; do not over-claim that the current implementation supports them — only that the *architecture* generalizes. If asked which condition is next, honest answer is "PD is the focus today; other motor-symptom conditions are the natural next instances."

---

## Slide 10 — Questions? (3:00)

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
  2. "What about the parts you said are pending — flex sensors, the ML model?" → "Fair question. The five-finger flex prototype is mounted, and the thumb channel has bench data behind it — Cohen's d of 2.15 separating flat from bent on the Arduino Nano. What is still ahead is the Pi 5 plus MCP3008 multi-finger integration, and the scoring model. The tremor dataset we showed is the training input for that model." Don't apologize.
  3. "Why not just use an Apple Watch?" → Backup B3.

---

## Backup slides (have ready, don't show by default)

### Backup B1 — The actual numbers, if asked

**Title (on slide):** "Validation Numbers"

**On-slide text:** Table I from the paper (Person A and B, tremor vs rest, min/max/median band power), a slim flex-bench sub-panel (Table II: 0° mean 1036.08, 30° mean 961.89, 60° mean 924.91, N=10 per angle), and a strapline:

> **30× to 895× rest-to-tremor separation across all IMU channels and subjects · flex thumb: d = 2.15 between 0° and 60°.**

**Talking points:**
- Tremor: nine validation tests across two subjects, 72 per-finger feature vectors total. All tremor captures landed in the 4–6 Hz Parkinsonian band. Rest band power stayed below 70 across every channel and subject; tremor band power ranged from ~670 up to ~26,000.
- Flex: single thumb sensor, 10 trials × 3 angles (0/30/60°) off-platform on Arduino Nano 33 BLE Sense Lite at 12-bit ADC. Monotonic decrease in ADC mean with bend; 0°/60° cleanly separable (d = 2.15); 30°/60° envelopes overlap (d = 0.68) — i.e., flat-vs-bent works, fine-grained graded angle does not on this rig.
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
- **Slide masters:** Use one master slide for the eight content slides (2, 3, 4, 6, 7, 8, 9, 10) so headers and footers stay consistent. Slide 1 (title) and Slide 5 (demo) can have their own layouts.
- **Footer (every content slide):** small line bottom-left — "AIIoT 2026 · An Nguyen · Northeastern" — plus slide number bottom-right.
- **Avoid:** dense bullets, animations, transitions, screenshots of the paper. The slides must be readable from the back of the room.

## Pre-talk checklist

- [ ] Confirm talk length and AV format with session chair
- [ ] Demo laptop charged, glove + Pi powered, network ready, demo loaded *before* Slide 1
- [ ] Backup: bring slides on a USB stick in PDF format in case AV fails on your laptop
- [ ] Time the slides-only run (target ~6 min) and a full run with demo (target ~11 min)
- [ ] Practice Slide 3 (privacy by architecture) and Slide 7 (scale) until you can deliver them without notes — these are the two slides that carry the talk
- [ ] If the demo fails live, pivot to "what you'd see is…" and keep moving — do not debug on stage
- [ ] Generate the QR code for Slide 10 once the IEEE Xplore listing is live

## Tone reminders

- This is a story about access and privacy at global scale, illustrated by a working device. The device is the evidence; the mission is the message.
- Don't apologize for what's pending. Reviewers accepted the work knowing the scope. The audience will follow your lead — if you treat it as a strength, they will too.
- Speak slowly. Pause after the "phone charger" line on Slide 7 and the "by architecture, not by policy" line on Slide 3. Both are designed to land.
