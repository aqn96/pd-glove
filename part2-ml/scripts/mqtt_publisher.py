"""
D3 — MQTT publisher: encrypts a payload and publishes it with an MQTT v5
Message Expiry Interval, so the broker guarantees it's discarded if not
delivered within that window (bounded, protocol-enforced retention, not a
"please delete this" policy -- see docs/D3_report.md).

Usage:
    .venv/bin/python3 scripts/mqtt_publisher.py [--expiry-seconds N] [--raw]
"""
import argparse
import sys
import time

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from mqtt_common import BROKER_HOST, BROKER_PORT, TOPIC, build_demo_payload, load_demo_key
from security import encrypt_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expiry-seconds", type=int, default=8,
                        help="MQTT v5 message expiry interval")
    parser.add_argument("--raw", action="store_true",
                        help="Include a demo raw sensor window in the payload")
    args = parser.parse_args()

    key = load_demo_key()
    payload = build_demo_payload(include_raw_window=args.raw)
    blob = encrypt_payload(payload, key)
    print(f"Payload (plaintext, for reference): {payload}")
    print(f"Encrypted size: {len(blob)} bytes")

    published = {"done": False, "reason": None}

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            print(f"Connect failed: {reason_code}")
            sys.exit(1)
        props = Properties(PacketTypes.PUBLISH)
        props.MessageExpiryInterval = args.expiry_seconds
        client.publish(TOPIC, blob, qos=1, properties=props)
        print(f"Published to '{TOPIC}' with {args.expiry_seconds}s expiry")

    def on_publish(client, userdata, mid, reason_code, properties):
        published["done"] = True
        client.disconnect()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(BROKER_HOST, BROKER_PORT, clean_start=True)
    client.loop_start()

    t0 = time.time()
    while not published["done"] and time.time() - t0 < 5:
        time.sleep(0.05)
    client.loop_stop()

    if not published["done"]:
        print("WARNING: publish not confirmed within timeout")


if __name__ == "__main__":
    main()
