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
   100Hz Raw Data               Compliance flags (later stage)
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

## Wiring

**I2C Subsystem (Tremor Detection):**
Pi GPIO2 (SDA) / GPIO3 (SCL) → TCA9548A (0x70) → Channels 0–4 → 5× MPU6050 (0x68 each)

- Ch0: Thumb
- Ch1: Index
- Ch2: Middle
- Ch3: Ring
- Ch4: Pinky

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
- [x] 2 IMUs reading independently on channels 0 and 1 (Thumb, Index)
- [x] 4 IMUs reading stably on channels 0-3 (Thumb, Index, Middle, Ring) ✅
- [ ] Channel 4 (Pinky) stable independent read path (currently failing with `Errno 121`)
- [ ] MCP3008 ADC on SPI bus
- [ ] Flex sensor voltage divider circuits
- [ ] Full sensor array mounted on glove
- [x] Tremor software pipeline (`sensor_reader.py` + `dsp_pipeline.py`) validated end-to-end on Pi

## Software Modules

```
sensor_reader.py          ← 5x IMU polling at 100Hz via TCA9548A
dsp_pipeline.py           ← Butterworth filter + FFT (4-6Hz tremor metrics)
transformer_inference.py  ← TFLite INT8 model runner (next stage)
mqtt_publisher.py         ← JSON payload → MQTT broker (next stage)
main.py                   ← Orchestrates staged pipeline
```

## Current Prototype Notes (Tremor Phase)

- Current implementation scope is tremor-first (IMU only). Flex/bradykinesia remains pending hardware integration.
- Phone video is reserved for post-session compliance validation; no real-time camera gating in the live pipeline.
- Stable wiring topology is critical: shared 3.3V and shared GND rails across Pi, TCA9548A, and all IMUs.
- Current known hardware issue: one faulty IMU module plus suspected CH3/CH4 SDA/SCL crossover/bridge causing CH4 discovery failures.
- `test_imus.py` now accepts compatible WHO_AM_I responses (`0x68`, `0x70`, `0x71`) and supports both `--scan-only` and `--scan only`.
- Temporary operating mode: use channels `0,1,2,3` for capture/analysis until CH4 wiring and sensor replacement are completed.
- Current measured capture throughput is approximately 71 Hz under full 5-channel polling. This reflects current software/I2C throughput limits, not fundamental signal instability, and remains sufficient for 4-6 Hz tremor-band experiments.

## Future Work

- Integrate flex sensor + MCP3008 pathway for bradykinesia and rigidity metrics.
- Add structured app/session timestamp protocol to formalize exercise semantics.
- Add Transformer/TFLite inference module for MDS-UPDRS-aligned scoring.
- Add MQTT clinical payload publishing and robust session state handling.
- Add security layer (payload encryption, TLS/mTLS transport, and key lifecycle controls).
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
python3 test_imus.py

# Current stable operation (4 IMUs): channels 0-3
python3 test_imus.py --channels 0,1,2,3
```

### Capture + DSP Validation (Pi)

```bash
# Capture 10s multi-IMU session
python3 sensor_reader.py --duration 10 --output imu_capture.csv
# Temporary 4-channel capture
python3 sensor_reader.py --duration 10 --output imu_capture_4ch.csv

# Run tremor-band analysis for each channel
for ch in 0 1 2 3 4; do
  python3 dsp_pipeline.py --input imu_capture.csv --channel $ch --axis ax
done

# Temporary 4-channel analysis
for ch in 0 1 2 3; do
  python3 dsp_pipeline.py --input imu_capture_4ch.csv --channel $ch --axis ax
done
```

### Rest vs Tremor Comparison

```bash
python3 sensor_reader.py --duration 10 --output rest_$(date +%Y%m%d_%H%M%S).csv
python3 sensor_reader.py --duration 10 --output tremor_$(date +%Y%m%d_%H%M%S).csv
ls -1 rest_*.csv tremor_*.csv
```

## Testing IMU Channels

The `test_imus.py` script sequentially selects each TCA9548A channel, reads WHO_AM_I, wakes the sensor, and reads accelerometer X-axis data.

```bash
python3 test_imus.py
python3 test_imus.py --scan-only
python3 test_imus.py --scan only
```

Expected output (healthy channel):
```
CH0: OK WHO_AM_I=0x70 (MPU6500-class clone) Accel X = 57748
```

If a channel shows `Remote I/O error` or `not found`, check branch wiring continuity and verify shared 3.3V/GND rails are common across all IMUs and the multiplexer.
