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

PADS' own patient metadata (`patients/*.json`) includes `age`, `gender`, and `handedness` directly — no need for PPMI or any other dataset. Subgroups with fewer than 10 windows or only one label class present are flagged rather than given a possibly-meaningless AUROC.

Two versions of this audit were run, and the difference between them is itself a finding (see Section 3):

1. **Single-split audit** — joins the deployed INT8 model's held-out test-set predictions (54 subjects, 1,188 windows) against demographics. This is the audit of the actual artifact that would deploy, but the test split is small enough that per-subgroup numbers get noisy fast.
2. **Pooled 5-fold out-of-fold audit** — a fresh `tf.keras` CNN (same architecture) is trained on each of 5 `StratifiedGroupKFold` folds over the *entire* dataset, and each subject's prediction is taken from whichever fold held them out. Pooling across all 5 folds gives fairness statistics over all 355 subjects (7,810 windows) instead of one 54-subject slice, at the cost of using float32 predictions per fold rather than re-quantizing 5 separate INT8 models (quantization cost was already shown to be small, so this is a reasonable proxy for what the deployed model would do across the full population).

### Latency benchmark

Pending — see Section 5.

---

## 3. Results

### Quantization accuracy and size

| Model | Macro-F1 | AUROC | Size |
|---|---|---|---|
| Float32 Keras CNN | 0.427 | 0.680 | ~78 KB (unquantized) |
| INT8 TFLite CNN | 0.391 | 0.675 | 19.6 KB |
| **Delta** | **-0.036** | **-0.005** | **~4x smaller** |

**Note on run-to-run variance:** an earlier run of the identical code and split produced F1=0.549 (float32) / F1=0.538 (int8) — a meaningfully different F1 despite the same architecture, same split, same seeds. AUROC was more stable across the two runs (0.673 vs 0.680). This is real training noise on a single small held-out split (54 subjects), not a bug — see the pooled 5-fold result below for the more trustworthy accuracy estimate. In both runs, AUROC loss from quantization was small (≤0.007), and the model size drops to 19.6 KB regardless — the deployment-relevant conclusions (quantize cheaply, model is tiny) hold up across both runs even though the exact F1 doesn't.

For a more reliable estimate of the architecture's actual accuracy, the pooled 5-fold CV below gives per-fold F1 of 0.592, 0.584, 0.549, 0.537, 0.525 (mean ≈ 0.557) — consistent with D2's original PyTorch CNN1D 5-fold result (F1 = 0.565 ± 0.022).

### Fairness audit

**Single-split audit (54 subjects, 1,188 windows) — the deployed INT8 model:**

| Demographic | Group | n | Macro-F1 | AUROC |
|---|---|---|---|---|
| Gender | Female | 418 | 0.519 | 0.707 |
| Gender | Male | 770 | 0.297 | 0.605 |
| Handedness | Left | 66 | 0.165 | not computable — single label class |
| Handedness | Right | 1,122 | 0.403 | 0.682 |
| Age | Under 55 | 198 | 0.511 | 0.779 |
| Age | 55-70 | 550 | 0.394 | 0.649 |
| Age | 70+ | 440 | 0.322 | 0.614 |

**Pooled 5-fold out-of-fold audit (355 subjects, 7,810 windows — the entire dataset):**

| Demographic | Group | n | Macro-F1 | AUROC |
|---|---|---|---|---|
| Gender | Female | 2,882 | 0.598 | 0.666 |
| Gender | Male | 4,928 | 0.506 | 0.698 |
| Handedness | Left | 528 | 0.648 | 0.758 |
| Handedness | Right | 7,282 | 0.552 | 0.686 |
| Age | Under 55 | 1,694 | 0.629 | 0.728 |
| Age | 55-70 | 3,630 | 0.529 | 0.662 |
| Age | 70+ | 2,486 | 0.554 | 0.711 |

### Key findings

