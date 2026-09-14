#!/usr/bin/env python3
"""
Retime an asciinema v2 .cast file to a target duration.

Terminal recordings can be too short (burst output) or too long (slow tests)
for a good website demo. This script proportionally scales all timestamps to
fit a target duration while preserving relative timing.

Usage:
    python3 ci/retime-cast.py INPUT.cast OUTPUT.cast [TARGET_SECONDS]

TARGET_SECONDS defaults to 15.
"""

import argparse
import json
import re
import sys
from typing import Any


def redact_event_paths(events: list[Any], paths: list[str]) -> list[Any]:
    """Redact literal and terminal-wrapped paths while retaining event timing."""
    combined = "".join(event[2] for event in events)
    for path in paths:
        combined = combined.replace(path, "<workspace>")
        # Rich may hard-wrap a long absolute path at the PTY width, placing
        # CRLF inside it. Match that rendering too so proof artifacts never
        # preserve a machine-local path just because the terminal wrapped.
        wrapped_path = "".join(f"{re.escape(character)}(?:\\r?\\n)?" for character in path)
        combined = re.sub(wrapped_path, "<workspace>", combined)
    cursor = 0
    sanitized_events: list[Any] = []
    for event in events:
        end = min(cursor + len(event[2]), len(combined))
        text = combined[cursor:end]
        cursor = end
        if text:
            sanitized_events.append([event[0], event[1], text])
    if cursor < len(combined):
        sanitized_events.append([events[-1][0], events[-1][1], combined[cursor:]])
    return sanitized_events


def retime(
    input_path: str,
    output_path: str,
    target_duration: float,
    *,
    title: str | None = None,
    redact_paths: list[str] | None = None,
) -> None:
    with open(input_path, encoding="utf-8") as f:
        header = json.loads(f.readline())
        events = [json.loads(line) for line in f]

    if title is not None:
        header["title"] = title

    if redact_paths:
        events = redact_event_paths(events, redact_paths)

    if not events:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
        return

    original_duration = events[-1][0] - events[0][0]
    if original_duration <= 0:
        scale = 1.0
    else:
        scale = target_duration / original_duration

    first_ts = events[0][0]
    # Small lead-in so it doesn't start at t=0
    offset = 0.5

    new_events: list[Any] = []
    for event in events:
        new_ts = round(offset + (event[0] - first_ts) * scale, 3)
        new_events.append([new_ts, event[1], event[2]])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in new_events:
            f.write(json.dumps(event) + "\n")

    final_duration = new_events[-1][0]
    print(
        f"Retimed {len(events)} events: {original_duration:.1f}s → {final_duration:.1f}s (scale {scale:.2f}x)",
        file=sys.stderr,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title")
    parser.add_argument("--redact-path", action="append", default=[])
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    parser.add_argument("target_seconds", nargs="?", type=float, default=15.0)
    arguments = parser.parse_args()
    retime(
        arguments.input_path,
        arguments.output_path,
        arguments.target_seconds,
        title=arguments.title,
        redact_paths=arguments.redact_path,
    )


if __name__ == "__main__":
    main()
