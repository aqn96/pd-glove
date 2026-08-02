"""
D3 — MQTT subscriber: receives an encrypted payload, decrypts it exactly
once, extracts only the derived summary worth keeping, and explicitly
discards the plaintext (including any raw sensor window) before the
process ends -- nothing plaintext is written to disk or logged beyond the
processed summary.

Usage:
    .venv/bin/python3 scripts/mqtt_subscriber.py [--listen-seconds N] [--persistent]
"""
import argparse
import sys
import time

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from mqtt_common import BROKER_HOST, BROKER_PORT, TOPIC, load_demo_key
from security import decrypt_payload

PERSISTENT_CLIENT_ID = "pd-glove-cloud-subscriber-demo"


def process_once_and_forget(blob: bytes, key: bytes):
    """Decrypt exactly once, keep only the derived summary, then let the
    plaintext (and any raw_window) go out of scope -- demonstrating
    'open once, process, then delete' rather than persisting raw content."""
    payload = decrypt_payload(blob, key)  # plaintext exists only in this local scope

    had_raw = "raw_window" in payload
    summary = {
        "device_id":       payload["device_id"],
        "session_ts":      payload["session_ts"],
        "exercise":        payload["exercise"],
        "mds_updrs_score": payload["mds_updrs_score"],
    }

    print(f"Processed summary (this is all that gets kept/logged): {summary}")
    if had_raw:
        print(f"Payload included a raw sensor window ({len(payload['raw_window'])} samples) "
              f"-- discarded now, never written to disk, not part of the retained summary.")

    del payload  # explicit: the plaintext (incl. raw window) is not retained past this point
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-seconds", type=int, default=15)
    parser.add_argument("--persistent", action="store_true",
                        help="Use a persistent MQTTv5 session (for the expiry test)")
    args = parser.parse_args()

    key = load_demo_key()
    state = {"received": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            print(f"Connect failed: {reason_code}")
            sys.exit(1)
        client.subscribe(TOPIC, qos=1)
        print(f"Subscribed to '{TOPIC}', listening for up to {args.listen_seconds}s...")

    def on_message(client, userdata, msg):
        state["received"] = True
        process_once_and_forget(msg.payload, key)

    connect_props = Properties(PacketTypes.CONNECT)
    if args.persistent:
        connect_props.SessionExpiryInterval = 3600  # keep the session (and any
        client_id = PERSISTENT_CLIENT_ID              # queued messages) around
        clean_start = False                            # while "offline"
    else:
        client_id = ""
        clean_start = True

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id,
                        protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, clean_start=clean_start,
                   properties=connect_props)
    client.loop_start()

    t0 = time.time()
    while not state["received"] and time.time() - t0 < args.listen_seconds:
        time.sleep(0.1)
    client.loop_stop()
    client.disconnect()

    if not state["received"]:
        print(f"No message received within {args.listen_seconds}s window.")


if __name__ == "__main__":
    main()
