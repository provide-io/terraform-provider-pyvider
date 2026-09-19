# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared schema, generation, and verification for provider-linting proof."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

SCHEMA_VERSION = 1
OPENTOFU_VERSION = "1.13.0-beta1"
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
SPLIT_COMMANDS = {
    "opentofu": [
        'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" '
        '--opentofu "$PYVIDER_OPENTOFU_BINARY" --lane opentofu'
    ],
    "direct_rpc": [
        'soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$PYVIDER_CONFORMANCE_PSP" '
        "--lane direct"
    ],
}
SPLIT_CASTS = {
    "opentofu": "provider-linting-opentofu.cast",
    "direct_rpc": "provider-linting-direct-rpc.cast",
}
RULES: list[dict[str, Any]] = [
    {
        "id": "provide-io/pyvider:insecure-tls",
        "kind": "provider",
        "attribute": "api_insecure_skip_verify",
        "observed_via": ["opentofu", "tofusoup"],
    },
    {
        "id": "provide-io/pyvider:world-writable-directory",
        "kind": "resource",
        "attribute": "permissions",
        "observed_via": ["opentofu", "tofusoup"],
    },
    {
        "id": "provide-io/pyvider:insecure-http",
        "kind": "data-source",
        "attribute": "url",
        "observed_via": ["opentofu", "tofusoup"],
    },
    {
        "id": "provide-io/pyvider:long-lived-lease",
        "kind": "ephemeral",
        "attribute": "ttl_seconds",
        "observed_via": ["opentofu", "tofusoup"],
    },
    {
        "id": "provide-io/pyvider:include-hidden-files",
        "kind": "list",
        "attribute": "include_hidden",
        "observed_via": ["tofusoup"],
    },
    {
        "id": "provide-io/pyvider:long-action-timeout",
        "kind": "action",
        "attribute": "timeout_seconds",
        "observed_via": ["tofusoup"],
    },
    {
        "id": "provide-io/pyvider:relative-state-store-path",
        "kind": "state-store",
        "attribute": "path",
        "observed_via": ["tofusoup"],
    },
]

_ANSI_CSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_ANSI_OSC = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
_USER_PATH = re.compile(r"(?:/(?:Users|home|Volumes|tmp|private/var)/[^/\s]+|[A-Za-z]:\\+Users\\+[^\\\s]+)")
_SECRET_KEY = re.compile(
    r"(?:token|password|passwd|secret|authorization|credential)",
    re.IGNORECASE,
)
_SERIALIZED_SECRET = re.compile(
    r"(?i)[\"']?[a-z0-9_-]*(?:token|password|passwd|secret|authorization|credential)"
    r"[a-z0-9_-]*[\"']?\s*[:=]"
)
_CAST_HEADER_KEYS = {"version", "width", "height", "timestamp", "title", "env"}
_CAST_TITLES = {
    "pyvider conformance suite",
    "Pyvider provider-native linting proof",
    "Pyvider linting — OpenTofu demonstration",
    "Pyvider linting — direct provider validation",
}
_CAST_ENV = {"TERM": "xterm-256color", "SHELL": "/bin/bash"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_terminal_controls(value: str) -> str:
    """Remove ANSI CSI/OSC terminal controls before semantic assertions."""
    return _ANSI_CSI.sub("", _ANSI_OSC.sub("", value)).replace("\r", "")


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"invalid {label}: expected an object")
    return loaded


