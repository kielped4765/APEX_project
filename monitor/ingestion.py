from .receiver import listen_unix, parse_frame
from .verifier import TelemetryVerifier, ThreatClass
from .classifier import ThreatClassifier
from database.crud import write_telemetry, write_security_event
import config
 
SEVERITY = {
    ThreatClass.CORRUPT: 'HIGH',
    ThreatClass.REPLAY: 'HIGH',
    ThreatClass.SPOOF: 'CRITICAL',
}
DESCS = {
    ThreatClass.CORRUPT: 'HMAC verification failed',
    ThreatClass.REPLAY: 'Replay attack — duplicate sequence number',
    ThreatClass.SPOOF: 'Physics rules — impossible sensor state',
}
 
def run():
    verifier   = TelemetryVerifier(config.get_aes_key(), config.get_hmac_key())
    classifier = ThreatClassifier()
    for raw in listen_unix(config.SOCKET_PATH):
        frame = parse_frame(raw)
        if not frame: continue
        threat, state = verifier.verify(frame)
        ml_conf = None
        if threat == ThreatClass.CLEAN and state:
            threat, ml_conf = classifier.predict(state)
        if state:
            write_telemetry(state, int(threat), ml_conf)
        if threat != ThreatClass.CLEAN:
            sev  = SEVERITY.get(threat,
                   'MEDIUM' if ml_conf and ml_conf > 0.85 else 'LOW')
            desc = DESCS.get(threat,
                   f'ML drift detection (conf={ml_conf:.2%})')
            write_security_event(int(frame.sequence_num),
                int(threat), sev, desc, ml_conf)
            print(f'[INGESTION] {sev}: {desc}')
 
if __name__ == '__main__':
    run()