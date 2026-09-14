#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate a checked provider-linting proof manifest."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from provider_linting_proof import generate_proof, github_environment, utc_now

__all__ = ["generate_proof"]


def _platform() -> str:
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{platform.system().lower()}_{architecture}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cast", type=Path, required=True)
    parser.add_argument("--build-provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        archive_sha = os.environ["PYVIDER_OPENTOFU_ARCHIVE_SHA256"]
        generate_proof(
            cast_path=args.cast,
            build_provenance_path=args.build_provenance,
            output_path=args.output,
            provider_version=(root / "VERSION").read_text(encoding="utf-8").strip(),
            opentofu_archive=f"tofu_1.13.0-beta1_{_platform()}.zip",
            opentofu_archive_sha256=archive_sha,
            generated_at=utc_now(),
            ci_environment=github_environment(),
        )
    except KeyError:
        print("error: PYVIDER_OPENTOFU_ARCHIVE_SHA256 is required", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print("error: proof generation failed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
