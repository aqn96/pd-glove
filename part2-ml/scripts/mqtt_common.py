"""
Shared config/payload builder for the D3 MQTT + encryption demo.

DEMO_KEY is hardcoded here purely for local testing -- a real deployment
would provision one key per device at enrollment via a secure key-exchange,
never hardcode a shared key in source.
"""
import os
import time

from security import generate_key

BROKER_HOST  = "localhost"
BROKER_PORT  = 1883
TOPIC        = "pd-glove/pt_demo/session"
_KEY_PATH    = "/tmp/mosquitto_pd_glove/demo.key"

# Fixed for the demo so publisher and subscriber (separate processes) agree
# on the same key. Real deployment: per-device key, not this. Generated
# once and persisted -- NOT regenerated on every import, or publisher and
# subscriber processes would each get a different key.


def load_demo_key() -> bytes:
    if not os.path.exists(_KEY_PATH):
        os.makedirs(os.path.dirname(_KEY_PATH), exist_ok=True)
        with open(_KEY_PATH, "wb") as f:
            f.write(generate_key())
    with open(_KEY_PATH, "rb") as f:
        return f.read()


def build_demo_payload(include_raw_window: bool = False) -> dict:
    """Matches the architecture's exercise-centric JSON payload: identifiers,
    exercise context, and the processed clinical output. `include_raw_window`
    simulates the separate, higher-sensitivity case discussed in the D3
    report -- shipping raw sensor data (e.g. for cloud-side MOMENT
    inference) rather than just the on-device model's score. This is NOT
    the routine payload; it's here to demonstrate that IF raw data is ever
    shipped, it goes through the same encryption + expiry protections.
    """
    payload = {
        "device_id":      "glove-pt_9f2c6f",
        "session_ts":     time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "exercise":       "Resting Tremor",
        "hand_side":      "right",
        "mds_updrs_score": 2,
        "confidence":      0.81,
    }
    if include_raw_window:
        # Small demo window (not the full 974x6) -- illustrative only.
        payload["raw_window"] = [[0.01 * i + 0.001 * c for c in range(6)]
                                  for i in range(20)]
    return payload
