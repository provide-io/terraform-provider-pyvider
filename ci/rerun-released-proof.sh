#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Re-run the provider-linting proof against a released, already-verified
# linux_amd64 binary: conformance, the OpenTofu lint lane, and the published
# proof films.
#
# The released conformance tests read the build provenance from dist/ at the
# repository root and require the binary it names to sit beside it, exactly as
# the build left them. verify-release-binding.py unpacked that layout under
# <released-dir>/dist/; this copies it into the checkout's dist/ and runs the
# binary from there. A dist/ that already equals the released one is reused, so
# a failed run can be retried; any other dist/ is refused. The released
# Makefile installs and checksum-verifies its own pinned OpenTofu.
#
# Usage: ci/rerun-released-proof.sh <released-dir>
set -euo pipefail

RELEASED="${1:?usage: $0 <released-dir>}"
RELEASED="$(CDPATH='' cd -- "${RELEASED}" && pwd)"
PROVENANCE="${PWD}/dist/provider-linting-build-provenance.json"

if [ -e dist ] && [ -n "$(ls -A dist)" ] && ! diff -rq "${RELEASED}/dist" dist >/dev/null; then
    echo "::error::dist/ already holds files; refusing to mix them with the released build" >&2
    exit 2
fi
mkdir -p dist
cp -R "${RELEASED}/dist/." dist/
BINARY=$(python3 "$(dirname "${BASH_SOURCE[0]}")/provider-linting-artifact-path.py" "${PROVENANCE}")
echo "Re-running the proof against ${BINARY}" >&2

make test-conformance-binary PYVIDER_CONFORMANCE_PSP="${BINARY}"
make test-linting-opentofu-binary PYVIDER_CONFORMANCE_PSP="${BINARY}" \
    PYVIDER_LINTING_PROVENANCE="${PROVENANCE}"
uv run python ci/verify-provider-linting-proof.py \
    "${RELEASED}/provider-linting-proof.json" \
    "${RELEASED}/provider-linting-opentofu.cast" \
    "${RELEASED}/provider-linting-direct.cast" \
    "${RELEASED}/provider-linting-walkthrough.cast"
