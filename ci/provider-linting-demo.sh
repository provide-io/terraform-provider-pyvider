#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Lane: OpenTofu runs the public suite through the checked provider and OpenTofu binary.'
printf '%s\n' 'Warnings are lint findings from this fixture; any nonzero lint result stops the recording.'
printf '%s\n' 'Coverage boundary: OpenTofu experimental lint validation reaches four ordinary validation paths.'

printf '\n'
show_command 'uv tool install --refresh --quiet tofusoup==0.8.2'
uv tool install --refresh --quiet tofusoup==0.8.2

printf '\n'
show_command 'provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)'
provider=$(uv run python ci/provider-linting-artifact-path.py dist/provider-linting-build-provenance.json)

printf '\n'
show_command 'tofu=$(ci/install-opentofu-experimental.sh --version 1.13.0-rc1 --cache-dir "$PWD/.cache/opentofu-prerelease")'
tofu=$(ci/install-opentofu-experimental.sh --version 1.13.0-rc1 --cache-dir "$PWD/.cache/opentofu-prerelease")

printf '\n'
show_command '"$tofu" version'
"$tofu" version

printf '\n'
show_command 'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$provider" --opentofu "$tofu" --lane opentofu'
soup lint tests/e2e/provider-linting/lint.soup.toml \
    --provider "$provider" \
    --opentofu "$tofu" --lane opentofu
printf '%s\n' 'OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)'
