
import base64

def generate_scte35(duration):
    # POC-only placeholder payload
    cue = b"ü0%" + duration.to_bytes(1, 'big')
    return base64.b64encode(cue).decode('utf-8')
