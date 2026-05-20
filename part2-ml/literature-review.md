# Literature Review: Machine Learning for Hand Tremor Analysis

**Author:** An Nguyen
**Course:** CS 8674 Part II — Intelligent IoT Frameworks for Chronic Disease Management (Summer 2026)
**Instructor:** Sarita Singh
**Due:** May 31, 2026

This review surveys twenty peer-reviewed and high-quality preprint sources covering the machine learning literature on hand tremor analysis, with deliberate breadth across sensing modalities (wrist and finger IMUs, smartphones, video, multimodal), method families (classical, 1D-CNN, CNN-LSTM, Transformer, multiple-instance learning, prototypical networks, self-supervised foundation models, federated learning), clinical tasks (tremor detection, severity rating, PD-versus-essential-tremor differentiation, freezing of gait, bradykinesia, gait severity), and deployment concerns (edge inference, privacy, fairness). The selection prioritizes work published 2021–2026 (seventeen of twenty entries), with three foundational papers (2010–2020) retained to anchor the datasets and methodological starting points the field continues to extend. Sources are sorted alphabetically by first-author surname (APA 7th edition). A Research Gap section follows the bibliography and synthesizes the findings against the Sensing-to-Decision framework developed in the PD-glove program.

---

## Annotated Bibliography

### 1. Adeli et al. (2025)

Adeli, V., Klabucar, I., Rajabi, J., Filtjens, B., Mehraban, S., Wang, D., Seo, H., Hoang, T.-H., Do, M. N., Muller, C., Oliveira, C., Coelho, D. B., Ginis, P., Gilat, M., Nieuwboer, A., Spildooren, J., McKay, L., Kwon, H., Clifford, G., … Taati, B. (2025). CARE-PD: A multi-site anonymized clinical dataset for Parkinson's disease gait assessment. *arXiv* (NeurIPS 2025 Datasets & Benchmarks Track). https://arxiv.org/abs/2510.04312

Adeli et al. introduce CARE-PD, the largest publicly available archive of anonymized 3D mesh gait recordings for Parkinson's disease, aggregating nine cohorts across eight clinical centers. RGB-video and motion-capture sources are harmonized into SMPL body meshes via a unified preprocessing pipeline, and the release supports two benchmark tracks: supervised UPDRS gait-score prediction and unsupervised motion pretext tasks including 2D-to-3D keypoint lifting and full-body reconstruction. Seven state-of-the-art motion encoders are evaluated — among them MotionBERT, MotionAGFormer, PoseFormerV2, and POTR. Learned motion encoders substantially outperform classical handcrafted gait features, but MotionBERT exhibits strong site-shift sensitivity, peaking at 0.49 on PD-GaM and degrading to 0.25 on T-SDU-PD.

The work achieves its stated objective of providing the first multi-site 3D-mesh PD gait resource with a reproducible cross-site evaluation protocol. The principal limitation is scope: gait severity, while clinically meaningful, covers only one slice of MDS-UPDRS Part III, and the observed site-shift variance indicates that current motion encoders are not yet domain-invariant.

For the PD-glove program, CARE-PD is directly load-bearing for the Part II auxiliary gait branch described in the syllabus (Weeks 7–8). The evaluated MotionBERT and POTR encoders are candidate backbones for the phone-video gait inference module that pairs with the IMU tremor model, and the reported site-shift behavior motivates fairness-aware splits in the present evaluation protocol.

### 2. Atri et al. (2022)

Atri, R., Urban, K., Marebwa, B., Simuni, T., Tanner, C., Siderowf, A., Frasier, M., Haas, M., & Lancashire, L. (2022). Deep learning for daily monitoring of Parkinson's disease outside the clinic using wearable sensors. *Sensors, 22*(18), Article 6831. https://doi.org/10.3390/s22186831

Atri et al. develop an end-to-end pipeline that segments continuous Verily Study Watch recordings (worn up to 23 hours per day) into "walk-like events" via human-activity-recognition heuristics, then classifies the segments with a 1D-CNN. The system was trained on seven PD patients and four healthy controls; it achieves approximately 90% accuracy on individual 5-second walk events and 100% accuracy when daily predictions are aggregated by majority vote, with stable behavior across three months of follow-up. The architecture establishes a now-canonical pattern: activity-gated 1D-CNN over wrist accelerometer and gyroscope segments.

The study accomplishes its goal of demonstrating that free-living monitoring is feasible on unconstrained wearable data. The eleven-subject cohort is small relative to the strength of the headline accuracy claim, and the 100% per-day result is best interpreted as showing how aggregation absorbs per-segment uncertainty rather than as a generalizable performance bound. The cohort is also too small to support fairness evaluation.

