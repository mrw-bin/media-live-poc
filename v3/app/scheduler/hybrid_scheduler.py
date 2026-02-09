
import json, os

DAILY = '/app/scheduler/daily_schedule.json'
PLAYLIST = '/app/playlist.txt'
MEDIA_DIR = '/media/'

# Default ad rules (could be made dynamic per asset/type)
RULES = {
    "pre_roll": True,
    "midroll_interval": 600,
    "ad_duration": 60,
    "min_tail": 300
}

def generate_breaks(duration, rules=None):
    rules = rules or RULES
    breaks = []
    if rules.get('pre_roll'):
        breaks.append({"offset": 0, "duration": rules['ad_duration']})
    pos = rules['midroll_interval']
    while pos < duration - rules['min_tail']:
        breaks.append({"offset": pos, "duration": rules['ad_duration']})
        pos += rules['midroll_interval']
    return breaks


def _load_daily():
    if not os.path.exists(DAILY):
        return {"playlist": [], "breaks": []}
    with open(DAILY) as f:
        return json.load(f)


def _save_daily(data):
    with open(DAILY, 'w') as f:
        json.dump(data, f, indent=2)


def _update_playlist(playlist):
    with open(PLAYLIST, 'w') as f:
        for slot in playlist:
            f.write(f"file {MEDIA_DIR}{slot['file']}")


def add_new_file(filename, duration, rules=None):
    # Append a new file to today's schedule with computed ad breaks (global offsets).
    data = _load_daily()

    # Global start offset => sum of durations of all scheduled items
    total_elapsed = sum(item['duration'] for item in data['playlist'])

    file_breaks = generate_breaks(duration, rules)
    data['playlist'].append({
        "file": filename,
        "duration": duration,
        "ad_breaks": file_breaks
    })

    # Convert file-relative offsets to global offsets
    for b in file_breaks:
        data['breaks'].append({
            "offset": total_elapsed + b['offset'],
            "duration": b['duration']
        })

    _save_daily(data)
    _update_playlist(data['playlist'])
    print(f"[HYBRID] Added {filename} with {len(file_breaks)} breaks (start@{total_elapsed}s)")
