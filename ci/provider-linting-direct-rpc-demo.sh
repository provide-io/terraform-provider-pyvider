#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
: "${PYVIDER_LINTING_DEMO_ROOT:?PYVIDER_LINTING_DEMO_ROOT is required}"

demo_root=$PYVIDER_LINTING_DEMO_ROOT
mkdir -p "$demo_root"
ln -s "$repo_root/ci" "$demo_root/ci"
cd "$demo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

# The literal variable is deliberately retained in the recording so the exact
# reusable command stays visible without leaking its machine-local expansion.
show_command 'uv run python ci/run-provider-linting-rpcs.py --binary "$PYVIDER_CONFORMANCE_PSP" --selector provide-io/pyvider:all --format terminal'
uv run python ci/run-provider-linting-rpcs.py --binary "$PYVIDER_CONFORMANCE_PSP" \
    --selector provide-io/pyvider:all --format terminal
