
# 🎬 FAST Channel POC – Hybrid Scheduler Edition
### 24/7 FAST Playout • Hybrid Scheduler (Daily + Real-Time Updates) • SCTE‑35 • HLS • VAST • Samsung SSAI Ready

This repository contains a complete FAST channel playout system with:

- Full **24-hour daily schedule generation**
- **Hybrid scheduler** that also ingests **new media files in real-time**
- Per-file ad break logic (pre-roll, mid-roll, tail rules)
- Global break offsets suitable for SSAI (e.g., Samsung TV Plus)
- FFmpeg-based HLS live packaging
- VAST server for SSAI ad decisioning (realistic VAST 4.0-style response)
- Simple HTTP server to serve `/output` on port **8080**

> ⚠️ **Note:** This POC computes ad-breaks and timing; it does not force FFmpeg to write `EXT-X-DATERANGE` automatically. In many production stacks the **packager** (e.g., MediaPackage/Unified/Nimble) maps SCTE‑35 to HLS tags. Here, the hybrid scheduler prepares the break plan (`daily_schedule.json`) and logs upcoming breaks. You can replace FFmpeg with a packager of choice to emit real DATERANGEs.

---
## 📁 Repository Structure
```
media-live-poc/
│
├── app/
│   ├── playout.py                 # Starts FFmpeg and logs scheduled breaks
│   ├── watcher.py                 # Watches /media; calls hybrid scheduler for new files
│   ├── playlist.txt               # FFmpeg concat playlist (live-updated)
│   ├── scte.py                    # (POC) SCTE-35 payload generator helper
│   └── scheduler/
│       ├── __init__.py
│       ├── hybrid_scheduler.py    # Real-time add-file scheduling + global break calc
│       ├── scheduler.py           # Daily 24h schedule generator
│       ├── schedule_template.json # Input rules
│       └── daily_schedule.json    # Channel plan + global breaks (live-updated)
│
├── vast/
│   ├── vast_server.py             # Realistic VAST endpoint
│   └── example_vast.xml
│
├── media/                         # Drop .mp4 files here (detected live)
├── output/                        # HLS output (served on :8080)
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---
## 🧠 Hybrid Scheduler Logic
**Two modes:**

### 1) Daily Schedule Generation
Creates a 24‑hour FAST programming grid using `schedule_template.json`.
- Generates per‑file ad maps
- Computes **global** offsets (seconds from channel start)
- Writes `daily_schedule.json` and `playlist.txt`

### 2) Real-Time Media Ingestion
When a new `.mp4` appears:
- `watcher.py` triggers `hybrid_scheduler.add_new_file()`
- The scheduler:
  - Calculates ad breaks for that file
  - Converts file-relative → global offsets
  - Appends to `daily_schedule.json`
  - Updates `playlist.txt`

> Result: **New media files get ad-breaks** without restart.

---
## ⚙️ Installation & Run
```bash
git clone <your-repo>
cd fast-channel-hybrid
# Add some .mp4 files to ./media first for immediate playout
docker-compose up
```

Open the HLS output in a player:
```
http://localhost:8080/live.m3u8
```

VAST endpoint (for SSAI tests):
```
http://localhost:9090/vast
```

---
## 🔧 Config: `schedule_template.json`
```json
{
  "slots": [
    { "title": "Show1 Ep1", "file": "show1_ep1.mp4", "duration": 1800 },
    { "title": "Show1 Ep2", "file": "show1_ep2.mp4", "duration": 1800 },
    { "title": "News",       "file": "news1.mp4",     "duration": 900  }
  ],
  "ad_rules": {
    "pre_roll": true,
    "midroll_interval": 600,
    "ad_duration": 60,
    "min_tail": 300
  }
}
```
- **pre_roll**: Insert ad break at offset 0 of each file
- **midroll_interval**: Mid-roll cadence in seconds
- **ad_duration**: Intended duration per break (POC)
- **min_tail**: Keep last N seconds ad-free

---
## 📡 Samsung SSAI Integration Notes
- Provide your origin HLS URL to Samsung (this POC serves `/output` at port 8080)
- Provide your **VAST URL** (`/vast`)
- This POC prepares the **ad opportunity plan** in `daily_schedule.json`. To output **real `EXT‑X‑DATERANGE`** tags, use a production packager that maps SCTE‑35 → HLS markers, or extend `playout.py` to post-process manifests.

---
## 🛠 Future Extensions
- Swap FFmpeg for a packager that emits `EXT‑X‑DATERANGE`
- CMAF/fMP4 output
- Auto-duration detection via `ffprobe`
- EPG (XMLTV / vendor formats)
- Multi-audio, captions, slates
- SSAI emulator

---
## 📄 License
MIT License.
