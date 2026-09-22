# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared schema, generation, and verification for provider-linting proof."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from typing import Any

SCHEMA_VERSION = 3
LEGACY_SCHEMA_VERSION = 1
OPENTOFU_VERSION = "1.13.0-rc1"
LEGACY_OPENTOFU_VERSION = "1.13.0-beta1"
TOFUSOUP_VERSION = "0.8.2"
PYPI_REGISTRY = "https://pypi.org/simple"
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
FILM_COMMANDS = {
    "opentofu": SPLIT_COMMANDS["opentofu"],
    "direct": SPLIT_COMMANDS["direct_rpc"],
    "walkthrough": [
        f"uv tool install --refresh --quiet tofusoup=={TOFUSOUP_VERSION}",
        "soup --version",
        (
            "provider=$(uv run python ci/provider-linting-artifact-path.py "
            "dist/provider-linting-build-provenance.json)"
        ),
        'tofu=$(ci/install-opentofu-beta.sh --version 1.13.0-rc1 --cache-dir "$PWD/.cache/opentofu-prerelease")',
        '"$tofu" version',
        (
            "soup lint tests/e2e/provider-linting/lint.soup.toml "
            '--provider "$provider" '
            '--opentofu "$tofu" --lane opentofu'
        ),
        ('soup lint tests/e2e/provider-linting/lint.soup.toml --provider "$provider" --lane direct'),
    ],
    "tutorial": [
        "uv sync --frozen",
        "uv run pytest tests/test_linting.py -q",
        "uv run flavor pack --manifest pyproject.toml",
        (
            "uvx --from tofusoup==0.8.2 soup lint lint.soup.toml "
            '--provider "$PWD/dist/terraform-provider-mycloud" --lane direct'
        ),
        "./install-opentofu.sh 1.13.0-rc1",
        '"$opentofu_rc1" version',
        (
            "uvx --from tofusoup==0.8.2 soup lint lint.soup.toml "
            '--provider "$PWD/dist/terraform-provider-mycloud" '
            '--opentofu "$opentofu_rc1" --lane opentofu'
        ),
    ],
}
LEGACY_FILM_COMMANDS = {
    "opentofu": SPLIT_COMMANDS["opentofu"],
    "direct": SPLIT_COMMANDS["direct_rpc"],
    "walkthrough": [
        "uv tool install --refresh tofusoup==0.8.0",
        "soup --version",
        *SPLIT_COMMANDS["opentofu"],
        *SPLIT_COMMANDS["direct_rpc"],
    ],
}
FILM_CASTS = {
    "opentofu": "provider-linting-opentofu.cast",
    "direct": "provider-linting-direct.cast",
    "walkthrough": "provider-linting-walkthrough.cast",
    "tutorial": "tutorial-part7-provider-linting.cast",
}
LEGACY_FILM_CASTS = {name: path for name, path in FILM_CASTS.items() if name != "tutorial"}
FILM_DURATION_RANGES = {
    "opentofu": (30.0, 36.0),
    "direct": (33.0, 39.0),
    "walkthrough": (36.0, 40.0),
    "tutorial": (36.0, 40.0),
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
    "Part 7 — author and verify a provider lint rule",
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


def _cast_duration(path: Path) -> float:
    """Return the terminal elapsed time from a checked asciinema v2 cast."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 2:
            raise ValueError("empty cast")
        _validate_cast_header(json.loads(lines[0]))
        timestamps: list[float] = []
        for line in lines[1:]:
            event = json.loads(line)
            if (
                not isinstance(event, list)
                or len(event) != 3
                or isinstance(event[0], bool)
                or not isinstance(event[0], (int, float))
                or event[1] != "o"
                or not isinstance(event[2], str)
            ):
                raise ValueError("invalid cast event")
            timestamp = float(event[0])
            if not math.isfinite(timestamp):
                raise ValueError("invalid cast event timestamp")
            timestamps.append(timestamp)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cast") from exc
    return max(timestamps)


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
            if "archive_sha256" in component:
                _assert_hash(component.get("archive_sha256"), label=f"{name} archive checksum")
            else:
                required = {"version", "sha", "tag", "registry", "wheel", "wheel_sha256"}
                if set(component) != required:
                    raise ValueError(f"invalid public wheel metadata for {name}")
                if component["registry"] != PYPI_REGISTRY:
                    raise ValueError(f"{name} does not use the public PyPI registry")
                if component["tag"] != f"v{component['version']}":
                    raise ValueError(f"{name} tag does not match its version")
                wheel = component["wheel"]
                normalized = name.replace("-", "[_-]")
                if (
                    not isinstance(wheel, str)
                    or re.fullmatch(
                        rf"{normalized}-{re.escape(component['version'])}-.*\.whl", wheel, re.IGNORECASE
                    )
                    is None
                ):
                    raise ValueError(f"{name} wheel does not match its version")
                _assert_hash(component["wheel_sha256"], label=f"{name} wheel checksum")


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
    version = value.get("version")
    if version not in {OPENTOFU_VERSION, LEGACY_OPENTOFU_VERSION}:
        raise ValueError(f"OpenTofu version must be {OPENTOFU_VERSION}")
    archive = value.get("archive")
    if not isinstance(archive, str) or not archive.startswith(f"tofu_{version}_"):
        raise ValueError("OpenTofu archive does not match the pinned prerelease")
    _assert_hash(value.get("archive_sha256"), label="OpenTofu archive checksum")


def _validate_provider_binary(value: Any) -> None:
    if not isinstance(value, dict) or set(value) not in (
        {"path", "sha256"},
        {"path", "sha256", "platform"},
    ):
        raise ValueError("provider binary metadata is invalid")
    path = value["path"]
    if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
        raise ValueError("provider binary path must be repository-relative")
    _assert_hash(value["sha256"], label="provider checksum")
    if "platform" in value and (
        not isinstance(value["platform"], str)
        or re.fullmatch(r"(?:linux|darwin|windows)_(?:amd64|arm64)", value["platform"]) is None
    ):
        raise ValueError("provider binary platform is invalid")


def checked_release_candidate(value: Mapping[str, Any], *, binary_platform: str) -> dict[str, Any]:
    """Validate the named matrix archive that supplied the proved binary."""
    required = {"github_artifact", "archive", "platform", "sha256"}
    if set(value) != required:
        raise ValueError("release candidate metadata is invalid")
    platform_value = value.get("platform")
    if platform_value != binary_platform:
        raise ValueError("release candidate platform does not match provider binary")
    if value.get("github_artifact") != f"provider-{platform_value}":
        raise ValueError("release candidate artifact does not match its platform")
    archive = value.get("archive")
    if not isinstance(archive, str) or not archive.endswith(f"_{platform_value}.zip"):
        raise ValueError("release candidate archive does not match its platform")
    _assert_hash(value.get("sha256"), label="release candidate checksum")
    return dict(value)


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


def _validate_film_casts(value: Any, *, legacy_release: bool) -> None:
    expected_casts = LEGACY_FILM_CASTS if legacy_release else FILM_CASTS
    if not isinstance(value, dict) or set(value) != set(expected_casts):
        raise ValueError("film cast metadata is incomplete")
    for name, expected_path in expected_casts.items():
        metadata = value[name]
        if not isinstance(metadata, dict) or set(metadata) != {"path", "sha256"}:
            raise ValueError("film cast metadata is invalid")
        if metadata["path"] != expected_path:
            raise ValueError("film cast metadata has an invalid path")
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
    if manifest["schema_version"] != LEGACY_SCHEMA_VERSION:
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
    if set(manifest) not in (required, required | {"release_candidate"}):
        raise ValueError("manifest schema keys do not match version 2")
    if manifest["schema_version"] != 2:
        raise ValueError("manifest schema version must be 2")
    _validate_generated_at(manifest["generated_at"])
    if not isinstance(manifest["ci"], dict):
        raise ValueError("ci identity must be an object")
    _validate_components(manifest["components"])
    _validate_opentofu(manifest["opentofu"])
    _validate_provider_binary(manifest["provider_binary"])
    if "release_candidate" in manifest:
        checked_release_candidate(
            manifest["release_candidate"],
            binary_platform=manifest["provider_binary"].get("platform", "linux_amd64"),
        )
    if manifest["commands"] != SPLIT_COMMANDS:
        raise ValueError("command catalog does not match the split proof")
    _validate_rules(manifest["rules"])
    _validate_split_casts(manifest["casts"])


def _validate_film_manifest(manifest: dict[str, Any]) -> None:
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
    if set(manifest) not in (required, required | {"release_candidate"}):
        raise ValueError("manifest schema keys do not match version 3")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("manifest schema version must be 3")
    _validate_generated_at(manifest["generated_at"])
    if not isinstance(manifest["ci"], dict):
        raise ValueError("ci identity must be an object")
    _validate_components(manifest["components"])
    _validate_opentofu(manifest["opentofu"])
    _validate_provider_binary(manifest["provider_binary"])
    if "release_candidate" in manifest:
        checked_release_candidate(
            manifest["release_candidate"],
            binary_platform=manifest["provider_binary"].get("platform", "linux_amd64"),
        )
    commands = manifest["commands"]
    legacy_release = (
        manifest["components"]["terraform-provider-pyvider"]["version"] == "0.5.0"
        and commands == LEGACY_FILM_COMMANDS
    )
    if commands != FILM_COMMANDS and not (legacy_release and commands == LEGACY_FILM_COMMANDS):
        raise ValueError("command catalog does not match the checked proof films")
    _validate_rules(manifest["rules"])
    _validate_film_casts(manifest["casts"], legacy_release=legacy_release)


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


def _opentofu_status_statement(manifest: Mapping[str, Any]) -> str:
    opentofu = manifest.get("opentofu", {})
    if opentofu.get("version") == LEGACY_OPENTOFU_VERSION:
        return "OpenTofu native linting: valid"
    return "OpenTofu experimental lint validation: valid"


def _validate_opentofu_cast(
    output: str, *, manifest: Mapping[str, Any], require_four_paths: bool = False
) -> None:
    for command in SPLIT_COMMANDS["opentofu"]:
        if f"$ {command}" not in output:
            raise ValueError(f"missing command from OpenTofu recording: {command}")
    statements: tuple[str, ...] = (
        "Direct provider validation: not requested",
        _opentofu_status_statement(manifest),
        "Experimental linting enabled",
    )
    if require_four_paths:
        statements += (
            "OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)",
        )
    for statement in statements:
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


def _validate_film_duration(lane: str, path: Path) -> None:
    lower, upper = FILM_DURATION_RANGES[lane]
    duration = _cast_duration(path)
    if not lower <= duration <= upper:
        raise ValueError(f"{lane} cast duration must be between {lower:g} and {upper:g} seconds")


def _validate_walkthrough_cast(output: str, manifest: Mapping[str, Any]) -> None:
    for command in manifest["commands"]["walkthrough"]:
        if f"$ {command}" not in output:
            raise ValueError(f"missing command from walkthrough recording: {command}")
    for statement in (
        _opentofu_status_statement(manifest),
        "Direct provider validation: 7/7 cases",
    ):
        if statement not in output:
            raise ValueError(f"missing proof statement from walkthrough recording: {statement}")
    if "run-provider-linting-rpcs.py" in output:
        raise ValueError("walkthrough recording contains an internal proof command")


def _validate_tutorial_cast(output: str, manifest: Mapping[str, Any]) -> None:
    for command in manifest["commands"]["tutorial"]:
        if f"$ {command}" not in output:
            raise ValueError(f"missing command from tutorial recording: {command}")
    for statement in (
        "Part 7: author and verify one provider lint rule.",
        "9 passed",
        "Direct provider validation: 1/1 cases",
        "OpenTofu v1.13.0-rc1",
        "OpenTofu experimental lint validation: valid",
        "example/mycloud:production-name",
    ):
        if statement not in output:
            raise ValueError(f"missing proof statement from tutorial recording: {statement}")
    if "PYVIDER_CONFORMANCE_PSP" in output or "PYVIDER_OPENTOFU_BINARY" in output:
        raise ValueError("tutorial recording contains an internal proof variable")
    if "run-provider-linting-rpcs.py" in output:
        raise ValueError("tutorial recording contains an internal proof command")


def _validate_film_opentofu_cast(output: str, manifest: Mapping[str, Any]) -> None:
    _validate_opentofu_cast(output, manifest=manifest, require_four_paths=True)
    expected_version = manifest["opentofu"]["version"]
    if f"OpenTofu v{expected_version}" not in output.splitlines():
        raise ValueError(f"cast does not show the exact OpenTofu version v{expected_version}")
    if f"$ {FILM_COMMANDS['direct'][0]}" in output or "Direct provider validation: 7/7 cases" in output:
        raise ValueError("OpenTofu recording contains direct provider evidence")


def verify_proof(manifest_path: Path, cast_path: Path) -> list[str]:
    """Validate the manifest and every semantic assertion in the complete cast."""
    manifest = _load_json_object(manifest_path, label="proof manifest")
    _validate_manifest(manifest)
    if sha256_file(cast_path) != manifest["cast"]["sha256"]:
        raise ValueError("cast checksum does not match manifest")
    output = _cast_output(cast_path)
    _assert_no_leaks(manifest, output)
    return _validate_cast(output, manifest)


def verify_split_proof(
    manifest_path: Path,
    opentofu_cast_path: Path,
    direct_rpc_cast_path: Path,
    walkthrough_cast_path: Path | None = None,
    tutorial_cast_path: Path | None = None,
) -> list[str]:
    """Validate legacy split casts or the schema-v3 public proof films."""
    if walkthrough_cast_path is not None:
        return verify_film_proof(
            manifest_path,
            opentofu_cast_path,
            direct_rpc_cast_path,
            walkthrough_cast_path,
            tutorial_cast_path,
        )
    manifest = _load_json_object(manifest_path, label="split proof manifest")
    _validate_split_manifest(manifest)
    for name, path in (("opentofu", opentofu_cast_path), ("direct_rpc", direct_rpc_cast_path)):
        if sha256_file(path) != manifest["casts"][name]["sha256"]:
            raise ValueError(f"{name} cast checksum does not match manifest")
    opentofu_output = _cast_output(opentofu_cast_path)
    direct_rpc_output = _cast_output(direct_rpc_cast_path)
    _assert_no_leaks(manifest, opentofu_output + "\n" + direct_rpc_output)
    _validate_opentofu_cast(opentofu_output, manifest=manifest)
    return _validate_direct_rpc_cast(direct_rpc_output, manifest)


def verify_film_proof(
    manifest_path: Path,
    opentofu_cast_path: Path,
    direct_cast_path: Path,
    walkthrough_cast_path: Path,
    tutorial_cast_path: Path | None = None,
) -> list[str]:
    """Validate all release-blocking schema-v3 public proof films."""
    manifest = _load_json_object(manifest_path, label="proof manifest")
    _validate_film_manifest(manifest)
    legacy_release = (
        manifest["components"]["terraform-provider-pyvider"]["version"] == "0.5.0"
        and manifest["commands"] == LEGACY_FILM_COMMANDS
    )
    if not legacy_release and tutorial_cast_path is None:
        raise ValueError("tutorial cast is required for provider 0.6 proof")
    paths = {
        "opentofu": opentofu_cast_path,
        "direct": direct_cast_path,
        "walkthrough": walkthrough_cast_path,
    }
    if tutorial_cast_path is not None:
        paths["tutorial"] = tutorial_cast_path
    for lane, path in paths.items():
        if sha256_file(path) != manifest["casts"][lane]["sha256"]:
            raise ValueError(f"{lane} cast checksum does not match manifest")
    outputs = {lane: _cast_output(path) for lane, path in paths.items()}
    _assert_no_leaks(manifest, "\n".join(outputs.values()))
    for lane in paths:
        if "run-provider-linting-rpcs.py" in outputs[lane]:
            raise ValueError(f"{lane} recording contains an internal proof command")
    _validate_film_opentofu_cast(outputs["opentofu"], manifest)
    rule_ids = _validate_direct_rpc_cast(outputs["direct"], manifest)
    _validate_walkthrough_cast(outputs["walkthrough"], manifest)
    if "tutorial" in outputs:
        _validate_tutorial_cast(outputs["tutorial"], manifest)
    for lane, path in paths.items():
        _validate_film_duration(lane, path)
    return rule_ids


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


def public_dependency_component(record: Mapping[str, Any], *, name: str) -> dict[str, Any]:
    """Translate checked schema-v2 build provenance into proof metadata."""
    version = record.get("version")
    tag = record.get("tag")
    registry = record.get("registry")
    wheel = record.get("wheel")
    if not isinstance(version, str) or not version:
        raise ValueError(f"build provenance {name} version is invalid")
    if tag != f"v{version}":
        raise ValueError(f"build provenance {name} tag does not match its version")
    if registry != PYPI_REGISTRY:
        raise ValueError(f"build provenance {name} must use the public PyPI registry")
    normalized = name.replace("-", "[_-]")
    if (
        not isinstance(wheel, str)
        or re.fullmatch(rf"{normalized}-{re.escape(version)}-.*\.whl", wheel, re.IGNORECASE) is None
    ):
        raise ValueError(f"build provenance {name} wheel does not match its version")
    commit = _assert_sha(record.get("commit"), label=f"{name} tag commit")
    wheel_sha = _assert_hash(record.get("sha256"), label=f"{name} wheel checksum")
    return {
        "version": version,
        "sha": commit,
        "tag": tag,
        "registry": registry,
        "wheel": wheel,
        "wheel_sha256": wheel_sha,
    }


def _proof_dependency_components(provenance: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read public schema-v2 dependencies or the legacy source archive shape."""
    dependencies = provenance.get("dependencies")
    if dependencies is not None:
        if provenance.get("schema_version") != 2 or not isinstance(dependencies, dict):
            raise ValueError("public build provenance must use schema version 2")
        return (
            public_dependency_component(_provenance_source(dependencies, "pyvider"), name="pyvider"),
            public_dependency_component(
                _provenance_source(dependencies, "pyvider-components"), name="pyvider-components"
            ),
        )

    sources = provenance.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("build provenance dependencies must be an object")
    pyvider_source = _provenance_source(sources, "pyvider")
    components_source = _provenance_source(sources, "pyvider-components")
    wheels = provenance.get("packaged_wheels")
    if not isinstance(wheels, list):
        raise ValueError("build provenance has no packaged wheel inventory")
    return (
        {
            "version": _wheel_version(wheels, "pyvider"),
            "sha": pyvider_source.get("sha"),
            "archive_sha256": pyvider_source.get("archive_sha256"),
        },
        {
            "version": _wheel_version(wheels, "pyvider-components"),
            "sha": components_source.get("sha"),
            "archive_sha256": components_source.get("archive_sha256"),
        },
    )


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
    dependencies = provenance.get("dependencies")
    if dependencies is not None:
        if provenance.get("schema_version") != 2 or not isinstance(dependencies, dict):
            raise ValueError("public build provenance must use schema version 2")
        pyvider_component = public_dependency_component(
            _provenance_source(dependencies, "pyvider"), name="pyvider"
        )
        components_component = public_dependency_component(
            _provenance_source(dependencies, "pyvider-components"), name="pyvider-components"
        )
    else:
        # Legacy schema-v1 proof remains readable so previously published proof
        # can still be verified. New release proof always takes the branch above.
        sources = provenance.get("sources")
        if not isinstance(sources, dict):
            raise ValueError("build provenance dependencies must be an object")
        pyvider_source = _provenance_source(sources, "pyvider")
        components_source = _provenance_source(sources, "pyvider-components")
        wheels = provenance.get("packaged_wheels")
        if not isinstance(wheels, list):
            raise ValueError("build provenance has no packaged wheel inventory")
        pyvider_component = {
            "version": _wheel_version(wheels, "pyvider"),
            "sha": pyvider_source.get("sha"),
            "archive_sha256": pyvider_source.get("archive_sha256"),
        }
        components_component = {
            "version": _wheel_version(wheels, "pyvider-components"),
            "sha": components_source.get("sha"),
            "archive_sha256": components_source.get("archive_sha256"),
        }
    manifest: dict[str, Any] = {
        "schema_version": LEGACY_SCHEMA_VERSION,
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
            "pyvider": pyvider_component,
            "pyvider-components": components_component,
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


def _build_split_manifest(
    *,
    opentofu_cast_path: Path,
    direct_rpc_cast_path: Path,
    build_provenance_path: Path,
    provider_version: str,
    opentofu_archive: str,
    opentofu_archive_sha256: str,
    generated_at: str,
    ci_environment: Mapping[str, str],
) -> dict[str, Any]:
    """Assemble schema-v2 metadata without publishing it."""
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
    pyvider_component, components_component = _proof_dependency_components(provenance)
    binary_platform = binary_metadata.get("platform")
    provider_binary = {"path": f"dist/{relative_binary}", "sha256": expected_binary_sha}
    release_candidate = provenance.get("release_candidate")
    if release_candidate is not None:
        if not isinstance(binary_platform, str) or not isinstance(release_candidate, dict):
            raise ValueError("build provenance release candidate is invalid")
        provider_binary["platform"] = binary_platform
        release_candidate = checked_release_candidate(release_candidate, binary_platform=binary_platform)
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
            "pyvider": pyvider_component,
            "pyvider-components": components_component,
        },
        "opentofu": {
            "version": OPENTOFU_VERSION,
            "archive": opentofu_archive,
            "archive_sha256": opentofu_archive_sha256,
        },
        "provider_binary": provider_binary,
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
    if release_candidate is not None:
        manifest["release_candidate"] = release_candidate
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
    manifest = _build_split_manifest(
        opentofu_cast_path=opentofu_cast_path,
        direct_rpc_cast_path=direct_rpc_cast_path,
        build_provenance_path=build_provenance_path,
        provider_version=provider_version,
        opentofu_archive=opentofu_archive,
        opentofu_archive_sha256=opentofu_archive_sha256,
        generated_at=generated_at,
        ci_environment=ci_environment,
    )
    _validate_split_manifest(manifest)
    opentofu_output = _cast_output(opentofu_cast_path)
    direct_rpc_output = _cast_output(direct_rpc_cast_path)
    _assert_no_leaks(manifest, opentofu_output + "\n" + direct_rpc_output)
    _validate_opentofu_cast(opentofu_output, manifest=manifest)
    _validate_direct_rpc_cast(direct_rpc_output, manifest)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _write_json_atomically(path: Path, value: Mapping[str, Any]) -> None:
    temporary: Path | None = None
    try:
        content = json.dumps(value, indent=2, sort_keys=True) + "\n"
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=f".{path.name}.", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def generate_film_proof(
    *,
    opentofu_cast_path: Path,
    direct_cast_path: Path,
    walkthrough_cast_path: Path,
    tutorial_cast_path: Path | None = None,
    build_provenance_path: Path,
    output_path: Path,
    provider_version: str,
    opentofu_archive: str,
    opentofu_archive_sha256: str,
    generated_at: str,
    ci_environment: Mapping[str, str],
) -> dict[str, Any]:
    """Generate a schema-v3 manifest for the four paced public proof films."""
    legacy = _build_split_manifest(
        opentofu_cast_path=opentofu_cast_path,
        direct_rpc_cast_path=direct_cast_path,
        build_provenance_path=build_provenance_path,
        provider_version=provider_version,
        opentofu_archive=opentofu_archive,
        opentofu_archive_sha256=opentofu_archive_sha256,
        generated_at=generated_at,
        ci_environment=ci_environment,
    )
    if provider_version != "0.5.0" and tutorial_cast_path is None:
        raise ValueError("tutorial cast is required for provider 0.6 proof")
    cast_paths: tuple[tuple[str, Path], ...] = (
        ("opentofu", opentofu_cast_path),
        ("direct", direct_cast_path),
        ("walkthrough", walkthrough_cast_path),
    )
    if tutorial_cast_path is not None:
        cast_paths += (("tutorial", tutorial_cast_path),)
    manifest = legacy | {
        "schema_version": SCHEMA_VERSION,
        "commands": FILM_COMMANDS,
        "casts": {lane: {"path": FILM_CASTS[lane], "sha256": sha256_file(path)} for lane, path in cast_paths},
    }
    _validate_film_manifest(manifest)
    outputs = {lane: _cast_output(path) for lane, path in cast_paths}
    _assert_no_leaks(manifest, "\n".join(outputs.values()))
    for lane, path in cast_paths:
        _validate_film_duration(lane, path)
    _validate_film_opentofu_cast(outputs["opentofu"], manifest)
    _validate_direct_rpc_cast(outputs["direct"], manifest)
    _validate_walkthrough_cast(outputs["walkthrough"], manifest)
    if "tutorial" in outputs:
        _validate_tutorial_cast(outputs["tutorial"], manifest)
    _write_json_atomically(output_path, manifest)
    return manifest


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def github_environment() -> dict[str, str]:
    return {
        name: os.environ[name]
        for name in ("GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_WORKFLOW")
        if name in os.environ
    }
