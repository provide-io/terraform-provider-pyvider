#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Extract the packaged provider's work environment ahead of a test run.
#
# Usage: warm-workenv.sh <provider-binary>
#
# The first launch after a build unpacks ~270MB. Left to happen inside a test,
# it overruns the plugin handshake window and the engine reports a provider
# that failed to start, so pay the cost here where nothing is waiting on it.
#
# Readiness is the handshake line on stdout: the provider prints it once it is
# serving, which is after extraction. Polling a file for that line uses only
# the shell, so this behaves the same under Git Bash on the Windows runner --
# `pgrep`, the obvious alternative, is not there.
#
# The provider serves until killed and stops writing once it has printed the
# handshake line, so it never sees SIGPIPE and has to be stopped explicitly.
# Failing to warm is not fatal: the tests that follow report the real problem
# with far more context than this script has.
set -uo pipefail

BINARY="${1:?usage: warm-workenv.sh <provider-binary>}"
TIMEOUT="${WARM_TIMEOUT:-300}"

handshake="$(mktemp "${TMPDIR:-/tmp}/warm-workenv.XXXXXX")"
trap 'rm -f "${handshake}"' EXIT

TF_PLUGIN_MAGIC_COOKIE=d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2 \
PLUGIN_PROTOCOL_VERSIONS=6 \
    "${BINARY}" >"${handshake}" 2>/dev/null &
pid=$!

waited=0
while [ "${waited}" -lt "${TIMEOUT}" ]; do
    if [ -s "${handshake}" ]; then
        echo "✅ Work environment extracted after ${waited}s"
        break
    fi
    # Exited on its own, which means it failed rather than finished.
    if ! kill -0 "${pid}" 2>/dev/null; then
        echo "⚠️  Provider exited before it began serving; leaving the work environment cold"
        break
    fi
    sleep 1
    waited=$((waited + 1))
done

[ "${waited}" -ge "${TIMEOUT}" ] && echo "⚠️  Gave up warming after ${TIMEOUT}s"

kill "${pid}" 2>/dev/null || true
wait "${pid}" 2>/dev/null || true
exit 0