The work is one of the closest methodological analogues to the baseline 1D-CNN classifiers planned for Deliverable 1 (June 16). The activity-gating principle — running the tremor model only when the wearer is in a relevant pose — directly parallels the MediaPipe Hand Landmarker compliance module in the present framework, which serves an analogous gating role on phone video.

### 3. Bachlin et al. (2010)

Bachlin, M., Plotnik, M., Roggen, D., Maidan, I., Hausdorff, J. M., Giladi, N., & Tröster, G. (2010). Wearable assistant for Parkinson's disease patients with the freezing of gait symptom. *IEEE Transactions on Information Technology in Biomedicine, 14*(2), 436–446. https://doi.org/10.1109/TITB.2009.2036165

Bachlin et al. introduce the Daphnet Freezing of Gait dataset and an online detection algorithm that triggers an auditory rhythmic cue when a freezing episode is detected. Three MEMS triaxial accelerometers (shank, thigh, lower back) are sampled at 64 Hz, and the freeze-index feature is computed as the power ratio between a 3–8 Hz "freeze band" and a 0.5–3 Hz "locomotion band," with subject-tailored thresholding. Across ten advanced-PD patients, the system achieves approximately 73% sensitivity and 82% specificity in real time on a body-worn computing platform.

The paper establishes both a public benchmark and a credible end-to-end wearable intervention. By contemporary standards the detector is simple — threshold on a hand-engineered ratio — and per-subject calibration is required; the cohort is small and homogeneous. These constraints, however, are precisely what motivated the deep-learning successors cited later in this review.

Daphnet is the syllabus-mandated training corpus for the Part II freezing-of-gait auxiliary model (Weeks 1–4). The freeze-band and locomotion-band framing also supplies a sanity-check baseline for any Transformer or CNN trained in the present program: a learned model that fails to outperform a threshold-on-power-ratio classifier on its native dataset would indicate a defect in either the architecture or the training pipeline.

### 4. Bot et al. (2016)

Bot, B. M., Suver, C., Chaibub Neto, E., Kellen, M., Klein, A., Bare, C., Doerr, M., Pratap, A., Wilbanks, J., Dorsey, E. R., Friend, S. H., & Trister, A. D. (2016). The mPower study, Parkinson disease mobile data collected using ResearchKit. *Scientific Data, 3*, Article 160011. https://doi.org/10.1038/sdata.2016.11

Bot et al. describe mPower, the foundational smartphone-based PD observational study, conducted entirely through an iPhone application and released as a public dataset on Synapse. Participants complete demographic, MDS-UPDRS, and PDQ-8 surveys plus four sensor-based activities — memory, finger tapping, voice, and walking — yielding a longitudinal corpus from over 9,000 enrolled participants in the first six months. The paper documents the consent flow, data schema, and rationale for releasing raw sensor traces under a controlled-access model rather than only derived summaries.

The release accomplishes its goal of providing the field with a large, demographically diverse, real-world PD-symptom dataset, and remains one of the most cited resources in digital-biomarker research. Limitations include self-selection bias (iPhone users who heard about the study), inconsistent task adherence, weak diagnosis confirmation, and the documented difficulty of extracting clean MDS-UPDRS-aligned labels from voluntary at-home recordings.

mPower is the syllabus-listed auxiliary corpus for the Transformer encoder's gait branch (walking task) and an informal pre-training source for the tremor branch (finger tapping). The study also functions as a cautionary template: the present protocol is designed to avoid the same label-quality and self-selection traps, which is why the Pi 5 deployment uses structured assessment tasks under app-controlled timestamps rather than free-form data capture.

### 5. Das et al. (2024)

Das, A. M., Tang, C. I., Kawsar, F., & Malekzadeh, M. (2024). PRIMUS: Pretraining IMU encoders with multimodal self-supervision. *arXiv* (NeurIPS 2024 TSALM Workshop; subsequently ICASSP 2025). https://arxiv.org/abs/2411.15127

Das et al. propose PRIMUS, a pretraining objective for IMU encoders that combines three losses: a self-supervised augmentation-invariance term, a multimodal alignment term that pulls IMU embeddings toward co-occurring video and text features, and a nearest-neighbor contrastive term in IMU space. The recipe targets the chronic label scarcity in human-motion sensing. Across in-domain and out-of-domain evaluations, PRIMUS improves downstream test accuracy by up to 15% over strong self-supervised baselines when fewer than 500 labeled samples per class are available; the implementation is open-sourced via Nokia Bell Labs' pretrained-imu-encoders repository.

The work accomplishes its stated objective of demonstrating a reusable, transferable IMU foundation-model recipe, and the ablations isolate each loss term. The principal caveat is that downstream benchmarks target general human-activity recognition; the paper does not evaluate on PD-specific or clinical-rating tasks, leaving the transfer magnitude to MDS-UPDRS scoring as an open question.

