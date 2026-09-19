#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
: "${PYVIDER_LINTING_DEMO_ROOT:?PYVIDER_LINTING_DEMO_ROOT is required}"

demo_root=$PYVIDER_LINTING_DEMO_ROOT
mkdir -p "$demo_root"
ln -s "$repo_root/tests" "$demo_root/tests"
cd "$demo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

# The literal variables are deliberately retained in the recording so the
# exact reusable command stays visible without leaking machine-local paths.
printf '%s\n' 'Lane: direct runs the public suite against the checked provider without OpenTofu orchestration.'
printf '%s\n' 'Warnings are lint findings from this fixture; any nonzero lint result stops the recording.'
printf '%s\n' 'Coverage boundary: this lane demonstrates direct provider validation, not OpenTofu-native behavior.'

show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" --lane direct'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$PYVIDER_CONFORMANCE_PSP" --lane direct
