# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenTofu v1.13.0-rc1 delivers refined unknowns to the packaged provider intact.

OpenTofu 1.13 adds the ``assume*`` functions (opentofu#4449). The fixture refines
an apply-time value to "not null, starts with ``refined:``" and passes it as
``pyvider_file_content.content``: required, not computed, so the planned value
is exactly what the provider decoded from PlanResourceChange's config and
encoded back. Core compares planned and config values with refinements
stripped (``objchange.unrefinedValue``) and never re-applies them, so the only
way ``startswith(pyvider_file_content.echo.content, "refined:")`` is known at
plan time is the refinement surviving pyvider-cty's decode and re-encode.

A provider whose msgpack decoder drops the refinement (``_ext_hook`` returning a
plain unknown) plans without error; these outputs just turn into
"known after apply", which is what the assertions below reject.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import pytest

from .test_provider_linting_opentofu import (
    install_provider_mirror,
    required_packaged_provider,
    resolve_tofu_binary,
    tofu_env,
)

FIXTURE = Path(__file__).resolve().parent / "refined-unknowns"


@pytest.fixture(scope="session")
def packaged_provider() -> Path:
    return required_packaged_provider()


@pytest.fixture(scope="session")
def tofu_binary(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return resolve_tofu_binary(tmp_path_factory.mktemp("opentofu-prerelease"))


@pytest.fixture(scope="module")
def saved_plan(
    tmp_path_factory: pytest.TempPathFactory,
    tofu_binary: Path,
    packaged_provider: Path,
) -> dict[str, Any]:
    root = tmp_path_factory.mktemp("refined-unknowns")
    destination, cli_config = install_provider_mirror(root, packaged_provider)
    assert (
        hashlib.sha256(destination.read_bytes()).hexdigest()
        == hashlib.sha256(packaged_provider.read_bytes()).hexdigest()
    )
    workspace = root / "workspace"
    workspace.mkdir()
    (workspace / "main.tf").write_text((FIXTURE / "main.tf").read_text(encoding="utf-8"), encoding="utf-8")
    env = tofu_env(cli_config, workspace / ".terraform")

    def tofu(*args: str) -> str:
        completed = subprocess.run(
            [tofu_binary, *args],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        return completed.stdout

    tofu("init", "-backend=false", "-input=false", "-no-color")
    tofu("plan", "-out=tfplan", "-input=false", "-no-color")
    plan: dict[str, Any] = json.loads(tofu("show", "-json", "tfplan"))
    assert not (workspace / "refined-unknown.txt").exists(), "plan must not write the file"
    return plan


def output_change(plan: dict[str, Any], name: str) -> dict[str, Any]:
    change: dict[str, Any] = plan["output_changes"][name]
    return change


def assert_known_true(plan: dict[str, Any], name: str) -> None:
    change = output_change(plan, name)
    assert change["after_unknown"] is False, f"{name} is unknown at plan time: {change}"
    assert change["after"] is True


def assert_unknown(plan: dict[str, Any], name: str) -> None:
    change = output_change(plan, name)
    assert change["after_unknown"] is True, f"{name} is known at plan time: {change}"
    assert "after" not in change


def test_fixture_refines_an_apply_time_value_with_opentofu_1_13_functions() -> None:
    source = (FIXTURE / "main.tf").read_text(encoding="utf-8")

    assert 'required_version = "= 1.13.0-rc1"' in source
    assert 'assumestringprefix(assumenotnull(terraform_data.seed.id), "refined:")' in source
    assert "content  = local.refined" in source


def test_opentofu_refines_the_value_before_it_reaches_the_provider(saved_plan: dict[str, Any]) -> None:
    # Core alone: the assume functions refine, and the seed is not refined by
    # itself, so any known result further down came from the refinement.
    assert_known_true(saved_plan, "core_prefix")
    assert_unknown(saved_plan, "unrefined_prefix")


def test_provider_plans_the_refined_unknown_back_intact(saved_plan: dict[str, Any]) -> None:
    (change,) = (
        resource["change"]
        for resource in saved_plan["resource_changes"]
        if resource["address"] == "pyvider_file_content.echo"
    )
    # Still unknown: the provider neither fabricated a value nor collapsed it.
    assert change["actions"] == ["create"]
    assert "content" not in change["after"]
    assert change["after_unknown"]["content"] is True

    # Known only because the provider's planned value carries the refinement.
    assert_known_true(saved_plan, "provider_prefix")
    assert_known_true(saved_plan, "provider_not_null")


def test_provider_does_not_invent_refinements(saved_plan: dict[str, Any]) -> None:
    # A computed attribute the provider plans as a plain unknown stays one.
    assert_unknown(saved_plan, "provider_computed_prefix")
