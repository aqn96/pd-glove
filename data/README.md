# Data Directory

This directory contains validated tremor detection datasets for the PD-glove sensing-to-decision framework.

## Files

### `tremor_validation_master.csv`

**Master dataset log** — All validation test results automatically appended by `scripts/run_tremor_validation.py`

**Design Rationale:**
Per-finger IMU placement enables isolation of the thumb-index interaction characteristic of Parkinsonian resting tremor, providing spatial granularity superior to single wrist-worn sensors for fine-grained motor pattern recognition.

**Columns (DSP Feature Vectors):**
- `person_id` — Subject identifier (e.g., person_1, person_2)
- `test_name` — Test identifier (e.g., test_one, test_two)
- `timestamp` — ISO 8601 timestamp of test execution
- `channel` — IMU channel (0=Thumb, 1=Index, 2=Middle, 3=Ring)
- `condition` — Either "rest" or "tremor" (app-controlled task window)
- `dominant_freq_hz` — Dominant frequency in 4-6 Hz Parkinsonian tremor band (FFT peak)
- `dominant_amp` — Amplitude at dominant frequency (g units)
- `band_power` — Total spectral power in 4-6 Hz band (primary tremor severity metric)
- `sampling_hz` — Measured sampling rate during capture (~89 Hz sustained)
- `retries` — Number of I2C retries (0 = perfect stability)
- `notes` — Optional notes about test conditions

**Structure:**
- Each test generates 8 rows: 4 channels × 2 conditions (rest/tremor)
- Data is append-only (never delete rows, mark bad tests in notes)
- Features extracted via 4th-order Butterworth bandpass filter (3-15 Hz) + FFT

**Usage:**
```python
import pandas as pd
df = pd.read_csv('data/tremor_validation_master.csv')
```

## Adding Data

Data is automatically appended when running:
```bash
python3 scripts/run_tremor_validation.py
```

Manual data entry is not recommended — always use the validation script to ensure consistent formatting.

## Dataset Versioning

When dataset reaches significant milestones, create snapshot copies:
```bash
cp data/tremor_validation_master.csv data/tremor_validation_v1.0_2026-03-25.csv
```
