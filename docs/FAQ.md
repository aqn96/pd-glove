# Frequently Asked Questions — PD Monitoring Glove

**Project:** Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification  
**Author:** An Nguyen — Northeastern University, Intelligent Automation (IoT) Research Group

---

## Clinical Background

### What is Parkinson's Disease?

Parkinson's Disease (PD) is a progressive neurodegenerative disorder caused by the loss of dopamine-producing neurons in the substantia nigra, a region of the brain that controls voluntary movement. As those neurons die, patients lose fine motor control and movement becomes increasingly impaired over time.

The four cardinal motor symptoms are **tremor** (involuntary shaking), **bradykinesia** (slowness of movement), **rigidity** (muscle stiffness), and **postural instability** (balance problems). PD currently affects around 10 million people worldwide and is the fastest-growing neurological disorder. There is no cure. The main treatment is dopamine replacement via L-dopa, which requires precise dose timing to stay within the therapeutic window — too little and the patient can barely move, too much and it triggers its own involuntary movements.

---

### What is bradykinesia?

Bradykinesia literally means "slow movement" in Greek. It is one of the defining features of Parkinson's Disease and is often the most functionally disabling symptom. Patients find it progressively harder to button shirts, type, write, or use utensils.

What distinguishes bradykinesia from just "being slow" is the **decremental amplitude pattern**: during a repetitive task like finger tapping, each tap becomes not only slower but also physically smaller than the last. The movement decays — both in speed and range — across the session. This specific pattern is what makes it a strong PD biomarker.

Measuring bradykinesia requires tracking **range of motion and movement amplitude over time**, which is why the system uses flex sensors in addition to the IMUs. IMUs capture oscillatory tremor well; flex sensors capture how far and how fast the finger actually bends and unbends.

---

### What is MDS-UPDRS?

MDS-UPDRS stands for the **Movement Disorder Society Unified Parkinson's Disease Rating Scale**. It is the clinical gold standard for evaluating PD severity and tracking disease progression. It covers everything from cognitive symptoms to daily living activities to the motor examination.

Part III of the scale — the motor examination — is the most relevant here. A trained clinician observes the patient performing standardized tasks (like the finger-tap test or resting hand posture) and scores each on a 0 to 4 scale:

- **0** — Normal
- **1** — Slight
- **2** — Mild
- **3** — Moderate
- **4** — Severe

This project targets an objective, sensor-derived approximation of those Part III scores for tremor and bradykinesia. Currently the system uses empirically validated band power thresholds; the planned next step is a trained Transformer model that maps directly to MDS-UPDRS output.

---

### Why does objective monitoring matter? Can't doctors just observe patients?

They do — but clinic visits happen every 3 to 6 months. PD symptoms fluctuate daily and are strongly affected by medication timing, sleep, stress, and activity. A 30-second clinical observation during a scheduled visit captures a single snapshot that may not reflect how the patient actually functions at home.

Wearable monitoring enables **longitudinal, continuous tracking** — data collected during daily life rather than during a performance in a clinic. This gives clinicians something concrete to work with between visits: whether a dose change is working, whether symptoms are worsening, or whether the patient is in a good window vs. an "off" period. That information directly supports better medication titration.

---

## Sensors and Hardware

### What is an IMU and what does it measure?

IMU stands for **Inertial Measurement Unit**. The specific chip used in this project is the **MPU6050**, packaged on a GY-521 breakout board. It combines two sensors in one:

- A **3-axis accelerometer** — measures linear acceleration (g-force) along the X, Y, and Z axes. For a tremoring finger, this captures the rapid back-and-forth oscillation.
- A **3-axis gyroscope** — measures angular rotation rate (degrees/second) around each axis. This adds rotational context to the motion.

That gives 6 total data streams per sensor. In this system we primarily analyze the accelerometer X-axis (`ax`) for tremor detection, since that aligns with the dominant oscillation direction. The sensors sample at approximately **89 Hz**, which is well above the Nyquist minimum needed to accurately represent 4–6 Hz tremor.

One IMU is mounted on each finger (thumb, index, middle, ring, pinky), giving per-digit resolution that a wrist sensor cannot provide.

---

### What are flex sensors and what do they measure?

Flex sensors are **resistive bend sensors** — thin strips of conductive film whose electrical resistance increases as they are physically bent. The project uses SparkFun 2.2" flex sensors, one per finger, running along the back of each finger joint.

Each sensor is wired into a **voltage divider circuit** with a 10kΩ pull-down resistor. As the finger bends, the sensor resistance increases, which drops the voltage at the measurement junction. That voltage change is what the ADC reads.

In practice: a fully straight finger produces a low resistance reading; a fully bent finger produces a high resistance reading. By tracking how that value changes over time during a finger-tapping task, the system can measure:
- How far each finger opens and closes (range of motion)
- How fast each tap cycle is (velocity)
- Whether amplitude decreases across the session (decremental pattern = bradykinesia signal)

> **Note:** Flex sensor hardware integration is the next phase of this project. The sensors and ADC are acquired but not yet wired into the active pipeline.

