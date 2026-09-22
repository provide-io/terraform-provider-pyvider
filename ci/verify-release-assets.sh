#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Verify a downloaded release: checksums, the SHA256SUMS signature, that the
# tag names the release commit, and that the proof and build provenance bind
# to that commit and to the linux_amd64 binary. Leaves the build's layout
# unpacked under <released-dir>/dist/ and logs the verified binary path.
#
# Usage: ci/verify-release-assets.sh <version> <release-target-sha> <released-dir>
# Needs GH_TOKEN, GITHUB_REPOSITORY and GPG_PRIVATE_KEY in the environment.
set -euo pipefail

VERSION="${1:?usage: $0 <version> <release-target-sha> <released-dir>}"
RELEASE_TARGET_SHA="${2:?usage: $0 <version> <release-target-sha> <released-dir>}"
RELEASED="${3:?usage: $0 <version> <release-target-sha> <released-dir>}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${GPG_PRIVATE_KEY:?GPG_PRIVATE_KEY is required}"
SUMS="terraform-provider-pyvider_${VERSION}_SHA256SUMS"

(cd "${RELEASED}" && sha256sum -c "${SUMS}") >&2
echo "${GPG_PRIVATE_KEY}" | gpg --batch --import 2>/dev/null
gpg --batch --verify "${RELEASED}/${SUMS}.sig" "${RELEASED}/${SUMS}" >&2

ref="repos/${GITHUB_REPOSITORY}/git/ref/tags/v${VERSION}"
tag_sha=$(gh api "${ref}" --jq .object.sha)
if [ "$(gh api "${ref}" --jq .object.type)" = tag ]; then
    tag_sha=$(gh api "repos/${GITHUB_REPOSITORY}/git/tags/${tag_sha}" --jq .object.sha)
fi
if [ "${tag_sha}" != "${RELEASE_TARGET_SHA}" ]; then
    echo "::error::v${VERSION} names ${tag_sha}, not the release commit ${RELEASE_TARGET_SHA}" >&2
    exit 1
fi

binary=$(python3 "$(dirname "${BASH_SOURCE[0]}")/verify-release-binding.py" "${RELEASED}" "${VERSION}" "${RELEASE_TARGET_SHA}")
echo "Verified ${binary}" >&2
