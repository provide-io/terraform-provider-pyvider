#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Sync the dev environment and install the released TofuSoup the proof pins,
# refusing any other version on PATH or in the environment.
#
# Usage: ci/install-released-tofusoup.sh <version>
set -euo pipefail

TOFUSOUP_VERSION="${1:?usage: $0 <version>}"
uv sync --frozen --group dev
uv tool install --refresh "tofusoup==${TOFUSOUP_VERSION}"
test "$(soup --version)" = "soup, version ${TOFUSOUP_VERSION}"
uv run python -c "import tofusoup, sys; sys.exit(tofusoup.__version__ != '${TOFUSOUP_VERSION}')"
