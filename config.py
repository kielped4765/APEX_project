import os
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv()  # load .env file into environment variables
 
BASE_DIR        = Path(__file__).parent
DB_URL          = f"sqlite:///{BASE_DIR}/data/apex.db"
SOCKET_PATH     = "/tmp/apex_telemetry.sock"
SHARED_MEM_NAME = "apex_ring_buffer"
MODEL_PATH      = BASE_DIR / "ml" / "classifier.pkl"
SCALER_PATH     = BASE_DIR / "ml" / "scaler.pkl"
 
SAMPLE_RATE_HZ   = 50      # engine runs at 50 Hz (20 ms per step)
RING_BUFFER_SIZE = 128     # must match C++ RING_SIZE
ATTACK_RATE      = 0.05    # 5% of frames are attack frames
 
API_HOST = "127.0.0.1"
API_PORT = 8000
 
# Keys loaded from .env — never hardcode secrets
AES_KEY_HEX  = os.getenv("AES_KEY_HEX",  "")

HMAC_KEY_HEX = os.getenv("HMAC_KEY_HEX", "")
 
def get_aes_key()  -> bytes: return bytes.fromhex(AES_KEY_HEX)
def get_hmac_key() -> bytes: return bytes.fromhex(HMAC_KEY_HEX)
