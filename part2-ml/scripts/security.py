"""
D3 — Application-layer encryption for the glove's cloud payload.

AES-256-GCM: authenticated encryption, so tampering with the ciphertext is
detected on decrypt (not just confidentiality -- integrity too). This
encrypts the payload the Pi would publish over MQTT before it ever reaches
the network layer, independent of whatever transport security (TLS) sits
underneath.

Threat model this addresses: an adversary who can read network traffic or
who compromises the cloud-side broker/storage should not be able to read
or silently modify a patient's payload. It does NOT protect data while
it's in plaintext during active processing (e.g. inside a cloud inference
service actually using the data) -- that's a separate, unsolved concern,
noted in docs/D3_report.md rather than glossed over here.

Usage:
    .venv/bin/python3 scripts/security.py
"""
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE_BYTES   = 32  # AES-256
NONCE_SIZE_BYTES = 12  # standard GCM nonce size


def generate_key() -> bytes:
    """A real deployment would provision one key per device (e.g. at
    enrollment, via a secure key-exchange), not generate one ad hoc like
    this -- this is for local testing only."""
    return AESGCM.generate_key(bit_length=KEY_SIZE_BYTES * 8)


def encrypt_payload(payload: dict, key: bytes) -> bytes:
    """Serializes payload to JSON and encrypts it. Returns nonce || ciphertext
    (ciphertext includes the GCM authentication tag), ready to publish."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE_BYTES)
    plaintext = json.dumps(payload).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return nonce + ciphertext


def decrypt_payload(blob: bytes, key: bytes) -> dict:
    """Inverse of encrypt_payload. Raises cryptography.exceptions.InvalidTag
    if the ciphertext was tampered with or the key is wrong -- this is GCM's
    built-in integrity check, not something this code adds on top."""
    aesgcm = AESGCM(key)
    nonce, ciphertext = blob[:NONCE_SIZE_BYTES], blob[NONCE_SIZE_BYTES:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return json.loads(plaintext.decode("utf-8"))


def _self_test():
    from cryptography.exceptions import InvalidTag

    key = generate_key()
    payload = {
        "device_id": "glove-pt_9f2c6f",
        "session_ts": "2026-07-30T14:22:00Z",
        "exercise": "Resting Tremor",
        "mds_updrs_score": 2,
        "confidence": 0.81,
    }

    print("=== Round-trip test ===")
    blob = encrypt_payload(payload, key)
    print(f"Plaintext size : {len(json.dumps(payload))} bytes")
    print(f"Ciphertext size: {len(blob)} bytes (includes 12-byte nonce + 16-byte auth tag)")
    print(f"Ciphertext is not readable JSON: {blob[:20]!r}...")
    recovered = decrypt_payload(blob, key)
    assert recovered == payload, "round-trip mismatch"
    print(f"Decrypted matches original: {recovered}")

    print("\n=== Tamper detection test ===")
    tampered = bytearray(blob)
    tampered[-1] ^= 0xFF  # flip the last byte
    try:
        decrypt_payload(bytes(tampered), key)
        print("FAIL: tampered ciphertext decrypted without error")
    except InvalidTag:
        print("PASS: tampered ciphertext correctly rejected (GCM auth tag mismatch)")

    print("\n=== Wrong key test ===")
    wrong_key = generate_key()
    try:
        decrypt_payload(blob, wrong_key)
        print("FAIL: decrypted with wrong key without error")
    except InvalidTag:
        print("PASS: wrong key correctly rejected")


if __name__ == "__main__":
    _self_test()
