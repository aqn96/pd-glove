# Literature Review: Machine Learning for Hand Tremor Analysis

**Author:** An Nguyen
**Course:** CS 8674 Part II — Intelligent IoT Frameworks for Chronic Disease Management (Summer 2026)
**Instructor:** Sarita Singh
**Due:** May 31, 2026

This review surveys 20 peer-reviewed and high-quality preprint sources spanning the machine learning literature on hand tremor analysis, with deliberate breadth across sensing modalities (wrist/finger IMUs, smartphones, video, multimodal), ML method families (classical, 1D-CNN, CNN-LSTM, Transformer, multiple-instance learning, prototypical networks, self-supervised foundation models, federated learning), clinical tasks (tremor detection, severity rating, PD-vs-essential-tremor differentiation, freezing of gait, bradykinesia, gait severity), and deployment concerns (edge inference, privacy, fairness). The selection prioritizes work from 2021–2026 (17 of 20 entries), while retaining three foundational papers (2010–2020) that define the datasets and methodological starting points the field continues to build on. Sources are sorted alphabetically by first author surname (APA 7th edition). A Research Gap section follows the bibliography and ties the synthesis explicitly to the PD-glove research program.

---

## Annotated Bibliography

### 1. Adeli et al. (2025)

Adeli, V., Klabucar, I., Rajabi, J., Filtjens, B., Mehraban, S., Wang, D., Seo, H., Hoang, T.-H., Do, M. N., Muller, C., Oliveira, C., Coelho, D. B., Ginis, P., Gilat, M., Nieuwboer, A., Spildooren, J., McKay, L., Kwon, H., Clifford, G., … Taati, B. (2025). CARE-PD: A multi-site anonymized clinical dataset for Parkinson's disease gait assessment. *arXiv* (NeurIPS 2025 Datasets & Benchmarks Track). https://arxiv.org/abs/2510.04312

CARE-PD is the largest publicly available archive of anonymized 3D mesh gait recordings for Parkinson's disease, drawing from nine cohorts across eight clinical centers. All RGB-video and motion-capture sources are harmonized into SMPL body meshes via a unified preprocessing pipeline, supporting two benchmark tracks: supervised UPDRS gait-score prediction and unsupervised motion pretext tasks such as 2D-to-3D keypoint lifting and full-body reconstruction. The authors evaluated seven state-of-the-art motion encoders — including MotionBERT, MotionAGFormer, PoseFormerV2, and POTR — and report that learned motion encoders substantially outperform classical handcrafted gait features, with MotionBERT achieving up to 0.49 on PD-GaM but only 0.25 on T-SDU-PD, exposing strong site-shift sensitivity.

The paper accomplishes its stated goal: it provides the first multi-site, anonymized 3D-mesh PD gait resource and a reproducible benchmark protocol with explicit cross-site generalization tests. Its key limitation is that gait severity, while clinically meaningful, is one slice of MDS-UPDRS Part III; tremor and bradykinesia are not in scope. Site-specific performance variance also signals that current motion encoders are not yet domain-invariant.

For PD-glove, CARE-PD is directly load-bearing for the Part II auxiliary gait branch outlined in the syllabus (Weeks 7–8): the MotionBERT/POTR encoders evaluated here are the candidate backbones for the phone-video gait inference module that will pair with my IMU tremor model. The site-shift findings also motivate fairness-aware splits in my own protocol.

### 2. Atri et al. (2022)

Atri, R., Urban, K., Marebwa, B., Simuni, T., Tanner, C., Siderowf, A., Frasier, M., Haas, M., & Lancashire, L. (2022). Deep learning for daily monitoring of Parkinson's disease outside the clinic using wearable sensors. *Sensors, 22*(18), Article 6831. https://doi.org/10.3390/s22186831

Atri and colleagues built an end-to-end pipeline that segments continuous Verily Study Watch recordings (worn up to 23 hours/day) into "walk-like events" via human-activity-recognition heuristics, then classifies those segments with a 1D-CNN to discriminate PD patients from healthy controls. The system was trained on 7 PD and 4 control participants and achieved roughly 90% accuracy on 5-second walk events, rising to 100% accuracy when daily predictions are aggregated by majority vote, with stability sustained across three months of follow-up. The work foregrounds an architecture pattern — activity-gated 1D-CNN over wrist accelerometer/gyroscope segments — that is now a standard baseline for wearable PD classification.

The paper meets its goal of demonstrating feasibility of unconstrained, free-living monitoring, but the sample size (11 total subjects) is small relative to the strength of the headline accuracy claim. The 100% per-day result is best read as showing how aggregation hides per-segment uncertainty rather than as a generalizable performance bound, and the cohort is too small to support fairness evaluation.

