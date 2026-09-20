#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
: "${PYVIDER_OPENTOFU_BINARY:?PYVIDER_OPENTOFU_BINARY is required}"

fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/provider-linting-walkthrough.XXXXXX")
trap 'rm -rf "$fixture_root"' EXIT HUP INT TERM
ln -s "$repo_root/tests" "$fixture_root/tests"
cd "$fixture_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Fixture: a temporary working directory links the repository provider-linting suite for this walkthrough.'
printf '%s\n' 'Warnings are lint findings from the documented fixture; any nonzero lint result stops the walkthrough.'
printf '%s\n' 'Coverage boundary: OpenTofu demonstrates native validation and direct demonstrates provider validation.'

printf '\n'
show_command 'uv tool install --refresh tofusoup==0.8.0'
uv tool install --refresh tofusoup==0.8.0
printf '\n'
show_command 'soup --version'
soup --version
printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" --opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$PYVIDER_CONFORMANCE_PSP" \
    --opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu
printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" --lane direct'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$PYVIDER_CONFORMANCE_PSP" --lane direct
