# CS 8674 Part II — Original Course Syllabus
**Intelligent IoT Frameworks for Chronic Disease Management**
**Summer 2026 (May 6 – August 16)**

---

## Course Information

| | |
|---|---|
| Instructor | Sarita Singh |
| Email | s.singh@northeastern.edu |
| Class Meeting | TBD via Teams |
| Location | Online (Teams) |
| Communication | All announcements and discussions via Teams |

---

## Course Description

This summer continuation course completes the machine learning core of the Sensing-to-Decision framework established in CS 8674 Part I (Spring 2026). Part I delivered a validated four-channel IMU glove prototype, a working DSP tremor pipeline, and a multi-subject validation dataset. This session addresses the remaining technical pipeline: curating and joining clinical training datasets, training the Transformer encoder model for MDS-UPDRS score prediction, deploying a TFLite INT8 artifact, and implementing the MQTT telemetry and compliance validation modules.

All coursework runs entirely online. No hardware access is required during this session. Model training is conducted on Kaggle Notebooks (free GPU, no session timeouts) for prototyping and iterative development, with full training jobs and artifact storage handled on AWS (school-provided account) via EC2 GPU instances and S3. Datasets are centrally stored in a private S3 bucket accessible from both environments. Hardware-dependent tasks resume upon return to campus.

Note: This course emphasizes System Architecture and Privacy-by-Design. All model training uses public clinical datasets (PPMI, ALAMEDA). No clinical trials or collection of sensitive personal data (PII) is required. Project continuation beyond August 16 may be discussed with the instructor (optional).

---

## Prerequisites

- Successful completion of CS 8674 Part I with a functional hardware prototype and validated DSP pipeline
- GitHub repository at aqn96/pd-glove with tremor_validation_master.csv committed
- PPMI data access registered at ida.loni.usc.edu
- Familiarity with PyTorch or TensorFlow and basic model training workflows
- AWS school account active with access to EC2 GPU instances and S3

---

## Course Objectives

Upon completion, students will be able to:

- Curate, join, and engineer features from PPMI and ALAMEDA clinical datasets for Transformer model training
- Train and evaluate a Transformer encoder model on multi-finger IMU feature vectors for MDS-UPDRS score prediction
- Apply INT8 post-training quantization and benchmark TFLite inference latency
- Implement the MQTT telemetry pipeline with AES-256-GCM encryption and TLS 1.3 transport
- Build a MediaPipe-based compliance validation module for retrospective rest-window gating
- Present a complete, reproducible ML pipeline with documented GitHub notebooks

---

## Deliverables and Grading

| Deliverable | Due Date | Weight |
|---|---|---|
| Dataset Pipeline & Baseline Classifiers | Jun 16 | 20% |
| Transformer Training & Evaluation | Jul 14 | 35% |
| Edge Deployment & Pipeline Integration | Aug 4 | 25% |
| Final Report, Presentation & Demo | Aug 16 | 20% |

---

## Deliverable 1: Dataset Pipeline & Baseline Classifiers (20%)

**Due: June 16**

- PPMI Part III and Roche PD App v2 data downloaded, joined on PATNO and EVENT_ID, and cleaned; subject-level train/validation/test splits with no longitudinal leakage
- ALAMEDA dataset downloaded and feature extraction reproduced in Python; feature format aligned to glove DSP output schema
- Daphnet Freezing of Gait dataset downloaded and preprocessed; accelerometer feature extraction aligned to glove IMU pipeline
- All cleaned datasets uploaded to AWS S3 (private bucket) for shared access across Kaggle and EC2 environments
- Unified feature schema documented and EDA completed across all four datasets
- Baseline classifiers benchmarked: SVM, Random Forest, 1D-CNN — for both tremor/bradykinesia and FOG detection tasks
- 3–5 page technical report + GitHub notebooks committed

---

## Deliverable 2: Transformer Training & Evaluation (35%)

**Due: July 14**