PRIMUS provides the most concrete template available for pretraining the per-finger IMU Transformer encoder on a generic motion corpus before fine-tuning on the multi-subject validation dataset (n=9 sessions, 72 per-finger feature vectors). End-to-end Transformer training typically demands substantially more labeled data than the current cohort supplies, and the PRIMUS recipe represents the most plausible path to a clinically useful model from this modest labeled base.

### 6. Duque-Quiceno et al. (2024)

Duque-Quiceno, F., Sarapata, G., Dushin, Y., Allen, M., & O'Keeffe, J. (2024). Deep learning for objective estimation of Parkinsonian tremor severity. *arXiv*. https://arxiv.org/abs/2409.02011

Duque-Quiceno et al. train a pixel-based deep learning model on 2,742 video assessments collected from five movement-disorder centers across two continents to predict MDS-UPDRS Part III tremor sub-scores directly from raw RGB frames. The model is reported to show robust concordance with clinical evaluations, generalize across distinct tremor types (rest, postural), and recover the expected dose-response signal for levodopa and deep brain stimulation in held-out longitudinal sub-cohorts. The work positions video as a low-friction alternative to wearables, suited for telemedicine and remote enrollment.

The study achieves its goal of demonstrating a video-only severity estimator at clinically meaningful scale. Three limitations qualify the result: the pipeline operates on pixel-level features without explicit pose extraction, inheriting camera-setup and background biases that pose-based methods partly mitigate; the dataset is not released, limiting independent reproduction; and pixel models are known to be sensitive to cosmetic confounders such as clothing and lighting, which the authors only partially probe.

The study is a useful contrast case for the present framework. The Part II design uses MediaPipe-derived landmarks rather than raw pixels precisely to avoid the confounders this work sidesteps with scale, and the reported accuracy establishes a credible video-only performance ceiling that an IMU-plus-video architecture should be positioned to exceed.

### 7. Evers et al. (2025)

Evers, L. J. W., Raykov, Y. P., Heskes, T. M., Krijthe, J. H., Bloem, B. R., & Little, M. A. (2025). Passive monitoring of Parkinson tremor in daily life: A prototypical network approach. *Sensors, 25*(2), Article 366. https://doi.org/10.3390/s25020366

Evers et al. develop a prototypical radial-basis-function network that encodes tremor not as a single binary class but as a mixture over seven clinically defined sub-prototypes (different muscle-involvement patterns) and seven daily-activity non-tremor prototypes. The model is trained on wrist accelerometer data from 8 PD tremor patients, 16 PD non-tremor patients, and 24 controls, with leave-one-subject-out validation. Reported performance is 66% sensitivity and 95% specificity, and the model is shown to be more robust to phenotype variation and activity confounders than standard classifier baselines, with strong sample efficiency in the low-label regime that defines free-living PD studies.

The paper accomplishes a narrow but important objective: it demonstrates that clinical expertise injected through prototype selection can substitute for large labeled corpora. The headline accuracy is modest, but the model degrades gracefully across phenotypes — a more clinically relevant property than aggregate accuracy.

For the present framework, this work represents a credible methodological alternative to standard end-to-end training given the small labeled dataset on hand. It also directly addresses the failure mode that warrants the closest attention — a model achieving high overall accuracy while collapsing on under-represented tremor phenotypes — by surfacing the phenotype mixture as part of the prediction. The architecture is a viable fallback if Transformer fine-tuning underperforms on the n=2-subject validation cohort.

### 8. Güney et al. (2022)

Güney, G., Jansen, T. S., Dill, S., Schulz, J. B., Dafotakis, M., Hoog Antink, C., & Braczynski, A. K. (2022). Video-based hand movement analysis of Parkinson patients before and after medication using high-frame-rate videos and MediaPipe. *Sensors, 22*(20), Article 7992. https://doi.org/10.3390/s22207992

Güney et al. record high-frame-rate (240 fps) video of 11 PD patients before and after standard oral medication and extract 21 hand landmarks per frame using MediaPipe. Tremor frequency and amplitude derived from MediaPipe traces are validated against a simultaneously recorded accelerometer. The video pipeline recovers tremor frequencies with a mean absolute error of 0.229 Hz, a post-medication frequency drop from 2.01 Hz to 1.53 Hz, and a halving of mean amplitude (8.17 → 4.03 a.u.) — the latter two findings recovering the expected pharmacological signature.

The study accomplishes its objective of validating MediaPipe as a credible substitute for accelerometers under controlled laboratory conditions. The principal limitation, acknowledged by the authors, is that MediaPipe degrades during kinetic-tremor tasks that occlude or distort the hand silhouette; the validation is therefore strongest on rest and postural tremor.

This work provides the strongest direct evidence that MediaPipe Hand Landmarker — the framework specified in the Deliverable 3 compliance module — can produce kinematically valid tremor signals. It also implicitly justifies the design choice in the present pipeline to use MediaPipe only for post-session compliance gating rather than as a primary signal source: the kinetic-tremor failure mode is precisely what makes real-time camera gating in the live IMU pipeline architecturally undesirable.

