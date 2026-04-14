# Assessment and Therapy Protocol

This document separates **measurement tasks** from **therapeutic exercises** so project usage remains clinically clear.

## 1) Intended Use (Important)

- PD-glove is positioned as a **research monitoring and decision-support** system.
- It is **not** a standalone diagnostic tool.
- MDS-UPDRS-aligned task outputs should be interpreted with clinician oversight.

## 2) Standardized Tremor Assessment Tasks (Data Capture)

Use all three tasks for the strongest signal diversity and better model training.

### A) `3.17_REST` — Rest Tremor of Hands

- Position: forearm supported on table, wrist/hand hanging relaxed over edge.
- Duration: 15-30 seconds.
- Notes: keep limb passive; optional mental distraction task can reduce voluntary suppression.

### B) `3.15_POSTURAL` — Postural Tremor of Hands

- Position: hand lifted level with forearm, palm down.
- Duration: 30 seconds.
- Notes: supports detection of delayed/re-emergent tremor behavior.

### C) `3.16_KINETIC` — Kinetic Tremor of Hands

- Position: controlled movement segment.
- Duration: 10-20 seconds.
- Suggested movement for constrained setup: slow lift -> brief hold -> slow lower.
- If range allows, include finger-to-target movement for richer kinetic signal.

## 3) Therapeutic Hand Exercises (Symptom Management)

These are separate from assessment scoring and should be logged as therapy mode, not diagnostic mode.

1. Finger tapping (thumb-index, large amplitude).
2. Thumb opposition (thumb to each fingertip, forward and reverse).
3. Hand open/close with full range.
4. Grip squeezes (light resistance).
5. Controlled wrist extension/flexion.

Suggested routine: short daily sessions with consistent timing, then compare pre/post metrics over time.

## 4) Documentation and Labeling Guidance

- Keep assessment labels explicit: `3.17_REST`, `3.15_POSTURAL`, `3.16_KINETIC`.
- Keep therapy labels separate (example: `THERAPY_TAP`, `THERAPY_OPPOSITION`).
- Do not mix assessment and therapy windows in one labeled segment.
