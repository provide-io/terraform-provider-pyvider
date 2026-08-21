#!/usr/bin/env bash
# Extract the packaged provider's work environment ahead of a test run.
#
# The first launch after a build unpacks ~270MB. Left to happen inside a test,
# it overruns the plugin handshake timeout and the run hangs on a provider that
# is still unpacking, so pay the cost here where nothing is waiting on it.
#
# The provider serves until killed and stops writing once it has printed its
# handshake line, so it never sees SIGPIPE from a `head` on the other end of a
# pipe -- it has to be stopped explicitly.
set -uo pipefail

BINARY="${1:?usage: warm-workenv.sh <provider-binary>}"
TIMEOUT="${WARM_TIMEOUT:-300}"

TF_PLUGIN_MAGIC_COOKIE=d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2 \
PLUGIN_PROTOCOL_VERSIONS=6 \
    "$BINARY" >/dev/null 2>&1 &
pid=$!

# Wait for the process to be serving, which means extraction finished.
waited=0
while [ "$waited" -lt "$TIMEOUT" ]; do
    kill -0 "$pid" 2>/dev/null || break   # exited on its own (e.g. an error)
    if pgrep -f "workenv/.*/bin/terraform-provider" >/dev/null 2>&1; then
        sleep 2   # let the handshake finish writing
        break
    fi
    sleep 1
    waited=$((waited + 1))
done

kill "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
pkill -f "workenv/.*/bin/terraform-provider" 2>/dev/null || true
exit 0