For PD-glove, this is one of the closest methodological analogues to the baseline 1D-CNN classifiers I will train for Deliverable 1 (June 16). The activity-gating idea — only running the tremor model when the wearer is in a relevant pose — also informs my MediaPipe Hand Landmarker compliance module, which serves an analogous gating role on phone video.

### 3. Bachlin et al. (2010)

Bachlin, M., Plotnik, M., Roggen, D., Maidan, I., Hausdorff, J. M., Giladi, N., & Tröster, G. (2010). Wearable assistant for Parkinson's disease patients with the freezing of gait symptom. *IEEE Transactions on Information Technology in Biomedicine, 14*(2), 436–446. https://doi.org/10.1109/TITB.2009.2036165

This foundational paper introduces the Daphnet Freezing of Gait dataset and an online detection algorithm that triggers an auditory rhythmic cue when a freezing episode is detected. The system uses three MEMS triaxial accelerometers (shank, thigh, lower back) sampled at 64 Hz; the freeze-index feature is computed as the power ratio between a 3–8 Hz "freeze band" and a 0.5–3 Hz "locomotion band," with subject-tailored thresholding for classification. Across ten advanced-PD patients, the system reaches roughly 73% sensitivity and 82% specificity for FoG detection in real time on a body-worn computing platform.

The paper accomplishes its goal: it establishes both a public benchmark and a credible end-to-end wearable intervention. By modern standards its detector is simple (threshold on a hand-engineered ratio), it relies on per-subject calibration, and the cohort is small and homogeneous, but those weaknesses are exactly what motivated the deep-learning successors cited later in this review.

For PD-glove, Daphnet is the syllabus-mandated training corpus for my Part II FoG auxiliary model (Weeks 1–4). Bachlin's freeze-band/locomotion-band framing also offers a sanity-check baseline for any Transformer or CNN model I train — if my model cannot beat a threshold-on-power-ratio classifier on its home turf, something is wrong.

### 4. Bot et al. (2016)

Bot, B. M., Suver, C., Chaibub Neto, E., Kellen, M., Klein, A., Bare, C., Doerr, M., Pratap, A., Wilbanks, J., Dorsey, E. R., Friend, S. H., & Trister, A. D. (2016). The mPower study, Parkinson disease mobile data collected using ResearchKit. *Scientific Data, 3*, Article 160011. https://doi.org/10.1038/sdata.2016.11

mPower is the foundational smartphone-based PD observational study, conducted entirely through an iPhone app and released as a public dataset on Synapse. Participants complete demographic, MDS-UPDRS, and PDQ-8 surveys plus four sensor-based activities — memory, finger tapping, voice, and walking — yielding a longitudinal corpus from over 9,000 enrolled participants in the first six months. The paper documents the consent flow, data schema, and rationale for releasing raw sensor traces under a controlled-access model rather than only derived summaries.

The paper succeeds at its goal of providing the field with a large, demographically diverse, real-world PD-symptom dataset; it remains one of the most cited resources in digital-biomarker research. Its main limitations are self-selection bias (iPhone owners who heard about the study), inconsistent task adherence, weak PD diagnosis confirmation, and the well-documented difficulty of extracting clean MDS-UPDRS-aligned labels from voluntary at-home recordings.

For PD-glove, mPower is the syllabus-listed auxiliary corpus for the Transformer encoder's gait branch (walking task) and an informal pre-training source for the tremor branch (finger tapping). It also serves as a cautionary template: my own protocol must avoid the same label-quality and self-selection traps, which is why the Pi-5 deployment uses structured assessment tasks rather than free-form data capture.

### 5. Das et al. (2024)

Das, A. M., Tang, C. I., Kawsar, F., & Malekzadeh, M. (2024). PRIMUS: Pretraining IMU encoders with multimodal self-supervision. *arXiv* (NeurIPS 2024 TSALM Workshop; subsequently ICASSP 2025). https://arxiv.org/abs/2411.15127

PRIMUS proposes a pretraining objective for IMU encoders that combines three losses: a self-supervised augmentation-invariance term, a multimodal alignment term that pulls IMU embeddings toward co-occurring video and text features, and a nearest-neighbor contrastive term in IMU space. The recipe is intended to address the chronic label scarcity in human-motion sensing. Across in-domain and out-of-domain evaluations, PRIMUS lifts downstream test accuracy by up to 15% over strong self-supervised baselines when fewer than 500 labeled samples per class are available, and the code is open-sourced via Nokia Bell Labs' pretrained-imu-encoders repository.

The work clearly accomplishes its stated goal: it demonstrates a reusable, transferable IMU foundation-model recipe and includes ablations that isolate each loss term. The main caveat is that the downstream benchmarks are general human-activity recognition; the paper does not evaluate on PD-specific or clinical-rating tasks, so the magnitude of transfer to MDS-UPDRS scoring is an open question.