def _validate_cast_header(header: Any) -> None:
    if not isinstance(header, dict):
        raise ValueError("cast header must be an object")
    _walk_keys(header)
    if set(header) != _CAST_HEADER_KEYS:
        raise ValueError("cast header keys do not match the checked schema")
    if header["version"] != 2:
        raise ValueError("cast is not asciinema v2")
    for dimension in ("width", "height"):
        value = header[dimension]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"cast header {dimension} must be a positive integer")
    timestamp = header["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp <= 0:
        raise ValueError("cast header timestamp must be a positive integer")
    if header["title"] not in _CAST_TITLES:
        raise ValueError("cast header title is not approved")
    if header["env"] != _CAST_ENV:
        raise ValueError("cast header environment does not match the checked schema")


def _cast_output(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            raise ValueError("empty cast")
        header = json.loads(lines[0])
        _validate_cast_header(header)
        chunks: list[str] = []
        for line in lines[1:]:
            event = json.loads(line)
            if (
                not isinstance(event, list)
                or len(event) != 3
                or not isinstance(event[0], (int, float))
                or event[1] != "o"
                or not isinstance(event[2], str)
            ):
                raise ValueError("invalid cast event")
            chunks.append(event[2])
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cast") from exc
    return strip_terminal_controls("".join(chunks))


def _assert_hash(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise ValueError(f"invalid {label}")
    return value


def _assert_sha(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _GIT_SHA.fullmatch(value) is None:
        raise ValueError(f"invalid {label}")
    return value


def _walk_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError("manifest object keys must be strings")
            if _SECRET_KEY.search(key):
                raise ValueError(f"secret-like key is forbidden: {key}")
            _walk_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_keys(nested)


def _assert_no_leaks(manifest: Mapping[str, Any], cast_output: str) -> None:
    _walk_keys(manifest)
    serialized = json.dumps(manifest, sort_keys=True) + "\n" + cast_output
    if _USER_PATH.search(serialized):
        raise ValueError("machine-local path is forbidden")
    if _SERIALIZED_SECRET.search(cast_output):
        raise ValueError("secret-like key is forbidden in cast")


def _validate_components(components: Any) -> None:
    if not isinstance(components, dict) or set(components) != {
        "terraform-provider-pyvider",
        "pyvider",
        "pyvider-components",
    }:
        raise ValueError("component provenance is incomplete")
    for name, component in components.items():
        if not isinstance(component, dict) or not isinstance(component.get("version"), str):
            raise ValueError(f"invalid component metadata for {name}")
        _assert_sha(component.get("sha"), label=f"{name} source SHA")
        if name != "terraform-provider-pyvider":
            _assert_hash(component.get("archive_sha256"), label=f"{name} archive checksum")


def _expected_manifest_rules() -> list[dict[str, Any]]:
    return [{"id": rule["id"], "kind": rule["kind"], "observed_via": rule["observed_via"]} for rule in RULES]


def _validate_generated_at(value: Any) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("generated_at must be a UTC timestamp")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("generated_at must be a UTC timestamp") from exc


def _validate_opentofu(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"version", "archive", "archive_sha256"}:
        raise ValueError("OpenTofu metadata is invalid")
    if value.get("version") != OPENTOFU_VERSION:
        raise ValueError(f"OpenTofu version must be {OPENTOFU_VERSION}")
    archive = value.get("archive")
    if not isinstance(archive, str) or not archive.startswith(f"tofu_{OPENTOFU_VERSION}_"):
        raise ValueError("OpenTofu archive does not match the pinned beta")
    _assert_hash(value.get("archive_sha256"), label="OpenTofu archive checksum")


def _validate_provider_binary(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise ValueError("provider binary metadata is invalid")
    path = value["path"]
    if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
        raise ValueError("provider binary path must be repository-relative")
    _assert_hash(value["sha256"], label="provider checksum")


def _validate_rules(value: Any) -> None:
    if not isinstance(value, list):
        raise ValueError("rule catalog must be a list")
    for rule in value:
        if not isinstance(rule, dict) or set(rule) != {"id", "kind", "observed_via"}:
            raise ValueError("rule catalog contains invalid metadata")
        channels = rule["observed_via"]
        if not isinstance(channels, list) or not set(channels).issubset({"opentofu", "tofusoup"}):
            raise ValueError("unknown observation channel")
    if value != _expected_manifest_rules():
        raise ValueError("rule catalog does not match the seven supported rules")


def _validate_cast_metadata(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise ValueError("cast metadata is invalid")
    if value["path"] != "provider-linting.cast":
        raise ValueError("cast path must be provider-linting.cast")
    _assert_hash(value["sha256"], label="cast checksum")


def _validate_split_casts(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != set(SPLIT_CASTS):
        raise ValueError("split cast metadata is incomplete")
    for name, expected_path in SPLIT_CASTS.items():
        metadata = value[name]
        if not isinstance(metadata, dict) or set(metadata) != {"path", "sha256"}:
            raise ValueError(f"invalid {name} cast metadata")
        if metadata["path"] != expected_path:
            raise ValueError(f"{name} cast path is invalid")
        _assert_hash(metadata["sha256"], label=f"{name} cast checksum")


def _validate_manifest(manifest: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "generated_at",
        "ci",
        "components",
        "opentofu",
        "provider_binary",
        "commands",
        "rules",
        "cast",
    }
    if set(manifest) != required:
        raise ValueError("manifest schema keys do not match version 1")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("manifest schema version must be 1")
    _validate_generated_at(manifest["generated_at"])
    if not isinstance(manifest["ci"], dict):
        raise ValueError("ci identity must be an object")
    _validate_components(manifest["components"])
    _validate_opentofu(manifest["opentofu"])
    _validate_provider_binary(manifest["provider_binary"])
    if manifest["commands"] != COMMANDS:
        raise ValueError("command catalog does not match the checked proof")
    _validate_rules(manifest["rules"])
    _validate_cast_metadata(manifest["cast"])


def _validate_split_manifest(manifest: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "generated_at",
        "ci",
        "components",
        "opentofu",
        "provider_binary",
        "commands",
        "rules",
        "casts",
    }
    if set(manifest) != required:
        raise ValueError("manifest schema keys do not match version 2")
    if manifest["schema_version"] != 2:
        raise ValueError("manifest schema version must be 2")
    _validate_generated_at(manifest["generated_at"])
    if not isinstance(manifest["ci"], dict):
        raise ValueError("ci identity must be an object")
    _validate_components(manifest["components"])
    _validate_opentofu(manifest["opentofu"])
    _validate_provider_binary(manifest["provider_binary"])
    if manifest["commands"] != SPLIT_COMMANDS:
        raise ValueError("command catalog does not match the split proof")
    _validate_rules(manifest["rules"])
    _validate_split_casts(manifest["casts"])


def _parse_observations(output: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        if not line.startswith("{"):
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and "rule_id" in candidate:
            records.append(candidate)
    return records


def _validate_cast(output: str, manifest: dict[str, Any]) -> list[str]:
    for command in COMMANDS:
        if f"$ {command}" not in output:
            raise ValueError(f"missing command from cast: {command}")
    required_statements = [
        "PASS: provider linting default-off (0 provider lint diagnostics)",
        "PASS: exact exclusion removed provide-io/pyvider:insecure-http",
        "OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)",
        "TofuSoup lifecycle: PASS (same packaged provider; not direct RPC coverage)",
        "TofuSoup direct RPC proof: 7/7 provider lint rules passed",
    ]
    for statement in required_statements:
        if statement not in output:
            raise ValueError(f"missing proof statement from cast: {statement}")
    if f"OpenTofu v{OPENTOFU_VERSION}" not in output.splitlines():
        raise ValueError(f"cast does not show the exact OpenTofu version v{OPENTOFU_VERSION}")
    observations = _parse_observations(output)
    expected_records = [
        {
            "attribute": rule["attribute"],
            "kind": rule["kind"],
            "observed_via": "tofusoup",
            "provider_sha256": manifest["provider_binary"]["sha256"],
            "rule_id": rule["id"],
            "severity": "warning",
        }
        for rule in RULES
    ]
    if observations != expected_records:
        if any(
            record.get("provider_sha256") != manifest["provider_binary"]["sha256"] for record in observations
        ):
            raise ValueError("provider checksum in cast observations does not match manifest")
        raise ValueError("cast rule observations do not match the seven-rule catalog")
    return [record["rule_id"] for record in observations]


def _validate_opentofu_cast(output: str) -> None:
    for command in SPLIT_COMMANDS["opentofu"]:
        if f"$ {command}" not in output:
            raise ValueError(f"missing command from OpenTofu recording: {command}")
    for statement in (
        "Direct provider validation: not requested",
        "OpenTofu native linting: valid",
        "Experimental linting enabled",
    ):
        if statement not in output:
            raise ValueError(f"missing proof statement from OpenTofu recording: {statement}")
    if "run-provider-linting-rpcs.py" in output:
        raise ValueError("OpenTofu recording contains an internal proof command")


def _validate_direct_rpc_cast(output: str, manifest: dict[str, Any]) -> list[str]:
    command = SPLIT_COMMANDS["direct_rpc"][0]
    if f"$ {command}" not in output:
        raise ValueError(f"missing command from direct RPC recording: {command}")
    if "Direct provider validation: 7/7 cases" not in output:
        raise ValueError("direct provider recording has no coverage heading")
    if any(rule["id"] not in output for rule in RULES):
        raise ValueError("direct RPC recording does not contain the seven-rule catalog")
    if "run-provider-linting-rpcs.py" in output:
        raise ValueError("direct provider recording contains an internal proof command")
    return [rule["id"] for rule in RULES]


def verify_proof(manifest_path: Path, cast_path: Path) -> list[str]:
    """Validate the manifest and every semantic assertion in the complete cast."""
    manifest = _load_json_object(manifest_path, label="proof manifest")
    _validate_manifest(manifest)
    if sha256_file(cast_path) != manifest["cast"]["sha256"]:
        raise ValueError("cast checksum does not match manifest")
    output = _cast_output(cast_path)
    _assert_no_leaks(manifest, output)
    return _validate_cast(output, manifest)


def verify_split_proof(manifest_path: Path, opentofu_cast_path: Path, direct_rpc_cast_path: Path) -> list[str]:
    """Validate both purpose-specific recordings from one schema-v2 manifest."""
    manifest = _load_json_object(manifest_path, label="split proof manifest")
    _validate_split_manifest(manifest)
    for name, path in (("opentofu", opentofu_cast_path), ("direct_rpc", direct_rpc_cast_path)):
        if sha256_file(path) != manifest["casts"][name]["sha256"]:
            raise ValueError(f"{name} cast checksum does not match manifest")
    opentofu_output = _cast_output(opentofu_cast_path)
    direct_rpc_output = _cast_output(direct_rpc_cast_path)
    _assert_no_leaks(manifest, opentofu_output + "\n" + direct_rpc_output)
    _validate_opentofu_cast(opentofu_output)
    return _validate_direct_rpc_cast(direct_rpc_output, manifest)


def _wheel_version(wheels: Sequence[Any], distribution: str) -> str:
    normalized = distribution.replace("-", "[_-]")
    pattern = re.compile(rf"{normalized}-(?P<version>[^-]+)-.*\.whl\Z", re.IGNORECASE)
    versions = {
        match.group("version")
        for wheel in wheels
        if isinstance(wheel, str) and (match := pattern.fullmatch(wheel)) is not None
    }
    if len(versions) != 1:
        raise ValueError(f"build provenance does not identify exactly one {distribution} wheel")
    return versions.pop()


def _provenance_source(sources: dict[str, Any], name: str) -> dict[str, Any]:
    source = sources.get(name)
    if not isinstance(source, dict):
        raise ValueError(f"build provenance {name} source must be an object")
    return source


def generate_proof(
    *,
    cast_path: Path,
    build_provenance_path: Path,
    output_path: Path,
    provider_version: str,
    opentofu_archive: str,
    opentofu_archive_sha256: str,
    generated_at: str,
    ci_environment: Mapping[str, str],
) -> dict[str, Any]:
    """Generate schema-v1 proof from checked build provenance and a completed cast."""
    provenance = _load_json_object(build_provenance_path, label="build provenance")
    _assert_hash(opentofu_archive_sha256, label="OpenTofu archive checksum")
    artifacts = provenance.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("build provenance artifacts must be an object")
    provider_source_sha = _assert_sha(provenance.get("provider_repository_head"), label="provider source SHA")
    binary_metadata = artifacts.get("binary")
    if not isinstance(binary_metadata, dict):
        raise ValueError("build provenance binary artifact must be an object")
    relative_binary = binary_metadata.get("path")
    if not isinstance(relative_binary, str):
        raise ValueError("build provenance provider binary path is invalid")
    binary_path = build_provenance_path.parent / relative_binary
    expected_binary_sha = _assert_hash(binary_metadata.get("sha256"), label="provider checksum")
    if sha256_file(binary_path) != expected_binary_sha:
        raise ValueError("provider checksum does not match build provenance")
    sources = provenance.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("build provenance sources must be an object")
    pyvider_source = _provenance_source(sources, "pyvider")
    components_source = _provenance_source(sources, "pyvider-components")
    wheels = provenance.get("packaged_wheels")
    if not isinstance(wheels, list):
        raise ValueError("build provenance has no packaged wheel inventory")
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "ci": {
            "repository": ci_environment.get("GITHUB_REPOSITORY"),
            "run_id": ci_environment.get("GITHUB_RUN_ID"),
            "run_attempt": ci_environment.get("GITHUB_RUN_ATTEMPT"),
            "workflow": ci_environment.get("GITHUB_WORKFLOW"),
        },
        "components": {
            "terraform-provider-pyvider": {
                "version": provider_version,
                "sha": provider_source_sha,
            },
            "pyvider": {
                "version": _wheel_version(wheels, "pyvider"),
                "sha": pyvider_source.get("sha"),
                "archive_sha256": pyvider_source.get("archive_sha256"),
            },
            "pyvider-components": {
                "version": _wheel_version(wheels, "pyvider-components"),
                "sha": components_source.get("sha"),
                "archive_sha256": components_source.get("archive_sha256"),
            },
        },
        "opentofu": {
            "version": OPENTOFU_VERSION,
            "archive": opentofu_archive,
            "archive_sha256": opentofu_archive_sha256,
        },
        "provider_binary": {
            "path": f"dist/{relative_binary}",
            "sha256": expected_binary_sha,
        },
        "commands": COMMANDS,
        "rules": _expected_manifest_rules(),
        "cast": {
            "path": "provider-linting.cast",
            "sha256": sha256_file(cast_path),
        },
    }
    _validate_manifest(manifest)
    cast_output = _cast_output(cast_path)
    _assert_no_leaks(manifest, cast_output)
    _validate_cast(cast_output, manifest)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def generate_split_proof(
    *,
    opentofu_cast_path: Path,
    direct_rpc_cast_path: Path,
    build_provenance_path: Path,
    output_path: Path,
    provider_version: str,
    opentofu_archive: str,
    opentofu_archive_sha256: str,
    generated_at: str,
    ci_environment: Mapping[str, str],
) -> dict[str, Any]:
    """Generate schema-v2 proof from separate OpenTofu and direct-RPC casts."""
    provenance = _load_json_object(build_provenance_path, label="build provenance")
    _assert_hash(opentofu_archive_sha256, label="OpenTofu archive checksum")
    artifacts = provenance.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("build provenance artifacts must be an object")
    provider_source_sha = _assert_sha(provenance.get("provider_repository_head"), label="provider source SHA")
    binary_metadata = artifacts.get("binary")
    if not isinstance(binary_metadata, dict):
        raise ValueError("build provenance binary artifact must be an object")
    relative_binary = binary_metadata.get("path")
    if not isinstance(relative_binary, str):
        raise ValueError("build provenance provider binary path is invalid")
    binary_path = build_provenance_path.parent / relative_binary
    expected_binary_sha = _assert_hash(binary_metadata.get("sha256"), label="provider checksum")
    if sha256_file(binary_path) != expected_binary_sha:
        raise ValueError("provider checksum does not match build provenance")
    sources = provenance.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("build provenance sources must be an object")
    pyvider_source = _provenance_source(sources, "pyvider")
    components_source = _provenance_source(sources, "pyvider-components")
    wheels = provenance.get("packaged_wheels")
    if not isinstance(wheels, list):
        raise ValueError("build provenance has no packaged wheel inventory")
    manifest: dict[str, Any] = {
        "schema_version": 2,
        "generated_at": generated_at,
        "ci": {
            "repository": ci_environment.get("GITHUB_REPOSITORY"),
            "run_id": ci_environment.get("GITHUB_RUN_ID"),
            "run_attempt": ci_environment.get("GITHUB_RUN_ATTEMPT"),
            "workflow": ci_environment.get("GITHUB_WORKFLOW"),
        },
        "components": {
            "terraform-provider-pyvider": {"version": provider_version, "sha": provider_source_sha},
            "pyvider": {
                "version": _wheel_version(wheels, "pyvider"),
                "sha": pyvider_source.get("sha"),
                "archive_sha256": pyvider_source.get("archive_sha256"),
            },
            "pyvider-components": {
                "version": _wheel_version(wheels, "pyvider-components"),
                "sha": components_source.get("sha"),
                "archive_sha256": components_source.get("archive_sha256"),
            },
        },
        "opentofu": {
            "version": OPENTOFU_VERSION,
            "archive": opentofu_archive,
            "archive_sha256": opentofu_archive_sha256,
        },
        "provider_binary": {"path": f"dist/{relative_binary}", "sha256": expected_binary_sha},
        "commands": SPLIT_COMMANDS,
        "rules": _expected_manifest_rules(),
        "casts": {
            name: {"path": path, "sha256": sha256_file(cast_path)}
            for name, path, cast_path in (
                ("opentofu", SPLIT_CASTS["opentofu"], opentofu_cast_path),
                ("direct_rpc", SPLIT_CASTS["direct_rpc"], direct_rpc_cast_path),
            )
        },
    }
    _validate_split_manifest(manifest)
    opentofu_output = _cast_output(opentofu_cast_path)
    direct_rpc_output = _cast_output(direct_rpc_cast_path)
    _assert_no_leaks(manifest, opentofu_output + "\n" + direct_rpc_output)
    _validate_opentofu_cast(opentofu_output)
    _validate_direct_rpc_cast(direct_rpc_output, manifest)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def github_environment() -> dict[str, str]:
    return {
        name: os.environ[name]
        for name in ("GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_WORKFLOW")
        if name in os.environ
    }