---

### Why does the system need a multiplexer (the TCA9548A)?

The I2C communication protocol identifies devices on the bus by a fixed address. The problem: all MPU6050 chips come from the factory with the **same hardwired address — 0x68**. There is no solder jumper or configuration pin to change it on the GY-521 breakout board.

If you connected all five IMUs directly to the Pi's I2C bus without a multiplexer, every read command would hit all five sensors simultaneously. The responses would collide on the wire and you'd get corrupt data or a locked bus.

The **TCA9548A** (sometimes also called TCA9548A) is an **8-channel I2C multiplexer**. It sits at its own address (0x70) and acts as a traffic director: you send it a command selecting which of its 8 downstream channels to activate, then send your normal I2C commands — which now only reach the single sensor on that channel. The software cycles through channels 0–3 (thumb, index, middle, ring) in sequence, reading one IMU at a time.

Without the multiplexer, five-finger IMU sensing would simply not be possible with this sensor model.

---

### Why does the system need an ADC (MCP3008)?

The Raspberry Pi's GPIO pins are **digital only** — they can detect a HIGH signal (~3.3V) or a LOW signal (~0V), but they cannot measure a voltage in between. Flex sensors produce a continuously varying analog voltage proportional to bend angle, which a digital pin cannot read.

The **MCP3008** is a 10-bit SPI Analog-to-Digital Converter. It reads the voltage at each of its 8 input channels and returns a digital value from **0 to 1023** (2¹⁰ levels). At 3.3V reference, each step represents about 3.2 mV of resolution — more than sufficient for flex sensor tracking.

It communicates with the Pi over the **SPI bus** (separate from the I2C bus used by the IMUs), so the two subsystems operate in parallel without interfering with each other.

---

### Why one sensor per finger instead of a single wrist sensor?

Commercial wearables like the Apple Watch or Empatica E4 use **wrist-mounted sensors** that measure aggregate hand motion. This works for gross activity detection, but for PD specifically it has key limitations:

1. **You cannot distinguish which fingers are affected.** PD often presents asymmetrically — one hand worse than the other, or specific fingers more impaired than others. Per-finger data reveals that asymmetry; wrist data averages it away.
2. **The bradykinesia task requires individual finger tracking.** The MDS-UPDRS finger-tap test scores each hand independently. Measuring which finger is tapping and how much it bends is impossible from a wrist accelerometer alone.
3. **Spatial resolution improves model accuracy.** Per-finger band power gives the Transformer model 4× as many features per hand, enabling it to learn finger-specific symptom patterns.

---

## Software and Signal Processing

### How was the Raspberry Pi set up?

The hardware platform is a **Raspberry Pi 5 (8GB RAM)**. Setup steps:

1. **OS:** Raspberry Pi OS 64-bit (Bookworm), flashed to a microSD card using Raspberry Pi Imager
2. **Interface enable:** I2C and SPI enabled via `sudo raspi-config` → Interface Options
3. **I2C verification:** `sudo i2cdetect -y 1` confirms TCA9548A at 0x70
4. **Python environment:** Python 3.11+, with a virtual environment (`python3 -m venv venv`)
5. **Dependencies installed:** `pip install -r requirements.txt` — covers numpy, scipy, smbus2 (I2C), spidev (SPI), paho-mqtt, flask
6. **Wiring:** 4.7kΩ pull-up resistors on the SDA/SCL lines ensure clean I2C signal levels; all components share 3.3V and GND rails

No external services or API keys are required to run the system.

---

### What does the signal processing pipeline do?

The pipeline runs entirely on the Pi in Python. Here is each stage:

**Stage 1 — Raw capture (`sensor_reader.py`):**  
Polls all four active IMU channels in round-robin at a target of 100 Hz. Measured throughput is ~89 Hz across four channels simultaneously. Outputs a CSV with columns: timestamp, channel, ax, ay, az, gx, gy, gz.

**Stage 2 — Butterworth bandpass filter (`dsp_pipeline.py`):**  
A 4th-order Butterworth filter passes frequencies between **3 and 15 Hz** and attenuates everything outside. This removes:
- DC offset and slow drift (< 3 Hz)
- Voluntary gross movements (typically < 2 Hz)
- High-frequency electrical noise (> 15 Hz)

What remains is the clinically relevant motion band.

**Stage 3 — FFT:**  
A real Fast Fourier Transform converts the filtered time-domain signal into the frequency domain. The output is a spectrum showing which frequencies are present and how much energy each carries.

**Stage 4 — Feature extraction:**  
Three features are pulled from the 4–6 Hz Parkinsonian tremor band:
- `dominant_freq_hz` — the frequency with the highest amplitude in the band
- `dominant_amp` — the magnitude at that frequency
- `band_power` — the sum of squared magnitudes across the entire 4–6 Hz window (the **primary severity metric**)

---

### What is band power and what do the numbers mean?

**Band power** = total spectral energy within the 4–6 Hz frequency window. Mathematically it is the sum of squared FFT magnitudes in that range — think of it as "how much of this signal's energy is in the Parkinsonian tremor zone."

