# Professor Meeting — CS 8674 Part II Setup & Next Steps

**With:** Sarita Singh (s.singh@northeastern.edu)
**Date:** _TBD_
**Format:** Teams (per syllabus)
**Prepared:** 2026-05-31

**Companion docs in the same folder:**
- [next-steps.md](next-steps.md) — full execution plan, risks, weekly schedule
- [literature-review.md](literature-review.md) — submitted, 20 entries + research gap

---

## 60-second briefing (what to lead with)

- **Literature review submitted today** (due 2026-05-31): 20 sources, alphabetical APA, research-gap synthesis tied to D2–D3 contributions.
- **Wrote a Part II execution plan** (`next-steps.md`): week-by-week through Aug 16 with risks and contingencies named.
- **Datasets started:** Daphnet FOG and ALAMEDA tremor downloaded locally; PPMI and mPower waiting on approvals; CARE-PD deferred to S3-via-EC2 in Week 7.
- **Net status:** ~1.5 weeks behind syllabus on the Pre-Planning + Weeks 1–2 technical work because the lit review consumed bandwidth. D1 (Jun 16) is recoverable but tight — the binding-path item is dataset-access lead time, which is why I want to lock AWS + PPMI today.

---

## 1. AWS account setup — top priority

**Headline:** I need this turned on this week. Most of D1 (and all of D2/D3) is blocked without it.

- [ ] How is the school AWS account activated — root credentials, IAM user provisioned by IT, SSO via Northeastern login?
- [ ] What credentials do I get on activation: access key + secret, or console login (I'll create IAM users myself)?
- [ ] **GPU quota** — does the account default to `g4dn.xlarge` access, or do I need to file an AWS support case to request `p3.2xlarge`? (The syllabus mentions both, but `p3` quotas often need a request.)
- [ ] **Region** — `us-east-1` (cheapest GPU) or institutional default?
- [ ] **Budget / spending cap** — anything I should know before spinning up GPU instances? Hard cap, billing alarm threshold?
- [ ] **S3 naming** — should I name the bucket `pd-glove-data-aqnguyen96` or follow a course-wide pattern?
- [ ] **IAM policy template** — anything pre-existing I should clone, or write from scratch?
- [ ] **Co-author access** — Hong Peng, Madhu, Vatsalya: should they get read access to the same S3 bucket, or stay siloed for this course?
- [ ] **Google Colab for early EDA.** The syllabus names Kaggle as the prototyping environment (no session timeouts). Is Colab acceptable for the initial EDA / schema-alignment work this week — before Kaggle is set up — as long as everything migrates to Kaggle once GPU training starts in Week 5? Notebooks land in GitHub either way.

---

## 2. Dataset access

- [ ] **PPMI** — does Northeastern have an institutional DUA / data-sharing arrangement with LONI, or do I apply individually as a graduate researcher? If individual: any letter-of-support template you've used before for previous students?
- [ ] **PPMI → Roche PD App v2** — confirm it's still listed in the LONI portal as a separate collection. (Want to verify before counting on it for the D1 join.)
- [ ] **mPower (Synapse)** — same question: institutional access path or qualified-researcher application?
- [ ] **CARE-PD license discrepancy** — the HuggingFace release `vida-adl/CARE-PD` is `CC BY-NC-ND 4.0`, not `CC BY 4.0` as the syllabus says. Is coursework / thesis use considered non-commercial here, or should I plan to derive only features from it without redistribution?

---

## 3. Scope and direction

- [ ] **Local cohort size.** The PD-glove validation data is currently 9 sessions / 2 subjects. For D2 Transformer training, is that acceptable as the labeled base (PRIMUS-pretrain → fine-tune recipe, per lit review entry #5), or is more data collection expected before D2?
- [ ] **Pi 5 access for D3 latency benchmark.** I'm in Seattle; the prototype is at the lab. Will the Pi 5 be reachable by Week 11 (Jul 29) for the on-device latency measurement, or should I plan an EC2 proxy now and add real Pi 5 numbers in D4?
- [ ] **Paper alignment.** The AIIoT 2026 paper has Hong Peng, Madhu Babu Cherukuri, Vatsalya Dabhi as co-authors. Are D2/D3 results headed toward a follow-on paper with the same team, or coursework-only? Affects how the D2 ablation is framed and whether artifacts need to be embargoed.
- [ ] **Report format.** Any preferred citation style or LaTeX/Word template for the D1–D4 reports? APA 7th (matches the lit review) acceptable?

---

## 4. Logistics

- [ ] **Meeting cadence.** Syllabus says weekly Teams check-ins as needed — would you like a standing slot, or ad-hoc by request?
- [ ] **Best channel for quick questions** — Teams DM, email, or a Teams course channel?
- [ ] **Presentation slots.** Confirming D1 = Jun 16, D2 = Jul 14, D3 = Aug 4, D4 = Aug 16 are the actual presentation dates (not just artifact-due dates).

---

## 5. Heads-up — risks already identified (FYI, not asking permission)

These are written up in full in [next-steps.md §8](next-steps.md); short version below so you've heard them in my voice before reading.

- **R1 — Dataset-access lead time.** PPMI / mPower approvals can take 3–10 days; starting today.
- **R2 — Small labeled cohort.** Plan B is PRIMUS pretrain + fine-tune; Plan C is Evers 2025 prototypical-network architecture.
- **R3 — AWS GPU quota.** Contingency: drop from `p3.2xlarge` to `g4dn.xlarge` with longer training time.
- **R4 — TFLite INT8 accuracy drop > ~3%.** Contingency: per-channel calibration; fallback to FP16.
- **R5 — Pi 5 unavailable for D3.** Contingency: EC2 c-class proxy for the latency benchmark; real Pi 5 numbers added in D4.

---

## 6. Action items / decisions (fill in during the meeting)

| Item | Decision / Owner | Due |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

---

## 7. Followups to send after the meeting

- [ ]
- [ ]
- [ ]

---

## 8. Things to confirm I'll do *before* the meeting

- [ ] Push the master branch so she can see the lit review + plan in `aqn96/pd-glove`.
- [ ] Submit Synapse mPower access application (independent of whether she has an institutional path — having both running in parallel costs nothing).
- [ ] Log into LONI/PPMI and confirm current account status, so the question in §2 is precise rather than open-ended.
