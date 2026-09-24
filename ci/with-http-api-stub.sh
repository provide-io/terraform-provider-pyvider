#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Run a command with the http_api examples pointed at a local server.
#
#   ci/with-http-api-stub.sh soup stir --recursive
#
# Starts ci/http_api_stub.py on a free loopback port, exports
# TF_VAR_api_base_url and TF_VAR_json_api_base_url at it, runs the command, and
# stops the server however the command ends. The examples' defaults are the
# public httpbin.org and JSONPlaceholder, so without this a run depends on both.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Seconds to wait for the server to write its URL before giving up.
READY_TIMEOUT="${HTTP_API_STUB_READY_TIMEOUT:-10}"

[ "$#" -gt 0 ] || { echo "usage: $0 <command> [args...]" >&2; exit 2; }

state_dir="$(mktemp -d)"
url_file="${state_dir}/url"

python3 "${REPO_ROOT}/ci/http_api_stub.py" --url-file "${url_file}" &
stub_pid=$!
cleanup() {
  kill "${stub_pid}" 2>/dev/null || true
  wait "${stub_pid}" 2>/dev/null || true
  rm -rf "${state_dir}"
}
trap cleanup EXIT

deadline=$(( $(date +%s) + READY_TIMEOUT ))
until [ -s "${url_file}" ]; do
  if ! kill -0 "${stub_pid}" 2>/dev/null; then
    echo "http_api stub exited before it was ready" >&2
    exit 1
  fi
  if [ "$(date +%s)" -ge "${deadline}" ]; then
    echo "http_api stub not ready after ${READY_TIMEOUT}s" >&2
    exit 1
  fi
  sleep 0.1
done

base_url="$(cat "${url_file}")"
export TF_VAR_api_base_url="${base_url}"
export TF_VAR_json_api_base_url="${base_url}"
echo "http_api examples -> ${base_url}" >&2

"$@"
