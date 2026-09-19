# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contracts for the checked provider-linting recording and manifest."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "ci" / "generate-provider-linting-proof.py"
VERIFIER = ROOT / "ci" / "verify-provider-linting-proof.py"
RETIMER = ROOT / "ci" / "retime-cast.py"

COMMANDS = [
    "tofu version",
    "tofu validate",
    "PYVIDER_LINT=provide-io/pyvider:all tofu validate -lint=all",
    "PYVIDER_LINT='provide-io/pyvider:all,!provide-io/pyvider:insecure-http' tofu validate",
    "soup stir provider-linting",
    (
        'uv run python ci/run-provider-linting-rpcs.py --binary "$PYVIDER_CONFORMANCE_PSP" '
        "--selector provide-io/pyvider:all --format json-lines"
    ),
]
RULES = [
    ("provide-io/pyvider:insecure-tls", "provider", ["opentofu", "tofusoup"], "api_insecure_skip_verify"),
    (
        "provide-io/pyvider:world-writable-directory",
        "resource",
        ["opentofu", "tofusoup"],
        "permissions",
    ),
    ("provide-io/pyvider:insecure-http", "data-source", ["opentofu", "tofusoup"], "url"),
    (
        "provide-io/pyvider:long-lived-lease",
        "ephemeral",
        ["opentofu", "tofusoup"],
        "ttl_seconds",
    ),
    ("provide-io/pyvider:include-hidden-files", "list", ["tofusoup"], "include_hidden"),
    ("provide-io/pyvider:long-action-timeout", "action", ["tofusoup"], "timeout_seconds"),
    (
        "provide-io/pyvider:relative-state-store-path",
        "state-store",
        ["tofusoup"],
        "path",
    ),
]
PROVIDER_SHA = "a" * 64
OPENTOFU_COMMANDS = [
    'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" '
    '--opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu'
]
DIRECT_RPC_COMMAND = (
    'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" --lane direct'
)


def test_public_tofusoup_lint_suite_replaces_the_private_rpc_driver() -> None:
    suite = ROOT / "tests" / "e2e" / "provider-linting" / "lint.soup.toml"
    direct_demo = (ROOT / "ci" / "provider-linting-direct-rpc-demo.sh").read_text(encoding="utf-8")
    native_demo = (ROOT / "ci" / "provider-linting-demo.sh").read_text(encoding="utf-8")

    assert suite.is_file()
    suite_text = suite.read_text(encoding="utf-8")
    assert 'source = "registry.opentofu.org/provide-io/pyvider"' in suite_text
    assert 'fixture = "."' in suite_text
    assert 'kind = "state-store"' in suite_text
    assert "soup lint tests/e2e/provider-linting/lint.soup.toml" in direct_demo
    assert "--lane direct" in direct_demo
    assert "soup lint tests/e2e/provider-linting/lint.soup.toml" in native_demo
    assert "--lane opentofu" in native_demo
    assert "run-provider-linting-rpcs.py" not in direct_demo + native_demo


