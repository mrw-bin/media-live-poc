import json, datetime, os

TEMPLATE = "/app/scheduler/schedule_template.json"
OUTPUT_SCHEDULE = "/app/scheduler/daily_schedule.json"
PLAYLIST_FILE = "/app/playlist.txt"
MEDIA_DIR = "/media/"

def generate_daily_schedule():
    with open(TEMPLATE) as f:
        template = json.load(f)

    slots = template["slots"]
    ad_cfg = template["ad_breaks"]

    start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    current = start

    playlist = []
    ad_breaks = []

    for slot in slots:
        playlist.append({
            "file": slot["file"],
            "start": current.isoformat() + "Z",
            "duration": slot["duration"]
        })

        if ad_cfg["mid_roll_interval"]:
            next_break = current + datetime.timedelta(seconds=ad_cfg["mid_roll_interval"])
            ad_breaks.append({
                "offset": (next_break - start).total_seconds(),
                "duration": ad_cfg["ad_duration"]
            })

        current += datetime.timedelta(seconds=slot["duration"])

    with open(OUTPUT_SCHEDULE, "w") as out:
        json.dump({"playlist": playlist, "breaks": ad_breaks}, out, indent=2)

    with open(PLAYLIST_FILE, "w") as p:
        for item in playlist:
            p.write(f"file {MEDIA_DIR}{item['file']}
")

    print("[SCHEDULER] Daily schedule generated.")

if __name__ == "__main__":
    generate_daily_schedule()
