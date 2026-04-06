# Gait Assessment: Phone Camera CV Pipeline

**Status:** Planned extension — Part II (Summer 2026)
**Related:** `mediapipe_compliance.py`, CARE-PD dataset, Exercise 5 protocol

---

## Overview

This document covers the design and implementation plan for camera-based gait assessment using the patient's phone. This extends the four existing upper-limb glove exercises with a fifth walking exercise, covering MDS-UPDRS Part III Item 3.10 (Gait).

The phone is already part of the system for session control and compliance video capture. The gait module reuses the same camera feed — no additional hardware is required.

---

## Exercise 5 — 10-Meter Walk Test (MDS-UPDRS Item 3.10)

**Protocol:**
- Patient walks in a straight line at comfortable pace, turns, and walks back for 2–3 passes
- Target corridor length: 10 meters (a hallway or living room end-to-end)
- Minimum usable space: 4 meters — clinically validated in home-based PD studies
- Phone placed on a stable surface (table, shelf) at roughly hip height, pointing down the walking path — side or back view both work
- App timestamps each walking pass; turn segments are discarded from scoring

**Why a small space works:** PD home gait studies consistently use 4–10 meter corridors. Shorter passes mean fewer full stride cycles per segment, but 2–3 passes still yield enough data for reliable feature extraction. Turn behavior (hesitation, freezing of gait) is captured separately and is itself clinically meaningful.

---

## Training Dataset: CARE-PD

| | |
|---|---|
| **Repo** | https://github.com/TaatiTeam/CARE-PD |
| **HuggingFace** | `vida-adl/CARE-PD` |
| **Paper** | NeurIPS 2025 — Adeli et al. |
| **License** | MIT (non-commercial research) |

CARE-PD is the largest publicly available 3D mesh gait dataset for PD. It aggregates 9 cohorts from 8 clinical sites (363 participants) covering a range of disease severity. All recordings — whether from RGB video or motion capture — are converted to anonymized SMPL body mesh sequences. Raw video is not distributed; only the extracted 3D meshes are released.

**What makes it suitable here:**
- Includes recordings from both ceiling-mounted cameras and smartphone video — covers informal home setups
- UPDRS-gait scores (0–3) annotated by expert clinicians on a per-walk basis
- Covers both medication-on and medication-off states
- Includes freezing of gait (FOG) labels in several cohorts

**Download:**
```bash
huggingface-cli download vida-adl/CARE-PD --repo-type dataset --local-dir ./assets/datasets
```

**Supplementary dataset:** Daphnet Freezing of Gait (UCI) provides additional accelerometer-based FOG labels that can be used alongside CARE-PD for FOG-specific training.
- Link: https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait

---

## CV Pipeline

```
Phone video (any framerate)
        ↓
MediaPipe Pose → 33 landmarks (3D world coordinates)
        ↓
Joint selection + mapping → 17 h36m joints (CARE-PD format)
        ↓
Root-relative normalization + temporal resampling
        ↓
CARE-PD trained model (MotionBERT or POTR backbone)
        ↓
UPDRS gait score (0–3)
```

### Step 1 — MediaPipe Pose Extraction
MediaPipe Pose outputs 33 3D landmarks per frame in world coordinates. Run on pre-recorded phone video post-session (not real-time), consistent with the existing compliance validation approach.

```python
import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
with mp_pose.Pose(static_image_mode=False, model_complexity=2) as pose:
    cap = cv2.VideoCapture("walk_session.mp4")
    landmarks_sequence = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.pose_world_landmarks:
            landmarks_sequence.append(results.pose_world_landmarks)
```

### Step 2 — Joint Mapping (MediaPipe → h36m)
CARE-PD uses the h36m 17-joint skeleton. The mapping selects the corresponding MediaPipe landmarks and discards the rest. This is a known, documented conversion — reference tables are publicly available.

| h36m Joint | MediaPipe Landmark Index |
|---|---|
| Pelvis (root) | mid-point of 23 + 24 |
| Right hip | 24 |
| Right knee | 26 |
| Right ankle | 28 |
| Left hip | 23 |
| Left knee | 25 |
| Left ankle | 27 |
| Spine | mid-point of 11 + 12 + 23 + 24 |
| Thorax | mid-point of 11 + 12 |
| Neck | mid-point of 9 + 10 |
| Head | mid-point of 7 + 8 |
| Left shoulder | 11 |
| Left elbow | 13 |
| Left wrist | 15 |
| Right shoulder | 12 |
| Right elbow | 14 |
| Right wrist | 16 |

**Key alignment steps:**
1. Subtract pelvis (root joint) from all joints — root-relative coordinates
2. Verify axis orientation matches h36m convention (Y-up, Z-forward) — flip axes if needed
3. Resample to match CARE-PD expected input length (typically 243 frames at 17 fps equivalent)

### Step 3 — Model Inference
Run the trained CARE-PD model checkpoint using the repo's existing `run.py` or `eval_only.py`. Output is a UPDRS gait score (0–3).

```bash
python eval_only.py \
  --backbone motionbert \
  --config CONFIGNAME.json \
  --hypertune 0 \
  --num_folds -1 \
  --tuned_config ./configs/best_configs_augmented/....json
```

---

## Implementation Notes

**Complexity:** Moderate. The joint mapping is a known conversion (~1–2 days of coding + visual debugging). The main risk is axis misalignment — if joints are flipped or rotated, model output will be unreliable. Always visualize the mapped skeleton before running inference.

**Recommended debugging tool:** Plot the 17 h36m joints as a stick figure on top of the original video frame to verify the skeleton looks correct before feeding into the model.

**Post-session processing:** Gait scoring runs post-session (not real-time), same as the existing MediaPipe compliance validation. Video is processed after upload, score is appended to the session JSON payload.

---

## Full Protocol Summary

| Exercise | Sensor | MDS-UPDRS Item | Training Data |
|---|---|---|---|
| Resting Tremor | Glove IMUs | 3.17–3.18 | PPMI / ALAMEDA |
| Finger Tapping | Glove flex + IMUs | 3.4 | PPMI / ALAMEDA |
| Hand Open/Close | Glove flex + IMUs | 3.5 | PPMI / ALAMEDA |
| Pronation/Supination | Glove IMUs | 3.6 | PPMI / ALAMEDA |
| 10-Meter Walk | Phone camera + MediaPipe Pose | 3.10 | CARE-PD / Daphnet |

---

## References

- Adeli et al., "CARE-PD: A Multi-Site Anonymized Clinical Dataset for Parkinson's Disease Gait Assessment," NeurIPS 2025
- Lugaresi et al., "MediaPipe: A Framework for Building Perception Pipelines," arXiv:1906.08172
- Daphnet Freezing of Gait Dataset — UCI ML Repository
