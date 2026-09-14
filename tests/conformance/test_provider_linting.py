# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Provider-native linting proof through the packaged tfprotov6 process."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any

import pytest
from tofusoup.tfplugin import TfPluginProvider, start_provider, unpack

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

from .conftest import CLAIMED_TERRAFORM_VERSION, child_env, provenance_source_paths

DRIVER = Path(__file__).resolve().parents[2] / "ci" / "run-provider-linting-rpcs.py"
RULE_SUMMARIES = {
    "provide-io/pyvider:insecure-tls": "TLS certificate verification is disabled",
    "provide-io/pyvider:world-writable-directory": "Directory permissions are world-writable",
    "provide-io/pyvider:insecure-http": "HTTP API uses an unencrypted connection",
    "provide-io/pyvider:long-lived-lease": "Lease lifetime exceeds one hour",
    "provide-io/pyvider:include-hidden-files": "File listing includes hidden files",
    "provide-io/pyvider:long-action-timeout": "Action timeout exceeds five minutes",
    "provide-io/pyvider:relative-state-store-path": "State store path is relative",
}


@dataclass(frozen=True)
class PackagedLintRPCCase:
    kind: str
    rule: str
    summary: str
    detail: str
    attribute: str


PACKAGED_LINT_RPC_CASES = {
    "provider": PackagedLintRPCCase(
        kind="provider",
        rule="provide-io/pyvider:insecure-tls",
        summary="TLS certificate verification is disabled",
        detail=(
            "Skipping TLS certificate verification may be intentional for local development, "
            "but it permits man-in-the-middle attacks. Set api_insecure_skip_verify to false "
            "for safer connections. Suppress with !provide-io/pyvider:insecure-tls."
        ),
        attribute="api_insecure_skip_verify",
    ),
    "resource": PackagedLintRPCCase(
        kind="resource",
        rule="provide-io/pyvider:world-writable-directory",
        summary="Directory permissions are world-writable",
        detail=(
            "World-writable permissions may be intentional for a shared scratch directory, "
            "but any local user can modify its contents. Remove the POSIX other-write bit "
            "(for example, set permissions to 0o755) for a safer directory. Suppress with "
            "!provide-io/pyvider:world-writable-directory."
        ),
        attribute="permissions",
    ),
    "data_source": PackagedLintRPCCase(
        kind="data_source",
        rule="provide-io/pyvider:insecure-http",
        summary="HTTP API uses an unencrypted connection",
        detail=(
            "Plain HTTP may be intentional for a local endpoint, but request data can be "
            "intercepted or changed. Set url to an https:// address for a safer connection. "
            "Suppress with !provide-io/pyvider:insecure-http."
        ),
        attribute="url",
    ),
    "ephemeral": PackagedLintRPCCase(
        kind="ephemeral_resource",
        rule="provide-io/pyvider:long-lived-lease",
        summary="Lease lifetime exceeds one hour",
        detail=(
            "A lease longer than one hour may be intentional for lengthy operations, but "
            "long-lived ephemeral values remain usable for longer if exposed. Set ttl_seconds "
            "to 3600 or less for a safer lease. Suppress with "
            "!provide-io/pyvider:long-lived-lease."
        ),
        attribute="ttl_seconds",
    ),
    "list": PackagedLintRPCCase(
        kind="list_resource",
        rule="provide-io/pyvider:include-hidden-files",
        summary="File listing includes hidden files",
        detail=(
            "Including hidden files may be intentional for configuration discovery, but it "
            "can expose secrets or metadata. Set include_hidden to false for safer listings. "
            "Suppress with !provide-io/pyvider:include-hidden-files."
        ),
        attribute="include_hidden",
    ),
    "action": PackagedLintRPCCase(
        kind="action",
        rule="provide-io/pyvider:long-action-timeout",
        summary="Action timeout exceeds five minutes",
        detail=(
            "A timeout longer than five minutes may be intentional for slow prerequisites, "
            "but it can leave Terraform waiting for an unresponsive action. Set "
            "timeout_seconds to 300 or less for a safer timeout. Suppress with "
            "!provide-io/pyvider:long-action-timeout."
        ),
        attribute="timeout_seconds",
    ),
    "state_store": PackagedLintRPCCase(
        kind="state_store",
        rule="provide-io/pyvider:relative-state-store-path",
        summary="State store path is relative",
        detail=(
            "A relative state store path may be intentional for a self-contained workspace, "
            "but it depends on the provider process's working directory. Set path to an "
            "absolute path for safer, predictable state storage. Suppress with "
            "!provide-io/pyvider:relative-state-store-path."
        ),
        attribute="path",
    ),
}
SECURITY_RULES = {
    rule
    for rule in RULE_SUMMARIES
    if rule
    not in {
        "provide-io/pyvider:long-lived-lease",
        "provide-io/pyvider:long-action-timeout",
        "provide-io/pyvider:relative-state-store-path",
    }
}
PROVIDER_BUILD_INPUTS = (
    ".python-version",
    "LICENSE",
    "VERSION",
    "README.md",
    "buildconfig.toml",
    "pyproject.toml",
    "uv.lock",
    "ci/build-provider-linting-stack.py",
)
STACK_SOURCE_BUILD_INPUTS = (
    ".python-version",
    "LICENSE",
    "README.md",
    "VERSION",
    "pyproject.toml",
    "uv.lock",
    "src",
)


