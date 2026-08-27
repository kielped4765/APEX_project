import socket, struct, os               # Python's built-in modules for handling network sockets, unpacking binary C-style data structures, and interacting with the file system
from dataclasses import dataclass       # Imports the @dataclass decorator, which simplifies creating classes primarily used to store data

FRAME_MAGIC = 0xAE1A337                 # Defines a unique 32-bit magic number header to identify and validate valid APEX telemetry frames
HMAC_SZ=32; IV_SZ=16; PAYLOAD_SZ=128    # Constants defining the exact byte sizes for the cryptographic HMAC (SHA-256), initialization vector (AES-CBC), and the encrypted telemetry payload.

# Mirrors C++ TelemetryFrame with #prgma pack(1)
# < = little-endian I=uint32 B=uint8 Q=uint64 q=int64
FRAME_FMT = f"<IBBQq{IV_SZ}s{PAYLOAD_SZ}{HMAC_SZ}s"     # C++ Calculates Constructs Decorator Defines HMAC[cite: IV, Python's RawFrame
FRAME_SIZE = struct.calcsize(FRAME_FMT)                 

@dataclass                                              # Decorator that automatically generates boilerplate methods
class RawFrame:                                         # Defines a data container class that mirrors the C++ telemetry frame layout
    magic:int; frame_type:int; attack_label:int         # Fields storing the header magic number, frame type, and attack classification label as integers
    sequence_num:int; timestamp_us:int                  # Fields storing the packet sequence number and the microsecond-precision timestamp
    iv:bytes; payload:bytes; hmac:bytes                 # Fields storing the AES initialization vector, encrypted payload, and HMAC bytes

def parse_frame(data:bytes) -> 'RawFrame|None':         # Function that takes raw bytes and parses them into a RawFrame object, or returns None if invalid
    if len(data) < FRAME_SIZE: return None              # Guard check ensuring the input data buffer is large enough to contain a complete frame
    f = RawFrame(*struct.unpack(FRAME_FMT, data[:FRAME_SIZE])) # Unpacks the exact binary byte slice using the defined format string and passes it into the RawFrame initializer
    return f if f.magic == FRAME_MAGIC else None
 
def listen_unix(socket_path:str):                       # Generator function that sets up a UNIX domain socket server to listen for incoming telemetry
    """Generator: yields exactly FRAME_SIZE bytes per frame."""
    if os.path.exists(socket_path): os.remove(socket_path)      # Removes any leftover socket server 
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as srv:  # Creates a stream-oriented UNIX domain socket
        srv.bind(socket_path)
        srv.listen(1)
        print(f'[RECEIVER] Listening on {socket_path}')
        conn, _ = srv.accept()
        print('[RECEIVER] Broker connected.')
        with conn:
            buf = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk: break
                buf += chunk
                while len(buf) >= FRAME_SIZE:
                    yield buf[:FRAME_SIZE]
                    buf = buf[FRAME_SIZE:]