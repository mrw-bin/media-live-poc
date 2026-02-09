
import json
from .hybrid_scheduler import generate_breaks, _save_daily, _update_playlist

TEMPLATE = '/app/scheduler/schedule_template.json'


def generate_schedule():
    with open(TEMPLATE) as f:
        template = json.load(f)

    slots = template['slots']
    rules = template['ad_rules']

    playlist = []
    global_breaks = []

    elapsed = 0
    for slot in slots:
        br = generate_breaks(slot['duration'], rules)
        playlist.append({
            "file": slot['file'],
            "duration": slot['duration'],
            "ad_breaks": br
        })
        for b in br:
            global_breaks.append({"offset": elapsed + b['offset'], "duration": b['duration']})
        elapsed += slot['duration']

    data = {"playlist": playlist, "breaks": global_breaks}
    _save_daily(data)
    _update_playlist(playlist)
    print('[SCHEDULER] Daily schedule generated.')


if __name__ == '__main__':
    generate_schedule()