def load_driver() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_provider_linting_rpcs", DRIVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_driver_results() -> list[dict[str, Any]]:
    names = {
        "provider": "pyvider",
        "resource": "pyvider_local_directory",
        "data_source": "pyvider_http_api",
        "ephemeral_resource": "pyvider_lease",
        "list_resource": "pyvider_file_content",
        "action": "pyvider_wait_for_file",
        "state_store": "pyvider_filesystem_store",
    }
    results: list[dict[str, Any]] = []
    for case in PACKAGED_LINT_RPC_CASES.values():
        diagnostic = pb.Diagnostic(
            severity=pb.Diagnostic.WARNING,
            summary=f"{case.summary} ({case.rule})",
            detail=case.detail,
        )
        diagnostic.attribute.steps.add(attribute_name=case.attribute)
        results.append(
            {
                "kind": case.kind,
                "name": names[case.kind],
                "diagnostics": [diagnostic],
            }
        )
    return results


def test_rpc_driver_is_importable() -> None:
    module = load_driver()

    assert callable(module.main)


def test_rpc_driver_cli_documents_the_proof_interface() -> None:
    completed = subprocess.run(
        [str(DRIVER), "--help"],
        check=True,
        close_fds=False,
        capture_output=True,
        text=True,
    )

    assert "--binary" in completed.stdout
    assert "--selector" in completed.stdout
    assert "--format {json-lines}" in completed.stdout


def test_rpc_driver_cli_emits_machine_readable_real_provider_findings(
    packaged_provider_path: Path,
) -> None:
    completed = subprocess.run(
        [
            str(DRIVER),
            "--binary",
            str(packaged_provider_path),
            "--selector",
            "provide-io/pyvider:insecure-http",
            "--format",
            "json-lines",
        ],
        check=True,
        close_fds=False,
        capture_output=True,
        text=True,
    )

    records = [json.loads(line) for line in completed.stdout.splitlines()]
    assert records == [
        {
            "attribute": ["url"],
            "detail": (
                "Plain HTTP may be intentional for a local endpoint, but request data can be "
                "intercepted or changed. Set url to an https:// address for a safer connection. "
                "Suppress with !provide-io/pyvider:insecure-http."
            ),
            "kind": "data_source",
            "name": "pyvider_http_api",
            "severity": "warning",
            "summary": ("HTTP API uses an unencrypted connection (provide-io/pyvider:insecure-http)"),
        }
    ]