### 9. Hemmerling et al. (2026)

Hemmerling, D., Dudek, M., Krzywdziak, J., Żbik, M., Szecowka, W., Daniol, M., Wodzinski, M., Rudzinska-Bar, M., & Wojcik-Pedziwiatr, M. (2026). GRU-based deep multimodal fusion of speech and head-IMU signals in mixed reality for Parkinson's disease detection. *Sensors, 26*(1), Article 269. https://doi.org/10.3390/s26010269

Hemmerling et al. build DiagNeuro, a Microsoft HoloLens 2 system that synchronously captures acoustic features and head-mounted IMU signals from 165 participants (72 PD, 93 HC) performing standardized mixed-reality speech tasks. Three fusion architectures are compared on top of a bidirectional GRU temporal backbone — early concatenation, cross-attention, and gated early fusion. Speech-only performance reaches AUC ≈ 0.865, and gated early fusion improves discrimination modestly to AUC ≈ 0.875. Gains concentrate in tasks that engage postural control, indicating that head kinematics function as a conditional discriminator rather than an independent biomarker.

The work meets its objective of producing a credible multimodal PD-detection prototype with a non-trivial subject count for this design space. Limitations are typical of multimodal sensor-fusion research: the marginal gain from adding the IMU is small (~0.01 AUC), the platform is expensive and not consumer-deployable, and the binary PD/HC task is easier than within-cohort severity prediction.

This study is the closest analogue to the fusion question that arises if a later phase extends the framework to voice or face biomarkers. More immediately, the gated-early-fusion architecture is a candidate for combining flex-sensor (bradykinesia) and IMU (tremor) channels in a single decision head once flex-sensor integration completes on the Pi 5 host.

### 10. Králik & Šuppa (2021)

Králik, M., & Šuppa, M. (2021). WaveGlove: Transformer-based hand gesture recognition using multiple inertial sensors. In *Proceedings of the 2021 29th European Signal Processing Conference (EUSIPCO)* (pp. 1576–1580). IEEE. https://arxiv.org/abs/2105.01753

Králik and Šuppa construct a five-finger IMU glove and train a Transformer encoder on patch-embedded multi-channel inertial signals, comparing against classical and CNN baselines on two custom datasets (over 11,000 samples) and nine public hand-gesture benchmarks. The Transformer achieves high accuracy across complex multi-finger gestures. An explicit ablation reports accuracy rising sharply as the number of sensors increases from one to three before plateauing — quantitative evidence that multi-finger spatial information is decisive for fine-grained hand-motion recognition.

The work accomplishes its stated objective of establishing that Transformers are competitive on multi-IMU inertial time-series and that multi-sensor placement materially outperforms single-sensor configurations. The principal limitation for tremor-specific application is scope: WaveGlove targets voluntary gesture recognition, not pathological-motion severity rating, and voluntary gestures present an easier classification surface than ordinal MDS-UPDRS scoring.

WaveGlove is foundational to the PD-glove program on two counts. First, it is cited in the accompanying AIIoT 2026 paper as the design rationale for per-finger IMU placement, and the multi-sensor ablation provides quantitative justification for five MPU6050s rather than a single wrist sensor. Second, it defines the Transformer-encoder architecture adopted for MDS-UPDRS prediction in Deliverable 2, with the substitution of an ordinal-regression head and uncertainty estimation for the original classification head.

### 11. Liu et al. (2023)

Liu, W., Lin, X., Chen, X., Wang, Q., Wang, X., Yang, B., Cai, N., Chen, R., Chen, G., & Lin, Y. (2023). Vision-based estimation of MDS-UPDRS scores for quantifying Parkinson's disease tremor severity. *Medical Image Analysis, 85*, Article 102754. https://doi.org/10.1016/j.media.2023.102754

Liu et al. propose the Global Temporal-difference Shift Network (GTSN), a ResNet-based architecture augmented with a temporal-difference module that stacks inter-frame differences onto optical flow. The pipeline ingests Eulerian-Video-Magnification-preprocessed clips that amplify subtle tremor motion before classification. Across four body regions and four MDS-UPDRS severity classes, GTSN achieves 90.6% accuracy on rest hand tremor, 89.0% on jaw, 85.9% on leg, and 84.9% on postural tremor — the strongest video-based MDS-UPDRS hand-tremor result at the time of submission.

The work accomplishes its objective of demonstrating that a vision-only system can recover MDS-UPDRS class labels with accuracy near the inter-rater agreement floor for human clinicians. The dataset is single-center and not publicly released, the temporal-difference module is brittle to camera shake, and accuracy is reported as class accuracy rather than calibration-aware metrics, which complicates direct comparison with regression-style severity estimators.

