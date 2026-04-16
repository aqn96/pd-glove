# Activity 7: Complete Project Report

## Introduction

Parkinson's disease (PD) motor symptoms such as resting tremor and bradykinesia are often assessed intermittently in clinic settings using observer-based scales. This can miss day-to-day variability and limit objective tracking of symptom progression. The PD Glove project addresses this gap by combining wearable sensing, edge signal processing, and machine-learning-ready feature extraction to support continuous and structured motor assessment.

This project focuses on a finger-mounted wearable architecture with multiple IMU channels to capture fine-grained tremor signatures. The current implementation emphasizes tremor quantification first, while preserving a clear path to bradykinesia assessment through planned flex-sensor integration.

## Aim and objective of the project

The aim is to design and validate an IoT-enabled glove system that measures PD-relevant motor behavior and supports MDS-UPDRS-aligned severity estimation.

Objectives:

1. Acquire stable, multi-channel finger IMU data from a wearable glove platform.
2. Implement an edge DSP pipeline to isolate tremor-relevant frequency components (4-6 Hz).
3. Produce reproducible tremor features that can be used for model training and longitudinal tracking.
4. Build a structured dataset workflow suitable for future Transformer/TFLite inference deployment.
5. Maintain privacy-by-design by keeping raw biometric streams local to the edge device.

## Literature review summary

Recent PD digital biomarker literature shows strong evidence that inertial sensing can quantify tremor and bradykinesia patterns beyond subjective observation. Challenge datasets and wearable studies demonstrate that accelerometer/gyroscope features, especially frequency-domain metrics, are effective for tremor characterization. Clinical framing through MDS-UPDRS remains important for interpretability and translational relevance.

This project is informed by:

- Sensor-based PD biomarker benchmarking efforts (e.g., DREAM/Synapse challenge ecosystems).
- Wearable longitudinal PD datasets (e.g., PD-BioStampRC21).
- Clinically grounded tremor feature datasets (e.g., ALAMEDA PD Tremor).
- MDS-UPDRS Part III motor assessment standards for score alignment.

The key gap in prior datasets is sensor placement mismatch with finger-level glove geometry, which motivates collecting a glove-native dataset for final model calibration.

## Methodology

System methodology follows a sensing-to-decision edge pipeline:

1. **Data acquisition**  
   Five MPU6050 IMUs are connected through a TCA9548A I2C multiplexer, with per-finger channel mapping.

2. **Signal conditioning and feature extraction**  
   A Butterworth band-pass filter and FFT-based analysis extract tremor power and dominant frequency metrics, with emphasis on the 4-6 Hz Parkinsonian tremor band.

3. **Structured protocol execution**  
   Sessions use standardized task captures (rest vs tremor windows), then append results to a master CSV for repeatable analysis.

4. **Clinical alignment and traceability**  
   Feature outputs are designed to support future mapping to MDS-UPDRS-like severity classes and longitudinal trend analysis.

5. **Security and privacy constraints**  
   Raw streams remain on-device; only processed summaries are intended for cloud messaging.

## Implementation

The implementation is organized into modular scripts:

- `scripts/test_imus.py` for per-channel hardware probing and WHO_AM_I compatibility checks.
- `scripts/sensor_reader.py` for multi-channel IMU polling and CSV capture.
- `scripts/dsp_pipeline.py` for filtering and spectral feature computation.
- `scripts/run_tremor_validation.py` for end-to-end validation workflow and automatic master CSV logging.

Current implementation status:

- Stable operation achieved on 4 channels (thumb, index, middle, ring).
- Sustained sampling near ~89 Hz measured in 4-channel operation.
- Tremor-focused pipeline validated end-to-end from acquisition to DSP outputs.
- Pinky channel remains a known hardware fault path under investigation.

## Testing

Testing was performed as staged hardware-to-pipeline validation:

1. **Hardware connectivity tests** using channel scan and sensor identity checks.
2. **Acquisition stability tests** for sustained multi-channel capture and retry/error monitoring.
3. **DSP verification tests** comparing rest vs tremor captures per channel.
4. **Multi-subject functional validation** with repeated runs and master CSV logging.

Observed outcomes:

- Distinct rest-to-tremor power separation was repeatedly observed.
- Dominant tremor frequencies aligned with expected Parkinsonian bands (4-6 Hz) in tremor captures.
- Dataset artifacts were generated in consistent tabular form for downstream model development.

## Conclusion

The PD Glove prototype demonstrates a viable edge-computing pathway for objective tremor assessment using finger-level wearable sensing. The current system has achieved robust tremor-phase readiness, including repeatable capture, DSP-based feature extraction, and structured dataset accumulation. These results support moving to the next phase: model training, five-channel stabilization, and flex-sensor integration for bradykinesia features.

## Reflection

This project reinforced that clinical IoT systems require equal attention to hardware reliability, signal quality, and protocol design. A major practical lesson was that sensor placement and wiring stability can dominate model-readiness more than algorithm complexity in early phases. Another key reflection is the value of building reproducible data workflows early (automatic logging, consistent metadata), which reduces friction for later ML experiments and reporting.

## References

1. Goetz, C. G., Tilley, B. C., Shaftman, S. R., et al. (2008). Movement Disorder Society-sponsored revision of the Unified Parkinson's Disease Rating Scale (MDS-UPDRS): Scale presentation and clinimetric testing results.
2. Parkinson's Disease Digital Biomarker DREAM Challenge resources (Synapse, `syn8717496`).
3. IEEE DataPort: PD-BioStampRC21 wearable Parkinson's dataset.
4. ALAMEDA Parkinson's Tremor Dataset. Zenodo. DOI: `10.5281/zenodo.10782573`.
