#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env bash
# Re-run the conformance suite under the PTY recorder to produce an asciinema
# v2 .cast file. Runs from the repo root; output written to conformance.cast.
# Called by the record-casts CI step (Linux only).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="${REPO_ROOT}/conformance.cast"

cd "${REPO_ROOT}/examples"

# record-to-cast.py strips screen-clear and cursor-position sequences in the
# captured output, so the player scrolls smoothly without flashing.
exec python3 "${REPO_ROOT}/ci/record-to-cast.py" "${OUTPUT}" \
    soup stir --recursive
