# PD Monitoring Glove

**Sensing-to-Decision: A Low-Cost, Privacy-Centric Edge Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification**

Authors: An Nguyen, Madhu Babu Cherukuri, Vatsalya Rohitbhai Dabhi, Sarita Singh, Hongpeng Fu
Lab: Intelligent Automation (IoT) Research Group

## Overview

An IoT-enabled wearable glove system for continuous, objective monitoring of Parkinson's Disease motor symptoms. The system targets two primary biomarkers from the MDS-UPDRS Part III motor examination: **resting tremor** (4–6 Hz involuntary oscillation) and **bradykinesia** (progressive slowness and decremental amplitude during repetitive movement).

All sensor data is processed locally on a Raspberry Pi 5 through a DSP pipeline and Transformer-based ML model, with only processed clinical scores published via MQTT to the cloud. Raw biometric data never leaves the device (Privacy-by-Design).

## Intended Use and Clinical Scope

- This prototype is intended for **research-grade monitoring and decision support**, not standalone diagnosis.
- MDS-UPDRS-aligned tremor tasks are used for structured data capture, but final clinical interpretation should remain clinician-supervised.
- For the standardized 3-task assessment protocol and separate therapeutic hand-exercise guidance, see `docs/assessment-and-therapy-protocol.md`.

## Team Cloud Handoff (CSV -> AWS)

When sharing data with backend teammates, credentials and config are not enough on their own:

- **Required:** message schema (IoT payload fields/types/units) and storage schema (DynamoDB key/attribute mapping, optional S3 layout).
- **Certificates/keys:** enable secure connection only; they do not define payload structure.
- **Security:** never commit private keys/cert bundles to this repository.

## System Architecture

```
[Glove Sensors]                   [Patient Phone Video]
5× MPU6050 IMU                    Encrypted session recording
5× Flex Sensor (thumb bench validated)  Post-session MediaPipe validation
        ↓                                  ↓
    ~89Hz measured (4ch), 100Hz target   Compliance flags (later stage)
        ↓
┌──────────────────────────────────────────┐
│   DSP: Butterworth Band-Pass (3-15 Hz)  │
│   + Fast Fourier Transform (FFT)        │
└──────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│   ML Inference (TFLite INT8)            │
│   Transformer Encoder → MDS-UPDRS 0-4   │
└──────────────────────────────────────────┘
        ↓
   MQTT JSON Payload → Cloud Web App
```

## Hardware

| Component | Qty | Purpose | Status |
|---|---|---|---|
| Raspberry Pi 5 (8GB) | 1 | Edge computing gateway | ✅ Acquired |
| MPU6050 IMU (GY-521) | 5 | 6-axis accel/gyro for tremor detection (one per finger) | ✅ Acquired & Soldered |
| TCA9548A I2C Multiplexer | 1 | Routes I2C bus for 5 IMUs sharing address 0x68 | ✅ Acquired & Soldered |
| SparkFun Flex Sensor 2.2" (SEN-10264) | 5 | Resistive bend sensors for bradykinesia measurement | 🧪 Bench validated (thumb only, off-platform on Arduino Nano — see `docs/flex-bench-characterization.md`); Pi 5 + MCP3008 integration pending |
| MCP3008 ADC | 1 | 10-bit SPI ADC for flex sensor voltage dividers | ✅ Acquired |
| 4.7kΩ Pull-up Resistors | 2 | I2C SDA/SCL pull-ups | ✅ Acquired |
| 10kΩ Resistors | 5 | Flex sensor voltage divider pull-downs | ✅ Acquired |

## Wiring & Sensor Placement

**I2C Subsystem (Tremor Detection):**
Pi GPIO2 (SDA) / GPIO3 (SCL) → TCA9548A (0x70) → Channels 0–4 → 5× MPU6050 (0x68 each)

**Per-Finger Channel Mapping:**
- Ch0: Thumb
- Ch1: Index
- Ch2: Middle
- Ch3: Ring
- Ch4: Pinky (hardware issue, under investigation)