- Transformer encoder trained and evaluated for tremor/bradykinesia: macro-F1, AUROC, calibration error, confusion matrix by MDS-UPDRS class
- Separate Transformer encoder trained for freezing of gait (FOG) detection using Daphnet accelerometer features; features aligned to MediaPipe Pose-derived motion signals for future camera-based gait inference
- mPower walking task accelerometer data incorporated as auxiliary gait training input
- Ablation study: per-finger multi-channel vs. simulated single-wrist configuration
- TFLite INT8 quantization applied to both models; accuracy delta vs. float32 baseline reported
- Uncertainty-aware scoring implemented: confidence intervals on MDS-UPDRS output
- Model artifacts (.pt, .tflite) stored in AWS S3
- 8–10 page technical report with training curves, error analysis, and clinical alignment discussion

---

## Deliverable 3: Edge Deployment & Pipeline Integration (25%)

**Due: August 4**

- TFLite artifact latency benchmarked on available hardware
- MQTT pipeline implemented and tested: AES-256-GCM encryption, TLS 1.3, exercise-centric JSON payload
- MediaPipe Hand Landmarker compliance validation module running on pre-recorded video; session flagging logic tested
- Fairness audit across PPMI demographic splits (age, sex, disease stage)
- 3–5 page integration report with latency, fairness, and security test results

---

## Deliverable 4: Final Report, Presentation & Demo (20%)

**Due: August 16**

- Comprehensive final report (10–12 pages) covering dataset pipeline, model training, evaluation, and system integration
- Complete GitHub repository: all notebooks, MQTT modules, README, requirements.txt
- 15-minute presentation with live demo of trained model inference and MQTT pipeline
- Q&A session

---

## Schedule

| Phase | Dates | Topics | Milestones |
|---|---|---|---|
| Pre-Planning P1 | Apr 26 – May 6 | Transformer encoder architectures for IMU time-series; MDS-UPDRS Part III scoring methodology | |
| Pre-Planning P2 | May 7 – May 13 | PPMI data dictionary; mPower walking task; Daphnet and PhysioNet VGRF formats; MediaPipe Hand Landmarker and Pose docs | |
| Pre-Planning P3 | May 14 – May 18 | PPMI + ALAMEDA + Daphnet + VGRF downloads; AWS S3 setup; Kaggle environment setup | Pre-planning complete: May 18 |
| Week 1 | May 19 – May 25 | PPMI Part III + Roche PD App v2 joins, EDA, subject-level splits; Daphnet loading and EDA | |
| Week 2 | May 26 – Jun 1 | ALAMEDA feature alignment; Daphnet EDA and FOG label analysis; unified feature schema; S3 upload | |
| Week 3 | Jun 2 – Jun 8 | Baseline classifiers (SVM, RF, 1D-CNN) for tremor/bradykinesia; baseline classifiers for FOG; feature importance | |
| Week 4 | Jun 9 – Jun 16 | Finalize baselines; technical report; D1 presentations | **D1 Due: Jun 16** |
| Week 5 | Jun 17 – Jun 23 | Transformer encoder architecture for tremor/bradykinesia on Kaggle; mPower preprocessing; initial training | |
| Week 6 | Jun 24 – Jun 30 | Full tremor Transformer training on AWS EC2; learning curves; multi-channel vs. single-wrist ablation | |
| Week 7 | Jul 1 – Jul 7 | CARE-PD gait model training; Daphnet FOG features as auxiliary input; uncertainty-aware scoring | |
| Week 8 | Jul 8 – Jul 14 | TFLite INT8 quantization; clinical alignment analysis; save artifacts to S3; D2 presentations | **D2 Due: Jul 14** |
| Week 9 | Jul 15 – Jul 21 | MQTT pipeline implementation; AES-256-GCM encryption testing; TLS 1.3 transport validation | |
| Week 10 | Jul 22 – Jul 28 | MediaPipe Hand Landmarker compliance module; gait inference pipeline end-to-end; session flagging | |
| Week 11 | Jul 29 – Aug 4 | Fairness audit across PPMI demographic splits; TFLite latency benchmarking; D3 presentations | **D3 Due: Aug 4** |
| Week 12 | Aug 5 – Aug 11 | Final report writing; GitHub repository cleanup and documentation | |
| Week 13 | Aug 12 – Aug 16 | Final presentation preparation and live demo | **D4 Due: Aug 16** |

