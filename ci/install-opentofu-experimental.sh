#!/bin/sh
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -eu

PINNED_VERSION="1.13.0-rc1"
VERSION=""
RELEASE_BASE_URL=""
CACHE_DIR=""

usage() {
    printf 'usage: %s --version 1.13.0-rc1 --cache-dir PATH [--release-base-url URL]\n' "$0" >&2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --version)
            [ "$#" -ge 2 ] || { usage; exit 2; }
            VERSION=$2
            shift 2
            ;;
        --cache-dir)
            [ "$#" -ge 2 ] || { usage; exit 2; }
            CACHE_DIR=$2
            shift 2
            ;;
        --release-base-url)
            [ "$#" -ge 2 ] || { usage; exit 2; }
            RELEASE_BASE_URL=$2
            shift 2
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

if [ -z "$VERSION" ]; then
    printf '%s\n' 'error: --version 1.13.0-rc1 is required' >&2
    exit 2
fi
if [ "$VERSION" != "$PINNED_VERSION" ]; then
    printf '%s\n' 'error: only OpenTofu 1.13.0-rc1 is supported' >&2
    exit 2
fi
if [ -z "$CACHE_DIR" ]; then
    printf '%s\n' 'error: --cache-dir is required' >&2
    exit 2
fi
if [ -z "$RELEASE_BASE_URL" ]; then
    RELEASE_BASE_URL="https://github.com/opentofu/opentofu/releases/download/v${VERSION}"
fi

case "$(uname -s)" in
    Darwin) os=darwin ;;
    Linux) os=linux ;;
    *) printf 'error: unsupported operating system: %s\n' "$(uname -s)" >&2; exit 2 ;;
esac

case "$(uname -m)" in
    x86_64) arch=amd64 ;;
    arm64|aarch64) arch=arm64 ;;
    *) printf 'error: unsupported architecture: %s\n' "$(uname -m)" >&2; exit 2 ;;
esac

platform="${os}_${arch}"
archive="tofu_${VERSION}_${platform}.zip"
sums="tofu_${VERSION}_SHA256SUMS"
install_dir="${CACHE_DIR}/${VERSION}/${platform}"
binary="${install_dir}/tofu"

mkdir -p "$CACHE_DIR"
work_dir=$(mktemp -d "${CACHE_DIR%/}/.install-${VERSION}-${platform}.XXXXXX")
cleanup() {
    rm -rf "$work_dir"
}
trap cleanup EXIT HUP INT TERM

download_dir="${work_dir}/downloads"
extract_dir="${work_dir}/extract"
mkdir -p "$download_dir" "$extract_dir"
curl --fail --location --silent --show-error --output "${download_dir}/${sums}" "${RELEASE_BASE_URL}/${sums}"
curl --fail --location --silent --show-error --output "${download_dir}/${archive}" "${RELEASE_BASE_URL}/${archive}"

checksum_line=$(awk -v archive="$archive" '$2 == archive { print; found = 1; exit } END { if (!found) exit 1 }' "${download_dir}/${sums}") || {
    printf 'error: checksum file has no entry for %s\n' "$archive" >&2
    exit 1
}
printf '%s\n' "$checksum_line" > "${download_dir}/${archive}.sha256"
(
    cd "$download_dir"
    shasum -a 256 -c "${archive}.sha256" >&2
)
printf 'verified %s\n' "${checksum_line%% *}" >&2

unzip -oq "${download_dir}/${archive}" tofu -d "$extract_dir"
chmod +x "${extract_dir}/tofu"
mkdir -p "$install_dir"
mv -f "${extract_dir}/tofu" "$binary"
printf '%s\n' "$binary"
