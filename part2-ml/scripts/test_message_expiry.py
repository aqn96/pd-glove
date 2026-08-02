"""
D3 — Validates that MQTT v5 Message Expiry Interval actually bounds how
long a payload can persist waiting for delivery, rather than just asserting
it in a report. Two cases:

1. SHORT expiry: publish while the subscriber is "offline" (a persistent
   session, disconnected), wait past the expiry, then reconnect. Message
   should NOT be delivered -- the broker discarded it.
2. LONG expiry (control): same setup, but wait less than the expiry.
   Message SHOULD be delivered -- proves the mechanism isn't just "nothing
   ever arrives," it specifically respects the configured expiry.

Usage:
    .venv/bin/python3 scripts/test_message_expiry.py
"""
import time

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from mqtt_common import BROKER_HOST, BROKER_PORT, TOPIC, build_demo_payload, load_demo_key
from security import encrypt_payload, decrypt_payload

CLIENT_ID = "pd-glove-cloud-subscriber-demo"


def establish_offline_session():
    """Connect with a persistent session (so the broker keeps the
    subscription even after we disconnect), then disconnect -- simulating
    a subscriber that's temporarily offline."""
    connected = {"ok": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        connected["ok"] = (reason_code == 0)
        client.subscribe(TOPIC, qos=1)

    props = Properties(PacketTypes.CONNECT)
    props.SessionExpiryInterval = 3600
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID,
                        protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT, clean_start=True, properties=props)
    client.loop_start()
    t0 = time.time()
    while not connected["ok"] and time.time() - t0 < 5:
        time.sleep(0.05)
    client.loop_stop()
    client.disconnect()


def publish_with_expiry(expiry_seconds: int, key: bytes):
    payload = build_demo_payload()
    blob = encrypt_payload(payload, key)
    done = {"ok": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        props = Properties(PacketTypes.PUBLISH)
        props.MessageExpiryInterval = expiry_seconds
        client.publish(TOPIC, blob, qos=1, properties=props)

    def on_publish(client, userdata, mid, reason_code, properties):
        done["ok"] = True
        client.disconnect()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(BROKER_HOST, BROKER_PORT, clean_start=True)
    client.loop_start()
    t0 = time.time()
    while not done["ok"] and time.time() - t0 < 5:
        time.sleep(0.05)
    client.loop_stop()


def reconnect_and_check(listen_seconds: int, key: bytes) -> bool:
    """Reconnects the SAME persistent session and checks whether a queued
    message arrives. Returns True if a message was received and decrypted."""
    received = {"ok": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        pass  # subscription persists from the earlier session

    def on_message(client, userdata, msg):
        payload = decrypt_payload(msg.payload, key)
        print(f"  -> message delivered: {payload['exercise']} @ {payload['session_ts']}")
        received["ok"] = True

    props = Properties(PacketTypes.CONNECT)
    props.SessionExpiryInterval = 3600
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID,
                        protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, clean_start=False, properties=props)
    client.loop_start()
    time.sleep(listen_seconds)
    client.loop_stop()
    client.disconnect()
    return received["ok"]


def run_case(name: str, expiry_seconds: int, wait_seconds: int, key: bytes) -> bool:
    print(f"\n=== {name} ===")
    print(f"Subscriber goes offline (persistent session)...")
    establish_offline_session()

    print(f"Publishing with {expiry_seconds}s expiry while subscriber is offline...")
    publish_with_expiry(expiry_seconds, key)

    print(f"Waiting {wait_seconds}s before reconnecting...")
    time.sleep(wait_seconds)

    print("Reconnecting subscriber...")
    delivered = reconnect_and_check(listen_seconds=3, key=key)
    print(f"Message delivered: {delivered}")
    return delivered


def main():
    key = load_demo_key()

    # Case 1: expiry (3s) shorter than the offline wait (6s) -> should be discarded
    case1_delivered = run_case("Case 1: short expiry, long offline wait -> expect DROP",
                               expiry_seconds=3, wait_seconds=6, key=key)

    # Case 2: expiry (60s) longer than the offline wait (2s) -> should be delivered
    case2_delivered = run_case("Case 2: long expiry, short offline wait -> expect DELIVER",
                               expiry_seconds=60, wait_seconds=2, key=key)

    print("\n=== Result ===")
    ok = (not case1_delivered) and case2_delivered
    if ok:
        print("PASS: message expiry is enforced by the broker as configured -- "
              "short-expiry messages are discarded before an offline subscriber "
              "returns, long-expiry messages survive and are delivered.")
    else:
        print(f"UNEXPECTED: case1_delivered={case1_delivered} (want False), "
              f"case2_delivered={case2_delivered} (want True)")


if __name__ == "__main__":
    main()
