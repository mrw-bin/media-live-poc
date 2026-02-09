import json, time, subprocess
from scte import generate_scte35

SCHEDULE = "/app/scheduler/daily_schedule.json"
PLAYLIST = "/app/playlist.txt"

with open(SCHEDULE) as f:
    schedule = json.load(f)

breaks = schedule.get("breaks", [])

ffmpeg_cmd = [
    "ffmpeg", "-re", "-f", "concat", "-safe", "0", "-i", PLAYLIST,
    "-c:v", "libx264", "-g", "48", "-keyint_min", "48",
    "-c:a", "aac", "-hls_time", "6", "-hls_list_size", "10",
    "-hls_flags", "delete_segments+independent_segments+program_date_time+add_daterange",
    "-master_pl_name", "/output/master.m3u8",
    "-hls_segment_filename", "/output/seg_%06d.ts",
    "/output/live.m3u8"
]

print("[PLAYOUT] Starting FFmpeg...")
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
start = time.time()

for br in breaks:
    offset, duration = br["offset"], br["duration"]
    while True:
        if time.time() - start >= offset:
            payload = generate_scte35(duration)
            print(f"[SCTE] Injecting break at {time.time()-start:.1f}s for {duration}s")
            process.stdin.write(f"{payload}
".encode())
            process.stdin.flush()
            break
        time.sleep(1)

process.wait()
