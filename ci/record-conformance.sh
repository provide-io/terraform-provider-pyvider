#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env bash
# Re-run the conformance suite under the PTY recorder to produce an asciinema
# v2 .cast file. Runs from the repo root; output written to conformance.cast.
# Called by the record-casts CI step (Linux only).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="${REPO_ROOT}/conformance.cast"
RAW="${REPO_ROOT}/conformance.raw.cast"

cd "${REPO_ROOT}/examples"

# record-to-cast.py strips screen-clear and cursor-position sequences in the
# captured output, so the player scrolls smoothly without flashing.
# Capture the test exit code so we can retime before propagating it.
python3 "${REPO_ROOT}/ci/record-to-cast.py" "${RAW}" \
    soup stir --recursive
RECORD_EXIT=$?

# retime-cast.py proportionally scales to a target duration for the website.
python3 "${REPO_ROOT}/ci/retime-cast.py" "${RAW}" "${OUTPUT}" 15

rm -f "${RAW}"

exit "${RECORD_EXIT}"
