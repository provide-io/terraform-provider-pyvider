#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Stage a release from one validated build run's downloaded artifacts.
#
# Usage: ci/stage-release-assets.sh <artifacts-dir> <release-dir> <version>
#
# upload-artifact stores each path relative to the upload list's common
# ancestor. build-provider.yml uploads the casts and manifest from the
# repository root and the build provenance from dist/, so the provenance
# arrives at provider-linting-proof/dist/ while everything else is at the
# artifact root. tests/test_stage_release_assets.py derives that layout from
# the workflow's upload list, so a change to either side fails there first.
set -euo pipefail

ARTIFACTS="${1:?usage: $0 <artifacts-dir> <release-dir> <version>}"
RELEASE="${2:?usage: $0 <artifacts-dir> <release-dir> <version>}"
VERSION="${3:?usage: $0 <artifacts-dir> <release-dir> <version>}"
PROOF="${ARTIFACTS}/provider-linting-proof"

mkdir "${RELEASE}"
find "${ARTIFACTS}"/provider-* -maxdepth 1 -name 'terraform-provider-pyvider_*.zip' \
    -type f -exec cp {} "${RELEASE}/" \;
for name in \
    provider-linting-proof.json \
    provider-linting-opentofu.cast \
    provider-linting-direct.cast \
    provider-linting-walkthrough.cast; do
    cp "${PROOF}/${name}" "${RELEASE}/${name}"
done
cp "${PROOF}/dist/provider-linting-build-provenance.json" "${RELEASE}/provider-linting-build-provenance.json"
cp terraform-registry-manifest.json "${RELEASE}/terraform-provider-pyvider_${VERSION}_manifest.json"
for target in linux_amd64 linux_arm64 darwin_amd64 darwin_arm64 windows_amd64; do
    test -f "${RELEASE}/terraform-provider-pyvider_${VERSION}_${target}.zip"
done
