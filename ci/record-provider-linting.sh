#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${PYVIDER_CONFORMANCE_PSP:?PYVIDER_CONFORMANCE_PSP is required}"
provenance=${PYVIDER_LINTING_PROVENANCE:-$repo_root/dist/provider-linting-build-provenance.json}
cache_dir=${OPENTOFU_LINTING_CACHE_DIR:-$repo_root/.cache/opentofu-prerelease}
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
        --version 1.13.0-rc1 --cache-dir "$cache_dir" 2>"$install_log")
    archive_sha=$(awk '/^verified [0-9a-f]{64}$/ { print $2 }' "$install_log")
fi
if [[ ! -x "$tofu" || ! "$archive_sha" =~ ^[0-9a-f]{64}$ ]]; then
    printf '%s\n' 'error: pinned OpenTofu binary/checksum is unavailable' >&2
    exit 2
fi
if ! "$tofu" version | grep -Fxq 'OpenTofu v1.13.0-rc1'; then
    printf '%s\n' 'error: OpenTofu v1.13.0-rc1 is required' >&2
    exit 2
fi

raw_opentofu_cast=$staging/provider-linting-opentofu.raw.cast
checked_opentofu_cast=$staging/provider-linting-opentofu.cast
raw_direct_cast=$staging/provider-linting-direct.raw.cast
checked_direct_cast=$staging/provider-linting-direct.cast
raw_walkthrough_cast=$staging/provider-linting-walkthrough.raw.cast
checked_walkthrough_cast=$staging/provider-linting-walkthrough.cast
raw_tutorial_cast=$staging/tutorial-part7-provider-linting.raw.cast
checked_tutorial_cast=$staging/tutorial-part7-provider-linting.cast
checked_manifest=$staging/provider-linting-proof.json
opentofu_demo_root=$staging/opentofu-demo
direct_demo_root=$staging/direct-demo

record_lane() {
    local lane=$1
    local width=$2
    local height=$3
    local raw_cast=$staging/provider-linting-${lane}.raw.cast
    local checked_cast=$staging/provider-linting-${lane}.cast
    if [[ "$lane" == tutorial ]]; then
        raw_cast=$raw_tutorial_cast
        checked_cast=$checked_tutorial_cast
    fi

    case "$lane" in
        opentofu)
            PYVIDER_OPENTOFU_BINARY="$tofu" \
            PYVIDER_LINTING_DEMO_ROOT="$opentofu_demo_root" \
            python3 "$repo_root/ci/record-to-cast.py" \
                --title 'Pyvider linting — OpenTofu demonstration' --width "$width" --height "$height" \
                "$raw_cast" "$repo_root/ci/provider-linting-demo.sh"
            python3 "$repo_root/ci/pace-provider-linting-cast.py" \
                --lane opentofu "$raw_cast" "$checked_cast"
            ;;
        direct)
            PYVIDER_LINTING_DEMO_ROOT="$direct_demo_root" \
            python3 "$repo_root/ci/record-to-cast.py" \
                --title 'Pyvider linting — direct provider validation' --width "$width" --height "$height" \
                "$raw_cast" "$repo_root/ci/provider-linting-direct-rpc-demo.sh"
            python3 "$repo_root/ci/pace-provider-linting-cast.py" \
                --lane direct "$raw_cast" "$checked_cast"
            ;;
        walkthrough)
            python3 "$repo_root/ci/record-to-cast.py" \
                --title 'Pyvider provider-native linting proof' --width "$width" --height "$height" \
                "$raw_cast" "$repo_root/ci/provider-linting-walkthrough.sh"
            python3 "$repo_root/ci/pace-provider-linting-cast.py" \
                --lane walkthrough "$raw_cast" "$checked_cast"
            ;;
        tutorial)
            python3 "$repo_root/ci/record-to-cast.py" \
                --title 'Part 7 — author and verify a provider lint rule' --width "$width" --height "$height" \
                "$raw_cast" "$repo_root/ci/provider-linting-tutorial.sh"
            python3 "$repo_root/ci/pace-provider-linting-cast.py" \
                --lane tutorial "$raw_cast" "$checked_cast"
            ;;
        *)
            printf 'error: unknown proof film lane: %s\n' "$lane" >&2
            return 2
            ;;
    esac

}

