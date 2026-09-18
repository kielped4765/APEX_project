import hmac     # Import built in library for Hash based message authentication
import hashlib  # Import Python's built in cryptographic library
import time     # Import built in library to track and generate time based values
import pytest   # Import the pytest framework for writing and running unit tests
from monitor.verifier import TelemetryVerifier, VerificationError

@pytest.fixture     # Decorator telling pytest that this function provides a reuseable test feature
def secret_key():
    """Fixture providing a standard secret key for testing HMAC verification."""
    return b"apex_secure_test_secret_2026"      # Return a raw byte string to act as a shared secret key

@pytest.fixture     # Decorator registering this function as a test fixture
def verifier(secret_key):
    """Fixture providing an initialized TelemetryVerifier instance."""
    return TelemetryVerifier(secret_key=secret_key, max_time_drift=5.0)     # Initialize and return the verifier using the secret key fixture

def generate_valid_payload(secret_key, sequence_num=1, timestamp=None): 
    """Helper function to create a valid signed telemetry payload."""
    ts = timestamp if timestamp is not None else time.time()    # Use the provided timestamp, or default to current system time
    # Construct the message payload string to sign
    message = f"{sequence_num}:{ts}:data_payload".encode("utf-8")
    signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest() # Generates a secure HMAC-SHA256 hash string

    return {
        "sequence_num": sequence_num,
        "timestamp": ts,
        "data": "data_payload",
        "signature": signature,
    }   # Returns a dictionary payload bundled with its valid cryptographic signature

def test_verify_valid_telemetry(verifier, secret_key):  
    """Test that a payload with a tampered signature is rejected."""
    payload = generate_valid_payload(secret_key, sequence_num=2)
    # Tamper with the signature
    payload["signature"] = "invalid_signature_hash_string"

    with pytest.raises(VerificationError) as excinfo:
        verifier.verify_frame(payload)
    assert "HMAC signature verification failed" in str(excinfo.value)

def test_verify_sequence_gap(verifier, secret_key):
    """Test that out-of-sequence frames trigger a sequence violation warning/error."""
    # Send sequence 1 first to establish baseline
    payload_1 = generate_valid_payload(secret_key, sequence_num=1)
    verifier.verify_frame(payload_1)

    # Send sequence 5 directly (skipping 2, 3, 4)
    payload_5 = generate_valid_payload(secret_key, sequence_num=5)

    with pytest.raises(VerificationError) as excinfo:
        verifier.verify_frame(payload_5)
    assert "Sequence number anomaly detected" in str(excinfo.value)

def test_verify_replay_attack(verifier, secret_key):
    """Test that replaying an older sequence number is blocked."""
    # Send sequence 10
    payload_10 = generate_valid_payload(secret_key, sequence_num=10)
    verifier.verify_frame(payload_10)

    # Attempt to replay sequence 10 (or lower)
    payload_old = generate_valid_payload(secret_key, sequence_num=10)

    with pytest.raises(VerificationError) as excinfo:
        verifier.verify_frame(payload_old)
    assert "Replay attack detected" in str(excinfo.value)

def test_verify_timestamp_drift(verifier, secret_key):
    """Test that payloads with a timestamp too far in the past or future are rejected."""
    # Create payload with a timestamp 10 seconds in the past (exceeding max_time_drift)
    expired_time = time.time() - 10.0
    payload = generate_valid_payload(
        secret_key, sequence_num=15, timestamp=expired_time
    )

    with pytest.raises(VerificationError) as excinfo:
        verifier.verify_frame(payload)
    assert "Timestamp drift out of acceptable bounds" in str(excinfo.value)