This work defines the video-based MDS-UPDRS performance ceiling that an IMU-plus-video architecture should target in the present program. It also reinforces the choice of MediaPipe-derived structured features rather than raw pixels for the compliance module, given the lower compute cost and better cross-site transfer characteristics of pose-based pipelines.

### 12. Muhammad et al. (2026)

Muhammad, J., Ghergherehchi, M., Ali, S., Song, H. S., & Rahim, N. (2026). Trustworthy AI for medical decisions: Adversarially robust and fair machine learning prediction for Parkinson's disease. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0342062

Muhammad et al. evaluate two interpretable PD classifiers — Random Forest and Decision Tree — trained on the Parkinson's Progression Markers Initiative cohort (n=1,084, spanning age, sex, and race) and subject them to two adversarial regimes: label-flipping leakage and data-poisoning. Without defenses, decision-tree accuracy drops by more than 10% and random-forest accuracy by more than 20% under attack, with disparities concentrated in minority demographic strata. Fairness-aware preprocessing reduces Statistical Parity Difference and Equal Opportunity Difference at the cost of modest absolute-accuracy decline.

The study accomplishes its objective of demonstrating that medical-AI fairness and adversarial robustness are tightly coupled: perturbations that appear as noise on aggregate metrics surface as bias amplification on subgroup metrics. Limitations include the relative homogeneity of PPMI itself as a research cohort, the interpretable-but-not-state-of-the-art classifier choices, and the dominance of distribution shift over synthetic attacks in real clinical settings.

This work is directly relevant to the Deliverable 3 fairness audit (Week 11). PPMI is one of the training corpora for the present framework, so the fairness-aware preprocessing recipes (resampling, reweighting) apply without modification. The broader takeaway — that subgroup metrics must be reported alongside aggregates — is adopted as a non-negotiable element of the evaluation protocol.

### 13. Nanayakkara & Chan (2025)

Nanayakkara, G. R. R., & Chan, P. Y. (2025). Subclinical tremor differentiation using long short-term memory networks. *Physical and Engineering Sciences in Medicine*. https://doi.org/10.1007/s13246-025-01526-0

Nanayakkara and Chan train an LSTM on short-time Fourier transform features of inertial-sensor recordings from 51 PD patients, 15 essential-tremor (ET) patients, and 58 healthy controls, focusing specifically on subclinical (low-amplitude) tremor that conventional detectors miss. The binary PD-versus-ET classifier reaches 95% accuracy and the three-class model reaches 93% — a 30–50% absolute improvement over a ConvLSTM benchmark on the same low-amplitude data. The architecture choice is deliberate: STFT features force the network to attend to frequency content even when amplitudes are too small for time-domain pattern matching.

The work accomplishes its objective of moving the differential-diagnosis problem out of the easy-amplitude regime into the clinically harder subclinical band. Limitations include imbalanced per-class cohort sizes (ET under-represented), single-center data collection, and the increasingly outdated LSTM backbone, which may underperform attention-based baselines on the same task.

The subclinical-tremor regime is precisely where the 4–6 Hz Butterworth and FFT DSP pipeline used in the AIIoT 2026 prototype is weakest, since frequency-domain peaks become indistinct at low amplitudes. The STFT and LSTM recipe described here is a plausible pre-processing front-end for the Transformer model on early-stage PD subjects, where amplitude separation between rest and tremor windows is narrow.

### 14. Paneru (2025)

Paneru, B. (2025). Prediction of freezing of gait in Parkinson's disease using explainable AI and federated deep learning for wearable sensors. *arXiv*. https://arxiv.org/abs/2507.01068

Paneru proposes a federated learning framework for freezing-of-gait prediction over wearable IMU data, in which local models (CatBoost, XGBoost, ExtraTrees, and a Conv1D+LSTM hybrid) train on individual devices and only model updates leave the client. A stacking ensemble reaches near-99% classification accuracy on held-out FoG events, and SHAP analysis isolates short-window temporal features as the dominant predictors. The federated configuration is positioned as a privacy-by-design alternative to centralized PD-monitoring deployments.

The paper accomplishes the structural objective of demonstrating end-to-end federated PD detection with explainability. The very high reported accuracy warrants caution: single-author preprint, sparse validation-protocol detail, and the known leakage risk in FoG classification when splits are not strictly per-subject. SHAP on temporal features is useful but does not substitute for an external test cohort.

For the present framework the relevance is conceptual rather than methodological. The PD-glove architecture is single-device on the Pi 5 with MQTT-published derived scores, and is therefore already privacy-preserving without federation. Should a later phase scale the deployment to a multi-subject cohort, federated training of the Transformer head — with the Pi 5 acting as the local client — is the natural extension, and Paneru's pipeline supplies the simplest reference architecture.

### 15. Papadopoulos et al. (2020)

