# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenTofu v1.13.0-beta1 proof for the four provider-reachable lint paths.

OpenTofu core does not yet call action, list-resource, or state-store validation.
Those three paths are deliberately asserted absent here and are proven through
the direct TofuSoup driver in ``tests/conformance/test_provider_linting.py``.
"""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "provider-linting"
INSTALLER = ROOT / "ci" / "install-opentofu-beta.sh"
PROVENANCE = ROOT / "dist" / "provider-linting-build-provenance.json"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
EXPECTED_RULES = {
    "provide-io/pyvider:insecure-tls": "api_insecure_skip_verify",
    "provide-io/pyvider:world-writable-directory": "permissions",
    "provide-io/pyvider:insecure-http": "url",
    "provide-io/pyvider:long-lived-lease": "ttl_seconds",
}
EXPECTED_DETAILS = {
    "provide-io/pyvider:insecure-tls": (
        "Skipping TLS certificate verification may be intentional for local development, "
        "but it permits man-in-the-middle attacks. Set api_insecure_skip_verify to false "
        "for safer connections. Suppress with !provide-io/pyvider:insecure-tls."
    ),
    "provide-io/pyvider:world-writable-directory": (
        "World-writable permissions may be intentional for a shared scratch directory, "
        "but any local user can modify its contents. Remove the POSIX other-write bit "
        "(for example, set permissions to 0o755) for a safer directory. Suppress with "
        "!provide-io/pyvider:world-writable-directory."
    ),
    "provide-io/pyvider:insecure-http": (
        "Plain HTTP may be intentional for a local endpoint, but request data can be "
        "intercepted or changed. Set url to an https:// address for a safer connection. "
        "Suppress with !provide-io/pyvider:insecure-http."
    ),
    "provide-io/pyvider:long-lived-lease": (
        "A lease longer than one hour may be intentional for lengthy operations, but "
        "long-lived ephemeral values remain usable for longer if exposed. Set ttl_seconds "
        "to 3600 or less for a safer lease. Suppress with "
        "!provide-io/pyvider:long-lived-lease."
    ),
}
EXPECTED_JSON_LOCATIONS = {
    "provide-io/pyvider:insecure-tls": {
        "summary": "TLS certificate verification is disabled",
        "address": 'provider["registry.opentofu.org/provide-io/pyvider"]',
        "line": 13,
        "start_column": 30,
        "end_column": 34,
        "code": "  api_insecure_skip_verify = true",
        "expression": "true",
    },
    "provide-io/pyvider:world-writable-directory": {
        "summary": "Directory permissions are world-writable",
        "address": "pyvider_local_directory.lint_target",
        "line": 18,
        "start_column": 17,
        "end_column": 24,
        "code": '  permissions = "0o777"',
        "expression": '"0o777"',
    },
    "provide-io/pyvider:insecure-http": {
        "summary": "HTTP API uses an unencrypted connection",
        "address": "data.pyvider_http_api.lint_target",
        "line": 23,
        "start_column": 13,
        "end_column": 51,
        "code": '  url     = "http://127.0.0.1/provider-lint-proof"',
        "expression": '"http://127.0.0.1/provider-lint-proof"',
    },
    "provide-io/pyvider:long-lived-lease": {
        "summary": "Lease lifetime exceeds one hour",
        "address": "ephemeral.pyvider_lease.lint_target",
        "line": 32,
        "start_column": 17,
        "end_column": 21,
        "code": "  ttl_seconds = 3601",
        "expression": "3601",
    },
}
UNREACHABLE_FROM_CORE = {
    "provide-io/pyvider:include-hidden-files",
    "provide-io/pyvider:long-action-timeout",
    "provide-io/pyvider:relative-state-store-path",
}
UNSET = object()


def current_platform() -> str:
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{platform.system().lower()}_{architecture}"


def required_packaged_provider() -> Path:
    value = os.environ.get("PYVIDER_CONFORMANCE_PSP")
    if not value:
        pytest.fail("PYVIDER_CONFORMANCE_PSP is required for the OpenTofu packaged-provider proof")
    path = Path(value).resolve()
    if not path.is_file():
        pytest.fail(f"packaged provider not found at {path}")
    return path


@pytest.fixture(scope="session")
def packaged_provider() -> Path:
    return required_packaged_provider()


def resolve_tofu_binary(cache: Path) -> Path:
    requested = os.environ.get("PYVIDER_OPENTOFU_BINARY")
    if requested:
        tofu = Path(requested).resolve()
        if not tofu.is_file():
            pytest.fail(f"preinstalled OpenTofu binary not found at {tofu}")
    else:
        completed = subprocess.run(
            [str(INSTALLER), "--cache-dir", str(cache), "--version", "1.13.0-beta1"],
            check=True,
            capture_output=True,
            text=True,
        )
        tofu = Path(completed.stdout.strip()).resolve()
    version = subprocess.run([tofu, "version"], check=True, capture_output=True, text=True).stdout
    assert "OpenTofu v1.13.0-beta1" in version
    return tofu


@pytest.fixture(scope="session")
def tofu_binary(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return resolve_tofu_binary(tmp_path_factory.mktemp("opentofu-beta"))


def install_provider_mirror(root: Path, binary: Path) -> tuple[Path, Path]:
    mirror = root / "mirror"
    destination = (
        mirror
        / "registry.opentofu.org"
        / "provide-io"
        / "pyvider"
        / VERSION
        / current_platform()
        / f"terraform-provider-pyvider_v{VERSION}"
    )
    destination.parent.mkdir(parents=True)
    shutil.copy2(binary, destination)
    destination.chmod(0o755)
    cli_config = root / "tofurc"
    cli_config.write_text(
        "provider_installation {\n"
        "  filesystem_mirror {\n"
        f"    path    = {json.dumps(str(mirror))}\n"
        '    include = ["registry.opentofu.org/provide-io/pyvider"]\n'
        "  }\n"
        "}\n",
        encoding="utf-8",
    )
    return destination, cli_config


def tofu_env(cli_config: Path, data_dir: Path, selector: str | object = UNSET) -> dict[str, str]:
    env = {
        name: value for name, value in os.environ.items() if not name.startswith(("TF_", "TOFU_", "PYVIDER_"))
    }
    env.update(
        {
            "PYVIDER_TESTMODE": "true",
            "PYVIDER_LOG_LEVEL": "ERROR",
            "TF_CLI_CONFIG_FILE": str(cli_config),
            "TF_DATA_DIR": str(data_dir),
        }
    )
    if selector is not UNSET:
        env["PYVIDER_LINT"] = str(selector)
    return env


@pytest.fixture
def validate_case(
    tmp_path: Path,
    tofu_binary: Path,
    packaged_provider: Path,
) -> Callable[..., dict[str, Any]]:
    destination, cli_config = install_provider_mirror(tmp_path, packaged_provider)
    assert (
        hashlib.sha256(destination.read_bytes()).hexdigest()
        == hashlib.sha256(packaged_provider.read_bytes()).hexdigest()
    )
    case_number = 0

    def _validate(
        *,
        selector: str | object = UNSET,
        file_rules: tuple[str, ...] | Path | None = None,
        http_listener: socket.socket | None = None,
    ) -> dict[str, Any]:
        nonlocal case_number
        case_number += 1
        workspace = tmp_path / f"case-{case_number}"
        workspace.mkdir()
        main_source = (FIXTURE / "main.tf").read_text(encoding="utf-8")
        if http_listener is not None:
            host, port = http_listener.getsockname()[:2]
            main_source = main_source.replace(
                "http://127.0.0.1/provider-lint-proof",
                f"http://{host}:{port}/provider-lint-proof",
            )
        (workspace / "main.tf").write_text(main_source, encoding="utf-8")
        if isinstance(file_rules, Path):
            shutil.copy2(file_rules, workspace / "pyvider.toml")
        elif file_rules is not None:
            rendered = ", ".join(json.dumps(rule) for rule in file_rules)
            (workspace / "pyvider.toml").write_text(f"[lint]\nrules = [{rendered}]\n", encoding="utf-8")
        env = tofu_env(cli_config, workspace / ".terraform", selector)
        initialized = subprocess.run(
            [tofu_binary, "init", "-backend=false", "-input=false", "-no-color"],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
        )
        assert initialized.returncode == 0, initialized.stdout + initialized.stderr
        completed = subprocess.run(
            [tofu_binary, "validate", "-json", "-no-color"],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        result: dict[str, Any] = json.loads(completed.stdout)
        assert result["valid"] is True
        return result

    return _validate


def rule_diagnostics(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    diagnostics: dict[str, dict[str, Any]] = {}
    for diagnostic in result["diagnostics"]:
        for rule in set(EXPECTED_RULES) | UNREACHABLE_FROM_CORE:
            if f"({rule})" in diagnostic["summary"]:
                diagnostics[rule] = diagnostic
    return diagnostics


def assert_json_location(rule: str, diagnostic: dict[str, Any]) -> None:
    expected = EXPECTED_JSON_LOCATIONS[rule]
    assert diagnostic["severity"] == "warning"
    assert diagnostic["summary"] == f"{expected['summary']} ({rule})"
    assert diagnostic["detail"] == EXPECTED_DETAILS[rule]
    assert diagnostic["address"] == expected["address"]
    assert diagnostic["range"]["filename"] == "main.tf"
    assert diagnostic["range"]["start"]["line"] == expected["line"]
    assert diagnostic["range"]["start"]["column"] == expected["start_column"]
    assert diagnostic["range"]["end"]["line"] == expected["line"]
    assert diagnostic["range"]["end"]["column"] == expected["end_column"]
    snippet = diagnostic["snippet"]
    assert snippet["start_line"] == expected["line"]
    assert snippet["code"] == expected["code"]
    assert snippet["code"].lstrip().startswith(f"{EXPECTED_RULES[rule]} ")
    highlighted = snippet["code"][snippet["highlight_start_offset"] : snippet["highlight_end_offset"]]
    assert highlighted == expected["expression"]


def test_opentofu_e2e_requires_an_explicit_packaged_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PYVIDER_CONFORMANCE_PSP", raising=False)

    with pytest.raises(pytest.fail.Exception, match="PYVIDER_CONFORMANCE_PSP is required"):
        required_packaged_provider()


def test_packaged_binary_matches_coordinated_build_provenance(packaged_provider: Path) -> None:
    data = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    expected = PROVENANCE.parent / data["artifacts"]["binary"]["path"]

    assert packaged_provider == expected.resolve()
    assert hashlib.sha256(packaged_provider.read_bytes()).hexdigest() == data["artifacts"]["binary"]["sha256"]


def test_fixture_contains_the_four_currently_reachable_triggering_paths() -> None:
    source = (FIXTURE / "main.tf").read_text(encoding="utf-8")

    assert "api_insecure_skip_verify = true" in source
    assert 'permissions = "0o777"' in source
    assert 'url     = "http://127.0.0.1/provider-lint-proof"' in source
    assert "ttl_seconds = 3601" in source
    assert "action " not in source
    assert "list " not in source
    assert "state_store " not in source


def test_e2e_uses_the_exact_preinstalled_opentofu_binary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    tofu = tmp_path / "tofu"
    tofu.write_text("#!/bin/sh\nprintf 'OpenTofu v1.13.0-beta1\\n'\n", encoding="utf-8")
    tofu.chmod(0o755)
    monkeypatch.setenv("PYVIDER_OPENTOFU_BINARY", str(tofu))

    assert resolve_tofu_binary(tmp_path / "unused-cache") == tofu.resolve()
    assert not (tmp_path / "unused-cache").exists()


@pytest.mark.parametrize("poison", ["TF_REATTACH_PROVIDERS", "TF_CLI_ARGS_validate"])
def test_tofu_environment_removes_terraform_command_poisoning(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    poison: str,
    validate_case: Callable[..., dict[str, Any]],
) -> None:
    monkeypatch.setenv(poison, "poisoned")

    env = tofu_env(tmp_path / "tofurc", tmp_path / "data")
    result = validate_case(selector="provide-io/pyvider:insecure-tls")

    assert poison not in env
    assert set(rule_diagnostics(result)) == {"provide-io/pyvider:insecure-tls"}


def test_validate_makes_zero_http_connections(
    validate_case: Callable[..., dict[str, Any]],
) -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        result = validate_case(
            selector="provide-io/pyvider:insecure-http",
            http_listener=listener,
        )
        listener.setblocking(False)
        with pytest.raises(BlockingIOError):
            listener.accept()

    assert set(rule_diagnostics(result)) == {"provide-io/pyvider:insecure-http"}


def test_provider_linting_is_off_by_default(
    validate_case: Callable[..., dict[str, Any]],
) -> None:
    result = validate_case()

    assert rule_diagnostics(result) == {}
    assert result["warning_count"] == 0
    assert result["diagnostics"] == []


def test_namespaced_all_selects_exactly_the_four_core_reachable_rules(
    validate_case: Callable[..., dict[str, Any]],
) -> None:
    result = validate_case(selector="provide-io/pyvider:all")

    diagnostics = rule_diagnostics(result)
    assert set(diagnostics) == set(EXPECTED_RULES)
    assert result["warning_count"] == len(EXPECTED_RULES)
    assert len(result["diagnostics"]) == len(EXPECTED_RULES)
    for rule, diagnostic in diagnostics.items():
        assert_json_location(rule, diagnostic)
    assert all(rule not in json.dumps(result) for rule in UNREACHABLE_FROM_CORE)


@pytest.mark.parametrize(
    ("selector", "file_rules", "expected"),
    [
        pytest.param(
            UNSET,
            FIXTURE / "pyvider.toml",
            {"provide-io/pyvider:insecure-http"},
            id="file-rules",
        ),
        pytest.param(
            "provide-io/pyvider:all",
            None,
            set(EXPECTED_RULES),
            id="namespaced-all-env",
        ),
        pytest.param(
            "provide-io/pyvider:insecure-tls",
            FIXTURE / "pyvider.toml",
            {"provide-io/pyvider:insecure-tls"},
            id="environment-overrides-file",
        ),
        pytest.param(
            "",
            FIXTURE / "pyvider.toml",
            set(),
            id="empty-environment-disables-file",
        ),
        pytest.param(
            "provide-io/pyvider:security",
            None,
            {
                "provide-io/pyvider:insecure-tls",
                "provide-io/pyvider:world-writable-directory",
                "provide-io/pyvider:insecure-http",
            },
            id="security-group",
        ),
        pytest.param(
            "provide-io/pyvider:long-lived-lease",
            None,
            {"provide-io/pyvider:long-lived-lease"},
            id="exact-rule",
        ),
        pytest.param(
            "provide-io/pyvider:all,!provide-io/pyvider:insecure-http",
            None,
            set(EXPECTED_RULES) - {"provide-io/pyvider:insecure-http"},
            id="exact-exclusion",
        ),
    ],
)
def test_selector_and_configuration_precedence_through_opentofu(
    validate_case: Callable[..., dict[str, Any]],
    selector: str | object,
    file_rules: tuple[str, ...] | Path | None,
    expected: set[str],
) -> None:
    result = validate_case(selector=selector, file_rules=file_rules)

    diagnostics = rule_diagnostics(result)
    assert set(diagnostics) == expected
    assert result["warning_count"] == len(expected)
    assert len(result["diagnostics"]) == len(expected)
    for rule, diagnostic in diagnostics.items():
        assert_json_location(rule, diagnostic)
    assert all(rule not in json.dumps(result) for rule in UNREACHABLE_FROM_CORE)
