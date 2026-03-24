# Validation Results (2026-03-21)

This document captures the current tremor-phase validation status for the PD glove prototype on Raspberry Pi 5.

## Environment

- Hardware: Raspberry Pi 5 + 5x MPU6050 + TCA9548A
- Pipeline:
  - `scripts/sensor_reader.py` (multi-IMU capture)
  - `scripts/dsp_pipeline.py` (3-15 Hz Butterworth + FFT 4-6 Hz metrics)
- Scope: tremor only (flex/bradykinesia pending)

## Final Stable Hardware State

During debugging, channel failures (`Errno 121`) were traced to unstable power/ground distribution and branch path reliability.

Stable configuration used for final validation:

- shared 3.3V rail for all IMUs + TCA9548A
- shared GND rail for all IMUs + TCA9548A + Pi
- ordered channel wiring (CH0..CH4)

## Capture Performance

Command:

```bash
python3 scripts/sensor_reader.py --duration 10 --output imu_capture_all5_fixed.csv
```

Observed output:

- `retries=0`
- `wall_time=14.01s`
- `effective_hz=71.36`

Interpretation:

- I2C reliability improved significantly versus earlier retries-heavy runs.
- Current effective throughput is below target 100 Hz, but sufficient for 4-6 Hz tremor-band analysis in prototype phase.

## FFT Tremor-Band Results (4-6 Hz)

Input file: `imu_capture_all5_fixed.csv`  
Axis: `ax`

| Channel | Dominant freq (Hz) | Dominant amp | Band power |
|---|---:|---:|---:|
| CH0 | 5.300 | 1.785462 | 23.555304 |
| CH1 | 6.000 | 1.717052 | 16.856509 |
| CH2 | 4.500 | 1.935278 | 24.790993 |
| CH3 | 4.800 | 2.111791 | 32.476557 |
| CH4 | 4.200 | 1.913614 | 19.898083 |

All channels produced plausible 4-6 Hz dominant peaks with no extreme outlier corruption.

## Rest vs Tremor Trial Pair

Files:

- `rest_20260321_163532.csv`
- `tremor_20260321_163551.csv`

Results indicate functional band extraction across channels but mixed rest-vs-tremor separation under current bench setup. This is expected given non-mounted sensors and short windows.

Planned improvement for stronger separation:

- mount sensors on PLA rings
- collect longer windows (20-30 s)
- run repeated trials and average per-channel metrics

## Conclusion

The repository currently satisfies tremor-phase architecture validation:

- multi-IMU acquisition working on Pi
- tremor-band DSP pipeline operational end-to-end
- wiring/power troubleshooting documented

Next stage is wearable mounting + repeated structured data collection before Transformer/MQTT integration.
