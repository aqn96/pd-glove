# Activity 5: Attributes, Predictions, and Datasets (PD Glove)

This draft aligns with the current repo state (IMU pipeline implemented; flex pipeline planned) and the paper direction.

## 1) IoT attributes the system will measure

### IMU attributes (implemented now)

From 5 finger-mounted MPU6050 sensors (target 100 Hz):

- `timestamp`
- `channel` (0-4 for thumb to pinky)
- `ax`, `ay`, `az`
- `gx`, `gy`, `gz`

Derived tremor features from DSP:

- `dominant_freq_hz_4_6`
- `dominant_amp_4_6`
- `band_power_4_6`
- `effective_sampling_hz`
- `retry_events_i2c`

### Flex attributes (planned integration)

From 5 flex sensors via MCP3008:

- `flex_adc_ch0..ch4` (0-1023)
- normalized bend/ROM per finger
- `tap_rate_hz`
- `velocity_mean`, `velocity_cv`
- `amplitude_decrement_pct`
- `stiffness_index`

### Session/context attributes

- `exercise_type` (`rest_tremor`, `finger_tapping`, `hand_open_close`, `pronation_supination`)
- mapped MDS-UPDRS item
- `expected_duration_s`, `actual_duration_s`
- `status` (`complete`, `incomplete`, `interrupted`, `invalidated`)
- medication state (`on`, `off`, `unknown`)
- compliance flag (post-session validation)

## 2) Predictions possible from these attributes

- Tremor severity (MDS-UPDRS aligned 0-4)
- Bradykinesia severity (MDS-UPDRS aligned 0-4)
- Tremor presence/absence in designated rest windows
- Session quality/compliance classification
- Longitudinal trajectory (improving/stable/worsening)
- Significant symptom-change alerts across sessions

## 3) Existing datasets with compatible attributes

### A) Synapse: Parkinsons Disease Digital Biomarker DREAM Challenge (`syn8717496`)

Why it matches:

- Built around sensor-derived PD digital biomarkers.
- Includes accelerometer/gyroscope/magnetometer task data.
- Includes tremor and bradykinesia subchallenges.

What new value it adds:

- Strong benchmark ecosystem and feature-extraction baselines.
- Public challenge documentation plus scoreboards for method comparison.

Limitations:

- Challenge is closed; parts require controlled access.
- Device/sensor placement differs from finger-glove geometry.

### B) IEEE DataPort: PD-BioStampRC21

Why it matches:

- Wearable PD dataset using 5 body-worn sensors.
- Includes timestamps, triaxial accelerometry, and UPDRS-linked annotation.
- Includes medication ON/OFF context.

What new value it adds:

- 34 participants (17 PD + 17 control).
- ~2 days data per participant.
- Large real-world corpus (~11 GB zip, ~56 GB extracted).

Limitations:

- Sensor placement (trunk/thigh/forearm) is not finger-level glove placement.
- Primarily accelerometer data; no flex-sensor channels.

### C) Zenodo: ALAMEDA PD Tremor Dataset (DOI: `10.5281/zenodo.10782573`)

Why it matches:

- PD tremor-focused dataset with clinically grounded labels.
- Includes 92 extracted features from triaxial accelerometer windows.
- Labels map to tremor phenotypes from MDS-UPDRS III (binary transformed).

What new value it adds:

- Ready-to-model feature table for fast prototyping.
- Clear preprocessing recipe (band-pass, PCA/magnitude transform, FFT features).

Limitations:

- Feature-engineered dataset (not raw stream first), so less flexible for end-to-end feature learning.
- Bracelet placement differs from glove sensors.

### D) Synapse mPower public portal (as available)

Why it matches:

- Longitudinal smartphone motion tasks for PD.
- Useful for pretraining and external robustness checks.

## 4) Datasets to create for this project (custom glove-native)

Because sensor geometry is unique (5 finger IMUs + flex), project-specific data collection is required.

### Raw table (`raw_sensor_timeseries.csv`)

- `session_id`, `patient_id_hash`, `hand_side`
- `exercise_type`, `window_start`, `window_end`
- `timestamp`, `channel`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`
- optional flex channels after integration

### Feature table (`exercise_features.csv`)

- per-finger tremor metrics
- bradykinesia/flex metrics
- quality metrics (jitter, missing samples, retries)

### Label table (`labels.csv`)

- MDS-UPDRS reference score (0-4) per exercise
- medication state
- completion/interruption status
- de-identified annotator metadata

## 5) Activity 5 recommendation

Use all three external sources as candidates:

- Synapse DREAM (`syn8717496`) for challenge-grounded benchmark context
- PD-BioStampRC21 for real-world multi-sensor wearable comparison
- ALAMEDA for rapid tremor feature-model prototyping

Then explicitly state that final training/calibration should use your own glove-native dataset for sensor-placement transfer.