Papadopoulos, A., Kyritsis, K., Klingelhoefer, L., Bostanjopoulou, S., Chaudhuri, K. R., & Delopoulos, A. (2020). Detecting Parkinsonian tremor from IMU data collected in-the-wild using deep multiple-instance learning. *IEEE Journal of Biomedical and Health Informatics, 24*(9), 2559–2569. https://doi.org/10.1109/JBHI.2019.2961748

Papadopoulos et al. formulate in-the-wild tremor detection as a Multiple Instance Learning (MIL) problem: each subject is represented as an unordered "bag" of smartphone IMU signal segments paired with a single expert-provided session-level label. A deep feature extractor processes each segment, and a learnable attention pooling layer selects the most informative instances during end-to-end training, sidestepping the need for clinician-annotated minute-by-minute tremor labels. The model is validated on 45 subjects with smartphone accelerometer data collected entirely in real-world conditions and outperforms instance-level supervised baselines.

The work accomplishes its central methodological claim — that MIL can extract a usable tremor signal from noisy, unconstrained smartphone recordings using only weak session-level labels. Accuracy reporting is not as strong as laboratory studies, which is appropriate given the deployment setting; the principal limitation is that the smartphone is held only intermittently, biasing the dataset toward stationary tremor episodes.

This work provides a direct template for handling label scarcity in continuous-wear deployments such as the PD-glove program. Rather than requiring subjects to self-annotate, the present framework can capture session-level MDS-UPDRS labels and apply MIL attention to extract the relevant time windows. The smartphone-versus-glove form-factor difference is significant — the noise profile of the in-the-wild smartphone dataset is harsher than that of the Pi 5 wearable pipeline — but the labeling-economics argument transfers.

### 16. Paucar-Escalante et al. (2025)

Paucar-Escalante, J., Alves da Silva, M., Sanches, B. D. L., Soriano-Vargas, A., Moriyama, L. S., & Colombini, E. L. (2025). Machine learning strategies for Parkinson tremor classification using wearable sensor data. *arXiv*. https://arxiv.org/abs/2501.18671

Paucar-Escalante et al. survey current ML methods for wearable PD tremor classification along three axes: data acquisition (sensor type, placement, sampling rate), signal processing (time-domain, frequency-domain, time-frequency representations), and modeling (SVM, RF, XGBoost on the classical side; CNN, LSTM, Transformer on the deep side). The authors curate explainability techniques and identify open challenges — small subject counts, weak external validation, inconsistent label conventions, and the absence of standardized benchmark splits.

The survey accomplishes its objective of mapping the landscape and is among the few recent reviews to explicitly call out methodological inconsistencies that block cross-study comparison. Limitations are inherent to survey-format work: no original experiments, partial coverage of self-supervised and foundation-model approaches (still emerging during the writing window), and limited engagement with deployment concerns such as quantization and latency.

This paper is the most useful single citation for grounding the Research Gap section of the present review and for framing the Part II baseline classifier choices in Deliverable 1 (SVM, RF, 1D-CNN — exactly the canonical baselines the survey identifies). It also explicitly enumerates methodological pitfalls — subject-level leakage, weak external validation — that the PD-glove evaluation protocol is designed to avoid.

### 17. Rodriguez et al. (2024)

Rodriguez, F., Krauss, P., Kluckert, J., Ryser, F., Stieglitz, L., Baumann, C., Gassert, R., Imbach, L., & Bichsel, O. (2024). Continuous and unconstrained tremor monitoring in Parkinson's disease using supervised machine learning and wearable sensors. *Parkinson's Disease, 2024*, Article 5787563. https://doi.org/10.1155/2024/5787563

Rodriguez et al. train a Support Vector Machine on a 67-hour database of IMU recordings from 24 PD patients at four extremities (approximately three hours per patient) during free-living activities, with manual minute-level tremor scoring performed by clinicians via a custom mobile application. The classifier achieves 0.90 sensitivity and 0.88 overall accuracy on the held-out test partition, and the authors demonstrate that class-rebalancing techniques materially improve performance on the imbalanced "tremor versus no-tremor" split.

The work accomplishes its objective of producing a free-living tremor monitor trainable from a modestly sized, manually labeled corpus. Limitations include the SVM backbone, which is well below current state-of-the-art for time-series classification; the per-subject calibration burden; and the 24-subject cohort, which is small relative to the cross-patient generalization claim. The manually labeled, clinician-supervised free-living dataset is, however, rare and load-bearing for the field.

This study is the closest free-living analogue to the PD-glove protocol scale (single-digit subjects, in-clinic plus at-home recording). It also provides a concrete recommendation — class-rebalancing matters more than algorithm choice when the dataset is small and imbalanced — that is adopted directly in the Deliverable 1 baseline benchmarks.

### 18. Timmermans et al. (2025)