For PD-glove, PRIMUS is the most concrete template available for pretraining a per-finger IMU Transformer encoder on a generic motion corpus and then fine-tuning on my multi-subject validation dataset (n=9 sessions, 72 per-finger feature vectors), which is much smaller than what end-to-end Transformer training typically demands. This is the most plausible path to a clinically useful model from my modest labeled cohort.

### 6. Duque-Quiceno et al. (2024)

Duque-Quiceno, F., Sarapata, G., Dushin, Y., Allen, M., & O'Keeffe, J. (2024). Deep learning for objective estimation of Parkinsonian tremor severity. *arXiv*. https://arxiv.org/abs/2409.02011

This paper trains a pixel-based deep learning model on 2,742 video assessments collected from five movement-disorder centers across two continents to predict MDS-UPDRS Part III tremor sub-scores directly from raw RGB frames. The model is reported to show "robust concordance with clinical evaluations," generalize across distinct tremor types (rest, postural), and recover the expected dose-response signal for levodopa and deep brain stimulation in held-out longitudinal sub-cohorts. The work positions video as a low-friction alternative to wearables, suited for telemedicine and remote enrollment.

The authors meet their goal of demonstrating a video-only severity estimator at clinically meaningful scale. Limitations: the paper relies on pixel-level features without explicit pose extraction, so it inherits camera-setup and background biases that pose-based pipelines (e.g., MediaPipe) partly mitigate; the absence of an open dataset release limits independent reproduction; and pixel models are notoriously sensitive to cosmetic confounders (clothing, lighting), which the authors only partially probe.

For PD-glove, this study is a useful contrast case: my Part II design uses MediaPipe-derived landmarks rather than raw pixels precisely to avoid the confounders this paper sidesteps with scale. It also defines a credible "video-only" performance ceiling that my IMU-plus-video architecture should aim to exceed by virtue of having direct kinematic signal.

### 7. Evers et al. (2025)

Evers, L. J. W., Raykov, Y. P., Heskes, T. M., Krijthe, J. H., Bloem, B. R., & Little, M. A. (2025). Passive monitoring of Parkinson tremor in daily life: A prototypical network approach. *Sensors, 25*(2), Article 366. https://doi.org/10.3390/s25020366

Evers and colleagues develop a prototypical radial-basis-function network that encodes tremor not as a single binary class but as a mixture over seven clinically defined sub-prototypes (different muscle-involvement patterns) and seven daily-activity non-tremor prototypes. The model is trained on wrist accelerometer data from 8 PD tremor patients, 16 PD non-tremor patients, and 24 controls, using leave-one-subject-out validation. It reaches 66% sensitivity and 95% specificity, and the authors show it is more robust to phenotype variation and activity confounders than standard classifier baselines, with strong sample efficiency on the low-label regime that defines free-living PD studies.

The paper accomplishes a narrower but important goal: it demonstrates that clinical expertise injected through prototype selection can substitute for large labeled corpora. The accuracy numbers are not exceptional, but the model degrades gracefully across phenotypes, which is the more clinically relevant property.

For PD-glove, this is a strong methodological alternative to standard end-to-end training given my small labeled dataset. It also explicitly addresses the failure mode that worries me most — a model that achieves high overall accuracy but collapses on under-represented tremor phenotypes — by surfacing the phenotype mixture as part of the prediction. I'll consider it as a fallback architecture if Transformer fine-tuning underperforms on my n=2-subject validation cohort.

### 8. Güney et al. (2022)

Güney, G., Jansen, T. S., Dill, S., Schulz, J. B., Dafotakis, M., Hoog Antink, C., & Braczynski, A. K. (2022). Video-based hand movement analysis of Parkinson patients before and after medication using high-frame-rate videos and MediaPipe. *Sensors, 22*(20), Article 7992. https://doi.org/10.3390/s22207992