---

## Required Tools & Resources

### Compute & Storage

| Platform | Purpose |
|---|---|
| Kaggle Notebooks | Free GPU (T4/P100, 30 hrs/week); EDA, data pipeline, baseline classifiers, initial Transformer training |
| AWS EC2 (school account) | Full Transformer training job (g4dn.xlarge or p3.2xlarge); TFLite benchmarking; MQTT broker hosting |
| AWS S3 (school account) | Central dataset and model artifact storage |
| GitHub (aqn96/pd-glove) | Version control for all notebooks and code |

### Software

- Python, Jupyter Notebooks
- ML Libraries: PyTorch, TensorFlow Lite, scikit-learn, pandas, numpy, scipy
- AWS: boto3, AWS CLI
- MQTT: paho-mqtt, broker hosted on AWS EC2
- Sensor Libraries: OpenCV, MediaPipe

### Datasets

| Dataset | Source |
|---|---|
| PPMI — MDS-UPDRS Part III + Roche PD App v2 | ida.loni.usc.edu |
| ALAMEDA Tremor Dataset | https://doi.org/10.5281/zenodo.10782573 (CC BY 4.0) |
| mPower — walking + tapping tasks | https://www.synapse.org/Synapse:syn4993293/wiki/247859 |
| Daphnet Freezing of Gait | https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait |
| CARE-PD — 3D mesh gait data, UPDRS gait scores | https://github.com/TaatiTeam/CARE-PD |
| tremor_validation_master.csv | Local glove validation data, GitHub aqn96/pd-glove |

---

## Repository Requirements

Final GitHub repository (aqn96/pd-glove) should include:

- README.md with setup instructions
- requirements.txt
- Dataset_Pipeline.ipynb
- Unimodal_Classifiers.ipynb
- Transformer_Training.ipynb
- TFLite_Deployment.ipynb
- mqtt_publisher.py and mediapipe_compliance.py
- aws_setup.md
- Documentation and sample data

---

## Key References

**Clinical Standard**
- Goetz et al., "MDS-sponsored revision of the Unified Parkinson's Disease Rating Scale (MDS-UPDRS)," Movement Disorders, 2007.

**Datasets**
- Marek et al., "The Parkinson Progression Marker Initiative (PPMI)," Progress in Neurobiology, 2011.
- Bot et al., "The mPower study, Parkinson disease mobile data collected using ResearchKit," Scientific Data, 2016.
- ALAMEDA Tremor Dataset (CC BY 4.0). https://doi.org/10.5281/zenodo.10782573
- Bachlin et al., "Wearable Assistant for Parkinson's Disease Patients With the Freezing of Gait Symptom," IEEE TITB, 2010.
- Adeli et al., "CARE-PD: A Multi-Site Anonymized Clinical Dataset for Parkinson's Disease Gait Assessment," NeurIPS, 2025.

**ML & Edge Deployment**
- Vaswani et al., "Attention Is All You Need," NeurIPS, 2017.
- Kralik & Suppa, "WAVEGLOVE: Transformer-based hand gesture recognition using multiple inertial sensors," arXiv:2105.01753, 2021.
- Vadlamudi, "The rise of edge computing in healthcare data processing," WJARR, 2025.

**Computer Vision**
- Lugaresi et al., "MediaPipe: A Framework for Building Perception Pipelines," arXiv:1906.08172, 2019.

**Privacy & Security**
- Rasool et al., "Security and privacy of Internet of Medical Things," JNCA, 2022.
- Shirali et al., "Information fusion in multimodal IoT systems for physical activity level monitoring," arXiv:2403.14707, 2025.
