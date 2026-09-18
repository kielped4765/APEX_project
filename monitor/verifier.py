import hmac, hashlib, time
from enum import IntEnum


class ThreatClass(IntEnum): 
    CLEAN = 0
    CORRUPT = 1
    REPLAY = 2
    SPOOF = 3
    DRIFT = 4  

class VerificationError(Exception):
    """Custom exception raised when telemetry verification fails."""
    pass

class TelemetryVerifier: 
    def __init__(self, secret_key: bytes, max_time_drift: float = 5.0):
        self.secret_key = secret_key
        self.max_time_drift = max_time_drift
        self.last_seq = -1 

    def verify_frame(self, frame) -> 'tuple[ThreatClass, dict|None]': 
        if isinstance(frame, dict):
            seq = frame.get("sequence_num", 0)
            ts = frame.get("timestamp", time.time())
            data = frame.get("data", "data_payload")
            
            # 1. Recreate the HMAC message exactly matching generate_valid_payload
            message = f"{seq}:{ts}:{data}".encode("utf-8")
            expected_sig = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
            
            frame_sig = frame.get("signature", "")
            if not hmac.compare_digest(expected_sig, frame_sig):  
                raise VerificationError("HMAC signature verification failed")

            # 2. Timestamp Drift Check
            if abs(time.time() - ts) > self.max_time_drift:
                raise VerificationError("Timestamp drift out of acceptable bounds")

            # 3. Sequence Number Checks (Replays and Gaps)
            if self.last_seq != -1:
                if seq <= self.last_seq:
                    raise VerificationError("Replay attack detected")
                if seq > self.last_seq + 1:
                    raise VerificationError("Sequence number anomaly detected")
            
            self.last_seq = seq 
 
            # Default state dictionary for successful validation
            state = {
                'altitude_m': 1000.0, 'latitude_deg': 0.0, 'longitude_deg': 0.0,
                'airspeed_mps': 100.0, 'vertical_speed': 0.0, 'ground_speed_mps': 100.0,
                'pitch_rad': 0.0, 'roll_rad': 0.0, 'yaw_rad': 0.0,
                'pitch_rate': 0.0, 'roll_rate': 0.0, 'yaw_rate': 0.0,
                'engine_rpm': 5000.0, 'thrust_n': 1000.0, 'fuel_flow_kgps': 0.1,
                'fuel_mass_kg': 500.0, 'g_load': 1.0, 'alpha_rad': 0.1,
                'sequence_num': seq, 'sim_time_s': ts
            }
            
            return ThreatClass.CLEAN, state
            
        raise VerificationError("Unsupported frame format")