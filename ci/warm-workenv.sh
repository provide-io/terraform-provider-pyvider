#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Extract the packaged provider's work environment ahead of a test run.
#
# Usage: warm-workenv.sh <provider-binary>
#
# The first launch after a build unpacks ~270MB, and paying that here means the
# first test to launch the provider finds it done. That is all this buys.
#
# It is worth saying what it does not buy, because this script was written
# believing otherwise: a provider that fails to hand shake is not, in general,
# a provider that was still unpacking. flavorpack's launcher defaulted to trace
# and wrote ~193KB to stderr per launch against a 64KB pipe, so a host that
# waits for stdout without draining stderr deadlocked it -- and this script
# could not see that, because it redirects stderr to a file, which has no
# buffer to fill. Fixed in flavorpack 0.5.3; the floor in pyproject.toml is
# what keeps it fixed.
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

# The launcher spawns the interpreter as a separate process and does not pass
# the signal on, so killing the launcher leaves the provider itself serving.
# One survivor per warm is enough to collide with the suite that follows: the
# next launch finds the port taken and the handshake never completes.
#
# Best-effort. Git Bash on the Windows runner has no pkill, and there the job's
# own container is what reclaims the process.
pkill -f "workenv/.*/bin/terraform-provider" 2>/dev/null || true
exit 0