def test_rpc_driver_cli_rejects_a_missing_binary_without_traceback(tmp_path: Path) -> None:
    missing = tmp_path / "missing-provider"

    completed = subprocess.run(
        [
            str(DRIVER),
            "--binary",
            str(missing),
            "--selector",
            "all",
            "--format",
            "json-lines",
        ],
        close_fds=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert completed.stderr == f"error: provider binary does not exist: {missing}\n"
    assert "Traceback" not in completed.stderr


def test_rpc_driver_cli_rejects_an_invalid_executable_without_traceback(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid-provider"
    invalid.write_text("not an executable\n", encoding="utf-8")

    completed = subprocess.run(
        [
            str(DRIVER),
            "--binary",
            str(invalid),
            "--selector",
            "all",
            "--format",
            "json-lines",
        ],
        close_fds=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr == f"error: provider proof failed for binary: {invalid}\n"
    assert "Traceback" not in completed.stderr


def test_rpc_driver_cli_rejects_an_empty_proof_catalog(packaged_provider_path: Path) -> None:
    completed = subprocess.run(
        [
            str(DRIVER),
            "--binary",
            str(packaged_provider_path),
            "--selector",
            "provide-io/pyvider:unknown-rule",
            "--format",
            "json-lines",
        ],
        close_fds=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert completed.stderr.startswith("error: provider lint proof returned no diagnostics")
    assert "Traceback" not in completed.stderr


def test_rpc_driver_rejects_an_incomplete_rpc_catalog() -> None:
    module = load_driver()

    with pytest.raises(ValueError, match="RPC catalog"):
        module.assert_expected_catalog([], "all")


def test_rpc_driver_rejects_a_diagnostic_owned_by_the_wrong_rpc() -> None:
    module = load_driver()
    results = valid_driver_results()
    results[0]["diagnostics"], results[1]["diagnostics"] = (
        results[1]["diagnostics"],
        results[0]["diagnostics"],
    )

    with pytest.raises(ValueError, match="diagnostic RPC ownership"):
        module.assert_expected_catalog(results, "all")


def test_rpc_driver_rejects_an_error_severity_lint_finding() -> None:
    module = load_driver()
    results = valid_driver_results()
    results[0]["diagnostics"][0].severity = pb.Diagnostic.ERROR

    with pytest.raises(ValueError, match="diagnostic severity"):
        module.assert_expected_catalog(results, "all")


def test_rpc_driver_rejects_a_lint_finding_with_wrong_detail() -> None:
    module = load_driver()
    results = valid_driver_results()
    results[0]["diagnostics"][0].detail = "wrong detail"

    with pytest.raises(ValueError, match="diagnostic detail"):
        module.assert_expected_catalog(results, "all")


def test_rpc_driver_rejects_a_lint_finding_with_wrong_attribute() -> None:
    module = load_driver()
    results = valid_driver_results()
    results[0]["diagnostics"][0].attribute.steps[0].attribute_name = "wrong_attribute"

    with pytest.raises(ValueError, match="diagnostic attribute"):
        module.assert_expected_catalog(results, "all")


def test_rpc_driver_rejects_a_duplicate_lint_diagnostic() -> None:
    module = load_driver()
    results = valid_driver_results()
    results[0]["diagnostics"].append(
        pb.Diagnostic.FromString(results[0]["diagnostics"][0].SerializeToString())
    )

    with pytest.raises(ValueError, match="diagnostic catalog"):
        module.assert_expected_catalog(results, "all")


@pytest.mark.parametrize("stage", ["GetProviderSchema", "ConfigureProvider"])
def test_rpc_driver_rejects_bootstrap_diagnostics(stage: str) -> None:
    module = load_driver()
    diagnostic = pb.Diagnostic(
        severity=pb.Diagnostic.ERROR,
        summary="configuration failed",
        detail="bootstrap detail",
    )

    with pytest.raises(ValueError, match=f"{stage} bootstrap diagnostics"):
        module.assert_no_bootstrap_diagnostics(
            {
                "GetProviderSchema": [diagnostic] if stage == "GetProviderSchema" else [],
                "ConfigureProvider": [diagnostic] if stage == "ConfigureProvider" else [],
            }
        )


def test_config_values_are_shaped_from_the_returned_schema() -> None:
    module = load_driver()
    schema = pb.Schema(
        block=pb.Schema.Block(
            attributes=[
                pb.Schema.Attribute(name="required"),
                pb.Schema.Attribute(name="computed"),
            ]
        )
    )

    dynamic = module.schema_config(schema, {"required": "configured"})

    assert unpack(dynamic) == {"required": "configured", "computed": None}


def test_provenance_source_paths_follow_the_build_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pyvider = tmp_path / "configured-pyvider"
    components = tmp_path / "configured-components"
    monkeypatch.setenv("PYVIDER_SOURCE", str(pyvider))
    monkeypatch.setenv("COMPONENTS_SOURCE", str(components))

    assert provenance_source_paths() == {
        "pyvider": pyvider,
        "pyvider-components": components,
    }


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def assert_revision_compatible(
    repository: Path,
    *,
    label: str,
    recorded_sha: str,
    recorded_archive_sha256: str,
    build_inputs: tuple[str, ...],
) -> None:
    """Prove a recorded build revision still represents the current checkout."""
    commit = subprocess.run(
        ["git", "cat-file", "-e", f"{recorded_sha}^{{commit}}"],
        cwd=repository,
        capture_output=True,
    )
    if commit.returncode != 0:
        raise AssertionError(f"{label} recorded commit does not exist: {recorded_sha}")

    current_head = _git(repository, "rev-parse", "HEAD")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", recorded_sha, current_head],
        cwd=repository,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise AssertionError(f"{label} recorded commit {recorded_sha} is not an ancestor of {current_head}")

    archive = subprocess.run(
        ["git", "archive", recorded_sha],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    actual_archive_sha256 = hashlib.sha256(archive).hexdigest()
    if actual_archive_sha256 != recorded_archive_sha256:
        raise AssertionError(
            f"{label} recorded archive checksum mismatch: "
            f"expected {recorded_archive_sha256}, got {actual_archive_sha256}"
        )

    changed = _git(
        repository,
        "diff",
        "--name-only",
        f"{recorded_sha}..{current_head}",
        "--",
        *build_inputs,
    )
    if changed:
        raise AssertionError(f"{label} build inputs changed after packaging:\n{changed}")


def _provenance_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "source"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Test Author")
    (repo / "src").mkdir()
    (repo / "src" / "runtime.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "proof.md").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "recorded")
    recorded = _git(repo, "rev-parse", "HEAD")
    archive = subprocess.run(
        ["git", "archive", recorded],
        cwd=repo,
        check=True,
        capture_output=True,
    ).stdout
    return repo, recorded, hashlib.sha256(archive).hexdigest()


def test_provenance_accepts_a_descendant_with_only_non_build_changes(tmp_path: Path) -> None:
    repo, recorded, archive_sha = _provenance_repo(tmp_path)
    (repo / "docs" / "proof.md").write_text("documented after build\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs only")

    assert_revision_compatible(
        repo,
        label="fixture",
        recorded_sha=recorded,
        recorded_archive_sha256=archive_sha,
        build_inputs=("src", "pyproject.toml"),
    )


@pytest.mark.parametrize("changed_path", ["src/runtime.py", "pyproject.toml"])
def test_provenance_rejects_runtime_or_build_input_changes(
    tmp_path: Path,
    changed_path: str,
) -> None:
    repo, recorded, archive_sha = _provenance_repo(tmp_path)
    changed = repo / changed_path
    changed.parent.mkdir(parents=True, exist_ok=True)
    changed.write_text("changed after build\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "change build input")

    with pytest.raises(AssertionError, match="build inputs changed"):
        assert_revision_compatible(
            repo,
            label="fixture",
            recorded_sha=recorded,
            recorded_archive_sha256=archive_sha,
            build_inputs=("src", "pyproject.toml"),
        )


@pytest.mark.parametrize(
    ("build_inputs", "changed_path"),
    [
        pytest.param(PROVIDER_BUILD_INPUTS, "buildconfig.toml", id="provider-buildconfig"),
        pytest.param(PROVIDER_BUILD_INPUTS, "LICENSE", id="provider-license"),
        pytest.param(STACK_SOURCE_BUILD_INPUTS, "VERSION", id="source-version"),
        pytest.param(STACK_SOURCE_BUILD_INPUTS, "LICENSE", id="source-license"),
    ],
)
def test_provenance_scopes_cover_root_packaging_inputs(
    tmp_path: Path,
    build_inputs: tuple[str, ...],
    changed_path: str,
) -> None:
    repo, recorded, archive_sha = _provenance_repo(tmp_path)
    (repo / changed_path).write_text("changed after build\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "change root packaging input")

    with pytest.raises(AssertionError, match="build inputs changed"):
        assert_revision_compatible(
            repo,
            label="fixture",
            recorded_sha=recorded,
            recorded_archive_sha256=archive_sha,
            build_inputs=build_inputs,
        )


def test_provenance_rejects_a_diverged_recorded_commit(tmp_path: Path) -> None:
    repo, recorded, archive_sha = _provenance_repo(tmp_path)
    _git(repo, "checkout", "--orphan", "unrelated")
    _git(repo, "rm", "-rf", ".")
    (repo / "unrelated.txt").write_text("unrelated history\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "unrelated")

    with pytest.raises(AssertionError, match="not an ancestor"):
        assert_revision_compatible(
            repo,
            label="fixture",
            recorded_sha=recorded,
            recorded_archive_sha256=archive_sha,
            build_inputs=("src",),
        )


def test_provenance_rejects_a_missing_recorded_commit(tmp_path: Path) -> None:
    repo, _, archive_sha = _provenance_repo(tmp_path)

    with pytest.raises(AssertionError, match="recorded commit does not exist"):
        assert_revision_compatible(
            repo,
            label="fixture",
            recorded_sha="0" * 40,
            recorded_archive_sha256=archive_sha,
            build_inputs=("src",),
        )


def test_provenance_rejects_an_archive_hash_mismatch(tmp_path: Path) -> None:
    repo, recorded, _ = _provenance_repo(tmp_path)

    with pytest.raises(AssertionError, match="archive checksum mismatch"):
        assert_revision_compatible(
            repo,
            label="fixture",
            recorded_sha=recorded,
            recorded_archive_sha256="0" * 64,
            build_inputs=("src",),
        )


def test_packaged_binary_has_coordinated_build_provenance(packaged_provider_path: Path) -> None:
    provenance = Path(__file__).resolve().parents[2] / "dist" / "provider-linting-build-provenance.json"

    assert provenance.is_file(), "run `make build-linting-stack` before lint conformance"
    data = json.loads(provenance.read_text(encoding="utf-8"))
    assert "PYVIDER_CONFORMANCE_PSP" in os.environ
    assert packaged_provider_path.resolve() == Path(os.environ["PYVIDER_CONFORMANCE_PSP"]).resolve()
    named_binary = provenance.parent / data["artifacts"]["binary"]["path"]
    assert packaged_provider_path.resolve() == named_binary.resolve()
    actual_sha = hashlib.sha256(packaged_provider_path.read_bytes()).hexdigest()
    assert actual_sha == data["artifacts"]["binary"]["sha256"]
    assert actual_sha == data["artifacts"]["psp"]["sha256"]
    provider_repository = Path(__file__).resolve().parents[2]
    assert_revision_compatible(
        provider_repository,
        label="provider",
        recorded_sha=data["provider_repository_head"],
        recorded_archive_sha256=data["provider_repository_archive_sha256"],
        build_inputs=PROVIDER_BUILD_INPUTS,
    )
    assert [
        "uv",
        "run",
        "flavor",
        "inspect",
        "--json",
        "--provenance",
        "dist/terraform-provider-pyvider.psp",
    ] in data["commands"]

    for name, source in provenance_source_paths().items():
        assert (
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=source,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            == ""
        )
        assert_revision_compatible(
            source,
            label=name,
            recorded_sha=data["sources"][name]["sha"],
            recorded_archive_sha256=data["sources"][name]["archive_sha256"],
            build_inputs=STACK_SOURCE_BUILD_INPUTS,
        )

    assert any(wheel.startswith("pyvider-") for wheel in data["packaged_wheels"])
    assert any(wheel.startswith("pyvider_components-") for wheel in data["packaged_wheels"])


async def run_selected_lints(
    packaged_provider_path: Path,
    selector: str | None,
    working_directory: Path,
    *,
    config_rules: tuple[str, ...] | None = None,
    include_failure_fixture: bool = False,
) -> list[dict[str, Any]]:
    driver = load_driver()
    lint_env = {} if selector is None else {"PYVIDER_LINT": selector}
    if config_rules is not None:
        config_file = working_directory / "provider-linting-pyvider.toml"
        rendered_rules = ", ".join(json.dumps(rule) for rule in config_rules)
        config_file.write_text(f"[lint]\nrules = [{rendered_rules}]\n", encoding="utf-8")
        lint_env["PYVIDER_CONFIG_FILE"] = str(config_file)
    session: TfPluginProvider = await start_provider(
        packaged_provider_path,
        env=child_env(lint_env),
    )
    try:
        session.schema = await session.stub.GetProviderSchema(pb.GetProviderSchema.Request())
        await session.stub.ConfigureProvider(
            pb.ConfigureProvider.Request(
                terraform_version=CLAIMED_TERRAFORM_VERSION,
                config=driver.schema_config(session.schema.provider, {}),
            )
        )
        results: list[dict[str, Any]] = await driver.validate_configurations(session, working_directory)
        if include_failure_fixture:
            results.append(await driver.validate_failing_action_fixture(session))
        return results
    finally:
        await session.stop()


def assert_finding(
    results: list[dict[str, Any]],
    *,
    kind: str,
    rule: str,
    summary: str,
    detail: str,
    attribute: str,
) -> None:
    result = next(item for item in results if item["kind"] == kind)
    diagnostics: list[Any] = result["diagnostics"]
    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.severity == pb.Diagnostic.WARNING
    assert diagnostic.summary == f"{summary} ({rule})"
    assert diagnostic.detail == detail
    assert [step.attribute_name for step in diagnostic.attribute.steps] == [attribute]


def lint_summaries(results: list[dict[str, Any]]) -> set[str]:
    return {
        diagnostic.summary
        for result in results
        for diagnostic in result["diagnostics"]
        if diagnostic.severity == pb.Diagnostic.WARNING
    }


def summaries_for(rule_ids: set[str]) -> set[str]:
    return {f"{RULE_SUMMARIES[rule]} ({rule})" for rule in rule_ids}


def test_packaged_lint_rpc_case_catalog_has_exact_collection_ids() -> None:
    assert tuple(PACKAGED_LINT_RPC_CASES) == (
        "provider",
        "resource",
        "data_source",
        "ephemeral",
        "list",
        "action",
        "state_store",
    )


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("selector", "expected_rules"),
    [
        pytest.param(None, set(), id="default-off"),
        pytest.param(
            "provide-io/pyvider:insecure-http",
            {"provide-io/pyvider:insecure-http"},
            id="exact",
        ),
        pytest.param(
            "provide-io/pyvider:security",
            SECURITY_RULES,
            id="group",
        ),
        pytest.param("all", set(RULE_SUMMARIES), id="all"),
        pytest.param("provide-io/pyvider:all", set(RULE_SUMMARIES), id="namespaced-all"),
        pytest.param(
            "provide-io/pyvider:all,!provide-io/pyvider:insecure-http",
            set(RULE_SUMMARIES) - {"provide-io/pyvider:insecure-http"},
            id="exclusion",
        ),
        pytest.param("", set(), id="empty-override"),
        pytest.param("malformed selector", set(), id="malformed-selector-fail-open"),
    ],
)
async def test_selector_matrix_through_packaged_binary(
    packaged_provider_path: Path,
    tmp_path: Path,
    selector: str | None,
    expected_rules: set[str],
) -> None:
    # Selector matching is Task 1 production behavior in the archived Pyvider
    # source, so these coordination cases were first-run green. Task 8's honest
    # REDs were the missing process/RPC harness and the file-config helper below.
    results = await run_selected_lints(packaged_provider_path, selector, tmp_path)

    assert lint_summaries(results) == summaries_for(expected_rules)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("selector", "file_rules", "expected_rules"),
    [
        pytest.param(
            None,
            ("provide-io/pyvider:insecure-http",),
            {"provide-io/pyvider:insecure-http"},
            id="file-rules",
        ),
        pytest.param(
            "provide-io/pyvider:insecure-tls",
            ("provide-io/pyvider:insecure-http",),
            {"provide-io/pyvider:insecure-tls"},
            id="env-over-file",
        ),
        pytest.param(
            "",
            ("provide-io/pyvider:insecure-http",),
            set(),
            id="empty-env-disables-file",
        ),
    ],
)
async def test_file_selector_precedence_through_packaged_binary(
    packaged_provider_path: Path,
    tmp_path: Path,
    selector: str | None,
    file_rules: tuple[str, ...],
    expected_rules: set[str],
) -> None:
    results = await run_selected_lints(
        packaged_provider_path,
        selector,
        tmp_path,
        config_rules=file_rules,
    )

    assert lint_summaries(results) == summaries_for(expected_rules)


@pytest.mark.asyncio(loop_scope="session")
async def test_malformed_selector_is_permissive_through_packaged_binary(
    packaged_provider_path: Path, tmp_path: Path
) -> None:
    # Malformed selectors exercise permissive parsing independently from the real
    # packaged hook-exception fixture exercised immediately below.
    results = await run_selected_lints(
        packaged_provider_path,
        "malformed selector",
        tmp_path,
    )

    assert len(results) == 7
    assert all(result["diagnostics"] == [] for result in results)


@pytest.mark.asyncio(loop_scope="session")
async def test_failing_lint_hook_is_nonblocking_through_packaged_binary(
    packaged_provider_path: Path, tmp_path: Path
) -> None:
    results = await run_selected_lints(
        packaged_provider_path,
        "provide-io/pyvider:test-lint-failure",
        tmp_path,
        include_failure_fixture=True,
    )

    result = next(item for item in results if item["kind"] == "failing_action_fixture")
    diagnostics: list[Any] = result["diagnostics"]
    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.severity == pb.Diagnostic.WARNING
    assert diagnostic.summary == "Provider linting did not complete"
    assert diagnostic.detail == (
        "The provider could not complete the requested lint checks. Review provider logs for details."
    )
    rendered = f"{diagnostic.summary}\n{diagnostic.detail}".lower()
    assert "packaged-lint-hook-sentinel" not in rendered
    assert "traceback" not in rendered
    assert list(diagnostic.attribute.steps) == []


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "case",
    [pytest.param(case, id=case_id) for case_id, case in PACKAGED_LINT_RPC_CASES.items()],
)
async def test_packaged_lint_rpc(
    packaged_provider_path: Path,
    tmp_path: Path,
    case: PackagedLintRPCCase,
) -> None:
    results = await run_selected_lints(packaged_provider_path, case.rule, tmp_path)

    assert_finding(
        results,
        kind=case.kind,
        rule=case.rule,
        summary=case.summary,
        detail=case.detail,
        attribute=case.attribute,
    )
