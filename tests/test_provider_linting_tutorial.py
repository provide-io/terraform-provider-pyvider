# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Release contracts for the checked-in Part 7 provider-linting tutorial."""

from __future__ import annotations

from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "examples" / "tutorials" / "part7-provider-linting"


def test_part7_tutorial_is_a_self_contained_public_example() -> None:
    expected = {
        "README.md",
        ".gitignore",
        "install-opentofu.sh",
        "lint-fixture/main.tf",
        "lint.soup.toml",
        "my_provider/__init__.py",
        "my_provider/server.py",
        "pyproject.toml",
        "tests/test_linting.py",
        "uv.lock",
    }

    ignored_roots = {".cache", ".pytest_cache", ".venv", "build", "dist"}
    checked_files = {
        str(path.relative_to(TUTORIAL))
        for path in TUTORIAL.rglob("*")
        if path.is_file()
        and not set(path.relative_to(TUTORIAL).parts) & ignored_roots
        and not any(part.endswith(".egg-info") for part in path.relative_to(TUTORIAL).parts)
        and not path.name.endswith(".pyc")
    }
    assert checked_files == expected


def test_part7_tutorial_pins_the_public_release_stack() -> None:
    project = tomllib.loads((TUTORIAL / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["dependencies"]
    dev = project["dependency-groups"]["dev"]

    assert "pyvider==0.8.1" in dependencies
    assert "flavorpack==0.5.3" in dev
    assert "pytest>=8" in dev
    assert "pytest-asyncio>=0.25" in dev

    lock = tomllib.loads((TUTORIAL / "uv.lock").read_text(encoding="utf-8"))
    packages = {(item["name"], item["version"]) for item in lock["package"]}
    assert ("pyvider", "0.8.1") in packages
    assert ("flavorpack", "0.5.3") in packages


def test_part7_rule_has_stable_addresses_and_is_advisory() -> None:
    source = (TUTORIAL / "my_provider" / "server.py").read_text(encoding="utf-8")

    assert 'PRODUCTION_NAME = "example/mycloud:production-name"' in source
    assert 'ALL_LINTS = "example/mycloud:all"' in source
    assert 'NAMING = "example/mycloud:naming"' in source
    assert "async def lint(" in source
    assert "LintFinding(" in source
    assert 'attribute_path="name"' in source


def test_part7_suite_exercises_rule_group_exclusion_and_default_off() -> None:
    tests = (TUTORIAL / "tests" / "test_linting.py").read_text(encoding="utf-8")

    for behavior in (
        "test_exact_rule_enables_the_finding",
        "test_all_group_enables_the_finding",
        "test_naming_group_enables_the_finding",
        "test_exact_exclusion_suppresses_group_selection",
        "test_empty_selector_keeps_linting_off",
        "test_non_production_and_unknown_names_are_safe",
    ):
        assert behavior in tests


def test_part7_tofusoup_suite_runs_both_public_lanes() -> None:
    suite = (TUTORIAL / "lint.soup.toml").read_text(encoding="utf-8")
    fixture = (TUTORIAL / "lint-fixture" / "main.tf").read_text(encoding="utf-8")

    assert 'source = "registry.opentofu.org/example/mycloud"' in suite
    assert 'fixture = "lint-fixture"' in suite
    assert 'PYVIDER_LINT = "example/mycloud:all"' in suite
    assert 'type_name = "mycloud_server"' in suite
    assert "example/mycloud:production-name" in suite
    assert 'required_version = "= 1.13.0-rc1"' in fixture
    assert 'name = "web-prod"' in fixture


def test_part7_installer_is_pinned_and_checksum_verified() -> None:
    installer = (TUTORIAL / "install-opentofu.sh").read_text(encoding="utf-8")

    assert 'PINNED_VERSION="1.13.0-rc1"' in installer
    assert 'CACHE_DIR="$SCRIPT_DIR/.cache/opentofu"' in installer
    assert "curl --fail --location" in installer
    assert "shasum -a 256 -c" in installer
    assert "latest" not in installer.lower()


def test_part7_recording_uses_only_checked_in_user_commands() -> None:
    recorder = (ROOT / "ci" / "provider-linting-tutorial.sh").read_text(encoding="utf-8")

    for command in (
        "uv sync --frozen",
        "uv run pytest tests/test_linting.py -q",
        "uv run flavor pack --quiet --manifest pyproject.toml",
        "./install-opentofu.sh 1.13.0-rc1",
        "uvx --from tofusoup==0.8.2 soup lint lint.soup.toml",
    ):
        assert command in recorder
    assert "PYVIDER_CONFORMANCE_PSP" not in recorder
    assert "PYVIDER_OPENTOFU_BINARY" not in recorder
    assert "Built and verified dist/terraform-provider-mycloud.psp" in recorder
    assert "printf '\\n'" in recorder


def test_part7_generated_work_is_ignored() -> None:
    ignores = (TUTORIAL / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert {".cache/", ".pytest_cache/", ".venv/", "build/", "dist/", "*.egg-info/"}.issubset(ignores)


def test_repository_typecheck_excludes_nested_tutorial_build_outputs() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["tool"]["mypy"]["exclude"] == [r"(^|/)(workenv|\.venv|build|dist)/"]
