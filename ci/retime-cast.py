#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""
Retime an asciinema v2 .cast file so it looks natural when played back.

Commands like `soup stir` run fast and dump output in bursts, so the recorded
timestamps are all bunched together (e.g., 5 frames in 45 ms, then results
in 84 ms). This script spreads the distinct "frame groups" across a target
timeline so the player has something interesting to show.

Usage:
    python3 ci/retime-cast.py INPUT.cast OUTPUT.cast

Algorithm:
    1. Group events by timestamp (within 10 ms buckets).
    2. Detect burst boundaries: a gap > BURST_GAP_THRESHOLD separates bursts.
    3. Spread each burst across its target time window.
    4. Write the retimed cast to OUTPUT.cast.
"""
import json
import sys
from itertools import groupby

# Two bursts detected in conformance output:
#   Burst 0 — progress spinner frames (few groups, should be slow / human-readable)
#   Burst 1 — results table dump     (many groups, slightly faster)
#
# Each entry: (start_time, seconds_per_frame)
BURST_SCHEDULE = [
    (1.0, 1.2),   # spinner: 1.2 s between each frame → ~6 s for 5 frames
    (9.0, 0.18),  # results: 0.18 s between each group → ~3.6 s for 20 groups
]

# Gap (seconds) between consecutive original timestamps that signals a new burst
BURST_GAP_THRESHOLD = 0.5


def retime(input_path: str, output_path: str) -> None:
    with open(input_path, encoding="utf-8") as f:
        header = json.loads(f.readline())
        events = [json.loads(line) for line in f]

    # ── Group events by timestamp (10 ms buckets) ──────────────────────────
    def bucket(ts: float) -> int:
        return int(ts * 100)  # 10 ms resolution

    frame_groups: list[tuple[float, list]] = []
    for _, grp in groupby(events, key=lambda e: bucket(e[0])):
        items = list(grp)
        frame_groups.append((items[0][0], items))

    # ── Split into bursts (large gap between timestamps = new burst) ────────
    bursts: list[list[tuple[float, list]]] = []
    current_burst: list[tuple[float, list]] = []
    for i, (ts, items) in enumerate(frame_groups):
        if i > 0:
            prev_ts = frame_groups[i - 1][0]
            if ts - prev_ts > BURST_GAP_THRESHOLD:
                bursts.append(current_burst)
                current_burst = []
        current_burst.append((ts, items))
    if current_burst:
        bursts.append(current_burst)

    # ── Assign new timestamps ───────────────────────────────────────────────
    new_events: list = []
    for burst_idx, burst in enumerate(bursts):
        if burst_idx < len(BURST_SCHEDULE):
            start_t, step = BURST_SCHEDULE[burst_idx]
        else:
            # Fallback: continue from last scheduled burst
            last_start, last_step = BURST_SCHEDULE[-1]
            last_len = len(bursts[len(BURST_SCHEDULE) - 1])
            start_t = last_start + last_step * last_len + 1.0
            step = last_step

        for frame_idx, (_orig_ts, items) in enumerate(burst):
            new_ts = round(start_t + frame_idx * step, 3)
            for event in items:
                new_events.append([new_ts, event[1], event[2]])

    # ── Write output ────────────────────────────────────────────────────────
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in new_events:
            f.write(json.dumps(event) + "\n")

    duration = new_events[-1][0] if new_events else 0
    print(
        f"Retimed {len(events)} events → {len(new_events)} events  "
        f"({len(bursts)} bursts, ~{duration:.1f}s duration)",
        file=sys.stderr,
    )


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} INPUT.cast OUTPUT.cast", file=sys.stderr)
        sys.exit(1)
    retime(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
