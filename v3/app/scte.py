import base64

def generate_scte35(duration):
    if not 0 <= duration <= 255:
        raise ValueError("duration must be 0..255")
    cue = b"\xFC0%" + duration.to_bytes(1, "big")
    return base64.b64encode(cue).decode("utf-8")