# Demo Day Script — PD Monitoring Glove

**Target time:** ~5 minutes  
**Audience:** Mixed — CS/ECE students, faculty, non-technical visitors  
**Setup:** Glove on your hand or on the table, browser open to `http://iotpi5.local:5000`

---

## Opening — The Problem (45 sec)

> "Imagine you have Parkinson's disease. Your medication window — the time when L-dopa actually works — is only about two to three hours. Miss that window and you can barely move. Take too much and you get uncontrollable shaking. Your doctor sees you every three to six months.
>
> How are they supposed to get your dose right?"

That's the gap this project addresses. Today's PD monitoring is **subjective, infrequent, and clinic-only**. A doctor watches you tap your fingers for 30 seconds and scores it 0 to 4. That's it.

What we built is a wearable glove that can measure PD motor symptoms **objectively, continuously, and at home** — without sending any raw health data to the cloud.

The two symptoms we target are **tremor** — that involuntary 4 to 6 Hz shaking you associate with PD — and **bradykinesia** — the progressive slowing and shrinking of voluntary movements like finger tapping. Both are core to the standard clinical rating scale doctors use.

---

## Hardware Walkthrough (60 sec)

> *(Hold up the glove or point to it on the table)*

"So here's the prototype."

Each finger has its own **MPU6050 IMU** — that small blue board. IMU stands for Inertial Measurement Unit. It's a 6-axis chip: three axes of accelerometer, three axes of gyroscope. It measures how fast and in what direction each finger is moving, at about 89 times per second.

Each finger also has a **flex sensor** running along the back — a thin strip whose electrical resistance changes as the finger bends. That's how we measure bradykinesia: tracking how far and how fast each finger opens and closes. *(All five sensors are mounted on the glove, and we've bench-validated the thumb channel off-platform on an Arduino Nano — flat-vs-bent cleanly separable. Pi 5 + MCP3008 multi-finger integration is the next hardware step.)*

All of that connects to a **Raspberry Pi 5** — this is the brain. Everything runs locally on this board. Signal processing, ML inference, all of it. No raw data ever leaves.

One thing worth calling out: all five IMUs share the same I2C address from the factory — you can't change it. So we added a **TCA9548A multiplexer** here on the breadboard. It's like a traffic director — it gives each sensor its own private channel so the Pi can talk to them one at a time without collisions.

The flex sensors produce an analog voltage, and since the Pi is digital-only, we use an **MCP3008 ADC** to convert that to a number the software can read.

The sensors themselves are mounted in these **custom 3D-printed PLA rings** — one per finger, with elastic bands underneath for fit and hot glue on the side bars to lock the sensor in place.

---

## Live Demo (90 sec)

> *(Open the browser to `http://iotpi5.local:5000`)*

"Let me show you what an actual assessment looks like."

I'll enter a subject ID and a test label here — *(type it in)* — and hit Begin.

The app first does a **hardware probe** — pings all four IMUs to make sure they're responding. You can see it checking each channel.

Now it's asking for the **resting baseline**. The subject puts their hand flat on the table and holds completely still for 10 seconds. This gives us the noise floor — what the signal looks like with no tremor. *(Wait through the countdown and capture.)*

Now it's asking for the **tremor assessment**. *(Shake your hand gently.)* The subject holds their hand in the air or shakes it while the system samples.

Under the hood, here's what's running on the Pi during those 10 seconds:

1. Raw accelerometer data comes in at ~89 Hz
2. A **Butterworth bandpass filter** strips out everything below 3 Hz (body motion, gravity) and above 15 Hz (noise)
3. An **FFT** converts the cleaned signal to the frequency domain
4. We pull out the **dominant frequency** and **band power** — total spectral energy — in the 4 to 6 Hz Parkinsonian tremor window

*(Results page loads.)*

"And here's the output."

That **band power** number is the key metric. At rest, a healthy hand reads somewhere between 13 and 70. Light tremor lands around 1,000 to 2,500. Moderate is 7,000 to 15,000. Our worst-case exaggerated test hit 26,000. The app classifies it and shows you how it compares to everyone else in the dataset.

---

## Results (30 sec)

Across our validation dataset — 9 tests, 2 subjects — we saw **30 to 895 times** more signal energy during tremor compared to rest. The system has no trouble discriminating.

Every single tremor capture landed in the 4 to 6 Hz clinical range. Zero hardware failures across all tests. Stable at 89 Hz on four channels simultaneously.

These are early numbers — two subjects is not a clinical trial — but the signal quality is strong enough to move to model training.

---

## What's Next (30 sec)

Three things on the roadmap:

1. **Flex sensor integration on the Pi 5 host** — the five SEN-10264 sensors are mounted on the glove and the thumb is bench-validated on an Arduino Nano (Cohen's d = 2.15, flat vs. bent); next step is wiring the MCP3008 SPI path on the Pi so the live bradykinesia pipeline can measure finger tapping speed and amplitude decay, not just tremor
2. **Transformer model training** — moving from these manually-tuned severity thresholds to a learned model, trained on this validation dataset, that outputs an MDS-UPDRS score directly
3. **Larger cohort** — validating against more subjects, eventually including diagnosed PD patients

The longer-term vision is daily at-home monitoring that feeds longitudinal data back to a clinician dashboard — so a neurologist can titrate medication between visits instead of flying blind.

---

## Close (15 sec)

> "The core idea is simple: move the measurement out of the clinic, keep the data on the device, and give clinicians something objective to work with. Happy to go deeper on the hardware, the signal processing, or the clinical context — there's also a FAQ sheet here if you want to dig into any of the specifics."

---

*See `docs/FAQ.md` for detailed answers to common questions about hardware, software, and clinical context.*
