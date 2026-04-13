# Testing Workflow

## 1) Quick Hardware Probe

Use `scripts/test_imus.py` to check channel health:

```bash
python3 scripts/test_imus.py
```

Probe selected channels only:

```bash
python3 scripts/test_imus.py --channels 0,1,2
```

Expected:

- `CHx: OK Accel X = ...` for healthy channels
- `CHx: FAIL [Errno 121] Remote I/O error` for channel path/wiring issues

## 2) Capture Session

```bash
python3 scripts/sensor_reader.py --duration 10 --output imu_capture.csv
```

Watch progress output:

- effective sampling rate
- retry count

## 3) DSP Analysis

Single channel:

```bash
python3 scripts/dsp_pipeline.py --input imu_capture.csv --channel 0 --axis ax
```

All channels:

```bash
for ch in 0 1 2 3 4; do
  python3 scripts/dsp_pipeline.py --input imu_capture.csv --channel $ch --axis ax
done
```

## 4) Rest vs Tremor Pair

```bash
python3 scripts/sensor_reader.py --duration 10 --output rest_$(date +%Y%m%d_%H%M%S).csv
python3 scripts/sensor_reader.py --duration 10 --output tremor_$(date +%Y%m%d_%H%M%S).csv
```

Compare per-channel 4-6 Hz metrics between the two files.

## 5) Troubleshooting Priority

When `Errno 121` appears:

1. verify shared 3.3V and shared GND rails
2. verify channel branch wiring order and continuity
3. probe channels individually with `test_imus.py --channels ...`
4. isolate sensor vs branch by swapping known-good IMU across channels
