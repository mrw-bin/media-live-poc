import json
import math
import os
from typing import List, Dict, Tuple
from ffprobe_utils import scan_media_directory

MEDIA_DIR = "/media/"
PLAYLIST = "/app/playlist.txt"
OUTPUT = "/app/scheduler/daily_schedule.json"

# ---- Config (env-overridable) ----
NUMBER_OF_BREAKS        = int(os.getenv("NUMBER_OF_BREAKS", "-1"))  # <0 means "auto-fill within caps"
BREAK_DURATION          = float(os.getenv("BREAK_DURATION", "60"))  # seconds per break

BREAKS_PER_WINDOW       = int(os.getenv("BREAKS_PER_WINDOW", "4"))   # cap per window
WINDOW_SECONDS          = float(os.getenv("WINDOW_SECONDS", "3600")) # length of a window in seconds

MIN_GAP_BETWEEN_BREAKS  = float(os.getenv("MIN_GAP_BETWEEN_BREAKS", "90"))
WINDOW_GUARD_START      = float(os.getenv("WINDOW_GUARD_START", "10"))
WINDOW_GUARD_END        = float(os.getenv("WINDOW_GUARD_END", "10"))

SUPPORTED_EXTS = {".mp4", ".mov", ".mkv", ".m4v"}  # matches ffprobe_utils


def windows(total: float, step: float) -> List[Tuple[float, float]]:
    """Return [(start, end), ...] windows covering [0, total)."""
    w = []
    start = 0.0
    while start < total:
        end = min(start + step, total)
        w.append((start, end))
        start = end
    return w


def max_breaks_for_window(win_len: float) -> int:
    """
    Given a window length, compute the maximum breaks we can place respecting:
      - guards
      - min gap between breaks
      - window cap
    Even spacing yields spacing = eff_len / (k+1). We require spacing >= MIN_GAP_BETWEEN_BREAKS.
    -> k <= floor(eff_len / MIN_GAP_BETWEEN_BREAKS) - 1
    """
    eff_len = max(0.0, win_len - (WINDOW_GUARD_START + WINDOW_GUARD_END))
    if eff_len <= 0:
        return 0
    # Find the largest k such that spacing >= MIN_GAP_BETWEEN_BREAKS
    # spacing = eff_len/(k+1) >= min_gap -> k+1 <= eff_len/min_gap -> k <= eff_len/min_gap - 1
    k_by_spacing = max(0, int(math.floor(eff_len / max(1.0, MIN_GAP_BETWEEN_BREAKS)) - 1))
    return max(0, min(BREAKS_PER_WINDOW, k_by_spacing))


def distribute_across_windows(win_bounds: List[Tuple[float, float]],
                              total_target: int) -> List[int]:
    """
    Distribute 'total_target' breaks across windows proportionally to window lengths,
    not exceeding each window's feasible maximum.
    Uses largest-remainder allocation for fair rounding.
    """
    lengths = [end - start for (start, end) in win_bounds]
    caps    = [max_breaks_for_window(L) for L in lengths]
    cap_sum = sum(caps)

    if total_target < 0:  # auto-fill within caps
        total_target = cap_sum
    else:
        total_target = min(total_target, cap_sum)

    if total_target == 0:
        return [0] * len(win_bounds)

    # Initial allocation by proportion (floor)
    total_len = sum(lengths) or 1.0
    raw = [(lengths[i] / total_len) * total_target for i in range(len(lengths))]
    alloc = [min(caps[i], int(math.floor(raw[i]))) for i in range(len(lengths))]

    # Distribute remaining by largest fractional remainders subject to caps
    remain = total_target - sum(alloc)
    remainders = [(raw[i] - math.floor(raw[i]), i) for i in range(len(lengths))]
    remainders.sort(reverse=True)  # largest remainder first

    j = 0
    while remain > 0 and j < len(remainders):
        _, idx = remainders[j]
        if alloc[idx] < caps[idx]:
            alloc[idx] += 1
            remain -= 1
        j += 1

    # If still remainder (rare when caps bind heavily), try any window with capacity left
    if remain > 0:
        for i in range(len(alloc)):
            spare = caps[i] - alloc[i]
            if spare > 0:
                take = min(spare, remain)
                alloc[i] += take
                remain -= take
                if remain == 0:
                    break

    return alloc


