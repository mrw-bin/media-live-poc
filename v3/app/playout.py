
import json, time, subprocess, threading

DAILY = '/app/scheduler/daily_schedule.json'

ffmpeg_cmd = [
    'ffmpeg', '-re', '-f', 'concat', '-safe', '0', '-i', '/app/playlist.txt',
    '-c:v', 'libx264', '-g', '48', '-keyint_min', '48',
    '-c:a', 'aac', '-ar', '48000', '-b:a', '160k',
    '-hls_time', '6', '-hls_list_size', '10',
    '-hls_flags', 'independent_segments+program_date_time',
    '-master_pl_name', 'master.m3u8',
    '-hls_segment_filename', '/output/seg_%06d.ts',
    '/output/live.m3u8'
]

process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Monitor scheduled breaks and log (POC)
def break_logger():
    start = time.time()
    with open(DAILY) as f:
        data = json.load(f)
    breaks = sorted(data.get('breaks', []), key=lambda b: b['offset'])

    for br in breaks:
        target = br['offset']
        while True:
            elapsed = time.time() - start
            if elapsed >= target:
                print(f"[BREAK] OUT for {br['duration']}s at t={elapsed:.1f}s (offset={target}s)")
                time.sleep(br['duration'])
                print(f"[BREAK] IN at t={time.time()-start:.1f}s")
                break
            time.sleep(0.5)

threading.Thread(target=break_logger, daemon=True).start()

for line in process.stdout:
    print(line, end='')