**Design Rationale:** Per-finger IMU placement enables spatial isolation of the thumb-index interaction characteristic of Parkinsonian pill-rolling tremor, providing superior resolution over single wrist-worn sensors for fine-grained motor pattern recognition.

**SPI Subsystem (Bradykinesia Detection — Pi 5 + MCP3008 integration pending; thumb-only bench characterization complete off-platform on Arduino Nano 33 BLE Sense Lite, see `docs/flex-bench-characterization.md`):**
5× Flex Sensors → 10kΩ voltage dividers → MCP3008 ADC (CH0–CH4) → Pi SPI bus (spidev0.0)

**Phone Video Subsystem (Post-Session Validation):**
Patient phone records encrypted session video for retrospective MediaPipe compliance checks. No real-time CV gating in the live tremor pipeline.

## Pi Setup

- **OS:** Raspberry Pi OS 64-bit (Bookworm)
- **Python:** 3.11+
- **I2C/SPI:** Enabled via raspi-config
- **Virtual Environment:** `source venv/bin/activate`

### Installed Packages

| Package | Purpose |
|---|---|
| smbus2 | I2C communication (IMUs) |
| spidev | SPI communication (MCP3008 ADC) |
| scipy | Butterworth filter + FFT |
| numpy | Sensor data processing |
| paho-mqtt | JSON payload publishing |

## Validated

- [x] TCA9548A detected at 0x70 via `i2cdetect`
- [x] MPU6050 detected at 0x68 through multiplexer
- [x] Accelerometer data read successfully via Python (smbus2)
- [x] 4 IMUs reading stably on channels 0-3 (Thumb, Index, Middle, Ring)
- [x] **Wearable mounting complete: PLA rings + elastic bands with hot glue on side-top bars** ✅
- [x] **Multi-subject validation: 9 tests across 2 subjects (Person A: 5, Person B: 4)** ✅
- [x] **Production-grade tremor discrimination: 30-895× rest-to-tremor separation** ✅
- [x] Tremor software pipeline (`scripts/sensor_reader.py` + `scripts/dsp_pipeline.py`) validated end-to-end on Pi
- [ ] Channel 4 (Pinky) stable independent read path (hardware issue + wiring crossover)
- [ ] MCP3008 ADC on SPI bus (Pi 5 host integration pending)
- [ ] Flex sensor voltage divider circuits on Pi 5 host (off-platform Arduino bench characterization complete; see `docs/flex-bench-characterization.md`)

## Software Modules

```
app.py                    ← Demo web app: guided UI served on local network (port 5000)
templates/index.html      ← Web UI for app.py

scripts/
  sensor_reader.py        ← Multi-IMU polling via TCA9548A (100Hz target)
  test_imus.py            ← Per-channel probe + WHO_AM_I compatibility checks
  dsp_pipeline.py         ← Butterworth filter + FFT (4-6Hz tremor metrics)
  run_tremor_validation.py← Terminal fallback: one-command probe + capture + DSP workflow

(planned)
  transformer_inference.py← TFLite INT8 model runner (next stage)
  mqtt_publisher.py       ← JSON payload → MQTT broker (next stage)
  main.py                 ← Orchestrates staged pipeline
```

## Current Prototype Status (Tremor Phase Complete)

### Hardware
- **Wearable form factor:** Custom 3D-printed PLA rings (one per finger) with:
  - Bottom: Two slots for elastic band threading (adjustable tension)
  - Top: Two side bars matching sensor width for hot glue stabilization
  - Top cavity designed to fit MPU6050 sensor precisely
  - Result: Stable mounting with minimal motion artifacts
- **Operational channels:** 4 IMUs on channels 0-3 (Thumb, Index, Middle, Ring)
- **Channel 4 issue:** Hardware fault + suspected SDA/SCL crossover preventing Pinky sensor operation
- **Sampling rate:** 88.9-89.3 Hz sustained (4-channel), vs. 100 Hz design target
- **I2C stability:** Zero retries across multi-subject validation

