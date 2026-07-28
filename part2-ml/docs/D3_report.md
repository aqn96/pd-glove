# Deliverable 3: Edge Deployment (INT8 TFLite) and Fairness Audit
**CS 8674 Part II - Intelligent IoT Frameworks for Chronic Disease Management**
An Nguyen · Northeastern University Khoury College · July 2026

---

## 1. Introduction

### Where D2 left off

D2 established that MOMENT-1-large, fully fine-tuned, is the strongest classifier on PADS (macro-F1=0.626, AUROC=0.731), but at 1.4 GB it cannot run on the Raspberry Pi 5. SVM and CNN1D remain the practical deployment candidates. D2 did not yet answer two questions the deployment story depends on: how much accuracy is lost when a model is actually compressed for the edge, and whether that model performs consistently across patient subgroups rather than just on average.

### What D3 addresses

Three things:

1. Quantize the CNN1D to INT8 TFLite and measure the accuracy cost of compression.
2. Benchmark inference latency as a proxy for the Pi 5 (the physical device is not currently accessible — see Section 5).
3. Audit the quantized model's fairness across PADS' own patient demographics (age, gender, handedness), since average accuracy hides subgroup failure.

---

## 2. Methodology

### Why a single train/test split instead of 5-fold CV

D2's 5-fold cross-validation reports the unbiased benchmark number already cited in the D2 report — that number should not change. D3 needs one concrete, deployable model artifact to quantize and audit, so a new CNN is trained on the D2 pipeline's original subject-level train split (247 subjects, 5,434 windows) and evaluated once on its held-out test split (54 subjects, 1,188 windows). Both splits are leakage-safe at the subject level (no patient appears in both).

### Why the CNN was reimplemented in Keras rather than converted from PyTorch

D2's CNN1D was trained in PyTorch. Converting a PyTorch model to TFLite requires an intermediate PyTorch → ONNX → TensorFlow path that frequently fails or silently drops unsupported ops. For a model this small (two convolutional blocks), it is simpler and lower-risk to rebuild the identical architecture directly in `tf.keras` and train it fresh on the same data, rather than convert weights. The architecture is unchanged:

```
Conv1D(32, k=5, same) -> BatchNorm -> ReLU -> MaxPool(2)
Conv1D(64, k=5, same) -> BatchNorm -> ReLU -> GlobalAveragePool
Dense(2)
```

Trained for 40 epochs, Adam optimizer, class-weighted `SparseCategoricalCrossentropy` (HC=2.17, PD=0.65).

### INT8 quantization

Post-training full-integer quantization via `TFLiteConverter`, calibrated on a 200-window sample from the training split (`representative_dataset`). Model input/output stay float32 at the interface; weights and activations are quantized to INT8 internally, which is what produces the latency and size benefits on ARM hardware while keeping the model simple to call.

One implementation issue worth recording: the first attempt declared the Keras input shape as `(None, n_channels)` (variable window length), which trains fine but caused TFLite's converter to default the unspecified dimension to 1 — the converted model then rejected real 974-sample windows with a dimension-mismatch error. Fixed by declaring the input shape concretely as `(974, n_channels)`, since every PADS window is a fixed length anyway.

### Fairness audit

PADS' own patient metadata (`patients/*.json`) includes `age`, `gender`, and `handedness` directly — no need for PPMI or any other dataset. The audit joins the INT8 model's held-out test-set predictions (window-level, consistent with every other D2/D3 metric) against these fields and reports per-subgroup macro-F1 and AUROC. Subgroups with fewer than 10 windows or only one label class present are flagged rather than given a possibly-meaningless AUROC. The INT8 model is audited specifically because that is the artifact that would actually deploy, not the float32 training-time model.

### Latency benchmark

Pending — see Section 5.

---

## 3. Results

### Quantization accuracy and size

