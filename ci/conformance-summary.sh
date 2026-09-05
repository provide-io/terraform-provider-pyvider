#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Report both test jobs and fail if either did.
#
# A summary that reads one job's result and exits 0 reports success for a run
# that failed, which is worse than having no summary.
set -euo pipefail

CONFORMANCE="${CONFORMANCE_RESULT:-unknown}"
PROTOCOL="${PROTOCOL_RESULT:-unknown}"

emit() { echo "$1" >> "${GITHUB_STEP_SUMMARY:-/dev/stdout}"; }

mark() { [ "$1" = "success" ] && echo "✅" || echo "❌"; }

if [ "${CONFORMANCE}" = "success" ] && [ "${PROTOCOL}" = "success" ]; then
    emit "## ✅ All Conformance Tests Passed!"
else
    emit "## ❌ Some Tests Failed"
fi

emit ""
emit "| Suite | Result |"
emit "| --- | --- |"
emit "| $(mark "${CONFORMANCE}") Terraform/OpenTofu examples | \`${CONFORMANCE}\` |"
emit "| $(mark "${PROTOCOL}") tfplugin6 protocol suite | \`${PROTOCOL}\` |"
emit ""

if [ "${CONFORMANCE}" = "success" ] && [ "${PROTOCOL}" = "success" ]; then
    emit "- ✅ Smoke Test 1: Production mode (minimal config)"
    emit "- ✅ Smoke Test 2: Test mode rejection (without PYVIDER_TESTMODE)"
    emit "- ✅ Smoke Test 3: Test mode success (with PYVIDER_TESTMODE)"
    emit "- ✅ Full conformance suite (all examples)"
    emit "- ✅ Protocol suite (tests/conformance, driving the binary directly)"
    exit 0
fi

emit "Test logs are available in the workflow artifacts."
exit 1
