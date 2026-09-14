#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
: "${PYVIDER_OPENTOFU_BINARY:?PYVIDER_OPENTOFU_BINARY is required}"
: "${PYVIDER_LINTING_DEMO_ROOT:?PYVIDER_LINTING_DEMO_ROOT is required}"

demo_root=$PYVIDER_LINTING_DEMO_ROOT
version=$(<"${repo_root}/VERSION")
case "$(uname -s)" in
    Darwin) os=darwin ;;
    Linux) os=linux ;;
    *) printf 'error: unsupported operating system\n' >&2; exit 2 ;;
esac
case "$(uname -m)" in
    x86_64) arch=amd64 ;;
    arm64|aarch64) arch=arm64 ;;
    *) printf 'error: unsupported architecture\n' >&2; exit 2 ;;
esac

mkdir -p "$demo_root" "$demo_root/mirror/registry.opentofu.org/provide-io/pyvider/$version/${os}_${arch}"
cp "$repo_root/tests/e2e/provider-linting/main.tf" "$demo_root/main.tf"
cp -R "$repo_root/tests/proof/fixtures/provider-linting" "$demo_root/provider-linting"
ln -s "$repo_root/ci" "$demo_root/ci"
provider_copy="$demo_root/mirror/registry.opentofu.org/provide-io/pyvider/$version/${os}_${arch}/terraform-provider-pyvider_v$version"
cp "$PYVIDER_CONFORMANCE_PSP" "$provider_copy"
chmod +x "$provider_copy"

mirror_json=$(uv run python -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$demo_root/mirror")
printf 'provider_installation {\n  filesystem_mirror {\n    path = %s\n    include = ["registry.opentofu.org/provide-io/pyvider"]\n  }\n}\n' \
    "$mirror_json" > "$demo_root/tofurc"

export TF_CLI_CONFIG_FILE="$demo_root/tofurc"
export TF_DATA_DIR="$demo_root/tfdata"
export TOFUSOUP_TF_COMMAND="$PYVIDER_OPENTOFU_BINARY"
export PYVIDER_TESTMODE=true
export PYVIDER_LOG_LEVEL=ERROR
tofu_dir=$(dirname "$PYVIDER_OPENTOFU_BINARY")
export PATH="${tofu_dir}:${repo_root}/.venv/bin:$PATH"
cd "$demo_root"

unset PYVIDER_LINT
tofu init -backend=false -input=false -no-color >/dev/null

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

assert_rule_set() {
    local selector=$1
    local expected=$2
    local output=$demo_root/validate.json
    shift 2
    if [[ "$selector" == __UNSET__ ]]; then
        env -u PYVIDER_LINT tofu validate -json -no-color "$@" > "$output"
    else
        PYVIDER_LINT="$selector" tofu validate -json -no-color "$@" > "$output"
    fi
    uv run python - "$output" "$expected" <<'PY'
import json
from pathlib import Path
import sys

known = {
    "provide-io/pyvider:insecure-tls",
    "provide-io/pyvider:world-writable-directory",
    "provide-io/pyvider:insecure-http",
    "provide-io/pyvider:long-lived-lease",
    "provide-io/pyvider:include-hidden-files",
    "provide-io/pyvider:long-action-timeout",
    "provide-io/pyvider:relative-state-store-path",
}
result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
observed = {
    rule
    for diagnostic in result["diagnostics"]
    for rule in known
    if f"({rule})" in diagnostic["summary"]
}
expected = set(filter(None, sys.argv[2].split(",")))
if observed != expected:
    raise SystemExit(f"provider lint catalog mismatch: expected {sorted(expected)!r}, got {sorted(observed)!r}")
PY
}

show_command 'tofu version'
tofu version

show_command 'tofu validate'
env -u PYVIDER_LINT tofu validate -no-color
assert_rule_set __UNSET__ ''
printf '%s\n' 'PASS: provider linting default-off (0 provider lint diagnostics)'

show_command 'PYVIDER_LINT=provide-io/pyvider:all tofu validate -lint=all'
PYVIDER_LINT=provide-io/pyvider:all tofu validate -lint=all -no-color
assert_rule_set provide-io/pyvider:all \
    'provide-io/pyvider:insecure-tls,provide-io/pyvider:world-writable-directory,provide-io/pyvider:insecure-http,provide-io/pyvider:long-lived-lease' \
    -lint=all
printf '%s\n' 'OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)'

show_command "PYVIDER_LINT='provide-io/pyvider:all,!provide-io/pyvider:insecure-http' tofu validate"
PYVIDER_LINT='provide-io/pyvider:all,!provide-io/pyvider:insecure-http' tofu validate -no-color
assert_rule_set 'provide-io/pyvider:all,!provide-io/pyvider:insecure-http' \
    'provide-io/pyvider:insecure-tls,provide-io/pyvider:world-writable-directory,provide-io/pyvider:long-lived-lease'
printf '%s\n' 'PASS: exact exclusion removed provide-io/pyvider:insecure-http'

show_command 'soup stir provider-linting'
env -u PYVIDER_LINT soup stir provider-linting
printf '%s\n' 'TofuSoup lifecycle: PASS (same packaged provider; not direct RPC coverage)'

# The literal variable is part of the reproducible command shown in the cast.
# shellcheck disable=SC2016
show_command 'uv run python ci/run-provider-linting-rpcs.py --binary "$PYVIDER_CONFORMANCE_PSP" --selector provide-io/pyvider:all --format json-lines'
uv run python ci/run-provider-linting-rpcs.py --binary "$PYVIDER_CONFORMANCE_PSP" \
    --selector provide-io/pyvider:all --format json-lines
printf '%s\n' 'TofuSoup direct RPC proof: 7/7 provider lint rules passed'
