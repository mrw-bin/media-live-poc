import base64

def generate_scte35(duration):
    duration_int = int(round(duration))
    byte_len = max(1, (duration_int.bit_length() + 7) // 8)
    cue = b"\xFC0%" + duration_int.to_bytes(byte_len, "big")
    return cue.decode("latin1")
