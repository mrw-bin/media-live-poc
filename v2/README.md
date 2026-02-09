
# 🎬 Full FAST Channel POC
### 24/7 FAST Playout • Scheduler • SCTE‑35 • HLS • VAST Ad Server • Samsung TV Plus–Ready

This repository contains a **complete, production‑inspired FAST Channel Proof of Concept**, including:

- ✔️ 24/7 FAST-style playout engine
- ✔️ Dynamic playlist + media injection
- ✔️ Daily scheduler (24-hour programming grid)
- ✔️ Automatic SCTE‑35 ad break insertion
- ✔️ Local VAST Ad Server (Flask)
- ✔️ FFmpeg HLS encoder (TS segments)
- ✔️ Samsung SSAI-ready output
- ✔️ Fully Dockerized environment

This repo is ideal for validating FAST workflows, ad-break behavior, and Samsung TV Plus onboarding.

---
# 📁 Repository Structure
```
full-fast-channel-repo/
│
├── app/
│   ├── playout.py                # Drives FFmpeg + SCTE-35 injection
│   ├── watcher.py                # Watches /media and updates playlist.txt
│   ├── playlist.txt              # Generated playlist for FFmpeg
│   ├── scte.py                   # SCTE-35 payload generator
│   └── scheduler/
│       ├── scheduler.py          # Generates daily FAST schedule
│       ├── schedule_template.json
│       └── daily_schedule.json
│
├── vast/
│   ├── vast_server.py            # Local mock VAST endpoint
│   └── example_vast.xml
│
├── media/                        # Drop mp4 files here
├── output/                       # FFmpeg HLS output
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---
# 🚀 Features

## ✔ 24/7 FAST Channel Engine
The playout engine:
- Reads the generated **24-hour schedule**
- Streams continuously through FFmpeg
- Automatically continues as new media files arrive

## ✔ Automatic Scheduler
The scheduler builds a daily programming grid from `schedule_template.json` and outputs:
- `playlist.txt` for FFmpeg
- `daily_schedule.json` for reference and potential EPG ingestion

It supports:
- Show rotation
- Timed durations
- Automatic mid-roll ad break generation

## ✔ SCTE‑35 Ad Breaks
SCTE‑35 ad markers are injected as:

```m3u8
#EXT-X-DATERANGE:ID="ad-1",
  CLASS="se.scte35",
  START-DATE="2026-02-09T10:02:00Z",
  DURATION=60.0,
  SCTE35-OUT="base64payload..."
```

Samsung SSAI reads these markers and triggers your VAST tag.

## ✔ Local VAST Ad Server
A simple VAST endpoint for testing:
```
http://localhost:9090/vast
```
It returns a valid VAST XML structure that Samsung SSAI (or any ad stack) can consume.

## ✔ Dynamic File Injection
Drop `.mp4` files into `/media` at any time. The watcher adds them to `playlist.txt` in real‑time.

## ✔ Fully Dockerized
Start everything using:
```bash
docker-compose up
```

---
# 🏗 How It Works

### 1. Scheduler builds a 24-hour FAST schedule
Files:
- `/app/scheduler/schedule_template.json`
- `/app/scheduler/daily_schedule.json`

### 2. Watcher monitors `/media`
Automatically appends new content to the playlist.

### 3. Playout engine (FFmpeg) outputs HLS
Located in:
```
/output/live.m3u8
/output/master.m3u8
```

### 4. SCTE‑35 ad breaks trigger VAST calls
Samsung SSAI will:
1. Read SCTE‑35 markers
2. Call your VAST endpoint
3. Stitch ads into user-specific manifests

---
# 🧪 Getting Started

### 1️⃣ Clone the repo
```bash
git clone <your repo>
cd full-fast-channel-repo
```

### 2️⃣ Add some MP4 files
```
media/
  ├── show1_ep1.mp4
  ├── show1_ep2.mp4
  ├── doc1.mp4
  └── news1.mp4
```

### 3️⃣ Start the system
```bash
docker-compose up
```

### 4️⃣ Play the stream
Use VLC, ffplay or Safari:
```
http://localhost:8080/output/live.m3u8
```

### 5️⃣ Test VAST server
```
http://localhost:9090/vast
```

---
# 📡 Samsung TV Plus Integration

Samsung TV Plus SSAI requires:

### ✔ An HLS feed with SCTE‑35
This repo provides this.

### ✔ A VAST ad tag
Provided via the included Flask VAST server.

Samsung will:
- Pull your HLS origin
- Detect SCTE‑35 ad markers
- Call your VAST URL
- Stitch ads based on your VAST responses

This repo is fully aligned with Samsung onboarding requirements.

---
# ⚠ Known Limitations
This POC is not production‑ready. Limitations include:
- No redundancy / failover
- Uses simplified SCTE‑35 payloads
- HLS TS only (no CMAF yet)
- No DRM
- No promo rotation system

---
# 🚀 Future Improvements
I can help extend the repo with:
- CMAF/fMP4 support
- Full EPG generator
- Samsung S3 push uploader
- Multi‑audio + subtitles
- SSAI emulator
- Advanced SCTE‑35 encoding

---
# 📄 License
MIT License.
