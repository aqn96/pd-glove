# PD Monitoring Glove

**Sensing-to-Decision: A Transformer-Based Edge Computing Framework for Objective Parkinsonian Tremor and Bradykinesia Quantification**

Author: An Nguyen
Lab: Intelligent Automation (IoT) Research Group

## Overview

An IoT-enabled wearable glove system for continuous, objective monitoring of Parkinson's Disease motor symptoms. The system targets two primary biomarkers from the MDS-UPDRS Part III motor examination: **resting tremor** (4–6 Hz involuntary oscillation) and **bradykinesia** (progressive slowness and decremental amplitude during repetitive movement).

All sensor data is processed locally on a Raspberry Pi 5 through a DSP pipeline and Transformer-based ML model, with only processed clinical scores published via MQTT to the cloud. Raw biometric data never leaves the device (Privacy-by-Design).

## System Architecture

```
[Glove Sensors]              [USB Webcam]
5× MPU6050 IMU               MediaPipe Pose Estimation
5× Flex Sensor (pending)     Contextual Gatekeeper
        ↓                           ↓
    100Hz Raw Data          Resting vs Active State
        ↓                           ↓
┌──────────────────────────────────────────┐
│   DSP: Butterworth Band-Pass (3-15 Hz)  │
│   + Fast Fourier Transform (FFT)        │
└──────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│   ML Inference (TFLite INT8)            │
│   Transformer Encoder → MDS-UPDRS 0-4  │
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
| EMEET C960 USB Webcam | 1 | MediaPipe contextual gating | ✅ Acquired |

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

**USB Subsystem:**
EMEET C960 Webcam → Pi USB → MediaPipe pipeline

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
- [x] 2 IMUs reading independently on channels 0 and 1
- [ ] All 5 IMUs on channels 0–4
- [ ] MCP3008 ADC on SPI bus
- [ ] Flex sensor voltage divider circuits
- [ ] Full sensor array mounted on glove
- [ ] Software pipeline (sensor_reader.py, dsp_pipeline.py, etc.)

## Software Modules (Planned)

```
sensor_reader.py          ← IMU + flex polling at 100Hz
dsp_pipeline.py           ← Butterworth filter + FFT
mediapipe_gate.py         ← Webcam resting state detection
transformer_inference.py  ← TFLite INT8 model runner
mqtt_publisher.py         ← JSON payload → MQTT broker
main.py                   ← Orchestrates all modules
```

## Quick Start

```bash
ssh aqnguyen96@iotpi5.local
cd pd-glove
source venv/bin/activate
pip install -r requirements.txt  # install dependencies

# Scan I2C bus
sudo i2cdetect -y 1

# Test IMU reading
python3 -c "
import smbus2, time
bus = smbus2.SMBus(1)
bus.write_byte_data(0x70, 0, 1 << 0)  # select channel 0
bus.write_byte_data(0x68, 0x6B, 0)    # wake IMU
time.sleep(0.01)
ax = bus.read_byte_data(0x68,0x3B)<<8 | bus.read_byte_data(0x68,0x3C)
print(f'Accel X: {ax}')
"
```
