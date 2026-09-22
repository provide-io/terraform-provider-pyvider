#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Lane: direct runs the public suite against the checked provider without OpenTofu orchestration.'
printf '%s\n' 'Warnings are lint findings from this fixture; any nonzero lint result stops the recording.'
printf '%s\n' 'Coverage boundary: direct validation is separate from the OpenTofu experimental lint lane.'

printf '\n'
show_command 'uv tool install --refresh --quiet tofusoup==0.8.2'
uv tool install --refresh --quiet tofusoup==0.8.2

printf '\n'
show_command 'provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)'
provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)

printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$provider" --lane direct'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$provider" --lane direct