def load_script(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cast_text() -> str:
    observations = [
        json.dumps(
            {
                "attribute": attribute,
                "kind": kind,
                "observed_via": "tofusoup",
                "provider_sha256": PROVIDER_SHA,
                "rule_id": rule_id,
                "severity": "warning",
            },
            sort_keys=True,
        )
        for rule_id, kind, _, attribute in RULES
    ]
    return "\n".join(
        [
            *(f"\x1b[1;36m$ {command}\x1b[0m" for command in COMMANDS),
            "OpenTofu v1.13.0-beta1",
            "PASS: provider linting default-off (0 provider lint diagnostics)",
            "PASS: exact exclusion removed provide-io/pyvider:insecure-http",
            "OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)",
            "TofuSoup lifecycle: PASS (same packaged provider; not direct RPC coverage)",
            *observations,
            "TofuSoup direct RPC proof: 7/7 provider lint rules passed",
            "",
        ]
    )


def write_cast(path: Path, text: str | None = None) -> None:
    header = {
        "version": 2,
        "width": 120,
        "height": 40,
        "timestamp": 1_789_344_000,
        "title": "Pyvider provider-native linting proof",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }
    path.write_text(
        json.dumps(header) + "\n" + json.dumps([0.5, "o", text or cast_text()]) + "\n",
        encoding="utf-8",
    )


def rewrite_cast_header(path: Path, **updates: Any) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = json.loads(lines[0])
    header.update(updates)
    path.write_text("\n".join([json.dumps(header), *lines[1:]]) + "\n", encoding="utf-8")


def manifest_for(cast: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": "2026-09-14T07:00:00Z",
        "ci": {
            "repository": "provide-io/terraform-provider-pyvider",
            "run_id": "1234",
            "run_attempt": "1",
            "workflow": "Build Provider Binary",
        },
        "components": {
            "terraform-provider-pyvider": {"version": "0.5.0", "sha": "1" * 40},
            "pyvider": {"version": "0.7.0", "sha": "2" * 40, "archive_sha256": "3" * 64},
            "pyvider-components": {
                "version": "0.7.2",
                "sha": "4" * 40,
                "archive_sha256": "5" * 64,
            },
        },
        "opentofu": {
            "version": "1.13.0-beta1",
            "archive": "tofu_1.13.0-beta1_linux_amd64.zip",
            "archive_sha256": "6" * 64,
        },
        "provider_binary": {
            "path": "dist/linux_amd64/terraform-provider-pyvider_v0.5.0",
            "sha256": PROVIDER_SHA,
        },
        "commands": COMMANDS,
        "rules": [
            {"id": rule_id, "kind": kind, "observed_via": observed_via}
            for rule_id, kind, observed_via, _ in RULES
        ],
        "cast": {
            "path": "provider-linting.cast",
            "sha256": hashlib.sha256(cast.read_bytes()).hexdigest(),
        },
    }


def write_valid_proof(tmp_path: Path) -> tuple[Path, Path]:
    cast = tmp_path / "provider-linting.cast"
    manifest = tmp_path / "provider-linting-proof.json"
    write_cast(cast)
    manifest.write_text(json.dumps(manifest_for(cast), indent=2) + "\n", encoding="utf-8")
    return manifest, cast


def verify(module: ModuleType, manifest: Path, cast: Path) -> None:
    module.verify_proof(manifest, cast)


def write_split_cast(path: Path, *, title: str, text: str) -> None:
    header = {
        "version": 2,
        "width": 120,
        "height": 40,
        "timestamp": 1_789_344_000,
        "title": title,
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }
    path.write_text(json.dumps(header) + "\n" + json.dumps([0.5, "o", text]) + "\n", encoding="utf-8")


def split_manifest_for(opentofu: Path, direct_rpc: Path) -> dict[str, Any]:
    manifest = manifest_for(opentofu)
    manifest["schema_version"] = 2
    manifest["commands"] = {"opentofu": OPENTOFU_COMMANDS, "direct_rpc": [DIRECT_RPC_COMMAND]}
    manifest.pop("cast")
    manifest["casts"] = {
        "opentofu": {
            "path": "provider-linting-opentofu.cast",
            "sha256": hashlib.sha256(opentofu.read_bytes()).hexdigest(),
        },
        "direct_rpc": {
            "path": "provider-linting-direct-rpc.cast",
            "sha256": hashlib.sha256(direct_rpc.read_bytes()).hexdigest(),
        },
    }
    return manifest


def test_split_proof_requires_a_complete_direct_rpc_recording(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_split")
    opentofu = tmp_path / "provider-linting-opentofu.cast"
    direct_rpc = tmp_path / "provider-linting-direct-rpc.cast"
    write_split_cast(
        opentofu,
        title="Pyvider linting — OpenTofu demonstration",
        text="\n".join(
            [
                *(f"$ {command}" for command in OPENTOFU_COMMANDS),
                "Direct provider validation: not requested",
                "OpenTofu native linting: valid",
                "Experimental linting enabled",
            ]
        ),
    )
    direct_rows = [rule_id for rule_id, _kind, _observed_via, _attribute in RULES]
    write_split_cast(
        direct_rpc,
        title="Pyvider linting — direct provider validation",
        text="\n".join(
            [
                f"$ {DIRECT_RPC_COMMAND}",
                "Direct provider validation: 7/7 cases",
                *direct_rows,
            ]
        ),
    )
    manifest = tmp_path / "provider-linting-proof.json"
    manifest.write_text(json.dumps(split_manifest_for(opentofu, direct_rpc)), encoding="utf-8")

    assert verifier.verify_split_proof(manifest, opentofu, direct_rpc) == [rule[0] for rule in RULES]

    incomplete = direct_rows[:-1]
    write_split_cast(
        direct_rpc,
        title="Pyvider linting — direct provider validation",
        text="\n".join(
            [
                f"$ {DIRECT_RPC_COMMAND}",
                *incomplete,
            ]
        ),
    )
    manifest.write_text(json.dumps(split_manifest_for(opentofu, direct_rpc)), encoding="utf-8")
    with pytest.raises(ValueError, match="direct provider recording"):
        verifier.verify_split_proof(manifest, opentofu, direct_rpc)


def test_proof_valid_fixture_reports_all_seven_rules(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_valid")
    manifest, cast = write_valid_proof(tmp_path)

    verified = verifier.verify_proof(manifest, cast)

    assert verified == [rule[0] for rule in RULES]


def test_proof_rejects_missing_command(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_command")
    manifest, cast = write_valid_proof(tmp_path)
    write_cast(cast, cast_text().replace(f"$ {COMMANDS[2]}", "$ command intentionally omitted"))
    data = manifest_for(cast)
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="missing command"):
        verify(verifier, manifest, cast)


def test_proof_rejects_missing_rule(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_rule")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["rules"] = data["rules"][:-1]
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="rule catalog"):
        verify(verifier, manifest, cast)


def test_proof_strips_ansi_before_checking_commands_and_observations(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_ansi")
    manifest, cast = write_valid_proof(tmp_path)

    assert verifier.strip_terminal_controls("\x1b[31mproof\x1b[0m") == "proof"
    verify(verifier, manifest, cast)


def test_proof_rejects_cast_checksum_mismatch(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_cast_hash")
    manifest, cast = write_valid_proof(tmp_path)
    with cast.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps([2.0, "o", "tampered"]) + "\n")

    with pytest.raises(ValueError, match="cast checksum"):
        verify(verifier, manifest, cast)


def test_proof_rejects_secret_like_cast_header_key(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_header_secret")
    manifest, cast = write_valid_proof(tmp_path)
    rewrite_cast_header(
        cast,
        env={"TERM": "xterm-256color", "SHELL": "/bin/bash", "API_TOKEN": "very-secret"},
    )
    manifest.write_text(json.dumps(manifest_for(cast)), encoding="utf-8")

    with pytest.raises(ValueError, match="secret-like key"):
        verify(verifier, manifest, cast)


def test_proof_rejects_machine_local_cast_header_cwd(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_header_cwd")
    manifest, cast = write_valid_proof(tmp_path)
    rewrite_cast_header(cast, cwd="/opt/runner/private/repo")
    manifest.write_text(json.dumps(manifest_for(cast)), encoding="utf-8")

    with pytest.raises(ValueError, match="cast header"):
        verify(verifier, manifest, cast)


def test_proof_rejects_provider_checksum_mismatch(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_provider_hash")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["provider_binary"]["sha256"] = "b" * 64
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="provider checksum"):
        verify(verifier, manifest, cast)


def test_proof_rejects_unknown_observation_channel(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_channel")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["rules"][0]["observed_via"] = ["opentofu", "tofusoup", "imaginary"]
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="observation channel"):
        verify(verifier, manifest, cast)


@pytest.mark.parametrize(
    "leak", ["/Users/alice/code/provider", "/home/alice/provider", r"C:\\Users\\alice\\provider"]
)
def test_proof_rejects_absolute_user_path_leakage(tmp_path: Path, leak: str) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_path")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["ci"]["workspace"] = leak
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="machine-local path"):
        verify(verifier, manifest, cast)


@pytest.mark.parametrize("key", ["token", "api_token", "access-token", "client_secret", "password"])
def test_proof_rejects_token_like_key_leakage(tmp_path: Path, key: str) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_secret")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["ci"][key] = "should-not-be-here"
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="secret-like key"):
        verify(verifier, manifest, cast)


def test_proof_rejects_non_beta_tofu_version(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_version")
    manifest, cast = write_valid_proof(tmp_path)
    data = manifest_for(cast)
    data["opentofu"]["version"] = "1.13.0"
    manifest.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="OpenTofu version"):
        verify(verifier, manifest, cast)


def test_proof_rejects_beta10_spoof_in_cast(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_beta10")
    manifest, cast = write_valid_proof(tmp_path)
    write_cast(cast, cast_text().replace("OpenTofu v1.13.0-beta1\n", "OpenTofu v1.13.0-beta10\n"))
    manifest.write_text(json.dumps(manifest_for(cast)), encoding="utf-8")

    with pytest.raises(ValueError, match="exact OpenTofu version"):
        verify(verifier, manifest, cast)


def test_proof_generator_uses_build_provenance_and_exact_schema(tmp_path: Path) -> None:
    generator = load_script(GENERATOR, "provider_linting_generator")
    cast = tmp_path / "provider-linting.cast"
    binary = tmp_path / "dist" / "linux_amd64" / "terraform-provider-pyvider_v0.5.0"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"packaged provider")
    write_cast(cast, cast_text().replace(PROVIDER_SHA, hashlib.sha256(binary.read_bytes()).hexdigest()))
    provenance = tmp_path / "dist" / "provider-linting-build-provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "provider_repository_head": "0" * 40,
                "sources": {
                    "pyvider": {"sha": "2" * 40, "archive_sha256": "3" * 64},
                    "pyvider-components": {"sha": "4" * 40, "archive_sha256": "5" * 64},
                },
                "packaged_wheels": [
                    "pyvider-0.7.0-py3-none-any.whl",
                    "pyvider_components-0.7.2-py3-none-any.whl",
                ],
                "artifacts": {
                    "binary": {
                        "path": "linux_amd64/terraform-provider-pyvider_v0.5.0",
                        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "proof.json"

    generator.generate_proof(
        cast_path=cast,
        build_provenance_path=provenance,
        output_path=output,
        provider_version="0.5.0",
        opentofu_archive="tofu_1.13.0-beta1_linux_amd64.zip",
        opentofu_archive_sha256="6" * 64,
        generated_at="2026-09-14T07:00:00Z",
        ci_environment={},
    )

    assert json.loads(output.read_text(encoding="utf-8")) == manifest_for(cast) | {
        "ci": {"repository": None, "run_id": None, "run_attempt": None, "workflow": None},
        "components": {
            "terraform-provider-pyvider": {"version": "0.5.0", "sha": "0" * 40},
            "pyvider": {"version": "0.7.0", "sha": "2" * 40, "archive_sha256": "3" * 64},
            "pyvider-components": {
                "version": "0.7.2",
                "sha": "4" * 40,
                "archive_sha256": "5" * 64,
            },
        },
        "provider_binary": {
            "path": "dist/linux_amd64/terraform-provider-pyvider_v0.5.0",
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        },
        "cast": {
            "path": "provider-linting.cast",
            "sha256": hashlib.sha256(cast.read_bytes()).hexdigest(),
        },
    }


def test_proof_generator_rejects_malformed_nested_provenance_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    generator = load_script(GENERATOR, "provider_linting_generator_malformed")
    cast = tmp_path / "provider-linting.cast"
    provenance = tmp_path / "broken-provenance.json"
    output = tmp_path / "proof.json"
    write_cast(cast)
    provenance.write_text('{"artifacts": []}\n', encoding="utf-8")
    monkeypatch.setenv("PYVIDER_OPENTOFU_ARCHIVE_SHA256", "6" * 64)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(GENERATOR),
            "--opentofu-cast",
            str(cast),
            "--direct-rpc-cast",
            str(cast),
            "--build-provenance",
            str(provenance),
            "--output",
            str(output),
        ],
    )

    assert generator.main() == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: build provenance artifacts must be an object\n"
    assert "Traceback" not in captured.err
    assert str(tmp_path) not in captured.err


def test_proof_scripts_and_workflow_preserve_the_one_binary_contract() -> None:
    opentofu_demo = (ROOT / "ci" / "provider-linting-demo.sh").read_text(encoding="utf-8")
    direct_rpc_demo = (ROOT / "ci" / "provider-linting-direct-rpc-demo.sh").read_text(encoding="utf-8")
    recorder = (ROOT / "ci" / "record-provider-linting.sh").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "build-provider.yml").read_text(encoding="utf-8")

    for command in OPENTOFU_COMMANDS:
        assert command in opentofu_demo
    assert DIRECT_RPC_COMMAND in direct_rpc_demo
    assert "soup stir provider-linting" not in opentofu_demo + direct_rpc_demo
    assert "run-provider-linting-rpcs.py" not in opentofu_demo + direct_rpc_demo
    assert "soup lint tests/e2e/provider-linting/lint.soup.toml" in opentofu_demo + direct_rpc_demo
    assert "provider-linting-opentofu.cast" in recorder
    assert "provider-linting-direct-rpc.cast" in recorder
    assert "--opentofu-cast" in recorder and "--direct-rpc-cast" in recorder
    assert "flavor pack" not in opentofu_demo + direct_rpc_demo + recorder
    assert "provider_linting_proof:" in workflow
    assert "pyvider_ref:" in workflow
    assert "components_ref:" in workflow
    assert "ci/build-provider-linting-stack.py" in workflow
    assert "test-conformance-binary" in workflow
    assert "test-linting-opentofu-binary" in workflow
    assert "provider-linting-proof" in workflow
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in workflow
    assert "grep -Fxq 'OpenTofu v1.13.0-beta1'" in recorder
    assert "grep -Fxq 'OpenTofu v1.13.0-beta1'" in workflow
    assert "uv tool install --refresh tofusoup==0.8.0" in workflow

    proof_job = workflow.split("  provider-linting-proof:", 1)[1].split("\n  summary:", 1)[0]
    assert (
        "provider-linting-proof.json provider-linting-opentofu.cast provider-linting-direct-rpc.cast"
        in proof_job
    )
    assert "            provider-linting-opentofu.cast" in proof_job
    assert "            provider-linting-direct-rpc.cast" in proof_job
    assert "            provider-linting.cast" not in proof_job
    assert "    env:\n      PYVIDER_SOURCE: ${{ github.workspace }}/.stack/pyvider" in proof_job
    assert "      COMPONENTS_SOURCE: ${{ github.workspace }}/.stack/pyvider-components" in proof_job


def test_retime_redacts_longest_nested_path_before_parent() -> None:
    retimer = load_script(RETIMER, "provider_linting_retimer_nested")
    repository = "/Users/example/provider"
    staging = f"{repository}/.provider-linting-proof.JuYZSQ"
    wrapped_staging = staging[:30] + "\r\n" + staging[30:]
    events = [
        [0.5, "o", f"artifact: {staging}/demo\n"],
        [1.0, "o", f"wrapped: {wrapped_staging}/provider-linting.cast\n"],
        [1.5, "o", f"repository: {repository}/README.md\n"],
    ]

    redacted = "".join(event[2] for event in retimer.redact_event_paths(events, [repository, staging]))

    assert ".provider-linting-proof." not in redacted
    assert "JuYZSQ" not in redacted
    assert repository not in redacted
    assert redacted.count("<workspace>") == 3


def test_rpc_driver_json_lines_include_proof_identity_fields() -> None:
    source = (ROOT / "ci" / "run-provider-linting-rpcs.py").read_text(encoding="utf-8")

    for field in ("rule_id", "kind", "severity", "attribute", "observed_via", "provider_sha256"):
        assert f'"{field}"' in source


def test_recording_utilities_keep_the_existing_conformance_interface(tmp_path: Path) -> None:
    legacy_cast = tmp_path / "legacy.cast"
    retimed_cast = tmp_path / "legacy-retimed.cast"

    completed = subprocess.run(
        ["uv", "run", "python", "ci/record-to-cast.py", str(legacy_cast), "printf", "legacy-proof"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(legacy_cast.read_text(encoding="utf-8").splitlines()[0])["title"] == (
        "pyvider conformance suite"
    )
    subprocess.run(
        ["uv", "run", "python", "ci/retime-cast.py", str(legacy_cast), str(retimed_cast), "15"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(retimed_cast.read_text(encoding="utf-8").splitlines()[0])["title"] == (
        "pyvider conformance suite"
    )
