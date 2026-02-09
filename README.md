# media-live-poc — root README

This repository contains three independent Proof-of-Concept (PoC) solutions for building a simple FAST-style live HLS channel with ad breaks suitable for validating Samsung SSAI / Samsung TV Plus workflows. Each solution is self-contained in its own folder: `v1/`, `v2/`, and `v3/`. Use the variant that best matches the scenario you want to test.

This root README summarizes each variant, highlights their differences, and shows an example workflow to run and test a variant (example uses `v2`). For full, variant-specific instructions and details, open the `README.md` inside the chosen subfolder.

---

## Quick summaries

- `v1/` — Basic playout PoC
  - Continuous HLS (MPEG-TS) output produced by FFmpeg.
  - Simple file watcher that appends new `.mp4` files to a `playlist.txt` used by FFmpeg.
  - Basic SCTE‑35 / `EXT-X-DATERANGE` insertion based on a simple schedule file.
  - Minimal Docker setup for running playout and output.
  - Use-case: validate HLS cadence, segmenting, and simple ad-marker behavior.

- `v2/` — Full FAST channel PoC (recommended for end-to-end tests)
  - 24/7 scheduler that builds a daily programming grid and generates `playlist.txt` and `daily_schedule.json`.
  - Local mock VAST server (Flask) to simulate SSAI/VAST requests for ad decisioning.
  - FFmpeg-based HLS packaging (TS segments) and a service to expose `/output` over HTTP.
  - Dockerized stack to run playout, VAST server, and the HTTP output together.
  - Use-case: full workflow testing (scheduler → SCTE‑35 markers → VAST call → HLS output) for Samsung integration demos.

- `v3/` — Hybrid scheduler PoC (daily + real-time)
  - Builds a daily schedule but also supports real-time ingestion of newly added media files.
  - Per-file ad rules (pre-roll, mid-roll cadence, tail rules) and translation of file-relative ad breaks to global offsets.
  - Produces `daily_schedule.json` and updates `playlist.txt` live without restarting playout.
  - Includes a realistic VAST endpoint and an HTTP server exposing `/output`.
  - Use-case: validate schedule updates while running and per-file ad-break planning.

---

## Differences and when to use each

- Scheduling complexity
  - `v1`: manual/simple schedule file — good for quick local tests.
  - `v2`: full 24-hour scheduler — use when you need a realistic programming grid.
  - `v3`: hybrid — best when you need both a daily grid and live updates when new media arrive.

- Ad decisioning / VAST
  - `v1`: emits SCTE-style markers but does not include a VAST server.
  - `v2`: includes a mock VAST server so you can exercise the full SSAI flow.
  - `v3`: includes a more realistic VAST endpoint and detailed ad rules per file.

- Manifest and SCTE tagging
  - All variants demonstrate ad-opportunity planning. `v1`/`v2`/`v3` differ in whether they emit `EXT-X-DATERANGE` directly or prepare schedules for a packager. Read the variant README for exact behavior — some packagers are required to convert SCTE‑35 into `EXT-X-DATERANGE` in production.

---

## How to choose

- Quick local HLS + ad-marker checks: pick `v1`.
- End-to-end FAST + VAST integration tests: pick `v2`.
- Live updates to schedules and per-file ad logic: pick `v3`.

---

## Example: run and test `v2` in Docker (step-by-step)

1. Open a shell and change into the `v2` folder:

   ```bash
   cd v2
   ```

2. (Optional) Add `.mp4` files to `media/` inside `v2` so the playlist has content. Example:

   ```bash
   mkdir -p media
   cp /path/to/your/video1.mp4 media/
   cp /path/to/your/video2.mp4 media/
   ```

3. Start the dockerized stack (build if needed):

   ```bash
   docker-compose up --build
   ```

   - This should start the playout service (FFmpeg), the mock VAST server, and an HTTP server serving `output/`.
   - Watch the logs for FFmpeg startup and any scheduler messages.

4. Confirm HLS files are being produced in the `v2/output/` folder (on the host) or by requesting the served URL.

5. Open the generated HLS manifest in an HLS-capable player:

   ```
   http://localhost:8080/output/live.m3u8
   ```

   - Use VLC, `ffplay`, Safari, or an HLS web player.

6. Verify the VAST endpoint is reachable (example):

   ```
   http://localhost:9090/vast
   ```

   - Tail the VAST server logs to confirm the SSAI flow when ad breaks occur.

7. Inspect `live.m3u8` for ad markers:
   - Look for `#EXT-X-DATERANGE` lines (or other DATERANGE-style tags) indicating ad opportunities.
   - If the variant logs break insertion, watch the playout logs for break timestamps.

8. To stop and clean up:

   ```bash
   docker-compose down
   ```

---

## How to test ad break behavior

- Inspect the generated HLS manifest (`output/live.m3u8`) for `EXT-X-PROGRAM-DATE-TIME` and `EXT-X-DATERANGE` entries.
- Monitor the playout service logs for scheduled break messages and VAST requests.
- Ensure the VAST mock server receives requests at break times and returns a VAST response (v2/v3).
- Add new `.mp4` files to `media/` while the system runs (v1/v3 support live file injection). Verify the playlist is updated and new media are played.

---

## Troubleshooting notes

- If FFmpeg exits or does not write segments:
  - Check `playlist.txt` for valid file paths and correct `file '...'` lines.
  - Verify your `media/` files are valid MP4s (use `ffprobe` locally).

- If you don't see `EXT-X-DATERANGE` tags:
  - Some variants prepare break plans rather than rewriting manifests; a packager or post-processor may be required to map SCTE‑35 into HLS DATERANGE tags. See the chosen variant README for details.

- If ports differ from the examples above, consult the variant README for the exact ports used by that solution.

---

## Where to find more details

Open the README inside the variant folder you want to run:

- `v1/README.md` — Quick playout PoC and simple schedule
- `v2/README.md` — Full FAST channel PoC with scheduler and VAST server
- `v3/README.md` — Hybrid scheduler with real-time ingestion and per-file ad rules

---

If you want, I can add a small helper script or a `docker-compose.override.yml` to make switching and running variants easier — tell me which variant to automate and I will add it.
