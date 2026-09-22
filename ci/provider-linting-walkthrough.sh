#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Public walkthrough: OpenTofu experimental lint and direct provider validation'
printf '%s\n' 'This uses the released TofuSoup CLI and the packaged provider from the release candidate.'
printf '%s\n' 'OpenTofu reaches four paths; direct provider validation reaches all seven.'

printf '\n'
show_command 'uv tool install --refresh tofusoup==0.8.2'
uv tool install --refresh tofusoup==0.8.2
printf '\n'
show_command 'soup --version'
soup --version
printf '\n'
show_command 'provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)'
provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)
printf '\n'
show_command 'tofu=$(ci/install-opentofu-beta.sh --version 1.13.0-rc1 --cache-dir "$PWD/.cache/opentofu-prerelease")'
tofu=$(ci/install-opentofu-beta.sh --version 1.13.0-rc1 --cache-dir "$PWD/.cache/opentofu-prerelease")
printf '\n'
show_command '"$tofu" version'
"$tofu" version
printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$provider" --opentofu "$tofu" --lane opentofu'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$provider" \
    --opentofu "$tofu" --lane opentofu
printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$provider" --lane direct'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$provider" --lane direct