### Validation Status
- ✅ **Multi-subject dataset collected:** 9 tests across 2 subjects (72 per-finger DSP feature vectors)
- ✅ **Tremor discrimination validated:** 30-895× power increase from rest to tremor
- ✅ **Clinical severity range:** Light (1.4K) → Moderate (2-7K) → High (7-15K) → Severe (26K)
- ✅ **Frequency accuracy:** All tremor captures in 4-6 Hz Parkinsonian range
- ✅ **Environmental controls documented:** Contamination effects identified and logged
- ✅ **Dataset ready for Transformer training:** `data/tremor_validation_master.csv`
- 🧪 **Off-platform flex bench characterization (thumb):** 10 trials × 0°/30°/60° on Arduino Nano 33 BLE Sense Lite — flat-vs-bent separable (Cohen's d = 2.15 between 0° and 60°); `data/flex_bench_thumb_2026-05-07.csv`

### Implementation Scope
- Current focus is tremor-first on the Pi 5. Flex/bradykinesia bench characterization is complete on a thumb-mounted SparkFun SEN-10264 sampled by an Arduino Nano 33 BLE Sense Lite (see `docs/flex-bench-characterization.md`); Pi 5 + MCP3008 multi-finger integration remains pending.
- Phone video is reserved for post-session compliance validation; no real-time camera gating in the live pipeline.
- Stable wiring topology critical: shared 3.3V and shared GND rails across Pi, TCA9548A, and all IMUs.
- `scripts/test_imus.py` accepts compatible WHO_AM_I responses (`0x68`, `0x70`, `0x71`) for MPU6050 clones.

## Future Work

- Train Transformer/TFLite INT8 model on multi-subject validation dataset for MDS-UPDRS-aligned scoring.
- Integrate flex sensor + MCP3008 pathway on the Pi 5 host for bradykinesia and rigidity metrics (off-platform Arduino bench characterization already documented in `docs/flex-bench-characterization.md`).
- Add MQTT clinical payload publishing and robust session state handling.
- Add structured app/session timestamp protocol to formalize exercise semantics.
- Add security layer (payload encryption, TLS/mTLS transport, and key lifecycle controls).
- Resolve CH4 wiring/hardware issue to enable 5-channel operation.
- Evaluate and optimize sustained sampling rate toward full 100 Hz multi-channel acquisition.

## Documentation

**Demo day:**
- `docs/DEMO_SCRIPT.md` — ~5-minute spoken walkthrough for presenting at the booth
- `docs/FAQ.md` — answers to common questions: what are IMUs, what is bradykinesia, how was the Pi set up, what does the circuit do, and more

**Setup and testing:**
- `docs/QUICKSTART.md` — first-run setup and bring-up
- `docs/testing-workflow.md` — standard validation flow used in this project

**Reference:**
- `docs/validation-results.md` — latest recorded tremor-phase run outcomes (Pi 5 + IMU integrated path)
- `docs/flex-bench-characterization.md` — off-platform thumb flex sensor bench protocol and results (Arduino Nano 33 BLE Sense Lite)
- `docs/camera-ready-edits.md` — AIIoT 2026 camera-ready paper edit checklist
- `docs/assessment-and-therapy-protocol.md` — 3-task assessment protocol + separate therapeutic routine
- `docs/mobile-web-data-contract.md` — cloud payload schema for MPU tremor and flex stiffness metrics
- `docs/blues-dpu-notes.md` — Blues platform, DPU framing, and PD-glove integration ideas
- `docs/activity5-datasets.md` — measurable attributes, predictions, external datasets, and custom dataset plan
- `docs/dataset-summary-2026-03-25.md` — baseline dataset observations
- `docs/gait-cv-pipeline.md` — gait capture and CV pipeline notes

## Repository Layout

```text
pd-glove/
├── app.py                           # Demo web app (Flask server — run this for demos)
├── templates/
│   └── index.html                   # Web UI served by app.py
├── scripts/
│   ├── run_tremor_validation.py     # Terminal fallback: full rest+tremor workflow
│   ├── sensor_reader.py             # Multi-IMU polling via TCA9548A
│   ├── test_imus.py                 # Per-channel hardware probe
│   ├── dsp_pipeline.py              # Butterworth filter + FFT tremor metrics
│   └── flex_bench/
│       └── plot_bench.py            # Regenerate flex bench Fig. 5 right panel
├── data/
│   ├── tremor_validation_master.csv      # Append-only log of all assessments
│   └── flex_bench_thumb_2026-05-07.csv   # Off-platform thumb flex bench characterization (10 trials × 4 angles)
├── docs/                            # Project docs (setup, testing, specs, notes)
├── images/                          # Architecture diagrams, circuit photos
├── requirements.txt                 # Python dependencies (includes Flask)
└── README.md
```

### How to Navigate This Repo

- **Running a demo:** see [Running the Demo](#running-the-demo) above.
- **Hardware bring-up / first time setup:** `docs/QUICKSTART.md`
- **Standard testing workflow:** `docs/testing-workflow.md`
- **Current results and dataset:** `docs/validation-results.md`
- **Cloud payload schema:** `docs/mobile-web-data-contract.md`

## Running the Demo

There are two ways to run an assessment. Use the **web app** for demos — it gives a guided step-by-step UI in the browser. Fall back to the **terminal script** if Flask has issues.

### Option A — Web App (primary)

`app.py` runs a local web server on the Pi. Open it from any browser on the same network (your laptop, tablet, etc.) — no installation needed on the client side.

```bash
ssh aqnguyen96@iotpi5.local
cd pd-glove
source venv/bin/activate
pip install -r requirements.txt   # first time only — adds Flask
python3 app.py
```

Then open **http://iotpi5.local:5000** in your browser (or use the Pi's IP address if mDNS isn't working).

**What it does:**
1. Enter a Subject ID and Test Label, click **Begin Assessment**
2. Hardware probe runs automatically
3. **5-second countdown** with prompt to hold hand still → 10s rest recording
4. **3-second countdown** with prompt to shake hand → 10s tremor recording
5. DSP analysis runs, result is saved to `data/tremor_validation_master.csv`
6. Results page shows rest power, tremor power, severity classification, and a bar chart comparing the subject against the population average

No need to restart between subjects — click **+ New Assessment** after each one. Use the **Records** tab to delete any subject's data.

> **Note — local hosting:** The server runs only on the Pi, on your local network. Nothing is sent to the internet. Anyone on the same WiFi can reach it at port 5000 while `app.py` is running.

---

### Option B — Terminal Script (fallback)

If the web app isn't working, use the original terminal workflow directly:

```bash
ssh aqnguyen96@iotpi5.local
cd pd-glove
source venv/bin/activate
python3 scripts/run_tremor_validation.py
```

The script will prompt for a Person ID and Test Name, then walk through the same hardware probe → rest capture → tremor capture → DSP → CSV append flow in the terminal.

**Cleanup after a demo:**
```bash
# Remove a demo subject by person ID
python3 scripts/run_tremor_validation.py --delete-person-id person_A

# More targeted: person ID + test name
python3 scripts/run_tremor_validation.py --delete-person-id person_A --delete-test-name test_one
```

---

## Quick Start (Hardware Bring-Up)

```bash
ssh aqnguyen96@iotpi5.local
cd pd-glove
source venv/bin/activate
pip install -r requirements.txt

# Scan I2C bus (shows TCA9548A at 0x70)
sudo i2cdetect -y 1

# Test all IMUs (stable on channels 0-3)
python3 scripts/test_imus.py --channels 0,1,2,3
```

## Testing IMU Channels

```bash
python3 scripts/test_imus.py
python3 scripts/test_imus.py --scan-only
```

Expected output (healthy channel):
```
CH0: OK WHO_AM_I=0x70 (MPU6500-class clone) Accel X = 57748
```

If a channel shows `Remote I/O error` or `not found`, check branch wiring continuity and verify shared 3.3V/GND rails are common across all IMUs and the multiplexer.
