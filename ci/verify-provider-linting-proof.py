#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Verify a provider-linting proof manifest and complete asciicast."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from provider_linting_proof import strip_terminal_controls, verify_proof, verify_split_proof

__all__ = ["strip_terminal_controls", "verify_proof", "verify_split_proof"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("casts", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        if len(args.casts) == 1:
            rule_ids = verify_proof(args.manifest, args.casts[0])
        elif len(args.casts) == 2:
            rule_ids = verify_split_proof(args.manifest, args.casts[0], args.casts[1])
        elif len(args.casts) == 3:
            rule_ids = verify_split_proof(args.manifest, args.casts[0], args.casts[1], args.casts[2])
        elif len(args.casts) == 4:
            rule_ids = verify_split_proof(
                args.manifest,
                args.casts[0],
                args.casts[1],
                args.casts[2],
                args.casts[3],
            )
        else:
            raise ValueError("provide one legacy cast, two split casts, or all four public proof films")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"verified provider linting proof: {len(rule_ids)}/7 rules")
    for rule_id in rule_ids:
        print(rule_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
