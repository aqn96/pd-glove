# PD Monitoring Glove

**Sensing-to-Decision: A Transformer-Based Edge Computing Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification**

Author: An Nguyen
Lab: Intelligent Automation (IoT) Research Group

## Overview

An IoT-enabled wearable glove system for continuous, objective monitoring of Parkinson's Disease motor symptoms. The system targets two primary biomarkers from the MDS-UPDRS Part III motor examination: **resting tremor** (4–6 Hz involuntary oscillation) and **bradykinesia** (progressive slowness and decremental amplitude during repetitive movement).

All sensor data is processed locally on a Raspberry Pi 5 through a DSP pipeline and Transformer-based ML model, with only processed clinical scores published via MQTT to the cloud. Raw biometric data never leaves the device (Privacy-by-Design).

## System Architecture

```
[Glove Sensors]                   [Patient Phone Video]
5× MPU6050 IMU                    Encrypted session recording
5× Flex Sensor (pending)          Post-session MediaPipe validation
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
| SparkFun Flex Sensor 2.2" (SEN-10264) | 5 | Resistive bend sensors for bradykinesia measurement | ⏳ Pending |
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

**SPI Subsystem (Bradykinesia Detection — pending flex sensors):**
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
- [ ] MCP3008 ADC on SPI bus
- [ ] Flex sensor voltage divider circuits

## Software Modules

```
sensor_reader.py          ← Multi-IMU polling via TCA9548A (100Hz target)
test_imus.py              ← Per-channel probe + WHO_AM_I compatibility checks
dsp_pipeline.py           ← Butterworth filter + FFT (4-6Hz tremor metrics)
run_tremor_validation.py  ← One-command probe + capture + DSP workflow
transformer_inference.py  ← TFLite INT8 model runner (next stage)
mqtt_publisher.py         ← JSON payload → MQTT broker (next stage)
main.py                   ← Orchestrates staged pipeline
```

## Current Prototype Status (Tremor Phase Complete)

### Hardware
- **Wearable form factor:** PLA rings + elastic bands with hot glue securing sensors to side-top bars (stable mounting achieved)
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

### Implementation Scope
- Current focus is tremor-first (IMU only). Flex/bradykinesia remains pending hardware integration.
- Phone video is reserved for post-session compliance validation; no real-time camera gating in the live pipeline.
- Stable wiring topology critical: shared 3.3V and shared GND rails across Pi, TCA9548A, and all IMUs.
- `scripts/test_imus.py` accepts compatible WHO_AM_I responses (`0x68`, `0x70`, `0x71`) for MPU6050 clones.

## Future Work

- Train Transformer/TFLite INT8 model on multi-subject validation dataset for MDS-UPDRS-aligned scoring.
- Integrate flex sensor + MCP3008 pathway for bradykinesia and rigidity metrics.
- Add MQTT clinical payload publishing and robust session state handling.
- Add structured app/session timestamp protocol to formalize exercise semantics.
- Add security layer (payload encryption, TLS/mTLS transport, and key lifecycle controls).
- Resolve CH4 wiring/hardware issue to enable 5-channel operation.
- Evaluate and optimize sustained sampling rate toward full 100 Hz multi-channel acquisition.

## Documentation

- `docs/testing-workflow.md` — repeatable hardware/DSP validation procedure
- `docs/validation-results.md` — latest recorded tremor-phase run outcomes
- `docs/blues-dpu-notes.md` — Blues platform, DPU framing, and PD-glove integration ideas
- `docs/mobile-web-data-contract.md` — cloud payload schema for MPU tremor and flex stiffness metrics
- `docs/activity5-datasets.md` — Activity 5 write-up: measurable attributes, predictions, external datasets, and custom dataset plan

## Quick Start

```bash
ssh aqnguyen96@iotpi5.local
cd pd-glove
source venv/bin/activate
pip install -r requirements.txt  # install dependencies

# Scan I2C bus (shows TCA9548A at 0x70)
sudo i2cdetect -y 1

# Test all 5 IMUs on multiplexer channels 0-4
python3 scripts/test_imus.py

# Current stable operation (4 IMUs): channels 0-3
python3 scripts/test_imus.py --channels 0,1,2,3
```

### Manual Capture + DSP Validation

If you need manual control instead of the automated workflow:

```bash
# Manual capture
python3 scripts/sensor_reader.py --channels 0,1,2,3 --duration 10 --output imu_capture_4ch.csv

# Manual analysis for each channel
for ch in 0 1 2 3; do
  python3 scripts/dsp_pipeline.py --input imu_capture_4ch.csv --channel $ch --axis ax
done
```

### One-Command Tremor Validation Workflow (Recommended)

**Run the complete validation workflow with automatic master CSV logging:**

```bash
python3 scripts/run_tremor_validation.py
```

The script will prompt for:
- **Person ID** (e.g., `person_1`, `person_A`, `person_C`)
- **Test name** (e.g., `test_one`, `test_two`)

Then automatically:
1. Probes hardware channels (`scripts/test_imus.py`)
2. Captures rest data (10s)
3. Captures tremor data (10s) — user performs tremor during this
4. Runs DSP analysis on both captures
5. **Appends results to `data/tremor_validation_master.csv`**

**Advanced usage:**

```bash
# Specify person/test via command line
python3 scripts/run_tremor_validation.py --person-id person_C --test-name test_one

# Add notes about the test
python3 scripts/run_tremor_validation.py --notes "Exaggerated tremor test"

# Custom channels or duration
python3 scripts/run_tremor_validation.py --channels 0,1,2,3 --duration 15
```

**Output:**
- `rest_4ch.csv` — temporary rest capture (overwritten each run)
- `tremor_4ch.csv` — temporary tremor capture (overwritten each run)
- `data/tremor_validation_master.csv` — **permanent log of all validation tests** ✅

### Rest vs Tremor Comparison

```bash
python3 scripts/sensor_reader.py --channels 0,1,2,3 --duration 10 --output rest_$(date +%Y%m%d_%H%M%S).csv
python3 scripts/sensor_reader.py --channels 0,1,2,3 --duration 10 --output tremor_$(date +%Y%m%d_%H%M%S).csv
ls -1 rest_*.csv tremor_*.csv
```

## Testing IMU Channels

The `scripts/test_imus.py` script sequentially selects each TCA9548A channel, reads WHO_AM_I, wakes the sensor, and reads accelerometer X-axis data.

```bash
python3 scripts/test_imus.py
python3 scripts/test_imus.py --scan-only
python3 scripts/test_imus.py --scan only
```

Expected output (healthy channel):
```
CH0: OK WHO_AM_I=0x70 (MPU6500-class clone) Accel X = 57748
```

If a channel shows `Remote I/O error` or `not found`, check branch wiring continuity and verify shared 3.3V/GND rails are common across all IMUs and the multiplexer.
