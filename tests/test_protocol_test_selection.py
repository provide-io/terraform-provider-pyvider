# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for ordinary versus coordinated protocol-test selection."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDINATED_LINTING_MODULE = "tests/conformance/test_provider_linting.py"


def test_ordinary_protocol_suite_excludes_only_coordinated_linting_module() -> None:
    script = (ROOT / "ci" / "protocol-tests.sh").read_text(encoding="utf-8")

    assert (
        f"uv run --no-sync pytest tests/conformance -v -p no:randomly --ignore={COORDINATED_LINTING_MODULE}"
    ) in script
    assert script.count("--ignore=") == 1


def test_dedicated_binary_target_includes_coordinated_linting_module() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("test-conformance-binary:", 1)[1].split(
        "\n.PHONY: test-linting-opentofu-binary", 1
    )[0]

    assert "PYVIDER_CONFORMANCE_TESTS ?= tests/conformance" in makefile
    assert "uv run pytest $(PYVIDER_CONFORMANCE_TESTS) -q" in target
    assert "--ignore=" not in target
