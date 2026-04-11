#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""
Record a command's terminal output as an asciinema v2 .cast file.

Uses Python's pty module to allocate a real PTY so terminal escape sequences,
colors, and cursor movement are captured correctly — no asciinema binary required.

Usage:
    python3 ci/record-to-cast.py OUTPUT.cast COMMAND [ARGS...]

Example:
    python3 ci/record-to-cast.py conformance.cast soup stir --recursive
"""
import fcntl
import json
import os
import pty
import re
import struct
import subprocess
import sys
import termios
import time

# Strip only the sequences that cause the player to flash — specifically the
# alternate screen buffer switch and full-screen clears. Leave everything else
# (colors, erase-line, cursor movement) intact so the output renders correctly.
_STRIP_RE = re.compile(
    r"\x1b\["
    r"(?:"
    r"\?(?:1049|1047|47)[hl]"   # alternate screen buffer enter/exit (the flash cause)
    r"|\?25[lh]"                 # cursor hide/show
    r"|[23]J"                    # erase entire screen / clear scrollback
    r")"
)


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} OUTPUT.cast COMMAND [ARGS...]", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[1]
    command = sys.argv[2:]

    events: list = []
    start_time = time.time()

    cols, rows = 120, 40
    master_fd, slave_fd = pty.openpty()

    # Set the PTY size so the child process renders at the target dimensions.
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

    proc = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )
    os.close(slave_fd)

    while True:
        try:
            chunk = os.read(master_fd, 4096)
        except OSError:
            break
        if not chunk:
            break
        elapsed = round(time.time() - start_time, 6)
        text = _STRIP_RE.sub("", chunk.decode("utf-8", errors="replace"))
        if text:
            events.append([elapsed, "o", text])
        sys.stdout.buffer.write(chunk)
        sys.stdout.flush()

    proc.wait()
    exit_code = proc.returncode
    os.close(master_fd)

    header = {
        "version": 2,
        "width": cols,
        "height": rows,
        "timestamp": int(start_time),
        "title": "pyvider conformance suite",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in events:
            f.write(json.dumps(event) + "\n")

    print(
        f"\n✅ Cast written to {output_path} ({len(events)} events, {time.time() - start_time:.1f}s)",
        file=sys.stderr,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
