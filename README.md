
# 🎬 FAST Channel POC – Complete Repo (fast-channel-updated)
### 24/7 FAST Playout • Advanced Scheduler (Per‑File Ad Breaks) • SCTE‑35 • HLS • VAST Ad Server • Samsung TV Plus–Ready

This repository provides a **fully updated, production‑aligned FAST channel pipeline**, combining the strengths of the original Media‑to‑Live POC and the improved FAST channel architecture. It includes:

- ✔️ **24/7 FAST channel playout**
- ✔️ **Advanced scheduler with per‑file ad break mapping**
- ✔️ **Dynamic file ingestion**
- ✔️ **Automatic SCTE‑35 ad insertion (EXT‑X‑DATERANGE)**
- ✔️ **Live HLS output (TS segments)**
- ✔️ **Integrated VAST mock server**
- ✔️ **Samsung SSAI‑ready feed**
- ✔️ **Fully Dockerized setup**

This repo is suitable for POCs, partner onboarding, FAST QA validation, and forming the foundation of a scalable production FAST channel.

---
# 📚 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Advanced Scheduler Logic](#advanced-scheduler-logic)
5. [Installation](#installation)
6. [Running the System](#running-the-system)
7. [Adding Media While Running](#adding-media-while-running)
8. [Directory Structure](#directory-structure)
9. [HLS Output](#hls-output)
10. [Samsung TV Plus SSAI Integration](#samsung-tv-plus-ssai-integration)
11. [Future Improvements](#future-improvements)
12. [License](#license)

---
# 🌐 Overview
This FAST channel solution creates a **continuous live HLS stream** that simulates a full 24/7 linear channel. It includes:

- Dynamic playout of `.mp4` files
- Ad‑break signalling using SCTE‑35
- A scheduler that builds a 24‑hour programming grid
- A VAST server that can be consumed by Samsung TV Plus SSAI
- FFmpeg‑based HLS packaging

It is suitable for validating live ingest, SSAI ad‑stitching, and FAST programming logic before scaling to production.

---
# ✨ Features

### 🎞️ Continuous 24/7 Playout
The system runs indefinitely and loops through scheduled media, generating ad opportunities without interruption.

### 📅 Advanced Scheduler (NEW)
The scheduler now:
- Generates **unique ad breaks per file**
- Supports **pre‑roll**, **mid‑roll**, and **tail‑gap rules**
- Builds a complete 24‑hour FAST schedule
- Produces file‑specific ad maps
- Converts file‑relative ad offsets to **global channel offsets**
- Creates a live `playlist.txt` for FFmpeg

### 🛰️ SCTE‑35 Ad Break Signaling
Breaks are inserted using HLS `EXT‑X‑DATERANGE` tags.

Example:
```m3u8
#EXT-X-DATERANGE:ID="ad-123",
  CLASS="se.scte35",
  START-DATE="2026-02-09T10:02:00Z",
  DURATION=60.0,
  SCTE35-OUT="base64payload..."
```

### 📡 VAST Mock Server Included
Available at:
```
http://localhost:9090/vast
```
Used by Samsung SSAI or other ad‑decisioning systems.

### 🔄 Dynamic Content Injection
Drop new `.mp4` files into `/media` to immediately extend the playout queue.

### 🐳 Fully Dockerized
No dependencies needed on your machine.

```bash
docker-compose up
```

---
# 🧠 Advanced Scheduler Logic
This version introduces a **true FAST‑grade scheduler**, addressing the limitations of global‑interval ad breaks.

### ✔ Per‑File Ad Map Generation
For each media file, breaks are computed as:
- **Pre‑roll** (optional)
- **Mid‑rolls every X seconds**
- **Avoid last N seconds** (tail)

### ✔ Flexible Rule Set (Defined in schedule_template.json)
```json
"ad_rules": {
  "pre_roll": true,
  "midroll_interval": 600,
  "ad_duration": 60,
  "min_tail": 300
}
```

### ✔ File‑Relative → Global Timeline Conversion
If a media file begins 7200 seconds into the 24‑hour schedule, and has a mid‑roll at 600 seconds, the global offset becomes:
```
7200 + 600 = 7800 seconds
```

### ✔ daily_schedule.json New Structure
```json
{
  "playlist": [
    {
      "file": "show1.mp4",
      "start": "2026-02-09T00:00:00Z",
      "duration": 1800,
      "ad_breaks": [
        {"offset": 0, "duration": 60},
        {"offset": 600, "duration": 60}
      ]
    }
  ],
  "breaks": [
    {"offset": 0, "duration": 60},
    {"offset": 600, "duration": 60}
  ]
}
```

---
# ⚙️ Installation
```bash
git clone <your repo>
cd fast-channel-updated
docker-compose up
```

Place `.mp4` files in:
```
media/
```

---
# ▶️ Running the System
When started, Docker runs:
1. The **scheduler** → generates daily FAST schedule
2. The **watcher** → detects new media
3. The **playout engine** → drives FFmpeg
4. The **VAST server** → serves ad responses

HLS output appears in:
```
output/live.m3u8
```

---
# 📥 Adding Media While Running
Simply drop new `.mp4` files into:
```
media/
```
The watcher will automatically append them to the playlist.

---
# 📁 Directory Structure
```
fast-channel-updated/
│
├── app/
│   ├── playout.py
│   ├── watcher.py
│   ├── playlist.txt
│   ├── scte.py
│   └── scheduler/
│       ├── scheduler.py
│       ├── schedule_template.json
│       └── daily_schedule.json
│
├── vast/
│   ├── vast_server.py
│   └── example_vast.xml
│
├── media/
├── output/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---
# 📡 Samsung TV Plus SSAI Integration
Samsung requires:
- HLS input with SCTE‑35 ad markers
- A VAST URL (provided by this repo)

They will:
1. Pull your origin HLS stream
2. Detect SCTE‑35 markers
3. Call your VAST endpoint
4. Stitch ads dynamically

This repo satisfies all Samsung onboarding prerequisites.

---
# 🚀 Future Improvements
- CMAF/fMP4 support
- Multi‑audio & subtitles
- Advanced SCTE‑35 splice_insert
- EPG (XMLTV / Gracenote / Samsung) generator
- Promo & bumper insertion system
- SSAI emulator environment

---
# 📄 License
MIT License.
