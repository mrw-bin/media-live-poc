import subprocess
import json
import os


def get_media_duration(path: str) -> float:
    """
    Return duration (seconds) using ffprobe.
    Falls back to 0.0 on failure.
    """
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            path
        ]
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)

        # Prefer format.duration, fall back to max stream duration if present
        dur = None
        if "format" in data and "duration" in data["format"]:
            dur = float(data["format"]["duration"])
        else:
            # Try streams duration
            stream_durs = []
            for st in data.get("streams", []):
                d = st.get("duration")
                if d is not None:
                    try:
                        stream_durs.append(float(d))
                    except ValueError:
                        pass
            if stream_durs:
                dur = max(stream_durs)

        return float(dur) if dur is not None else 0.0

    except Exception as e:
        print(f"[FFPROBE] Failed to read duration for {path}: {e}")
        return 0.0


def scan_media_directory(media_dir: str):
    """
    Scan media directory for playable files and return a list of dicts:
    [{"file": "name.mp4", "duration": 123.45}, ...]
    """
    exts = {".mp4", ".mov", ".mkv", ".m4v"}
    items = []
    try:
        for f in sorted(os.listdir(media_dir)):
            if f.startswith("."):
                continue
            _, ext = os.path.splitext(f)
            if ext.lower() in exts:
                full = os.path.join(media_dir, f)
                d = get_media_duration(full)
                items.append({"file": f, "duration": d})
    except FileNotFoundError:
        print(f"[FFPROBE] Media directory does not exist: {media_dir}")
    return items