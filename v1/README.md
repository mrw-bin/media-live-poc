
# 🎬 Media‑to‑Live HLS POC
### Dynamic FAST‑style Playout • SCTE‑35 Ad Markers • HLS Output • Samsung TV Plus–Ready

This repository contains a **fully‑contained Proof of Concept** that turns a folder of media files into a **continuous live HLS stream**, complete with:

- ✔️ **HLS (TS) output**  
- ✔️ **Dynamic file ingest** → add new `.mp4` files while the system is running  
- ✔️ **Automatic playlist expansion**  
- ✔️ **SCTE‑35 ad break insertion** (`EXT-X-DATERANGE`)  
- ✔️ **Dockerized pipeline**  
- ✔️ **Samsung TV Plus SSAI integration–ready**  

This POC simulates a **FAST channel playout engine** suitable for demonstrating HLS behavior, ad‑break signaling, and live stream cadence before integrating with Samsung, Roku, Pluto, or any other SSAI-based platform.

---

# 📚 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Running the POC](#running-the-poc)
6. [Adding Media While Running](#adding-media-while-running)
7. [Ad Break Insertion (SCTE‑35)](#ad-break-insertion-scte-35)
8. [Directory Structure](#directory-structure)
9. [HLS Output](#hls-output)
10. [How to Integrate With Samsung TV Plus](#how-to-integrate-with-samsung-tv-plus)
11. [Known Limitations](#known-limitations)
12. [Future Improvements](#future-improvements)
13. [License](#license)

---

# 🌐 Overview

This POC demonstrates how to:

- Playout local mp4 files in a **continuous live stream**  
- Insert SCTE‑35 **ad break markers** at defined offsets  
- Generate an HLS stream that **Samsung SSAI can ingest**  
- Dynamically extend the playout while running (just drop more videos into `/media`)  

This architecture mimics a simple FAST channel and helps validate your stream with partners before building a production-grade pipeline.

---

# ✨ Features

### 🎞️ Continuous Media Playback  
Reads a list of media files and plays them back as a single seamless live stream.

### ➕ Dynamic File Injection  
Drop new `.mp4` files into `/media` during runtime → automatically added to the playout queue.

### 🛰️ SCTE‑35 Ad Break Signaling  
SCTE‑35 is injected based on a schedule (`schedule.json`):

- Supports **EXT‑X‑DATERANGE** (recommended for Samsung SSAI)  
- Each ad break includes:  
  - `START-DATE`  
  - `DURATION`  
  - Base64 SCTE‑35 payload  

### 📦 HLS Output (TS segments)
FFmpeg emits:

- `master.m3u8`  
- `live.m3u8`  
- `seg_000001.ts` etc.  

### 🐳 Fully Dockerized  
No local tool installs required.

---

# 🏗️ Architecture
```
        +---------------------------+
        |   media/ (mp4 files)      |
        +-------------+-------------+
                      |
               (file watcher)
                      ↓
           +---------------------+
           |  watcher.py         |
           | Appends new files   |
           | to playlist.txt     |
           +---------+-----------+
                     |
                     ↓
           +---------------------+
           |  playout.py         |
           |  - loads schedule   |
           |  - triggers SCTE35  |
           |  - drives FFmpeg    |
           +---------+-----------+
                     |
                     ↓
              +-------------+
              |   FFmpeg    |
              | HLS packager|
              +------+------+ 
                     |
                     ↓
        +----------------------------+
        |       output/ (HLS)        |
        | live.m3u8, master.m3u8     |
        +----------------------------+
```

---

# ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-org>/media-to-live-poc.git
cd media-to-live-poc
```

### 2. Add media files  
Place `.mp4` files in:
```
media/
```

### 3. Start Docker environment
```bash
docker-compose up
```

---

# ▶️ Running the POC

When started, the system will:

1. Begin streaming the files listed in `app/playlist.txt`  
2. Watch the `media/` folder and auto‑append new `.mp4` files  
3. Insert SCTE‑35 ad cues from `schedule.json`  
4. Output live HLS segments into `/output`  

Play the stream via:
```
output/live.m3u8
```

You can open this URL using:
- VLC  
- ffplay  
- Safari  
- Any HLS-compatible web player

---

# 📥 Adding Media While Running

Just drop files into `/media`:
```
cp new_show.mp4 media/
```

The watcher will detect it and append to:
```
app/playlist.txt
```

FFmpeg will automatically ingest it when the current file ends.

---

# 🎯 Ad Break Insertion (SCTE‑35)

Ad break configuration lives in:
```
app/schedule.json
```

Example:
```json
{
  "breaks": [
    { "offset": 120, "duration": 60 }
  ]
}
```

HLS output includes:
```m3u8
#EXT-X-DATERANGE:ID="ad-1",
  CLASS="se.scte35",
  START-DATE="2026-02-09T10:02:00Z",
  DURATION=60.0,
  SCTE35-OUT="base64..."
```

---

# 📁 Directory Structure
```
media-to-live-poc/
│
├── app/
│   ├── playout.py
│   ├── watcher.py
│   ├── scte.py
│   ├── schedule.json
│   ├── playlist.txt
│   └── requirements.txt
│
├── media/                # Drop mp4 files here
├── output/               # HLS live output
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

# 📡 HLS Output

After startup, you will find:
```
output/
  master.m3u8
  live.m3u8
  seg_000001.ts
  seg_000002.ts
```

The manifest includes:
- `EXT-X-PROGRAM-DATE-TIME`  
- 6‑second segments  
- SCTE‑35 DATERANGE markers  

---

# 📺 How to Integrate With Samsung TV Plus

Samsung requires two items:

### 1. Your HLS URL
Provide:
```
https://your-origin/live.m3u8
```

### 2. Your VAST Ad Tag
Samsung inserts your VAST URL into their SSAI.

Your SCTE‑35 → triggers their ad stitching.

---

# ⚠️ Known Limitations
- Simplified SCTE‑35 payloads  
- No redundancy  
- Uses MPEG‑TS (CMAF optional extension)  
- Not a full FAST scheduler  

---

# 🚀 Future Improvements
- CMAF/fMP4 output  
- Full FAST programming grid  
- VAST server integration  
- S3 push for Samsung ingestion  
- DRM support  
- SSAI emulation  

---

# 📄 License
MIT License.

