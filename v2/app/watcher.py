import time
import os
import subprocess
import sys

MEDIA_DIR = "/media"
KNOWN = set()

def regenerate_schedule():
    print("[WATCHER] Detected media change, regenerating schedule...")
    # Use the same interpreter that launched this script
    py = sys.executable or "python3"
    try:
        subprocess.call([py, "/app/scheduler.py"])
    except Exception as e:
        print(f"[WATCHER] Failed to run scheduler: {e}")

def snapshot(dirpath: str):
    try:
        return set(os.listdir(dirpath))
    except FileNotFoundError:
        return set()

def main():
    global KNOWN
    KNOWN = snapshot(MEDIA_DIR)

    print(f"[WATCHER] Watching {MEDIA_DIR} for changes...")
    while True:
        current = snapshot(MEDIA_DIR)
        if current != KNOWN:
            # Any change (add/remove/rename) triggers regeneration
            added = current - KNOWN
            removed = KNOWN - current
            if added:
                print("[WATCHER] Added:", ", ".join(sorted(added)))
            if removed:
                print("[WATCHER] Removed:", ", ".join(sorted(removed)))
            regenerate_schedule()
            KNOWN = current
        time.sleep(2)

if __name__ == "__main__":
    main()