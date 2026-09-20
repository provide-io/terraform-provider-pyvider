#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
: "${PYVIDER_OPENTOFU_BINARY:?PYVIDER_OPENTOFU_BINARY is required}"
: "${PYVIDER_LINTING_DEMO_ROOT:?PYVIDER_LINTING_DEMO_ROOT is required}"

demo_root=$PYVIDER_LINTING_DEMO_ROOT
mkdir -p "$demo_root"
ln -s "$repo_root/tests" "$demo_root/tests"
cd "$demo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Lane: OpenTofu runs the public suite through the checked provider and OpenTofu binary.'
printf '%s\n' 'Warnings are lint findings from this fixture; any nonzero lint result stops the recording.'
printf '%s\n' 'Coverage boundary: this lane demonstrates OpenTofu-native validation, not direct provider RPC coverage.'

printf '\n'
show_command 'tofu version'
"$PYVIDER_OPENTOFU_BINARY" version

printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" --opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$PYVIDER_CONFORMANCE_PSP" \
    --opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu
printf '%s\n' 'OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)'
