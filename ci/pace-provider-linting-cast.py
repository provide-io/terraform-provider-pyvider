#!/usr/bin/env python3
"""Pace a provider-linting asciinema v2 recording without changing its output.

The recordings are evidence, so this utility deliberately changes timestamps
only.  It emits output at complete terminal-line boundaries and keeps each
line's terminal control sequences exactly as captured.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


@dataclass(frozen=True)
class PaceProfile:
    """A named presentation lane and its observed-duration target."""

    target_seconds: float
    command_weight: float = 3.0
    heading_weight: float = 3.0
    warning_weight: float = 2.2
    result_weight: float = 2.0
    text_weight: float = 1.0


PROFILES = {
    "opentofu": PaceProfile(target_seconds=40.0),
    "direct": PaceProfile(target_seconds=58.0),
    "walkthrough": PaceProfile(target_seconds=80.0),
}


class CastError(ValueError):
    """A recording cannot safely be paced."""


def _parse_json_line(line: str, *, label: str) -> Any:
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise CastError(f"invalid {label}") from exc


def _read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except OSError as exc:
        raise CastError(f"cannot read cast: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CastError("cast contains invalid UTF-8") from exc


def _validate_utf8_strings(value: Any, *, label: str) -> None:
    """Reject lone surrogates before any destination file is touched."""
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise CastError(f"{label} contains invalid UTF-8") from exc
    elif isinstance(value, list):
        for nested in value:
            _validate_utf8_strings(nested, label=label)
    elif isinstance(value, dict):
        for key, nested in value.items():
            _validate_utf8_strings(key, label=label)
            _validate_utf8_strings(nested, label=label)


def _validate_event(event: Any, *, number: int) -> list[Any]:
    if not isinstance(event, list) or len(event) != 3:
        raise CastError(f"invalid cast event on line {number}")
    timestamp, event_type, payload = event
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise CastError(f"invalid timestamp on event line {number}")
    if not isinstance(event_type, str) or not isinstance(payload, str):
        raise CastError(f"invalid cast event on line {number}")
    if event_type == "o":
        try:
            payload.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise CastError("output event payload is not valid UTF-8") from exc
    _validate_utf8_strings(event, label=f"cast event on line {number}")
    try:
        finite_timestamp = math.isfinite(float(timestamp))
    except OverflowError as exc:
        raise CastError(f"invalid timestamp on event line {number}") from exc
    if not finite_timestamp:
        raise CastError(f"invalid timestamp on event line {number}")
    return event


def load_cast(path: Path) -> tuple[dict[str, Any], list[list[Any]]]:
    """Load and validate the subset of asciinema v2 needed for pacing."""
    text = _read_utf8(path)
    # JSON Lines has physical LF record separators.  str.splitlines() also
    # treats Unicode line-separator characters in a JSON string as records.
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    if not lines:
        raise CastError("cast is empty")
    header = _parse_json_line(lines[0], label="cast header")
    if not isinstance(header, dict):
        raise CastError("cast header must be an object")
    _validate_utf8_strings(header, label="cast header")
    if header.get("version") != 2:
        raise CastError("unsupported asciinema cast version (expected version 2)")

    events: list[list[Any]] = []
    for number, line in enumerate(lines[1:], start=2):
        events.append(
            _validate_event(_parse_json_line(line, label=f"cast event on line {number}"), number=number)
        )
    if not any(event[1] == "o" for event in events):
        raise CastError("cast has no output events")
    return header, events


def _after_escape(value: str, position: int) -> int:
    """Return the first position after an ANSI escape sequence."""
    limit = len(value)
    if position + 1 >= limit:
        return position + 1
    sequence = value[position + 1]
    if sequence == "[":
        position += 2
        while position < limit:
            character = value[position]
            position += 1
            if "@" <= character <= "~":
                break
        return position
    if sequence == "]":
        position += 2
        while position < limit:
            if value[position] == "\x07":
                return position + 1
            if value[position : position + 2] == "\x1b\\":
                return position + 2
            position += 1
        return position
    return position + 2


def _complete_visible_lines(output: str) -> list[str]:
    """Split at LF outside ANSI control sequences, retaining every character."""
    lines: list[str] = []
    start = 0
    position = 0
    limit = len(output)
    while position < limit:
        if output[position] == "\x1b":
            position = _after_escape(output, position)
            continue
        if output[position] == "\n":
            lines.append(output[start : position + 1])
            start = position + 1
        position += 1
    if start < limit:
        lines.append(output[start:])
    return lines


def _visible_text(value: str) -> str:
    """Drop terminal controls only for classification; never for serialization."""
    characters: list[str] = []
    position = 0
    limit = len(value)
    while position < limit:
        if value[position] == "\x1b":
            position = _after_escape(value, position)
            continue
        characters.append(value[position])
        position += 1
    return "".join(characters).replace("\r", "").strip()


def _line_weight(value: str, profile: PaceProfile) -> float:
    visible = _visible_text(value).lower()
    if visible.startswith(("$ ", "> ")):
        return profile.command_weight
    if visible.endswith(":") or visible.startswith(("==", "##")):
        return profile.heading_weight
    if any(marker in visible for marker in ("warning", "warn:", "error:")):
        return profile.warning_weight
    if visible.startswith(("pass", "fail", "success", "valid")) or "/" in visible:
        return profile.result_weight
    return profile.text_weight


def pace_output(output: str, profile: PaceProfile) -> list[tuple[str, float]]:
    """Return byte-preserving logical output chunks with presentation times."""
    chunks: list[str] = []
    pending = ""
    for line in _complete_visible_lines(output):
        visible = _visible_text(line)
        complete = line.endswith("\n")
        if not visible or not complete:
            if chunks:
                chunks[-1] += line
            else:
                pending += line
            continue
        chunks.append(pending + line)
        pending = ""
    if pending:
        if chunks:
            chunks[-1] += pending
        else:
            chunks.append(pending)

    weights = [_line_weight(chunk, profile) for chunk in chunks]
    total_weight = sum(weights)
    if total_weight == 0:
        return []
    elapsed = 0.0
    paced: list[tuple[str, float]] = []
    for index, (chunk, weight) in enumerate(zip(chunks, weights, strict=True)):
        elapsed += profile.target_seconds * weight / total_weight
        timestamp = profile.target_seconds if index == len(chunks) - 1 else round(elapsed, 3)
        paced.append((chunk, timestamp))
    return paced


def _ordered_paced_events(events: list[list[Any]], paced_output: list[tuple[str, float]]) -> list[list[Any]]:
    """Keep non-output events in source order without splitting output early."""
    paced_events: list[list[Any]] = []
    available_output = 0
    emitted_output = 0
    chunk_index = 0
    for event in events:
        if event[1] == "o":
            available_output += len(event[2])
            while chunk_index < len(paced_output):
                chunk, timestamp = paced_output[chunk_index]
                if emitted_output + len(chunk) > available_output:
                    break
                paced_events.append([timestamp, "o", chunk])
                emitted_output += len(chunk)
                chunk_index += 1
            continue
        if emitted_output != available_output:
            raise CastError("non-output event interrupts output outside a complete visible line")
        timestamp = paced_output[max(chunk_index - 1, 0)][1]
        paced_events.append([timestamp, event[1], event[2]])
    if chunk_index != len(paced_output):
        raise CastError("unable to preserve output event order")
    return paced_events


def _serialize_cast(header: dict[str, Any], events: list[list[Any]]) -> bytes:
    try:
        document = "\n".join(
            [
                json.dumps(header, ensure_ascii=False),
                *(json.dumps(event, ensure_ascii=False) for event in events),
            ]
        )
        return (document + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise CastError("paced cast cannot be serialized as UTF-8") from exc


def _atomic_write(path: Path, content: bytes) -> None:
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(mode="wb", prefix=f".{path.name}.", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    except OSError as exc:
        raise CastError(f"cannot write paced cast: {exc}") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def pace_cast(input_path: Path, output_path: Path, lane: str) -> None:
    header, events = load_cast(input_path)
    profile = PROFILES[lane]
    output = "".join(event[2] for event in events if event[1] == "o")
    paced_output = pace_output(output, profile)
    if not paced_output:
        raise CastError("cast has no paceable output")
    paced_events = _ordered_paced_events(events, paced_output)
    _atomic_write(output_path, _serialize_cast(header, paced_events))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=tuple(PROFILES), required=True, help="named presentation lane")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_path", type=Path)
    arguments = parser.parse_args()
    try:
        pace_cast(arguments.input_path, arguments.output_path, arguments.lane)
    except CastError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
