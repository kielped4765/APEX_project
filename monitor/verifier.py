import hmac as py_hmac, hashlib, struct, math   # Imports built in modules for HMAC generation
from enum import IntEnum    # Imports IntEnum to create integer-backed enumerated constants
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # Imports cryptographic primitives for AES encryption/decryption
from cryptography.hazmat.backends import default_backend # Imports the default cryptographic backend handler
from receiver import RawFrame, IV_SZ, PAYLOAD_SZ # Imports the RawFrame structure and size constants from the receiver module

class ThreatClass(IntEnum): # Defines an enumeration class
    CLEAN=0; CORRUPT=1; REPLAY=2; SPOOF=3; DRIFT=4  # Enumerated threat levels

STATE_FMT = '17dQd'     # 17 doubles, uint64, double # Format string matching the C++ struct layout for binary
STATE_SIZE = struct.calcsize(STATE_FMT) # Calculates the exact byte size of the state struct
STATE_KEYS = ['altitude_m','latitude_deg','longitude_deg','airspeed_mps', # List of keys used to map unpacked state values into a dictionary
    'vertical_speed','ground_speed_mps','pitch_rad','roll_rad','yaw_rad', # State keys continued
    'pitch_rate','roll_rate','yaw_rate','engine_rpm','thrust_n', # State keys continued
    'fuel_flow_kgps','fuel_mass_kg','g_load','alpha_rad', # State keys continued
    'sequence_num','sim_time_s'] # State keys continued

class FrameVerifier: # Class responsible for verifying frame integrity, sequence,  and rules
    def __init__(self, aes_key:bytes, hmac_key:bytes): # Initializes the verifier with encryption and HMAC keys
        self.aes_key=aes_key; self.hmac_key=hmac_key; self.last_seq=-1 # Sets instance variables

    def verify(self, frame:RawFrame) -> 'tuple[ThreatClass, dict|None]': # Main verification pipeline method returning threat classification and state data
            # 1 HMAC - authenticate before anything else
        body = struct.pack(f'<IBBQq{IV_SZ}s{PAYLOAD_SZ}s', # Reconstructs the exact binary body used to generate the original HMAC
            frame.magic,frame.frame_type,frame.attack_label, # Packs frame header fields
            frame.sequence_num,frame.timestamp_us,frame.iv,frame.payload) # Packs sequence, timestamp, IV, and payload fields
        exp = py_hmac.new(self.hmac_key, body, hashlib.sha256).digest() # Computes the expected SHA-256 HMAC digest using the secret key
        if not py_hmac.compare_digest(exp, frame.hmac):  # constant-time # Compares the expected HMAC with the frame's HMAC in constant time to prevent timing attacks
            return ThreatClass.CORRUPT, None # Returns CORRUPT threat class if HMAC verification fails

        # 2. Sequence Number - catch replays 
        if frame.sequence_num <= self.last_seq: # Checks if the current sequence number is less than or equal to the last seen sequence number
            return ThreatClass.REPLAY, None # Returns REPLAY threat class if sequence number is stale or duplicated
        self.last_seq = frame.sequence_num # Updates the last seen sequence number tracker
 
        # 3. Decrypt # Comment step for decryption
        state = self._decrypt(frame) # Attempts to decrypt the payload into state data
        if state is None: return ThreatClass.CORRUPT, None # Returns CORRUPT if decryption fails
 
        # 4. Physics rules # Comment step for physics validation
        return self._rules(state), state # Evaluates physics rules on the state and returns the resulting threat class and state dictionary
 
    def _rules(self, s:dict) -> ThreatClass: # Helper method to check telemetry values against realistic flight physics boundaries
        if not (-500.0 < s['altitude_m'] < 20000.0):      return ThreatClass.SPOOF # Flags spoofing if altitude is outside valid physical limits
        if not (0.0 <= s['airspeed_mps'] <= 408.0):       return ThreatClass.SPOOF # Flags spoofing if airspeed exceeds maximum structural limits
        if not (-5.0 <= s['g_load'] <= 12.0):             return ThreatClass.SPOOF # Flags spoofing if G-load exceeds structural thresholds
        if s['engine_rpm'] < 0 or s['fuel_mass_kg'] < 0: return ThreatClass.SPOOF # Flags spoofing if engine RPM or fuel mass drops below zero
        if s['vertical_speed']>20.0 and s['thrust_n']<500.0: return ThreatClass.SPOOF # Flags spoofing if climbing fast with near-zero thrust (impossible physics)
        if abs(s['pitch_rad']) > math.pi/2.0:             return ThreatClass.SPOOF # Flags spoofing if pitch exceeds 90 degrees
        return ThreatClass.CLEAN # Returns CLEAN if all physics checks pass
 
    def _decrypt(self, frame:RawFrame) -> 'dict|None': # Helper method to handle AES-CBC payload decryption and unpacking
        try: # Try block to catch any decryption or unpacking errors
            c = Cipher(algorithms.AES(self.aes_key), modes.CBC(frame.iv), # Initializes the AES cipher in CBC mode using the frame's IV
                       backend=default_backend()) # Specifies the cryptographic backend
            plain = c.decryptor().update(frame.payload) # Decrypts the encrypted payload bytes
            return dict(zip(STATE_KEYS, struct.unpack(STATE_FMT, plain[:STATE_SIZE]))) # Unpacks the plaintext bytes into state values and maps them to keys in a dictionary
        except: return None # Returns None if an exception occurs during decryption or parsing