Timmermans, N. A., Terranova, R., Soriano, D. C., Cagnan, H., Raykov, Y. P., Bucur, I. G., Bloem, B. R., Helmich, R. C., & Evers, L. J. W. (2025). A generalizable and open-source algorithm for real-life monitoring of tremor in Parkinson's disease. *npj Parkinson's Disease, 11*, Article 205. https://doi.org/10.1038/s41531-025-01056-2

Timmermans et al. build a logistic-regression classifier on cepstral coefficients extracted from wrist gyroscope data and pair it with a two-dataset training strategy: a small, extensively video-labeled at-home dataset (24 PD + 24 controls) for supervised training and a large unsupervised cohort (517 PD + 50 controls) collected on different hardware for external validation. The algorithm achieves 0.61 (±0.20) sensitivity and 0.97 (±0.05) specificity on real-life recordings and generalizes across two distinct wearable devices. The code is released as the open-source Paradigma toolbox.

The work accomplishes its objective of producing a deployment-ready tremor monitor that survives cross-device evaluation — a notoriously brittle property — and explicitly documents its failure modes. Sensitivity is modest, reflecting the difficulty of free-living tremor detection; the logistic-regression backbone is more interpretable than a deep model but likely under-fits richer tremor phenotypes; and the external validation cohort lacks ground-truth labels, so specificity numbers there are approximate.

Paradigma is the single most useful comparator for the PD-glove real-world deployment. The cross-device generalization result is encouraging — the Pi 5 + MPU6050 pipeline shares this design constraint — and the open-source release allows the present Butterworth and FFT DSP pipeline to be validated against an independent reference implementation in Week 1 (May 19–25).

### 19. Tumpa et al. (2025)

Tumpa, Z. N., Zawad, M. R. S., Sollis, L., Parab, S., Chen, I. Y., & Washington, P. (2025). Quantifying device type and handedness biases in a remote Parkinson's disease AI-powered assessment. *npj Digital Medicine, 8*, Article 550. https://doi.org/10.1038/s41746-025-01934-2

Tumpa et al. evaluate a web-based remote PD assessment that uses mouse-tracing and keyboard-pressing tasks on 251 participants (99 PD, 152 non-PD) and audit it across demographic, device, and handedness strata. No statistically significant F1 disparities by sex or race are detected after race resampling. The audit, however, quantifies a substantial unexpected bias: Windows users and left-handed individuals are 38–70% less likely to receive a PD-positive diagnosis than Mac users and right-handed individuals respectively. The paper traces these gaps to platform-specific input behavior and dataset-level handedness imbalance.

The work accomplishes its objective of exposing a class of fairness failures that the standard demographic-stratification audit overlooks entirely. Limitations include the small self-selected cohort, the input modalities (mouse and keyboard) that depart from the wearable form factor most of this literature uses, and headline disparities that reflect specific UI choices and may not generalize.

This paper crystallizes a fairness category not initially scoped for the PD-glove audit — hardware-specific bias. The Pi 5 + MPU6050 pipeline is a single fixed hardware stack, which protects against device-type drift, but handedness asymmetry is real: the present validation data is drawn entirely from right-dominant subjects. A handedness audit is therefore added explicitly to the Deliverable 3 protocol.

### 20. Xing et al. (2022)

Xing, X., Luo, N., Li, S., Zhou, L., Song, C., & Liu, J. (2022). Identification and classification of Parkinsonian and essential tremors for diagnosis using machine learning algorithms. *Frontiers in Neuroscience, 16*, Article 701632. https://doi.org/10.3389/fnins.2022.701632

Xing et al. compare seven machine learning classifiers — Random Forest, XGBoost, SVM, logistic regression, ridge classification, BP neural network, and a CNN — on a combined tremor-acceleration plus surface-EMG dataset from 398 patients held in four upper-limb postures. Ensemble methods dominate: Random Forest and XGBoost both reach accuracy above 0.84 and AUC above 0.90 for differential PD-versus-ET classification. Feature-importance analysis isolates the dominant frequency and average amplitude of flexor-muscle signals, plus specific arm postures, as the most discriminating inputs.

The work accomplishes its objective of establishing a strong classical-ML baseline for tremor differential diagnosis, and the cohort is unusually large by tremor-classification standards. The dataset is single-center; the deep-learning entry (CNN) underperforms the gradient-boosted baselines, which is more a comment on cohort size and feature engineering than on deep learning per se; and the assessment is in-clinic and posture-prompted, which presents an easier surface than continuous free-living recording.

This study is the clearest evidence that classical ensemble methods remain competitive on small-to-moderate clinical datasets, supporting the Deliverable 1 plan to benchmark SVM, Random Forest, and 1D-CNN before training a Transformer. The posture-specific feature importance also informs the present exercise protocol: the postures identified by Xing et al. as most discriminative are precisely the ones MDS-UPDRS Part III prescribes, so the structured three-task assessment captures the right kinematic regimes.

