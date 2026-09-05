#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Run tests/conformance against a packaged provider binary.
#
# These drive the binary directly over tfplugin6 and never invoke Terraform or
# OpenTofu, so they are engine-independent and run once per platform. That is
# also what they are for: the RPCs no example reaches -- state-store locking
# across two processes, chunked writes, identity round-trips, deferral -- are
# only reachable from here.
#
# PYVIDER_CONFORMANCE_PSP names the binary. PYVIDER_CONFORMANCE_REQUIRED makes a
# missing one a failure, so this cannot pass by testing nothing.
set -euo pipefail

PSP="${1:?usage: $0 <path-to-provider-binary>}"

if [ ! -x "${PSP}" ]; then
    echo "::error::provider binary is not executable: ${PSP}"
    exit 1
fi

export PYVIDER_CONFORMANCE_PSP="${PSP}"
export PYVIDER_CONFORMANCE_REQUIRED=1

echo "🧪 Driving ${PSP} over tfplugin6"

# -p no:randomly: the suite shares one provider process across the session, so
# a shuffled order changes what state each test sees.
uv run --no-sync pytest tests/conformance -v -p no:randomly