record_lane opentofu 110 26
record_lane direct 110 26
record_lane walkthrough 110 26
record_lane tutorial 110 26

PYVIDER_OPENTOFU_ARCHIVE_SHA256="$archive_sha" \
uv run python "$repo_root/ci/generate-provider-linting-proof.py" \
    --opentofu-cast "$checked_opentofu_cast" --direct-rpc-cast "$checked_direct_cast" \
    --walkthrough-cast "$checked_walkthrough_cast" \
    --tutorial-cast "$checked_tutorial_cast" \
    --build-provenance "$provenance" --output "$checked_manifest"
uv run python "$repo_root/ci/verify-provider-linting-proof.py" \
    "$checked_manifest" "$checked_opentofu_cast" "$checked_direct_cast" "$checked_walkthrough_cast" \
    "$checked_tutorial_cast"

if [[ "$(binary_sha)" != "$expected_sha" ]]; then
    printf '%s\n' 'error: provider binary checksum changed during recording' >&2
    exit 2
fi

backup_opentofu_cast=$staging/original-opentofu.cast
backup_direct_cast=$staging/original-direct.cast
backup_walkthrough_cast=$staging/original-walkthrough.cast
backup_tutorial_cast=$staging/original-tutorial.cast
backup_manifest=$staging/original.json
[[ ! -e "$repo_root/provider-linting-opentofu.cast" ]] || cp "$repo_root/provider-linting-opentofu.cast" "$backup_opentofu_cast"
[[ ! -e "$repo_root/provider-linting-direct.cast" ]] || cp "$repo_root/provider-linting-direct.cast" "$backup_direct_cast"
[[ ! -e "$repo_root/provider-linting-walkthrough.cast" ]] || cp "$repo_root/provider-linting-walkthrough.cast" "$backup_walkthrough_cast"
[[ ! -e "$repo_root/tutorial-part7-provider-linting.cast" ]] || cp "$repo_root/tutorial-part7-provider-linting.cast" "$backup_tutorial_cast"
[[ ! -e "$repo_root/provider-linting-proof.json" ]] || cp "$repo_root/provider-linting-proof.json" "$backup_manifest"
published_opentofu_cast=false
published_direct_cast=false
published_walkthrough_cast=false
published_tutorial_cast=false
published_manifest=false
rollback() {
    if [[ "$published_manifest" == true ]]; then
        if [[ -e "$backup_manifest" ]]; then cp "$backup_manifest" "$repo_root/provider-linting-proof.json"; else rm -f "$repo_root/provider-linting-proof.json"; fi
    fi
    if [[ "$published_walkthrough_cast" == true ]]; then
        if [[ -e "$backup_walkthrough_cast" ]]; then cp "$backup_walkthrough_cast" "$repo_root/provider-linting-walkthrough.cast"; else rm -f "$repo_root/provider-linting-walkthrough.cast"; fi
    fi
    if [[ "$published_tutorial_cast" == true ]]; then
        if [[ -e "$backup_tutorial_cast" ]]; then cp "$backup_tutorial_cast" "$repo_root/tutorial-part7-provider-linting.cast"; else rm -f "$repo_root/tutorial-part7-provider-linting.cast"; fi
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
mv "$checked_tutorial_cast" "$repo_root/tutorial-part7-provider-linting.cast"
published_tutorial_cast=true
mv "$checked_manifest" "$repo_root/provider-linting-proof.json"
published_manifest=true
trap - ERR

printf 'Published checked proof: provider-linting-opentofu.cast + provider-linting-direct.cast + provider-linting-walkthrough.cast + tutorial-part7-provider-linting.cast + provider-linting-proof.json\n'
