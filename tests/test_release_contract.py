# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Release-safety contracts for the provider linting proof."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from types import ModuleType

import pytest
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "ci" / "build-provider-linting-stack.py"
PROOF_LIBRARY = ROOT / "ci" / "provider_linting_proof.py"
PROOF_OUTPUTS = {
    "provider-linting-direct.cast",
    "provider-linting-opentofu.cast",
    "provider-linting-walkthrough.cast",
    "tutorial-part7-provider-linting.cast",
    "provider-linting-proof.json",
}


def load_build_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("provider_lint_release_build", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_proof_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("provider_lint_release_proof", PROOF_LIBRARY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def initialized_provider(tmp_path: Path) -> Path:
    repo = tmp_path / "provider"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Test Author")
    (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
    for name in PROOF_OUTPUTS:
        (repo / name).write_text("checkpoint\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    return repo


def test_pin_public_lint_dependencies_removes_sources(tmp_path: Path) -> None:
    module = load_build_module()
    project = tmp_path / "pyproject.toml"
    project.write_text(
        '[project]\ndependencies=["pyvider>=0.7.0", "pyvider-components>=0.7.2", "attrs>=25"]\n'
        '[tool.uv.sources]\npyvider={path="../pyvider"}\n',
        encoding="utf-8",
    )

    module.pin_public_lint_dependencies(project, pyvider="0.8.1", components="0.8.0")

    parsed = tomllib.loads(project.read_text(encoding="utf-8"))
    assert parsed["project"]["dependencies"] == [
        "pyvider==0.8.1",
        "pyvider-components==0.8.0",
        "attrs>=25",
    ]
    assert "sources" not in parsed.get("tool", {}).get("uv", {})


def test_pin_public_lint_dependencies_requires_both_coordinates(tmp_path: Path) -> None:
    module = load_build_module()
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\ndependencies=["pyvider>=0.7.0"]\n', encoding="utf-8")

    with pytest.raises(ValueError, match="both lint dependencies"):
        module.pin_public_lint_dependencies(project, pyvider="0.8.1", components="0.8.0")


def test_provider_cleanliness_allows_only_the_four_proof_outputs(tmp_path: Path) -> None:
    module = load_build_module()
    provider = initialized_provider(tmp_path)
    for name in PROOF_OUTPUTS:
        (provider / name).write_text("new proof\n", encoding="utf-8")

    assert module.inspect_provider_source(provider) == git(provider, "rev-parse", "HEAD")

    (provider / "unexpected.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected dirty paths"):
        module.inspect_provider_source(provider)


def test_build_workflow_consumes_linux_artifact_without_rebuilding_proof_binary() -> None:
    text = (ROOT / ".github" / "workflows" / "build-provider.yml").read_text(encoding="utf-8")
    proof_job = text.split("  provider-linting-proof:", 1)[1].split("  summary:", 1)[0]

    assert "provider-linux_amd64" in proof_job
    assert "actions/download-artifact" in proof_job
    assert "build-provider-linting-stack.py" not in proof_job
    assert "flavor pack" not in proof_job
    assert "pyvider_ref" not in text
    assert "components_ref" not in text
    assert ".stack/pyvider" not in text
    assert ".stack/pyvider-components" not in text


def test_release_workflow_binds_numeric_build_to_exact_release_sha_and_proof_assets() -> None:
    path = ROOT / ".github" / "workflows" / "release.yml"
    text = path.read_text(encoding="utf-8")
    yaml.safe_load(text)

    assert "latest successful" not in text.lower()
    assert "build_run_id must be numeric" in text
    assert "headSha" in text
    assert "github.sha" in text
    assert "provider-linting-proof" in text
    assert "verify-release-proof" in text
    for name in (
        "provider-linting-proof.json",
        "provider-linting-opentofu.cast",
        "provider-linting-direct.cast",
        "provider-linting-walkthrough.cast",
        "tutorial-part7-provider-linting.cast",
        "provider-linting-build-provenance.json",
        "windows_amd64",
    ):
        assert name in text


def test_publisher_targets_the_validated_release_sha() -> None:
    text = (ROOT / "ci" / "publish-release.sh").read_text(encoding="utf-8")

    assert "RELEASE_TARGET_SHA" in text
    assert "^[0-9a-f]{40}$" in text
    assert '--target "${RELEASE_TARGET_SHA}"' in text


def test_default_ci_runs_repository_tests() -> None:
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "run-tests: true" in text
    assert "There is no repo-local pytest suite" not in text


def test_proof_component_records_public_wheel_identity() -> None:
    module = load_proof_module()
    record = {
        "version": "0.8.1",
        "tag": "v0.8.1",
        "commit": "a" * 40,
        "registry": "https://pypi.org/simple",
        "wheel": "pyvider-0.8.1-py3-none-any.whl",
        "sha256": "b" * 64,
    }

    assert module.public_dependency_component(record, name="pyvider") == {
        "version": "0.8.1",
        "sha": "a" * 40,
        "tag": "v0.8.1",
        "registry": "https://pypi.org/simple",
        "wheel": "pyvider-0.8.1-py3-none-any.whl",
        "wheel_sha256": "b" * 64,
    }


def test_proof_component_rejects_non_registry_dependency() -> None:
    module = load_proof_module()
    record = {
        "version": "0.8.1",
        "tag": "v0.8.1",
        "commit": "a" * 40,
        "registry": "https://example.invalid/simple",
        "wheel": "pyvider-0.8.1-py3-none-any.whl",
        "sha256": "b" * 64,
    }

    with pytest.raises(ValueError, match="public PyPI registry"):
        module.public_dependency_component(record, name="pyvider")


def test_proof_release_candidate_binds_archive_platform_and_binary() -> None:
    module = load_proof_module()
    candidate = {
        "github_artifact": "provider-linux_amd64",
        "archive": "terraform-provider-pyvider_0.6.0_linux_amd64.zip",
        "platform": "linux_amd64",
        "sha256": "c" * 64,
    }

    assert module.checked_release_candidate(candidate, binary_platform="linux_amd64") == candidate
    with pytest.raises(ValueError, match="does not match provider binary"):
        module.checked_release_candidate(candidate, binary_platform="darwin_arm64")


def test_provider_0_6_coordinates_and_proof_dependency_are_declared() -> None:
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.6.0"
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["dependencies"]
    dev = project["dependency-groups"]["dev"]
    assert "pyvider>=0.8.1" in dependencies
    assert "pyvider-components>=0.8.0" in dependencies
    assert "tofusoup==0.8.2" in dev
    for relative in (
        "tests/e2e/provider-linting/main.tf",
        "tests/e2e/provider-linting/lint.soup.toml",
        "tests/proof/fixtures/provider-linting/main.tf",
    ):
        assert 'version = "0.6.0"' in (ROOT / relative).read_text(encoding="utf-8")


def test_proof_workflows_verify_tofusoup_cli_and_imported_version() -> None:
    for relative in (".github/workflows/build-provider.yml", ".github/workflows/release.yml"):
        workflow = (ROOT / relative).read_text(encoding="utf-8")
        assert 'test "$(soup --version)" = "soup, version 0.8.2"' in workflow
        assert 'assert tofusoup.__version__ == "0.8.2"' in workflow


def test_recorder_pins_tofusoup_before_the_first_film() -> None:
    recorder = (ROOT / "ci" / "record-provider-linting.sh").read_text(encoding="utf-8")

    assert recorder.index("uv tool install --refresh --quiet tofusoup==0.8.2") < recorder.index(
        "record_lane opentofu"
    )


def test_0_6_changelog_documents_the_release_proof_contract() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = changelog.split("## [0.6.0]", 1)[1]
    for phrase in (
        "seven direct",
        "four OpenTofu",
        "selectors",
        "provider-linting-proof.json",
        "public PyPI",
        "wheel SHA-256",
        "four paced",
        "Part 7",
    ):
        assert phrase in section


def test_user_facing_proof_copy_does_not_claim_opentofu_native_provider_linting() -> None:
    paths = [
        ROOT / "docs" / "guides" / "provider-linting-proof.md",
        ROOT / "ci" / "provider-linting-demo.sh",
        ROOT / "ci" / "provider-linting-walkthrough.sh",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    assert "opentofu native linting" not in combined
    assert "opentofu-native validation" not in combined
    assert "opentofu demonstrates native validation" not in combined
    assert "opentofu experimental lint validation" in combined
    assert "opentofu-native" not in combined


def test_public_recordings_do_not_expose_internal_proof_variables() -> None:
    for relative in (
        "ci/provider-linting-demo.sh",
        "ci/provider-linting-direct-rpc-demo.sh",
        "ci/provider-linting-walkthrough.sh",
        "ci/provider-linting-tutorial.sh",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        displayed_commands = "\n".join(
            line for line in text.splitlines() if line.lstrip().startswith("show_command ")
        )
        for internal in ("PYVIDER_CONFORMANCE_PSP", "PYVIDER_OPENTOFU_BINARY"):
            assert internal not in displayed_commands


def test_public_opentofu_installer_has_capability_based_name() -> None:
    assert (ROOT / "ci" / "install-opentofu-experimental.sh").is_file()
    assert not (ROOT / "ci" / "install-opentofu-beta.sh").exists()
    for relative in (
        "Makefile",
        ".github/workflows/build-provider.yml",
        ".github/workflows/release.yml",
        "ci/provider-linting-demo.sh",
        "ci/provider-linting-walkthrough.sh",
        "ci/provider_linting_proof.py",
        "ci/record-provider-linting.sh",
        "tests/e2e/test_provider_linting_opentofu.py",
        "tests/test_install_opentofu_experimental.py",
    ):
        assert "install-opentofu-beta.sh" not in (ROOT / relative).read_text(encoding="utf-8")


def test_public_walkthrough_discovers_the_current_platform_artifact() -> None:
    walkthrough = (ROOT / "ci" / "provider-linting-walkthrough.sh").read_text(encoding="utf-8")

    assert "dist/linux_amd64" not in walkthrough
    assert "provider=$(uv run python ci/provider-linting-artifact-path.py" in walkthrough
    assert '--provider "$provider"' in walkthrough


def test_public_artifact_path_helper_verifies_the_provenance_hash(tmp_path: Path) -> None:
    binary = tmp_path / "darwin_arm64" / "terraform-provider-pyvider_v0.6.0"
    binary.parent.mkdir()
    binary.write_bytes(b"provider")
    provenance = tmp_path / "provider-linting-build-provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "artifacts": {
                    "binary": {
                        "path": "darwin_arm64/terraform-provider-pyvider_v0.6.0",
                        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    helper = ROOT / "ci" / "provider-linting-artifact-path.py"

    valid = subprocess.run(
        [sys.executable, str(helper), str(provenance)], capture_output=True, text=True, check=False
    )
    assert valid.returncode == 0, valid.stderr
    assert valid.stdout == f"{binary.resolve()}\n"

    binary.write_bytes(b"tampered")
    invalid = subprocess.run(
        [sys.executable, str(helper), str(provenance)], capture_output=True, text=True, check=False
    )
    assert invalid.returncode == 2
    assert invalid.stdout == ""
    assert "checksum" in invalid.stderr


def test_superseded_legacy_casts_are_removed() -> None:
    assert not (ROOT / "provider-linting.cast").exists()
    assert not (ROOT / "provider-linting-direct-rpc.cast").exists()
