#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Report what the downloaded provider binary is, then prime it.
#
# Usage: verify-provider.sh <version> <platform>
#
# The report is diagnostic: when a leg fails at the handshake, the first
# question is whether the binary is for this architecture and whether its
# dynamic libraries resolve, and that answer belongs in the log of the run that
# failed rather than in a re-run with extra echoes added.
#
# Priming is not diagnostic. The packaged provider unpacks ~270MB of work
# environment on its first launch, and paying that here means the first test to
# launch it finds the work environment already extracted.
#
# It is not, on its own, why a provider fails to start -- see the note in
# warm-workenv.sh, which was written on that assumption and was wrong.
set -uo pipefail

VERSION="${1:?usage: verify-provider.sh <version> <platform>}"
PLATFORM="${2:?usage: verify-provider.sh <version> <platform>}"

if [ "${PLATFORM}" = "windows" ]; then
    BINARY="provider-binary/terraform-provider-pyvider_v${VERSION}.exe"
else
    BINARY="provider-binary/terraform-provider-pyvider_v${VERSION}"
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔍 PROVIDER BINARY VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo
echo "📋 Binary information:"
ls -lah "${BINARY}"
echo
echo "📋 File type:"
file "${BINARY}" || echo "file command not available"
echo

case "${PLATFORM}" in
    linux)  echo "📋 Library dependencies (ldd):"
            ldd "${BINARY}" 2>&1 || echo "not dynamically linked, or ldd unavailable" ;;
    darwin) echo "📋 Library dependencies (otool):"
            otool -L "${BINARY}" 2>&1 || echo "otool not available" ;;
esac
echo

echo "📋 Priming the packaged work environment:"
"$(dirname "$0")/warm-workenv.sh" "${BINARY}"
echo "✅ Provider binary is valid and primed"
echo
echo "════════════════════════════════════════════════════════════════"
