import time, os
MEDIA_DIR = "/media"
PLAYLIST = "/app/playlist.txt"
known = set(os.listdir(MEDIA_DIR))

def append_to_playlist(filename):
    with open(PLAYLIST, "a") as f:
        f.write(f"file {MEDIA_DIR}/{filename}")
    print(f"[WATCHER] Added: {filename}")

while True:
    current = set(os.listdir(MEDIA_DIR))
    new_files = current - known

    for f in new_files:
        if f.endswith(".mp4"):
            append_to_playlist(f)

    known = current
    time.sleep(2)
