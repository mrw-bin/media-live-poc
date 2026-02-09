
import time, os
from scheduler.hybrid_scheduler import add_new_file

MEDIA_DIR = "/media"
PLAYLIST = "/app/playlist.txt"

known = set(os.listdir(MEDIA_DIR))

def append_to_playlist(fname):
    with open(PLAYLIST, 'a') as p:
        p.write(f"file {MEDIA_DIR}/{fname}
")
    print(f"[WATCHER] Added to playlist: {fname}")

while True:
    current = set(os.listdir(MEDIA_DIR))
    new_files = current - known

    for f in sorted(new_files):
        if f.lower().endswith('.mp4'):
            append_to_playlist(f)
            # TODO: use ffprobe to detect real duration; for POC assume 1800s
            add_new_file(f, duration=1800)

    known = current
    time.sleep(2)