| Model | Macro-F1 | AUROC | Size |
|---|---|---|---|
| Float32 Keras CNN | 0.549 | 0.673 | ~78 KB (unquantized) |
| INT8 TFLite CNN | 0.538 | 0.666 | 19.6 KB |
| **Delta** | **-0.010** | **-0.007** | **~4x smaller** |

For context, this float32 number (F1=0.549) is consistent with D2's 5-fold CV CNN1D result (F1=0.565 ± 0.022) — within one standard deviation, on a single held-out split rather than an average of five. The quantized model loses essentially no accuracy (-0.010 F1) while shrinking to 19.6 KB, comfortably within reach of the Pi 5's resources.

### Fairness audit

**By gender:**

| Group | n | Macro-F1 | AUROC |
|---|---|---|---|
| Female | 418 | 0.621 | 0.706 |
| Male | 770 | 0.454 | 0.586 |

**By handedness:**

| Group | n | Macro-F1 | AUROC |
|---|---|---|---|
| Left | 66 | 0.340 | not computable — single label class in this split |
| Right | 1,122 | 0.548 | 0.673 |

**By age group:**

| Group | n | Macro-F1 | AUROC |
|---|---|---|---|
| Under 55 | 198 | 0.677 | 0.783 |
| 55-70 | 550 | 0.516 | 0.633 |
| 70+ | 440 | 0.485 | 0.608 |

### Key findings

Two real, measurable disparities: the model performs substantially worse on male subjects (AUROC 0.586 vs 0.706 for female, a 12-point gap) and on older subjects (AUROC 0.608 for 70+ vs 0.783 for under-55, a 17.5-point gap). Neither is a hypothetical concern raised for completeness — both are directly observed on this held-out test set. The handedness audit could not produce a reliable comparison: by chance, every left-handed subject in this test split shares the same diagnosis label, making AUROC uncomputable there. This is reported as a genuine limitation of the split rather than something to fix by re-splitting to get a "better" answer.

---

## 4. Discussion

### What the quantization result means for deployment

A 19.6 KB model losing 0.010 F1 from quantization is a strong result — this is well within the range where INT8 TFLite is a clear win for edge deployment, confirming the D2 report's earlier claim that a compressed CNN, not MOMENT, is the realistic Pi target.

### What the fairness result means

This is exactly the failure mode the project's literature review flagged as underreported: average accuracy (F1=0.538 overall) hides that the model works meaningfully better for some patients than others. A gap this size — 12 points of AUROC by gender, 17.5 by age — is not noise; a model this inconsistent across subgroups would need real scrutiny before any clinical use, regardless of its overall number.

One caveat this report has not yet ruled out: whether the disparities are driven by differing PD/HC class balance within each subgroup rather than the model handling one group's signal worse. That check is listed as a next step below rather than something resolved here — reporting an unconfirmed causal claim would be exactly the kind of over-claiming this project has otherwise tried to avoid.

---

## 5. Latency Benchmark — Pending

The Raspberry Pi 5 is not currently accessible. The plan is to benchmark the INT8 TFLite model's inference latency locally on an Apple M3 Pro (ARM64) as a directional proxy — the same instruction-set family as the Pi 5's Cortex-A76, but a substantially more powerful chip. Any number produced this way will be reported explicitly as a laptop-measured upper-bound-on-speed estimate, not an equivalent to real Pi 5 performance, since the M3 Pro's core design and clock speed are not comparable to the Pi's. This section will be completed once that benchmark is run.

---

## 6. Limitations and Next Steps

- **Real Pi 5 latency validation** is the most important open item — the simulated laptop number is a stand-in, not a substitute.
- **Subgroup class-balance confound**: check whether the gender/age fairness gaps track differing PD/HC ratios within each subgroup before attributing them to model behavior specifically.
- **Handedness audit needs a larger or rebalanced cohort** — the current test split cannot support it at all.
- These results feed into the Phase 3 glove fine-tuning plan (post-IRB): any subgroup weakness found here is worth checking again once glove-specific data exists, rather than assuming the public-dataset audit generalizes to the glove's own patient population.