---

## Identified Research Gap

Synthesizing across these twenty sources, the machine-learning literature on hand tremor has matured along several dimensions but leaves a coherent, exploitable gap that the PD-glove framework is positioned to fill.

**Per-finger spatial resolution remains rare.** With the single exception of Králik and Šuppa (2021), every IMU-based study in this review uses either a wrist-worn device (Bachlin et al., Atri et al., Rodriguez et al., Timmermans et al., Evers et al., Nanayakkara and Chan, Papadopoulos et al.) or a smartphone (Bot et al., Papadopoulos et al.), and every video-based study (Güney et al., Liu et al., Duque-Quiceno et al.) treats the hand as a single articulated object. WaveGlove demonstrates that multi-IMU placement materially raises ceiling accuracy on fine-grained hand-motion tasks, yet no published PD study extends that finding into MDS-UPDRS-aligned tremor scoring. The pill-rolling thumb-index interaction characteristic of Parkinsonian resting tremor is spatially specific in a way that wrist sensors and pixel-based video both blur. A five-finger IMU glove therefore occupies an under-occupied region of the design space.

**MDS-UPDRS-aligned ordinal severity is under-served relative to binary detection.** The dominant clinical task across the reviewed corpus is binary tremor versus no-tremor classification (Papadopoulos et al., Atri et al., Rodriguez et al., Timmermans et al., Evers et al., Paneru); only three papers explicitly target MDS-UPDRS severity (Liu et al., Duque-Quiceno et al.) or differential diagnosis (Xing et al., Nanayakkara and Chan). The transformation from binary detection to ordinal severity prediction is non-trivial: it requires calibrated probability outputs, ordinal loss functions, and uncertainty estimates that very few of the reviewed systems provide. The vision-based MDS-UPDRS classifier of Liu et al. and the pixel-based severity model of Duque-Quiceno et al. establish video baselines, but no wearable-only system covered in this review delivers full 0–4 MDS-UPDRS scores with calibrated uncertainty.

**Edge-deployable, quantized Transformer inference for tremor is essentially missing.** Across twenty papers, deployment is discussed but rarely instrumented: Atri et al. run their daily-monitoring pipeline in the cloud, Timmermans et al. release open-source code without quantization benchmarks, and Paneru reports model accuracy without inference latency. None of the reviewed work publishes INT8 TFLite latency numbers on edge-class hardware for a Transformer encoder operating on multi-channel IMU input. This is precisely the deployment regime that the Part II pipeline targets — TFLite INT8 on the Raspberry Pi 5, with sub-200 ms latency as the operational requirement.

**Privacy-by-design is under-addressed despite being clinically central.** Paneru (2025) provides the only federated-learning entry in this review, and Tumpa et al. (2025) raise remote-assessment fairness, but no paper combines on-device inference with raw-data-never-leaves-device guarantees. The dominant deployment pattern across the twenty studies is upload-and-process: raw IMU traces, raw video, or raw audio leave the patient device. The PD-glove MQTT-only-derived-scores architecture, with all DSP and Transformer inference local to the Pi 5, materially closes that gap and aligns with the privacy-by-design boundary established in the AIIoT 2026 paper.

**Fairness evidence remains thin and primarily framed around demographics.** Only Tumpa et al. (2025) and Muhammad et al. (2026) provide formal fairness audits, and both surface bias categories — hardware platform, handedness, adversarial robustness — that the canonical age, sex, and race stratification misses. PPMI itself, used by Muhammad et al. and central to the Part II training pipeline, is a relatively homogeneous specialist-recruited cohort; demographic generalization claims drawn from PPMI-only training therefore require explicit external validation. None of the reviewed work pairs MDS-UPDRS severity prediction with both demographic and hardware-stratified fairness reporting.

**Contribution against this gap.** The Part II program advances four claims that, taken together, are not jointly addressed by any single paper in this review. First, five-finger IMU placement captures the spatial signature of pill-rolling tremor, drawing on the WaveGlove design rationale but moving the methodology from gesture recognition to clinical scoring. Second, a Transformer encoder predicts calibrated, MDS-UPDRS-aligned 0–4 severity with uncertainty intervals, addressing the binary-versus-ordinal gap. Third, INT8 TFLite deployment on a Raspberry Pi 5 edge device produces documented inference latency, addressing the missing-deployment-numbers gap. Fourth, MQTT publication of derived scores only, with raw IMU data never leaving the device, addresses the privacy-by-design gap. A Deliverable-3 fairness audit across PPMI demographic splits plus handedness — the latter motivated directly by Tumpa et al. (2025) — closes the audit loop. Each individual element of this stack is anticipated somewhere in the prior literature; their integration into a single reproducible, edge-deployable pipeline is not.
