
import json, datetime

TEMPLATE = '/app/scheduler/schedule_template.json'
OUTPUT = '/app/scheduler/daily_schedule.json'
PLAYLIST = '/app/playlist.txt'
MEDIA_DIR = '/media/'

# Generate per-file ad break map
def generate_breaks(duration, rules):
    breaks = []
    if rules.get('pre_roll'):
        breaks.append({"offset": 0, "duration": rules['ad_duration']})
    pos = rules['midroll_interval']
    while pos < duration - rules['min_tail']:
        breaks.append({"offset": pos, "duration": rules['ad_duration']})
        pos += rules['midroll_interval']
    return breaks


def generate_schedule():
    with open(TEMPLATE) as f:
        template = json.load(f)

    slots = template['slots']
    rules = template['ad_rules']

    start_time = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    current = start_time

    playlist = []
    global_breaks = []

    for slot in slots:
        # Per-file ad breaks
        file_breaks = generate_breaks(slot['duration'], rules)

        playlist.append({
            "file": slot['file'],
            "start": current.isoformat() + 'Z',
            "duration": slot['duration'],
            "ad_breaks": file_breaks
        })

        # Convert file-relative offsets to global timeline
        for b in file_breaks:
            global_offset = (current - start_time).total_seconds() + b['offset']
            global_breaks.append({
                "offset": global_offset,
                "duration": b['duration']
            })

        current += datetime.timedelta(seconds=slot['duration'])

    result = {"playlist": playlist, "breaks": global_breaks}

    with open(OUTPUT, 'w') as f:
        json.dump(result, f, indent=2)

    # Write playlist for FFmpeg
    with open(PLAYLIST, 'w') as p:
        for slot in playlist:
            p.write(f"file {MEDIA_DIR}{slot['file']}
")


if __name__ == '__main__':
    generate_schedule()
    print('[SCHEDULER] Daily schedule generated.')