Empirically validated thresholds from this project:

| Classification | Band Power Range | MDS-UPDRS Analog |
|---|---|---|
| Resting baseline | 13 – 70 | Score 0 (normal) |
| Light tremor | 1,000 – 2,500 | Score 1 |
| Mild tremor | 2,500 – 7,000 | Score 2 |
| Moderate tremor | 7,000 – 15,000 | Score 3 |
| Marked / severe | 15,000+ | Score 4 |

Across validation, the system achieved **30 to 895× separation** between resting baseline and active tremor — the metric robustly discriminates presence and severity.

---

### Why does all processing happen on the Pi instead of the cloud?

This is a deliberate design choice called **Privacy-by-Design**.

Raw IMU data is high-frequency biometric data. Transmitting it continuously to a cloud server creates privacy risks — it could be used to infer gait, identity, or other sensitive attributes far beyond PD monitoring. Given that the intended users are patients with a serious medical condition, this is a meaningful concern.

By running the Butterworth filter, FFT, and eventually the TFLite Transformer model entirely on the Pi, **raw data never leaves the device**. The only thing transmitted is the final clinical score — a single number — via an encrypted MQTT payload. This satisfies privacy-by-design principles and also has practical benefits: the system works without internet connectivity, has lower latency, and has no recurring cloud processing cost.

---

## Circuit and Schematics

### What is the complete circuit — what does each component do?

| Component | Role |
|---|---|
| Raspberry Pi 5 (8GB) | Edge compute host — runs all software locally |
| 5× MPU6050 GY-521 | IMU sensors — measure 6-axis acceleration + rotation at ~89 Hz |
| TCA9548A I2C Multiplexer | Resolves I2C address conflict — gates each of 5 IMUs onto its own channel |
| MCP3008 SPI ADC | Converts analog flex sensor voltage to 10-bit digital value (0–1023) |
| 5× SparkFun 2.2" Flex Sensor | Resistive bend sensors — measure finger joint angle (pending integration) |
| 2× 4.7kΩ Pull-up Resistors | Maintain I2C signal integrity on SDA and SCL lines |
| 5× 10kΩ Pull-down Resistors | Voltage dividers for flex sensor signal conditioning |
| 3D-printed PLA rings | Custom per-finger sensor mounts (elastic band + hot glue) |

**Communication buses:**
- **I2C** (GPIO 2 / GPIO 3): Pi ↔ TCA9548A (0x70) ↔ 5× MPU6050 (0x68 each)
- **SPI** (MOSI/MISO/SCLK/CE0): Pi ↔ MCP3008 ↔ 5 flex sensor voltage dividers

All logic runs at **3.3V**. Shared GND across all components is critical for stable I2C readings — floating grounds cause erratic sensor behavior.

---

### Why are there pull-up resistors on the I2C lines?

I2C is an **open-drain** protocol: devices pull the line LOW to signal a 0, but nothing actively drives it HIGH. Pull-up resistors (connected between the data line and VCC) passively pull the line back HIGH when no device is asserting it. Without them, the line would float at an undefined voltage and communication would be unreliable. The standard value for 3.3V I2C at moderate speeds is **4.7kΩ**.

---

### Why are there 10kΩ resistors on the flex sensors?

Each flex sensor is wired as half of a **voltage divider**: 3.3V → flex sensor (variable resistance) → measurement junction → 10kΩ fixed resistor → GND. The voltage at the junction is:

`V_out = 3.3V × (10kΩ / (R_flex + 10kΩ))`

As the finger bends, `R_flex` increases, so `V_out` decreases. The MCP3008 reads `V_out` and maps it to a 0–1023 integer. The 10kΩ value was chosen to place the operating range of the flex sensor in the middle of the ADC's input range, maximizing resolution.

---

## Project Scope

### Is this a diagnostic device?

No. This prototype is a **research-grade monitoring and decision-support tool**, not a medical diagnostic device. It does not diagnose Parkinson's Disease and cannot replace a neurologist's clinical evaluation.

Its intended role is longitudinal symptom tracking: giving clinicians objective, continuous data to complement their periodic assessments — not replacing those assessments. FDA clearance as a medical device would require a formal clinical trial and regulatory submission, which is outside the current scope of this project.

---

### What are the current limitations?

- **Dataset size:** 9 tests across 2 healthy subjects performing simulated tremor. A validated dataset requires diagnosed PD patients across the full clinical severity spectrum.
- **Flex sensors not yet integrated:** Bradykinesia measurement is designed and wired in the schematic but not yet active.
- **Threshold-based scoring:** Current severity thresholds are empirically derived from this small dataset. The planned Transformer model will generalize better across subjects.
- **Channel 4 (pinky) hardware fault:** Suspected wiring crossover preventing stable operation on the fifth finger.
- **Sampling rate:** Measured 89 Hz vs. 100 Hz design target — 4-channel round-robin polling introduces minor overhead.
- **No longitudinal data yet:** The system is designed for longitudinal monitoring but has only run point-in-time assessments so far.
