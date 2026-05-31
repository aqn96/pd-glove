# Data Directory

This directory contains validated datasets for the PD-glove sensing-to-decision framework, plus external clinical corpora downloaded for CS 8674 Part II model training.

## Local files (committed)

### `flex_bench_thumb_2026-05-07.csv`

**Off-platform flex-sensor bench characterization** — 10 trials × 4 angles (0°, 30°, 60°, 90°) on a single SparkFun SEN-10264 mounted on a thumb jig, sampled by an Arduino Nano 33 BLE Sense Lite at 12-bit ADC resolution.

**Columns:**
- `trial` — Trial index (1–10 per angle)
- `angle_deg` — Bench-jig angle (0, 30, 60, 90)
- `adc_value` — Raw ADC reading
- `capture_date` — ISO 8601 capture date

**Scope and analysis notes:**
- Off-platform: not the Pi 5 + MCP3008 deployment path. See `docs/flex-bench-characterization.md` for the protocol, results, and reproducibility notes.
- 90° readings are retained for reproducibility but excluded from the paper analysis due to hysteresis-zone instability (SD ≈ ±145 ADC).
- Source of truth for paper §V-E and §VIII flex-sensor claims (AIIoT 2026 camera-ready).

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

## External datasets (not committed)

External clinical corpora live in per-dataset subdirectories under `data/`. The raw bundles are gitignored (too large, reproducible from source); each subdirectory ships a committed `README.md` documenting provenance, layout, file format, citation, and a one-shot restore command.

Canonical long-term storage for cross-environment access (Kaggle, EC2) is the AWS S3 bucket per the Part II syllabus; the local `data/<dataset>/` copies are for offline EDA and notebook development.

### `daphnet/` — Daphnet Freezing of Gait

10 PD patients, 17 sessions, ~86 MB unzipped, 64 Hz triaxial accelerometer at ankle/thigh/trunk with freeze annotation labels. Downloaded 2026-05-31 from UCI for D1 FOG baselines (syllabus Week 3) and D2 auxiliary input (syllabus Week 7).

See [`daphnet/README.md`](daphnet/README.md) for layout, column spec, quick-load snippet, and citation.

| Dataset | Status | Notes |
|---|---|---|
| Daphnet FOG | ✅ Downloaded 2026-05-31 | Open access (UCI), no approval needed |
| ALAMEDA Tremor | ⏳ Pending download | Open access (Zenodo CC BY 4.0), no approval needed |
| PPMI MDS-UPDRS + Roche PD App v2 | ⏳ Awaiting LONI DUA approval | Per-collection approval, 3–10 days typical |
| mPower walking + tapping | ⏳ Awaiting Synapse approval | Qualified-researcher application |
| CARE-PD 3D mesh gait | ⏳ Pending | GitHub / HuggingFace; large download |

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
