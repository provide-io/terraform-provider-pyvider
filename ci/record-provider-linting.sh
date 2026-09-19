#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
provenance=${PYVIDER_LINTING_PROVENANCE:-$repo_root/dist/provider-linting-build-provenance.json}
cache_dir=${OPENTOFU_LINTING_CACHE_DIR:-$repo_root/.cache/opentofu-beta}
staging=$(mktemp -d "$repo_root/.provider-linting-proof.XXXXXX")
trap 'rm -rf "$staging"' EXIT HUP INT TERM

expected_sha=$(uv run python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["artifacts"]["binary"]["sha256"])' "$provenance")
provenance_binary=$(uv run python -c 'import json,pathlib,sys; p=pathlib.Path(sys.argv[1]).resolve(); d=json.loads(p.read_text(encoding="utf-8")); print((p.parent / d["artifacts"]["binary"]["path"]).resolve())' "$provenance")
supplied_binary=$(uv run python -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$PYVIDER_CONFORMANCE_PSP")
if [[ "$supplied_binary" != "$provenance_binary" ]]; then
    printf '%s\n' 'error: PYVIDER_CONFORMANCE_PSP must be the binary named by build provenance' >&2
    exit 2
fi
binary_sha() {
    shasum -a 256 "$PYVIDER_CONFORMANCE_PSP" | awk '{print $1}'
}
if [[ "$(binary_sha)" != "$expected_sha" ]]; then
    printf '%s\n' 'error: provider binary checksum does not match build provenance' >&2
    exit 2
fi

if [[ -n "${PYVIDER_OPENTOFU_BINARY:-}" || -n "${PYVIDER_OPENTOFU_ARCHIVE_SHA256:-}" ]]; then
    : "${PYVIDER_OPENTOFU_BINARY:?both PYVIDER_OPENTOFU_BINARY and PYVIDER_OPENTOFU_ARCHIVE_SHA256 are required}"
    : "${PYVIDER_OPENTOFU_ARCHIVE_SHA256:?both PYVIDER_OPENTOFU_BINARY and PYVIDER_OPENTOFU_ARCHIVE_SHA256 are required}"
    tofu=$PYVIDER_OPENTOFU_BINARY
    archive_sha=$PYVIDER_OPENTOFU_ARCHIVE_SHA256
else
    install_log=$staging/opentofu-install.log
    tofu=$("$repo_root/ci/install-opentofu-beta.sh" \
        --version 1.13.0-beta1 --cache-dir "$cache_dir" 2>"$install_log")
    archive_sha=$(awk '/^verified [0-9a-f]{64}$/ { print $2 }' "$install_log")
fi
if [[ ! -x "$tofu" || ! "$archive_sha" =~ ^[0-9a-f]{64}$ ]]; then
    printf '%s\n' 'error: pinned OpenTofu binary/checksum is unavailable' >&2
    exit 2
fi
if ! "$tofu" version | grep -Fxq 'OpenTofu v1.13.0-beta1'; then
    printf '%s\n' 'error: OpenTofu v1.13.0-beta1 is required' >&2
    exit 2
fi

raw_opentofu_cast=$staging/provider-linting-opentofu.raw.cast
checked_opentofu_cast=$staging/provider-linting-opentofu.cast
raw_direct_cast=$staging/provider-linting-direct.raw.cast
checked_direct_cast=$staging/provider-linting-direct.cast
raw_walkthrough_cast=$staging/provider-linting-walkthrough.raw.cast
checked_walkthrough_cast=$staging/provider-linting-walkthrough.cast
checked_manifest=$staging/provider-linting-proof.json
opentofu_demo_root=$staging/opentofu-demo
direct_demo_root=$staging/direct-demo

PYVIDER_OPENTOFU_BINARY="$tofu" \
PYVIDER_LINTING_DEMO_ROOT="$opentofu_demo_root" \
python3 "$repo_root/ci/record-to-cast.py" \
    --title 'Pyvider linting — OpenTofu demonstration' --width 120 --height 40 \
    "$raw_opentofu_cast" "$repo_root/ci/provider-linting-demo.sh"

python3 "$repo_root/ci/pace-provider-linting-cast.py" \
    --lane opentofu "$raw_opentofu_cast" "$checked_opentofu_cast"

PYVIDER_LINTING_DEMO_ROOT="$direct_demo_root" \
python3 "$repo_root/ci/record-to-cast.py" \
    --title 'Pyvider linting — direct provider validation' --width 120 --height 40 \
    "$raw_direct_cast" "$repo_root/ci/provider-linting-direct-rpc-demo.sh"

python3 "$repo_root/ci/pace-provider-linting-cast.py" \
    --lane direct "$raw_direct_cast" "$checked_direct_cast"

PYVIDER_OPENTOFU_BINARY="$tofu" \
python3 "$repo_root/ci/record-to-cast.py" \
    --title 'Pyvider provider-native linting proof' --width 120 --height 40 \
    "$raw_walkthrough_cast" "$repo_root/ci/provider-linting-walkthrough.sh"

python3 "$repo_root/ci/pace-provider-linting-cast.py" \
    --lane walkthrough "$raw_walkthrough_cast" "$checked_walkthrough_cast"

PYVIDER_OPENTOFU_ARCHIVE_SHA256="$archive_sha" \
uv run python "$repo_root/ci/generate-provider-linting-proof.py" \
    --opentofu-cast "$checked_opentofu_cast" --direct-rpc-cast "$checked_direct_cast" \
    --build-provenance "$provenance" --output "$checked_manifest"
uv run python "$repo_root/ci/verify-provider-linting-proof.py" \
    "$checked_manifest" "$checked_opentofu_cast" "$checked_direct_cast"

if [[ "$(binary_sha)" != "$expected_sha" ]]; then
    printf '%s\n' 'error: provider binary checksum changed during recording' >&2
    exit 2
fi

backup_opentofu_cast=$staging/original-opentofu.cast
backup_direct_cast=$staging/original-direct.cast
backup_walkthrough_cast=$staging/original-walkthrough.cast
backup_manifest=$staging/original.json
[[ ! -e "$repo_root/provider-linting-opentofu.cast" ]] || cp "$repo_root/provider-linting-opentofu.cast" "$backup_opentofu_cast"
[[ ! -e "$repo_root/provider-linting-direct.cast" ]] || cp "$repo_root/provider-linting-direct.cast" "$backup_direct_cast"
[[ ! -e "$repo_root/provider-linting-walkthrough.cast" ]] || cp "$repo_root/provider-linting-walkthrough.cast" "$backup_walkthrough_cast"
[[ ! -e "$repo_root/provider-linting-proof.json" ]] || cp "$repo_root/provider-linting-proof.json" "$backup_manifest"
published_opentofu_cast=false
published_direct_cast=false
published_walkthrough_cast=false
published_manifest=false
rollback() {
    if [[ "$published_manifest" == true ]]; then
        if [[ -e "$backup_manifest" ]]; then cp "$backup_manifest" "$repo_root/provider-linting-proof.json"; else rm -f "$repo_root/provider-linting-proof.json"; fi
    fi
    if [[ "$published_walkthrough_cast" == true ]]; then
        if [[ -e "$backup_walkthrough_cast" ]]; then cp "$backup_walkthrough_cast" "$repo_root/provider-linting-walkthrough.cast"; else rm -f "$repo_root/provider-linting-walkthrough.cast"; fi
    fi
    if [[ "$published_direct_cast" == true ]]; then
        if [[ -e "$backup_direct_cast" ]]; then cp "$backup_direct_cast" "$repo_root/provider-linting-direct.cast"; else rm -f "$repo_root/provider-linting-direct.cast"; fi
    fi
    if [[ "$published_opentofu_cast" == true ]]; then
        if [[ -e "$backup_opentofu_cast" ]]; then cp "$backup_opentofu_cast" "$repo_root/provider-linting-opentofu.cast"; else rm -f "$repo_root/provider-linting-opentofu.cast"; fi
    fi
}
trap 'rollback; rm -rf "$staging"' ERR
mv "$checked_opentofu_cast" "$repo_root/provider-linting-opentofu.cast"
published_opentofu_cast=true
mv "$checked_direct_cast" "$repo_root/provider-linting-direct.cast"
published_direct_cast=true
mv "$checked_walkthrough_cast" "$repo_root/provider-linting-walkthrough.cast"
published_walkthrough_cast=true
mv "$checked_manifest" "$repo_root/provider-linting-proof.json"
published_manifest=true
trap - ERR

printf 'Published checked proof: provider-linting-opentofu.cast + provider-linting-direct.cast + provider-linting-walkthrough.cast + provider-linting-proof.json\n'