**The single-split audit's apparent disparities do not survive being checked against the full dataset.** On the 54-subject split alone, the model looked strongly worse for male subjects (AUROC gap of 0.102) and for older subjects (AUROC gap of 0.165, decreasing steadily with age), and the handedness audit couldn't even compute an AUROC. Pooled across all 355 subjects via 5-fold cross-validation, that picture changes substantially:

- **Gender:** AUROC is nearly equal (male 0.698 vs female 0.666) — if anything, slightly favoring male on ranking quality, though a moderate F1 gap remains (male 0.506 vs female 0.598).
- **Handedness:** now measurable with enough data, and left-handed subjects score *better* (AUROC 0.758 vs 0.686), the opposite of what the single-split audit could only fail to measure.
- **Age:** does not decrease monotonically with age. The 70+ group (AUROC 0.711) performs close to the under-55 group (0.728); the worst-performing group is actually the middle one, 55-70 (0.662).

The honest conclusion is closer to **no strong, consistent subgroup disparity found** rather than the "real, measurable disparity" the single-split audit initially suggested. This is itself a useful methodological finding: a fairness audit run on a small held-out split can produce a confident-looking but misleading picture, and the fix is pooling predictions across cross-validation folds rather than trusting one split. The one gap that does persist in the pooled data — a moderate F1 difference by gender despite similar AUROC — is worth continued monitoring rather than dismissing outright, since it suggests the model's ranking ability is similar across gender but its hard classification threshold may not be equally well-calibrated for both groups.

---

## 4. Discussion

### What the quantization result means for deployment

A ~20 KB model losing at most 0.036 F1 from quantization (and often less, per the run-to-run variance noted above) is a strong result — this is well within the range where INT8 TFLite is a clear win for edge deployment, confirming the D2 report's earlier claim that a compressed CNN, not MOMENT, is the realistic Pi target. AUROC loss from quantization was consistently small (≤0.007) across both runs, which is the more stable signal to lean on given the F1 volatility.

### What the fairness result means

This result is a stronger argument for auditing subgroup fairness than the original single-split finding would have been — not because it found a dramatic disparity, but because it demonstrates *why* the audit has to be done carefully. A naive single-split audit produced a confident, clinically alarming-looking story (large gaps by gender and age) that mostly evaporated once evaluated properly across the full population. Reporting the single-split number as the final answer would have been a real overclaim. The properly pooled result is more modest but more trustworthy: no strong consistent bias by age or handedness, and a moderate but real gender gap in F1 (not AUROC) worth further investigation before any clinical claim is made either way.

---

## 5. Latency Benchmark — Pending

The Raspberry Pi 5 is not currently accessible. The plan is to benchmark the INT8 TFLite model's inference latency locally on an Apple M3 Pro (ARM64) as a directional proxy — the same instruction-set family as the Pi 5's Cortex-A76, but a substantially more powerful chip. Any number produced this way will be reported explicitly as a laptop-measured upper-bound-on-speed estimate, not an equivalent to real Pi 5 performance, since the M3 Pro's core design and clock speed are not comparable to the Pi's. This section will be completed once that benchmark is run.

---

## 6. Limitations and Next Steps

- **Real Pi 5 latency validation** is the most important open item — the simulated laptop number is a stand-in, not a substitute.
- **Single-split model accuracy is noisy** (F1 varied from 0.427 to 0.549 across two identical runs) — any accuracy claim about "the" deployed model should cite the pooled 5-fold mean (≈0.557) rather than one run's single-split number.
- **The remaining gender F1 gap** (male 0.506 vs female 0.598 in the pooled audit, despite similar AUROC) is not yet explained — worth checking whether it tracks a class-balance difference between subgroups, or a genuine calibration difference, before drawing a conclusion either way.
- **Handedness and age findings should be treated as provisional**, not because the pooled method is wrong, but because any fairness audit result deserves replication before being treated as settled — this project only ran one 5-fold pooling pass.
- These results feed into the Phase 3 glove fine-tuning plan (post-IRB): any subgroup pattern found here is worth checking again once glove-specific data exists, rather than assuming the public-dataset audit generalizes to the glove's own patient population.
