import json
import time
import os
import subprocess
from scte import generate_scte35

SCHEDULE = "/app/scheduler/daily_schedule.json"
PLAYLIST = "/app/playlist.txt"

def load_schedule():
    with open(SCHEDULE) as f:
        schedule = json.load(f)
    breaks = schedule.get("breaks", [])
    total = float(schedule.get("total_duration") or 0.0)
    return breaks, total

def safe_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0

def start_ffmpeg():
    ffmpeg_cmd = [
        "ffmpeg",
        # Try to loop at the ffmpeg level. If ffmpeg still exits (e.g., demuxer quirks),
        # we will restart it from Python.
        "-stream_loop", "-1",
        "-re",
        "-f", "concat", "-safe", "0",
        "-i", PLAYLIST,
        "-c:v", "libx264",
        "-g", "48", "-keyint_min", "48",
        "-c:a", "aac",
        "-hls_time", "6",
        "-hls_list_size", "10",
        "-hls_flags", "delete_segments+independent_segments+program_date_time",
        "-hls_start_number_source", "datetime",
        "-hls_segment_filename", "/output/seg_%06d.ts",
        "/output/live.m3u8"
    ]
    print("[PLAYOUT] Starting FFmpeg...")
    return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

def main():
    # Load initial schedule (wait until available if needed)
    while not os.path.exists(SCHEDULE) or not os.path.exists(PLAYLIST):
        print("[PLAYOUT] Waiting for schedule/playlist...")
        time.sleep(1)

    breaks, total_duration = load_schedule()
    schedule_mtime = safe_mtime(SCHEDULE)

    if total_duration <= 0:
        print("[PLAYOUT] Warning: total_duration is 0. SCTE scheduling will not advance until schedule is rebuilt.")

    process = start_ffmpeg()

    start = time.time()
    break_index = 0

    # Hot-reload support: if schedule.json changes during playback,
    # reload and advance break_index to the next break >= now
    def maybe_reload(now):
        nonlocal breaks, total_duration, schedule_mtime, break_index
        mtime = safe_mtime(SCHEDULE)
        if mtime != schedule_mtime and mtime > 0:
            try:
                new_breaks, new_total = load_schedule()
                schedule_mtime = mtime
                breaks = new_breaks
                total_duration = float(new_total or 0.0)
                # Reposition break_index to the first future break
                bi = 0
                while bi < len(breaks) and breaks[bi].get("offset", 0.0) < now:
                    bi += 1
                break_index = bi
                print(f"[PLAYOUT] Reloaded schedule. total_duration={total_duration:.2f}s, "
                      f"pending breaks={len(breaks)-break_index}.")
            except Exception as e:
                print(f"[PLAYOUT] Failed to reload schedule: {e}")

    while True:
        # If ffmpeg died for any reason, restart to maintain continuity
        if process.poll() is not None:
            print("[PLAYOUT] FFmpeg exited; restarting...")
            time.sleep(1)
            process = start_ffmpeg()
            start = time.time()
            break_index = 0

        now = time.time() - start

        # Detect playlist loop boundary and reset timing for SCTE schedule
        if total_duration > 0 and now >= total_duration:
            print("[PLAYOUT] Playlist loop detected — resetting SCTE timing.")
            start = time.time()
            now = 0.0
            break_index = 0

        # Attempt to hot-reload schedule if changed on disk
        maybe_reload(now)

        # Inject next scheduled break
        if break_index < len(breaks):
            b = breaks[break_index]
            offset = float(b.get("offset", 0.0))
            dur = float(b.get("duration", 0.0))
            if now >= offset:
                payload = generate_scte35(dur)
                print(f"[SCTE] Break #{break_index+1} at {now:.1f}s for {dur:.0f}s")
                try:
                    if process.stdin:
                        process.stdin.write(payload.encode())
                        process.stdin.flush()
                except (BrokenPipeError, ValueError) as e:
                    print(f"[SCTE] FFmpeg stdin issue; skipping injection. {e}")
                break_index += 1

        time.sleep(0.1)

if __name__ == "__main__":
    main()