def place_evenly_in_window(win_start: float, win_end: float, k: int) -> List[float]:
    """Return k offsets evenly spaced inside [win_start, win_end] obeying guards and min spacing."""
    if k <= 0:
        return []
    L = win_end - win_start
    eff_len = L - (WINDOW_GUARD_START + WINDOW_GUARD_END)
    if eff_len <= 0:
        return []
    # Ensure spacing works; reduce k if necessary (safety net)
    while k > 0 and eff_len / (k + 1) < MIN_GAP_BETWEEN_BREAKS:
        k -= 1
    if k <= 0:
        return []

    spacing = eff_len / (k + 1)
    base = win_start + WINDOW_GUARD_START
    return [base + spacing * (i + 1) for i in range(k)]


def generate_breaks_timeline(total_duration: float,
                             target_breaks: int) -> List[Dict[str, float]]:
    """Main routine to construct break offsets across the entire timeline."""
    if total_duration <= 0:
        return []

    win_bounds = windows(total_duration, WINDOW_SECONDS)
    per_win = distribute_across_windows(win_bounds, target_breaks)

    offsets = []
    for (win_idx, ((ws, we), k)) in enumerate(zip(win_bounds, per_win)):
        local = place_evenly_in_window(ws, we, k)
        offsets.extend(local)

    # Sort and return with durations
    offsets.sort()
    return [{"offset": float(o), "duration": float(BREAK_DURATION)} for o in offsets]


def write_playlist(media_files):
    with open(PLAYLIST, "w") as p:
        for m in media_files:
            p.write(f"file '{MEDIA_DIR}{m['file']}'\n")


def generate_schedule():
    # 1) Scan media and measure durations
    media_files = scan_media_directory(MEDIA_DIR)

    # Filter to supported extensions only (paranoia)
    media_files = [m for m in media_files
                   if os.path.splitext(m["file"])[1].lower() in SUPPORTED_EXTS]

    # 2) Write playlist.txt for ffmpeg concat demuxer
    write_playlist(media_files)

    # 3) Total duration
    total = sum(max(0.0, m["duration"]) for m in media_files)

    # 4) Construct breaks with window caps + spacing
    breaks = generate_breaks_timeline(
        total_duration=total,
        target_breaks=NUMBER_OF_BREAKS
    )

    # 5) Persist schedule JSON
    schedule = {
        "playlist": media_files,     # [{file, duration}]
        "breaks": breaks,            # [{offset, duration}]
        "total_duration": total      # seconds
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(schedule, f, indent=2)

    # ---- Additional verbose output ----
    print("\n================= [SCHEDULER REPORT] =================")
    print(f"Total media files: {len(media_files)}")
    print(f"Total playlist duration: {total:.2f} seconds ({total/60:.2f} min)")

    print("\nWindow settings:")
    print(f"  WINDOW_SECONDS        = {WINDOW_SECONDS}")
    print(f"  BREAKS_PER_WINDOW     = {BREAKS_PER_WINDOW}")
    print(f"  MIN_GAP_BETWEEN_BREAKS= {MIN_GAP_BETWEEN_BREAKS}")
    print(f"  BREAK_DURATION        = {BREAK_DURATION}")
    print(f"  Guards: start={WINDOW_GUARD_START}, end={WINDOW_GUARD_END}")
    print(f"  Requested NUMBER_OF_BREAKS = {NUMBER_OF_BREAKS}")

    # Reconstruct window distribution
    win_bounds = windows(total, WINDOW_SECONDS)
    win_lengths = [end - start for (start, end) in win_bounds]

    print("\nWindows:")
    for i, (ws, we) in enumerate(win_bounds):
        print(f"  Window {i+1}: {ws:.1f}s → {we:.1f}s  (length {we-ws:.1f}s)")

    # Count how many breaks ended up in each window
    per_window = [0] * len(win_bounds)
    for br in breaks:
        for i, (ws, we) in enumerate(win_bounds):
            if ws <= br["offset"] < we:
                per_window[i] += 1
                break

    print("\nBreak allocation per window:")
    for i, count in enumerate(per_window):
        print(f"  Window {i+1}: {count} breaks")

    print("\nBreak timeline:")
    for i, br in enumerate(breaks):
        off = br["offset"]
        dur = br["duration"]
        print(f"  Break {i+1}: offset={off:.2f}s  (t={off/60:.2f} min), duration={dur}s")

    print("=======================================================\n")


if __name__ == "__main__":
    generate_schedule()