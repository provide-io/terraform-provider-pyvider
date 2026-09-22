#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Re-run the provider-linting proof against a released, already-verified
# linux_amd64 binary: conformance, the OpenTofu lint lane, and the published
# proof films. The build provenance is the copy verify-release-binding.py
# placed beside the unpacked binary, since the checkout has no dist/.
#
# Usage: ci/rerun-released-proof.sh <released-dir> <binary> <opentofu-binary>
set -euo pipefail

RELEASED="${1:?usage: $0 <released-dir> <binary> <opentofu-binary>}"
BINARY="${2:?usage: $0 <released-dir> <binary> <opentofu-binary>}"
TOFU="${3:?usage: $0 <released-dir> <binary> <opentofu-binary>}"
RELEASED="$(cd "${RELEASED}" && pwd)"

make test-conformance-binary PYVIDER_CONFORMANCE_PSP="${BINARY}"
make test-linting-opentofu-binary PYVIDER_CONFORMANCE_PSP="${BINARY}" \
    PYVIDER_OPENTOFU_BINARY="${TOFU}" \
    PYVIDER_LINTING_PROVENANCE="${RELEASED}/dist/provider-linting-build-provenance.json"
uv run python ci/verify-provider-linting-proof.py \
    "${RELEASED}/provider-linting-proof.json" \
    "${RELEASED}/provider-linting-opentofu.cast" \
    "${RELEASED}/provider-linting-direct.cast" \
    "${RELEASED}/provider-linting-walkthrough.cast"
