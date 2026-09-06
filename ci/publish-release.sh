#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Publish the GitHub release for a tag, with the signed artifacts attached.
#
# The tag alone ships nothing. Everything a consumer installs -- the per-platform
# archives, the SHA256SUMS, and the detached signature over them -- lives in
# release/ and reaches users only by being attached here.
#
# Refuses to publish an empty release: a release carrying no archive is worse
# than no release, because it looks installed and resolves to nothing.
set -euo pipefail

VERSION="${1:?usage: $0 <version>}"
TAG="v${VERSION}"
DIR="${2:-release}"

if [ ! -d "${DIR}" ]; then
    echo "::error::no ${DIR}/ directory; nothing was staged to publish"
    exit 1
fi

shopt -s nullglob
archives=("${DIR}"/*.zip)
sums=("${DIR}"/*SHA256SUMS*)
shopt -u nullglob

if [ ${#archives[@]} -eq 0 ]; then
    echo "::error::${DIR}/ holds no .zip archive; refusing to publish an empty ${TAG}"
    exit 1
fi
if [ ${#sums[@]} -eq 0 ]; then
    echo "::error::${DIR}/ holds no SHA256SUMS; refusing to publish ${TAG} unverifiable"
    exit 1
fi

echo "📦 Publishing ${TAG} with ${#archives[@]} archive(s):"
ls -la "${DIR}"

# Idempotent: a re-run attaches to the release the previous attempt created
# rather than failing, which is what makes recovering from a partial release
# possible without deleting anything.
if gh release view "${TAG}" >/dev/null 2>&1; then
    echo "🔁 ${TAG} exists; uploading assets with --clobber"
    gh release upload "${TAG}" "${DIR}"/* --clobber
else
    gh release create "${TAG}" "${DIR}"/* \
        --title "${TAG}" \
        --generate-notes
fi

echo "✅ ${TAG} published with:"
gh release view "${TAG}" --json assets --jq '.assets[] | "  \(.name)  \(.size) bytes"'
