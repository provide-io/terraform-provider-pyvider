#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Print the provider binary named and hashed by build provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_binary_path(provenance_path: Path) -> Path:
    loaded: Any = json.loads(provenance_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("provenance must be an object")
    artifacts = loaded.get("artifacts")
    binary = artifacts.get("binary") if isinstance(artifacts, dict) else None
    if not isinstance(binary, dict):
        raise ValueError("provenance does not name a binary")
    relative = binary.get("path")
    expected_sha = binary.get("sha256")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("provider binary path is invalid")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ValueError("provider binary checksum is invalid")
    root = provenance_path.resolve().parent
    path = (root / relative).resolve()
    if path.parent != root and root not in path.parents:
        raise ValueError("provider binary path escapes the build directory")
    if not path.is_file() or sha256_file(path) != expected_sha:
        raise ValueError("provider binary checksum does not match build provenance")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provenance", type=Path)
    args = parser.parse_args()
    try:
        print(verified_binary_path(args.provenance))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
