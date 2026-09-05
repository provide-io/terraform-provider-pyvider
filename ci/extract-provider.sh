#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Unpack a downloaded provider artifact and record where the binary landed.
#
# Writes the path to provider-binary/BINARY_PATH so a caller does not have to
# rebuild the name from version and platform a second time.
set -euo pipefail

VERSION="${1:?usage: $0 <version> <target> <platform>}"
TARGET="${2:?usage: $0 <version> <target> <platform>}"
PLATFORM="${3:?usage: $0 <version> <target> <platform>}"

cd provider-binary

unzip -o "terraform-provider-pyvider_${VERSION}_${TARGET}.zip"

if [ "${PLATFORM}" = "windows" ]; then
    BINARY="terraform-provider-pyvider_v${VERSION}.exe"
else
    BINARY="terraform-provider-pyvider_v${VERSION}"
fi

if [ ! -f "${BINARY}" ]; then
    echo "::error::expected ${BINARY} in the artifact; got:"
    ls -la
    exit 1
fi

# The zip carries no POSIX permission bits when it is built on Windows.
chmod +x "${BINARY}" 2>/dev/null || true

# Absolute, because the caller runs from the repository root.
printf '%s\n' "$(pwd)/${BINARY}" > BINARY_PATH
echo "✅ ${BINARY}"