The authors record high-frame-rate (240 fps) video of 11 PD patients before and after standard oral medication and extract 21 hand landmarks per frame using MediaPipe. Tremor frequency and amplitude derived from MediaPipe traces are validated against a simultaneously recorded accelerometer (Cohen's kappa not central; the comparison is reported as strong agreement). They report a mean absolute error of 0.229 Hz in tremor frequency, a drop in mean tremor frequency from 2.01 Hz to 1.53 Hz post-medication, and a halving of mean amplitude (8.17 → 4.03 a.u.) — the latter two findings recovering the expected pharmacological signature.

The paper accomplishes its goal of validating MediaPipe as a credible substitute for accelerometers under controlled laboratory conditions. The principal limitation is the same one acknowledged by the authors: MediaPipe degrades during kinetic-tremor tasks that occlude or distort the hand silhouette, so the validation is strongest on rest and postural tremor.

For PD-glove, this paper is the strongest direct evidence that MediaPipe Hand Landmarker (the framework specified in my Deliverable 3 compliance module) can produce kinematically valid tremor signals. It also implicitly justifies the design choice to use MediaPipe only for post-session compliance gating rather than as a primary signal source — the kinetic-tremor failure mode is exactly what makes real-time camera gating in the live IMU pipeline a poor idea.

### 9. Hemmerling et al. (2026)

Hemmerling, D., Dudek, M., Krzywdziak, J., Żbik, M., Szecowka, W., Daniol, M., Wodzinski, M., Rudzinska-Bar, M., & Wojcik-Pedziwiatr, M. (2026). GRU-based deep multimodal fusion of speech and head-IMU signals in mixed reality for Parkinson's disease detection. *Sensors, 26*(1), Article 269. https://doi.org/10.3390/s26010269

Hemmerling and colleagues built DiagNeuro, a Microsoft HoloLens 2 system that synchronously captures acoustic features and head-mounted IMU signals from 165 participants (72 PD, 93 HC) performing standardized mixed-reality speech tasks. They compare three fusion architectures on top of a bidirectional GRU temporal backbone — early concatenation, cross-attention, and gated early fusion — and report AUC ≈ 0.865 for speech-only, lifting to AUC ≈ 0.875 for gated early fusion. Gains are concentrated in tasks that engage postural control, suggesting head kinematics function as a conditional discriminator rather than an independent biomarker.

The paper meets its goal of producing a credible multimodal PD-detection prototype with a non-trivial subject count for this design space. Limitations are typical of multimodal sensor-fusion work: the marginal gain from adding the IMU is small (~0.01 AUC), the platform is expensive and not consumer-deployable, and the binary PD/HC task is easier than within-cohort severity prediction.

For PD-glove, this paper is the closest analogue to the fusion question I will face if Part III extends to voice or face biomarkers. More immediately, the gated-early-fusion architecture is a candidate for combining flex-sensor (bradykinesia) and IMU (tremor) channels in a single decision head once flex-sensor integration completes on the Pi 5.

### 10. Králik & Šuppa (2021)

Králik, M., & Šuppa, M. (2021). WaveGlove: Transformer-based hand gesture recognition using multiple inertial sensors. In *Proceedings of the 2021 29th European Signal Processing Conference (EUSIPCO)* (pp. 1576–1580). IEEE. https://arxiv.org/abs/2105.01753

WaveGlove is the methodological cornerstone of the PD-glove project. The authors built a custom five-finger-IMU glove and trained a Transformer encoder on patch-embedded multi-channel inertial signals, comparing against classical and CNN baselines on two custom datasets (>11,000 samples) plus nine public hand-gesture benchmarks. The Transformer reaches high accuracy across complex multi-finger gestures, and an explicit ablation shows accuracy rising sharply as the number of sensors increases from one to three, then plateauing — quantitative evidence that multi-finger spatial information is decisive for fine-grained hand-motion recognition.

The paper accomplishes its goal of establishing that Transformers are competitive on multi-IMU inertial time-series and that multi-sensor placement materially outperforms single-sensor configurations. The principal limitation for tremor-specific work is that WaveGlove targets gesture recognition, not pathological-motion severity rating; the gestures are voluntary and well-separated, which is an easier classification surface than ordinal MDS-UPDRS scoring.

For PD-glove, this paper is foundational on two counts. (1) It is cited in my own AIIoT 2026 paper as the design rationale for per-finger IMU placement, and the multi-sensor ablation provides quantitative justification for choosing five MPU6050s over a single wrist sensor. (2) It defines the Transformer-encoder architecture I will adapt for MDS-UPDRS prediction in Deliverable 2, with the substitution of an ordinal-regression head and uncertainty estimation for the original classification head.

### 11. Liu et al. (2023)

Liu, W., Lin, X., Chen, X., Wang, Q., Wang, X., Yang, B., Cai, N., Chen, R., Chen, G., & Lin, Y. (2023). Vision-based estimation of MDS-UPDRS scores for quantifying Parkinson's disease tremor severity. *Medical Image Analysis, 85*, Article 102754. https://doi.org/10.1016/j.media.2023.102754

Liu and colleagues propose the Global Temporal-difference Shift Network (GTSN), a ResNet-based architecture augmented with a temporal-difference module that stacks inter-frame differences onto optical flow. The pipeline is fed with Eulerian-Video-Magnification-preprocessed clips, which amplify subtle tremor motion before classification. Across four body regions and four MDS-UPDRS severity classes the model reaches 90.6% accuracy on rest hand tremor, 89.0% on jaw, 85.9% on leg, and 84.9% on postural tremor — the strongest published video-based MDS-UPDRS hand-tremor result at submission.

The paper accomplishes its goal: it shows that a vision-only system can recover MDS-UPDRS class labels with accuracy near the inter-rater agreement floor for human clinicians. The limitations are that the dataset is single-center and not publicly released, the temporal-difference module is brittle to camera shake, and accuracy is reported as class accuracy rather than calibration-aware metrics, which complicates direct comparison with regression-style severity estimators.

For PD-glove, this paper defines the video-based MDS-UPDRS performance ceiling I should aim to clear with an IMU-plus-video architecture. It also reinforces the choice to use MediaPipe-derived structured features rather than raw pixels for my compliance module — at lower compute cost, with better cross-site transfer.

### 12. Muhammad et al. (2026)

Muhammad, J., Ghergherehchi, M., Ali, S., Song, H. S., & Rahim, N. (2026). Trustworthy AI for medical decisions: Adversarially robust and fair machine learning prediction for Parkinson's disease. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0342062

The authors evaluate two interpretable PD classifiers (Random Forest and Decision Tree) trained on the Parkinson's Progression Markers Initiative cohort (n=1,084, spanning age, sex, and race) and submit them to two adversarial regimes: label-flipping leakage and data-poisoning. Without defenses, decision-tree accuracy drops by more than 10% and random-forest accuracy by more than 20% under attack, with disparities concentrated in minority demographic strata. Fairness-aware preprocessing reduces Statistical Parity Difference and Equal Opportunity Difference at the cost of modest absolute-accuracy decline.

The paper accomplishes its goal of demonstrating that medical-AI fairness and adversarial robustness are tightly coupled — perturbations that look like noise on aggregate metrics surface as bias amplification on subgroup metrics. Limitations: PPMI itself is a relatively homogeneous research cohort (US/EU specialist centers); the classifiers tested are interpretable but not state-of-the-art; and adversarial robustness in clinical settings is dominated by distribution shift, not the synthetic attacks tested.

For PD-glove, this paper is directly relevant to the Deliverable 3 fairness audit (Week 11). PPMI is one of my training corpora, so the fairness-aware preprocessing recipes (resampling, reweighting) apply directly. The broader takeaway — report subgroup metrics alongside aggregates — should be a non-negotiable in my final evaluation protocol.

### 13. Nanayakkara & Chan (2025)

Nanayakkara, G. R. R., & Chan, P. Y. (2025). Subclinical tremor differentiation using long short-term memory networks. *Physical and Engineering Sciences in Medicine*. https://doi.org/10.1007/s13246-025-01526-0

Nanayakkara and Chan train an LSTM on short-time Fourier transform features of inertial-sensor recordings from 51 PD patients, 15 essential-tremor (ET) patients, and 58 healthy controls, focusing specifically on subclinical (low-amplitude) tremor that conventional detectors miss. The binary PD-vs-ET classifier reaches 95% accuracy and the three-class model reaches 93% — a 30–50% absolute improvement over a ConvLSTM benchmark on the same low-amplitude data. The architecture choice is deliberate: STFT features force the network to attend to frequency content even when amplitudes are too small for time-domain pattern matching.

The paper accomplishes its goal of moving the differential-diagnosis problem out of the easy-amplitude regime and into the clinically harder subclinical band. Limitations: cohort sizes per class are imbalanced (ET is under-represented), the dataset is single-center, and LSTM is increasingly being displaced by attention-based models — the gains over ConvLSTM may shrink against Transformer baselines.

For PD-glove, the subclinical-tremor regime is precisely where my 4–6 Hz Butterworth + FFT DSP pipeline is weakest, because frequency-domain peaks become indistinct at low amplitudes. The STFT + LSTM recipe here is a plausible pre-processing front-end for my Transformer model on early-stage PD subjects, where amplitude separation between rest and tremor is small.

### 14. Paneru (2025)

Paneru, B. (2025). Prediction of freezing of gait in Parkinson's disease using explainable AI and federated deep learning for wearable sensors. *arXiv*. https://arxiv.org/abs/2507.01068

Paneru proposes a federated learning framework for FoG prediction over wearable IMU data, where local models (CatBoost, XGBoost, ExtraTrees, and a Conv1D+LSTM hybrid) train on individual devices and only model updates — not raw data — leave the client. A stacking ensemble reaches nearly 99% classification accuracy on held-out FoG events, and SHAP analysis isolates short-window temporal features as the dominant predictors. The federated configuration is positioned as a privacy-by-design alternative to centralized PD-monitoring deployments.

The paper accomplishes the structural goal of demonstrating end-to-end federated PD detection with explainability, but the very high reported accuracy warrants caution — single-author preprint, dataset details and validation protocol are thin, and FoG classification typically benefits from subject-level leakage if splits are not strictly per-subject. SHAP on temporal features is useful but not a substitute for an external test cohort.

For PD-glove, the relevance is conceptual rather than methodological. My architecture is single-device-on-Pi-5 with MQTT-published derived scores, which is already privacy-preserving without federation. But if Part III scales to a multi-subject deployment, federated training of the Transformer head — with the Pi 5 as the local client — is the natural extension, and this paper supplies the simplest reference architecture.

### 15. Papadopoulos et al. (2020)

Papadopoulos, A., Kyritsis, K., Klingelhoefer, L., Bostanjopoulou, S., Chaudhuri, K. R., & Delopoulos, A. (2020). Detecting Parkinsonian tremor from IMU data collected in-the-wild using deep multiple-instance learning. *IEEE Journal of Biomedical and Health Informatics, 24*(9), 2559–2569. https://doi.org/10.1109/JBHI.2019.2961748

This work formulates in-the-wild tremor detection as a Multiple Instance Learning problem: each subject is represented as an unordered "bag" of smartphone IMU signal segments paired with a single expert-provided session-level label. A deep feature extractor processes each segment, and a learnable attention pooling layer selects the most informative instances during end-to-end training, sidestepping the need for clinician-annotated minute-by-minute tremor labels. The model is validated on 45 subjects with smartphone accelerometer data collected entirely in real-world conditions and outperforms instance-level supervised baselines.

The paper accomplishes its central methodological claim — that MIL can extract a usable tremor signal from noisy, unconstrained smartphone recordings using only weak (session-level) labels. The accuracy reporting is not as strong as that in laboratory studies, which is honest given the setting; the main limitation is that the smartphone is held only intermittently, biasing the dataset toward stationary tremor episodes.

For PD-glove, this paper provides a direct template for handling label scarcity in my own continuous-wear deployment: rather than asking subjects to self-annotate, I can capture session-level MDS-UPDRS labels and let MIL attention extract the relevant time windows. The smartphone-versus-glove form factor difference is important — the paper's noise profile is much harsher than mine — but the labeling-economics argument transfers.

### 16. Paucar-Escalante et al. (2025)

Paucar-Escalante, J., Alves da Silva, M., Sanches, B. D. L., Soriano-Vargas, A., Moriyama, L. S., & Colombini, E. L. (2025). Machine learning strategies for Parkinson tremor classification using wearable sensor data. *arXiv*. https://arxiv.org/abs/2501.18671

This is a current-state-of-the-art survey of ML methods for wearable PD tremor classification, organized along three axes: data acquisition (sensor type, placement, sampling rate), signal processing (time-domain, frequency-domain, time-frequency representations), and modeling (SVM, RF, XGBoost on the classical side; CNN, LSTM, Transformer on the deep side). The authors curate explainability techniques and identify open challenges — small subject counts, weak external validation, inconsistent label conventions, and the absence of standardized benchmark splits.

The survey accomplishes its goal of mapping the landscape and is one of the few recent reviews to explicitly call out methodological inconsistencies that block cross-study comparison. Its limitations are inherent to survey-format work: no original experiments, partial coverage of self-supervised and foundation-model approaches (which were emerging during the writing window), and limited engagement with deployment concerns like quantization or latency.

For PD-glove, this paper is the most useful single citation for grounding the Research Gap section of this very review and for framing my Part II baseline classifier choices in Deliverable 1 (SVM, RF, 1D-CNN — exactly the canonical baselines the survey identifies). It also explicitly lists the methodological pitfalls — subject-level leakage, weak external validation — that my own protocol is designed to avoid.

### 17. Rodriguez et al. (2024)

Rodriguez, F., Krauss, P., Kluckert, J., Ryser, F., Stieglitz, L., Baumann, C., Gassert, R., Imbach, L., & Bichsel, O. (2024). Continuous and unconstrained tremor monitoring in Parkinson's disease using supervised machine learning and wearable sensors. *Parkinson's Disease, 2024*, Article 5787563. https://doi.org/10.1155/2024/5787563

This ETH-Zurich/University-Hospital-Zurich collaboration trains a Support Vector Machine on a 67-hour database of IMU recordings from 24 PD patients at four extremities (about three hours per patient) during free-living activities, with manual minute-level tremor scoring performed by clinicians via a custom mobile app. The classifier reaches 0.90 sensitivity and 0.88 overall accuracy on a held-out portion of the dataset, and the authors demonstrate that class-rebalancing techniques materially improve performance on the typically imbalanced "tremor vs no-tremor" split.

The paper accomplishes its stated goal of producing a free-living tremor monitor that is trainable from a modestly sized, manually labeled corpus. Limitations: SVM is well below current state-of-the-art for time-series classification, the per-subject calibration burden is high, and 24 subjects is small for cross-patient generalization claims. But the manually labeled, clinician-supervised free-living dataset is rare and load-bearing.

For PD-glove, this study is the closest free-living analogue to my own protocol scale (single-digit subjects, in-clinic plus at-home recording). It also provides a concrete recommendation — class-rebalancing matters more than algorithm choice when the dataset is small and imbalanced — that I will apply directly in Deliverable 1.

### 18. Timmermans et al. (2025)

Timmermans, N. A., Terranova, R., Soriano, D. C., Cagnan, H., Raykov, Y. P., Bucur, I. G., Bloem, B. R., Helmich, R. C., & Evers, L. J. W. (2025). A generalizable and open-source algorithm for real-life monitoring of tremor in Parkinson's disease. *npj Parkinson's Disease, 11*, Article 205. https://doi.org/10.1038/s41531-025-01056-2

Timmermans and colleagues build a logistic-regression classifier on cepstral coefficients extracted from wrist gyroscope data and pair it with a two-dataset training strategy: a small, extensively video-labeled at-home dataset (24 PD + 24 controls) for supervised training and a large unsupervised cohort (517 PD + 50 controls) collected on different hardware for external validation. The algorithm achieves 0.61 (±0.20) sensitivity and 0.97 (±0.05) specificity on real-life recordings and generalizes across two distinct wearable devices. The code is released as the open-source Paradigma toolbox.

The paper accomplishes its goal of producing a deployment-ready tremor monitor that survives cross-device evaluation — a notoriously brittle property — and explicitly documents its failure modes. Limitations: sensitivity is modest, reflecting the difficulty of free-living tremor detection; the logistic-regression backbone is more interpretable than a deep model would be but likely under-fits richer tremor phenotypes; and the external validation cohort lacks ground-truth labels, so specificity numbers there should be read as approximate.

For PD-glove, Paradigma is the single most useful comparator for my own real-world deployment. The cross-device generalization result is encouraging — my Pi-5 + MPU6050 pipeline shares this design constraint — and the open-source code means I can validate my own Butterworth/FFT DSP pipeline against an independent reference implementation in Week 1 (May 19–25).

### 19. Tumpa et al. (2025)

Tumpa, Z. N., Zawad, M. R. S., Sollis, L., Parab, S., Chen, I. Y., & Washington, P. (2025). Quantifying device type and handedness biases in a remote Parkinson's disease AI-powered assessment. *npj Digital Medicine, 8*, Article 550. https://doi.org/10.1038/s41746-025-01934-2

Tumpa and colleagues evaluate a web-based remote PD assessment that uses mouse-tracing and keyboard-pressing tasks on 251 participants (99 PD, 152 non-PD) and audit it across demographic, device, and handedness strata. They find no statistically significant F1 disparities by sex or race (after race resampling), but quantify a substantial unexpected bias: Windows users and left-handed individuals are 38–70% less likely to receive a PD-positive diagnosis than Mac users and right-handed individuals respectively. The paper traces these gaps to platform-specific input behavior and dataset-level handedness imbalance.

The paper accomplishes its goal of exposing a class of fairness failures that the standard demographic-stratification audit misses entirely. Limitations: the cohort is small and self-selected, the input modalities (mouse/keyboard) are far from the wearable form factor most of this literature uses, and the headline disparities reflect specific UI choices that may not generalize.

For PD-glove, this paper crystallizes a fairness category I had not previously planned to audit — hardware-specific bias. My Pi 5 + MPU6050 pipeline is a single fixed hardware stack, which protects against device-type drift, but handedness asymmetry is real (my own validation data is from right-dominant subjects). I will explicitly add a handedness audit to Deliverable 3.

### 20. Xing et al. (2022)

Xing, X., Luo, N., Li, S., Zhou, L., Song, C., & Liu, J. (2022). Identification and classification of Parkinsonian and essential tremors for diagnosis using machine learning algorithms. *Frontiers in Neuroscience, 16*, Article 701632. https://doi.org/10.3389/fnins.2022.701632

Xing and colleagues compare seven machine learning classifiers — Random Forest, XGBoost, SVM, logistic regression, ridge classification, BP neural network, and a CNN — on a combined tremor-acceleration plus surface-EMG dataset from 398 patients held in four upper-limb postures. Ensemble methods dominate: Random Forest and XGBoost both reach accuracy above 0.84 and AUC above 0.90 for differential PD-vs-ET classification. Feature-importance analysis isolates the dominant frequency and average amplitude of flexor-muscle signals, plus specific arm postures, as the most discriminating inputs.

The paper accomplishes its goal of establishing a strong classical-ML baseline for tremor differential diagnosis, and the cohort is unusually large by tremor-classification standards. Limitations: the dataset is single-center; the deep-learning entry (CNN) underperforms the gradient-boosted baselines, which is more a comment on cohort size and feature engineering than on deep learning per se; and the assessment is in-clinic and posture-prompted, which is easier than continuous free-living recording.

For PD-glove, this is the clearest evidence that classical ensemble methods remain competitive on small-to-moderate clinical datasets — directly supporting my Deliverable 1 plan to benchmark SVM, Random Forest, and 1D-CNN before training a Transformer. The posture-specific feature importance also informs my exercise protocol: the postures Xing finds most discriminative are exactly the ones MDS-UPDRS Part III prescribes, so my structured 3-task assessment captures the right kinematic regimes.

---

## Identified Research Gap

Synthesizing across these twenty sources, the machine-learning literature on hand tremor has matured along several dimensions but left a coherent, exploitable gap that PD-glove is positioned to fill.

**Per-finger spatial resolution is still rare.** With the single exception of Králik & Šuppa (2021), every IMU-based study in this review uses either a wrist-worn device (Bachlin, Atri, Rodriguez, Timmermans, Evers, Nanayakkara, Papadopoulos) or a smartphone (Bot, Papadopoulos), and every video-based study (Güney, Liu, Duque-Quiceno) treats the hand as a single articulated object. WaveGlove demonstrates that multi-IMU placement materially raises ceiling accuracy on fine-grained hand-motion tasks — and yet no published PD study has carried that finding into MDS-UPDRS-aligned tremor scoring. The pill-rolling thumb-index interaction that defines Parkinsonian rest tremor is spatially specific in a way that wrist sensors and pixel-based video both blur. A five-finger IMU glove sits in an under-occupied region of the design space.

**MDS-UPDRS-aligned ordinal severity is under-served relative to binary detection.** The dominant clinical task in this corpus is binary tremor / no-tremor classification (Papadopoulos, Atri, Rodriguez, Timmermans, Evers, Paneru); only three papers explicitly target MDS-UPDRS severity (Liu, Duque-Quiceno) or differential diagnosis (Xing, Nanayakkara). The transformation from binary detection to ordinal severity prediction is non-trivial: it requires calibrated probability outputs, ordinal loss functions, and uncertainty estimates that virtually none of the reviewed work provides. Liu's vision-based MDS-UPDRS classifier and Duque-Quiceno's pixel-based severity model establish video baselines, but no wearable-only system covered in this review delivers full 0–4 MDS-UPDRS scores with calibrated uncertainty.

**Edge-deployable, quantized Transformer inference for tremor is essentially missing.** Across twenty papers, deployment is discussed but rarely instrumented: Atri's daily-monitoring pipeline runs in the cloud, Timmermans releases open-source code without quantization benchmarks, and Paneru's federated framework reports model accuracy but not inference latency. None of the reviewed work publishes INT8 TFLite latency numbers on edge-class hardware for a Transformer encoder operating on multi-channel IMU input. This is precisely the deployment regime my Part II pipeline targets (TFLite INT8 on the Pi 5, with sub-200 ms latency as the operational requirement).

**Privacy-by-design is under-addressed despite being clinically central.** Paneru (2025) provides the only federated-learning entry in this review, and Tumpa (2025) raises remote-assessment fairness, but no paper combines on-device inference with raw-data-never-leaves-device guarantees. The dominant deployment pattern across these twenty studies is upload-and-process: raw IMU traces, raw video, or raw audio leave the patient device. PD-glove's MQTT-only-derived-scores architecture, with all DSP and Transformer inference local to the Pi 5, materially closes that gap.

**Fairness evidence remains thin and primarily framed around demographics.** Only Tumpa (2025) and Muhammad (2026) provide formal fairness audits, and both surface bias categories — hardware platform, handedness, adversarial robustness — that the canonical age/sex/race stratification misses. PPMI itself, used by Muhammad and central to my own Part II pipeline, is a relatively homogeneous specialist-recruited cohort, so demographic generalization claims drawn from PPMI-only training need explicit external validation. None of the reviewed work pairs MDS-UPDRS severity prediction with both demographic and hardware-stratified fairness reporting.

**PD-glove's contribution against this gap.** The Part II program in this course makes four claims that, taken together, are not jointly addressed by any single paper in this review: (1) five-finger IMU placement to capture pill-rolling tremor's spatial signature, drawing on the WaveGlove design rationale but moving the methodology from gesture recognition to clinical scoring; (2) a Transformer encoder predicting calibrated, MDS-UPDRS-aligned 0–4 severity with uncertainty intervals, addressing the binary-vs-ordinal gap; (3) INT8 TFLite deployment on a Raspberry Pi 5 edge device with documented inference latency, addressing the missing-deployment-numbers gap; and (4) MQTT publication of derived scores only, with raw IMU data never leaving the device, addressing the privacy-by-design gap. A Deliverable-3 fairness audit across PPMI demographic splits plus handedness — the latter motivated directly by Tumpa (2025) — closes the audit loop. Each individual element of this stack is anticipated somewhere in the prior literature; their integration into a single reproducible, edge-deployable pipeline is not.
