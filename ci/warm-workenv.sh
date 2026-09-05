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
#
# A provider that exits instead of serving has already failed, and its stderr
# is the only account of why -- the engine that launches it next reports no
# more than "failed to read any lines from plugin's stdout". So stderr is kept
# and printed here, where the launch that produced it is the only thing going
# on. Warming is still not fatal: the tests that follow decide that.
set -uo pipefail

BINARY="${1:?usage: warm-workenv.sh <provider-binary>}"
TIMEOUT="${WARM_TIMEOUT:-300}"

handshake="$(mktemp "${TMPDIR:-/tmp}/warm-workenv.XXXXXX")"
errors="$(mktemp "${TMPDIR:-/tmp}/warm-workenv-err.XXXXXX")"
trap 'rm -f "${handshake}" "${errors}"' EXIT

TF_PLUGIN_MAGIC_COOKIE=d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2 \
PLUGIN_PROTOCOL_VERSIONS=6 \
    "${BINARY}" >"${handshake}" 2>"${errors}" &
pid=$!

waited=0
while [ "${waited}" -lt "${TIMEOUT}" ]; do
    if [ -s "${handshake}" ]; then
        echo "✅ Work environment extracted after ${waited}s"
        break
    fi
    # Exited on its own, which means it failed rather than finished.
    if ! kill -0 "${pid}" 2>/dev/null; then
        wait "${pid}" 2>/dev/null
        echo "⚠️  Provider exited (status $?) before it began serving, after ${waited}s"
        echo "--- provider stderr ---"
        tail -n 40 "${errors}"
        echo "--- end provider stderr ---"
        exit 0
    fi
    sleep 1
    waited=$((waited + 1))
done

[ "${waited}" -ge "${TIMEOUT}" ] && echo "⚠️  Gave up warming after ${TIMEOUT}s"

kill "${pid}" 2>/dev/null || true
wait "${pid}" 2>/dev/null || true
exit 0
