# Blues + DPU Notes for PD Glove

This note summarizes key takeaways from the Gemini discussion and maps them to this repository's current architecture.

## What "Blues" means in practice

Blues is best treated as an IoT connectivity platform built around:

- **Notecard**: a hardware module handling WAN connectivity, secure transport, and low-power data pumping.
- **Notehub**: a routing/orchestration layer that forwards device data into cloud targets.
- **Open-at-the-edge model**: SDKs/reference hardware are generally open; managed cloud services and core modem firmware remain vendor-managed.

For this project, that means Blues can be added without rewriting the local tremor DSP stack.

## DPU framing (useful mental model)

For PD glove design discussions, it is reasonable to frame Notecard as an **"IoT-scale connectivity DPU"**:

- It offloads WAN concerns (networking, retries, secure transport, power-aware sync).
- It isolates the host (Pi) from direct internet exposure.
- It keeps the host focused on sensing, DSP, and clinical inference.

Important caveat: this is a **functional analogy**, not a throughput equivalence to data-center DPUs/SmartNICs.

## Why this helps PD glove specifically

Given the current repo architecture (Pi 5 + multi-IMU + local DSP), Blues-style offload can improve:

- **Reliability**: durable store-and-forward uplink for clinical summaries.
- **Power profile**: less always-on network management on the Pi side.
- **Security posture**: reduced attack surface vs directly exposing host networking.
- **Operational simplicity**: JSON request-driven API rather than custom modem/network stack code.

## What to keep local vs what to offload

Keep local on Pi (already aligned with this repo):

- 5-channel IMU acquisition (`sensor_reader.py`)
- tremor-band filtering + FFT (`dsp_pipeline.py`)
- future local model inference (TFLite Transformer)

Offload to Notecard/Notehub path:

- encrypted backhaul transport
- retry/backoff + intermittent connectivity handling
- delayed/batched uploads of compact session summaries
- lightweight "device heartbeat" and remote health signals

## Implementations to speed up sensory processing

The fastest path is not moving DSP off Pi; it is reducing network/IO overhead around it.

### 1) Event-driven uplink instead of continuous raw streaming

Upload only when local features cross significance thresholds (e.g., tremor band power/frequency stability windows). This preserves CPU cycles and network budget for sensing.

### 2) Feature-first payloads

Transmit derived features per window/channel rather than raw IMU streams:

- dominant frequency
- band power (4-6 Hz)
- confidence/quality flags
- per-session metadata (duration, effective_hz, retries)

This reduces serialization/transmit load and keeps local loop timing stable.

### 3) Dual-path buffering

- **Fast path**: immediate alert/event notes for high-confidence symptom spikes.
- **Bulk path**: periodic summary notes for trend analysis.

This avoids blocking critical uploads behind larger routine payloads.

### 4) Backpressure-safe sensor loop

Enforce strict separation between acquisition/DSP cadence and uplink cadence:

- acquisition and DSP stay deterministic
- networking remains asynchronous and non-blocking to sensor read timing

### 5) Health telemetry as first-class signal

Publish infrastructure metrics (effective_hz, retries, dropped windows) beside clinical metrics so downstream systems can distinguish physiology from pipeline artifacts.

## Suggested message contract (minimal)

Example compact event body:

```json
{
  "req": "note.add",
  "body": {
    "device_id": "pdg-001",
    "session_id": "20260322T1100Z",
    "window_s": 2.0,
    "channel": 3,
    "axis": "ax",
    "dom_freq_hz": 4.8,
    "band_power_4_6": 32.48,
    "quality": {
      "effective_hz": 71.3,
      "retries": 0
    },
    "event": "tremor_window"
  }
}
```

## Integration sketch for this repo

1. Keep `sensor_reader.py` + `dsp_pipeline.py` as source of truth for feature generation.
2. Add a small transport adapter module (future) that converts DSP outputs into compact event/summary JSON.
3. Use configurable thresholds for event emission to avoid noise-triggered bursts.
4. Preserve privacy-by-design: no raw biometric export unless explicitly needed for debug sessions.

## Risks and controls

- **Risk**: over-aggressive thresholding misses subtle episodes.  
  **Control**: combine event thresholds with periodic low-rate summaries.

- **Risk**: transport queue growth during long outages.  
  **Control**: cap queue, prioritize high-severity events, emit queue-depth health metrics.

- **Risk**: cloud coupling.  
  **Control**: keep local schema/versioning explicit and transport adapter modular.

## Bottom line

For this PD glove, Blues is most valuable as a **connectivity and reliability offload layer** around an on-device sensing/DSP pipeline. The architecture should optimize local deterministic signal processing first, then ship compact, clinically meaningful features/events through a resilient WAN path.
