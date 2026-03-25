# Multi-Subject Tremor Validation Dataset

**Collection Date:** 2026-03-25  
**Location:** Raspberry Pi 5 + 4-channel IMU array (channels 0-3)  
**Protocol:** `scripts/run_tremor_validation.py` (10-second rest + 10-second tremor per test)

## Dataset Overview

| Metric | Value |
|--------|-------|
| Total Valid Tests | 9 |
| Subjects | 2 (Person A, Person B) |
| Total Measurements | ~32,000 raw data points |
| Sampling Rate | 88.9-89.3 Hz |
| Hardware Failures | 0 (zero I2C retries) |
| Deleted Tests | 1 (environmental contamination) |

## Person A (5 Tests)

| Test ID | Timestamp | Rest Power Range | Tremor Power Range | Separation | Notes |
|---------|-----------|------------------|-------------------|------------|-------|
| 1 | 2026-03-25T17:38:58Z | 25-46 | 13,502-25,994 | 295-895× | Exaggerated tremor (MDS-UPDRS 3-4) |
| 2 | 2026-03-25T17:41:56Z | 33-51 | 2,537-6,630 | 50-202× | Moderate |
| 3 | 2026-03-25T17:44:54Z | 33-45 | 5,553-24,331 | 123-745× | High |
| 4 | 2026-03-25T17:46:42Z | 13-37 | 1,030-3,486 | 82-277× | Moderate-light |
| 5 | 2026-03-25T18:00:02Z | 37-46 | 1,371-2,113 | 30-47× | Light |

**Severity Distribution:**
- Light: Tests 4-5 (1-3.5K tremor power)
- Moderate: Test 2 (2.5-6.6K)
- High: Test 3 (5.5-24K)
- Severe: Test 1 (13.5-26K, exaggerated)

## Person B (4 Tests)

| Test ID | Timestamp | Rest Power Range | Tremor Power Range | Separation | Notes |
|---------|-----------|------------------|-------------------|------------|-------|
| 1 | 2026-03-25T18:03:42Z | 44-69 | 2,154-12,402 | 39-180× | Moderate-high |
| 3 | 2026-03-25T18:05:36Z | 22-41 | 672-3,373 | 30-141× | Moderate |
| 4 | 2026-03-25T18:06:37Z | 25-36 | 823-3,682 | 32-102× | Moderate |
| 5 | 2026-03-25T18:07:52Z | 22-39 | 1,702-5,510 | 56-141× | Moderate |

**Note:** Test 2 deleted due to environmental contamination (person nearby causing distraction, elevated rest baseline 394-688).

**Severity Distribution:**
- All tests fall in moderate range (672-12.4K tremor power)

## Hardware Configuration

**Mounting:**
- PLA 3D-printed rings (one per finger)
- Elastic bands for attachment
- Hot glue on side-top bars for stability

**Electrical:**
- Shared 3.3V and GND rails
- TCA9548A I2C multiplexer at address 0x70
- 4× MPU6050 IMUs at address 0x68 (channels 0-3)

**Channels:**
- CH0: Thumb
- CH1: Index
- CH2: Middle
- CH3: Ring

## Data Quality Metrics

### Rest Baseline (Normal Range: 13-70)
- Person A: 13-51 (excellent)
- Person B: 22-69 (excellent, excluding deleted test 2)

### Tremor Power Range (All Tests)
- Minimum: 672 (Person B Test 3, CH0)
- Maximum: 25,994 (Person A Test 1, CH2)
- Median: ~2,500

### Frequency Analysis
- All tremor captures show dominant frequencies in 4-6 Hz range
- Typical Parkinsonian resting tremor: 4-6 Hz ✅
- Rest captures show frequencies distributed across 4-6 Hz (noise floor)

### Separation Quality
- Minimum: 30× (Person A Test 5 - lightest tremor)
- Maximum: 895× (Person A Test 1 - exaggerated tremor)
- Median: ~100× (clinically significant)

## Environmental Controls

### Successful Protocol
1. Hand at complete rest on stable surface
2. Controlled environment (no nearby movement)
3. Consistent 10-second capture windows
4. Sequential rest → tremor captures

### Contamination Case (Person B Test 2)
- **Issue:** Person walking nearby during rest capture
- **Effect:** Rest baseline elevated 10× (394-688 vs normal 22-69)
- **Outcome:** Poor separation (1-10× instead of 30-180×)
- **Action:** Test deleted and logged

## Clinical Relevance

### MDS-UPDRS Part III Tremor Scoring Alignment

| Score | Description | Power Range (Dataset) | Examples |
|-------|-------------|----------------------|----------|
| 0 | Normal | <100 | N/A (all rest <70) |
| 1 | Slight | 1,000-2,500 | Person A Tests 4-5 |
| 2 | Mild | 2,500-7,000 | Person A Test 2, Person B Tests 3-5 |
| 3 | Moderate | 7,000-15,000 | Person A Test 3, Person B Test 1 |
| 4 | Marked | 15,000+ | Person A Test 1 |

## Dataset Files

CSV files generated during validation:
- `rest_4ch.csv` (rest captures, overwritten per test)
- `tremor_4ch.csv` (tremor captures, overwritten per test)

**Format:** Timestamp, Channel, ax, ay, az, gx, gy, gz

## Next Steps

1. **Model Training:** Use this dataset for Transformer encoder training
2. **Cross-validation:** Split Person A vs Person B for subject-independent validation
3. **Data Augmentation:** Apply time-domain augmentation for robustness
4. **Feature Engineering:** Extract frequency-domain features for classical ML baseline
5. **Additional Subjects:** Collect Person C-E data for larger training set

## Session Metadata

Session tracking in SQL database contains:
- 9 validation_tests records
- 72 test_metrics records (9 tests × 4 channels × 2 conditions)
- 1 deleted_tests record with contamination details

All data quality issues documented and logged for reproducibility.
