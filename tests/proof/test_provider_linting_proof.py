# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contracts for the checked provider-linting recording and manifest."""

from __future__ import annotations

import hashlib
import importlib.util
from itertools import pairwise
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
PACER = ROOT / "ci" / "pace-provider-linting-cast.py"
PROOF_LIBRARY = ROOT / "ci" / "provider_linting_proof.py"

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
WALKTHROUGH_COMMANDS = [
    "uv tool install --refresh tofusoup==0.8.2",
    "soup --version",
    *OPENTOFU_COMMANDS,
    DIRECT_RPC_COMMAND,
]
FILM_CASTS = {
    "opentofu": "provider-linting-opentofu.cast",
    "direct": "provider-linting-direct.cast",
    "walkthrough": "provider-linting-walkthrough.cast",
}
FILM_COMMANDS = {
    "opentofu": OPENTOFU_COMMANDS,
    "direct": [DIRECT_RPC_COMMAND],
    "walkthrough": WALKTHROUGH_COMMANDS,
}
FILM_DURATION_RANGES = {
    "opentofu": (30, 36),
    "direct": (33, 39),
    "walkthrough": (36, 40),
}
FILM_CAPTURE_GEOMETRIES = {
    "opentofu": (110, 26),
    "direct": (110, 26),
    "walkthrough": (110, 26),
}


def test_public_film_pace_profiles_are_readable_and_fit_the_short_showcase_window() -> None:
    """Every public proof film stays observable without becoming a long demo."""
    pacer = load_script(PACER, "provider_linting_pacer_showcase_window")
    verifier = load_script(PROOF_LIBRARY, "provider_linting_proof_showcase_window")
    expected = {
        "opentofu": {"target": 34.0, "range": (30.0, 36.0)},
        "direct": {"target": 37.0, "range": (33.0, 39.0)},
        "walkthrough": {"target": 40.0, "range": (36.0, 40.0)},
    }

    assert {
        lane: {"target": profile.target_seconds, "range": verifier.FILM_DURATION_RANGES[lane]}
        for lane, profile in pacer.PROFILES.items()
    } == expected


def test_pacer_keeps_every_visible_walkthrough_line_on_screen_for_at_least_1_2_seconds() -> None:
    """Bridge, command, and status lines must remain observable in the short film."""
    pacer = load_script(PACER, "provider_linting_pacer_visible_dwell")
    output = "".join(
        [
            *(f"$ public command {index}\n" for index in range(6)),
            *(f"warning: checked finding {index}\n" for index in range(10)),
            *(f"status: bridge line {index}\n" for index in range(11)),
        ]
    )

    timestamps = [timestamp for _chunk, timestamp in pacer.pace_output(output, pacer.PROFILES["walkthrough"])]
    visible_dwells = [later - earlier for earlier, later in pairwise(timestamps)]

    assert timestamps[-1] == 40.0
    assert min(round(dwell, 3) for dwell in visible_dwells) >= 1.2


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
    assert (
        "OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)"
    ) in native_demo
    assert "show_command 'tofu version'" in native_demo
    assert '"$PYVIDER_OPENTOFU_BINARY" version' in native_demo
    assert "run-provider-linting-rpcs.py" not in direct_demo + native_demo


def load_script(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
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


def film_cast_text(lane: str) -> str:
    commands = FILM_COMMANDS[lane]
    if lane == "opentofu":
        statements = [
            "OpenTofu v1.13.0-beta1",
            "Direct provider validation: not requested",
            "OpenTofu native linting: valid",
            "Experimental linting enabled",
            "OpenTofu core proof: 4/7 provider validation paths (provider, resource, data-source, ephemeral)",
        ]
    elif lane == "direct":
        statements = [
            "Direct provider validation: 7/7 cases",
            *(rule_id for rule_id, _kind, _observed_via, _attribute in RULES),
        ]
    else:
        statements = [
            "Public walkthrough: OpenTofu native and direct provider validation",
            "OpenTofu native linting: valid",
            "Direct provider validation: 7/7 cases",
        ]
    return "\n".join([*(f"$ {command}" for command in commands), *statements]) + "\n"


def write_film_cast(path: Path, *, lane: str, timestamp: float = 0.5, text: str | None = None) -> None:
    write_split_cast(
        path,
        title={
            "opentofu": "Pyvider linting — OpenTofu demonstration",
            "direct": "Pyvider linting — direct provider validation",
            "walkthrough": "Pyvider provider-native linting proof",
        }[lane],
        text=text or film_cast_text(lane),
    )
    if timestamp != 0.5:
        lines = path.read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[1])
        event[0] = timestamp
        path.write_text("\n".join([lines[0], json.dumps(event)]) + "\n", encoding="utf-8")


def film_manifest_for(casts: dict[str, Path]) -> dict[str, Any]:
    """Schema-v3 fixture; keep manifest_for() as the legacy-v1 compatibility fixture."""
    manifest = manifest_for(casts["opentofu"])
    manifest["schema_version"] = 3
    manifest["commands"] = FILM_COMMANDS
    manifest.pop("cast")
    manifest["casts"] = {
        lane: {
            "path": FILM_CASTS[lane],
            "sha256": hashlib.sha256(cast.read_bytes()).hexdigest(),
        }
        for lane, cast in casts.items()
    }
    return manifest


def write_film_proof(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    casts = {lane: tmp_path / filename for lane, filename in FILM_CASTS.items()}
    for lane, cast in casts.items():
        lower, upper = FILM_DURATION_RANGES[lane]
        write_film_cast(cast, lane=lane, timestamp=(lower + upper) / 2)
    manifest = tmp_path / "provider-linting-proof.json"
    manifest.write_text(json.dumps(film_manifest_for(casts), indent=2) + "\n", encoding="utf-8")
    return manifest, casts


def verify_films(module: ModuleType, manifest: Path, casts: dict[str, Path]) -> None:
    module.verify_split_proof(manifest, casts["opentofu"], casts["direct"], casts["walkthrough"])


def test_provider_0_6_proof_requires_beta_validation_wording() -> None:
    module = load_script(PROOF_LIBRARY, "provider_linting_proof_beta_wording")
    manifest = {"components": {"terraform-provider-pyvider": {"version": "0.6.0"}}}
    output = "\n".join(
        [
            *(f"$ {command}" for command in OPENTOFU_COMMANDS),
            "Direct provider validation: not requested",
            "OpenTofu beta validation: valid",
            "Experimental linting enabled",
        ]
    )

    module._validate_opentofu_cast(output, manifest=manifest)
    with pytest.raises(ValueError, match="OpenTofu beta validation"):
        module._validate_opentofu_cast(
            output.replace("OpenTofu beta validation", "OpenTofu native linting"),
            manifest=manifest,
        )


def write_film_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def refresh_film_cast_hash(manifest: dict[str, Any], lane: str, cast: Path) -> None:
    manifest["casts"][lane]["sha256"] = hashlib.sha256(cast.read_bytes()).hexdigest()


def write_cast_events(path: Path, events: list[list[Any]]) -> None:
    header = {
        "version": 2,
        "width": 120,
        "height": 40,
        "timestamp": 1_789_344_000,
        "title": "Pyvider provider-native linting proof",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }
    path.write_text(
        "\n".join([json.dumps(header), *(json.dumps(event) for event in events)]) + "\n",
        encoding="utf-8",
    )


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


def test_schema_v3_fixture_declares_three_public_proof_films(tmp_path: Path) -> None:
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))

    assert data["schema_version"] == 3
    assert set(data["casts"]) == {"opentofu", "direct", "walkthrough"}
    assert data["commands"] == FILM_COMMANDS
    for lane, cast in casts.items():
        assert data["casts"][lane] == {
            "path": cast.name,
            "sha256": hashlib.sha256(cast.read_bytes()).hexdigest(),
        }


@pytest.mark.parametrize("lane", tuple(FILM_CASTS))
def test_checked_schema_v3_films_use_the_canonical_compact_capture_geometry(lane: str) -> None:
    """The public film viewport is capture metadata, never a site-side crop."""
    header = json.loads((ROOT / FILM_CASTS[lane]).read_text(encoding="utf-8").splitlines()[0])

    assert (header["width"], header["height"]) == FILM_CAPTURE_GEOMETRIES[lane]


def test_schema_v3_proof_accepts_an_unmodified_valid_three_film_fixture(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_valid")
    manifest, casts = write_film_proof(tmp_path)

    verify_films(verifier, manifest, casts)


@pytest.mark.parametrize(
    ("missing_kind", "lane"),
    [
        ("cast", "opentofu"),
        ("cast", "direct"),
        ("cast", "walkthrough"),
        ("hash", "opentofu"),
        ("hash", "direct"),
        ("hash", "walkthrough"),
    ],
)
def test_schema_v3_proof_requires_each_checked_cast_and_hash(
    tmp_path: Path, missing_kind: str, lane: str
) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_metadata")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if missing_kind == "cast":
        data["casts"].pop(lane)
    else:
        data["casts"][lane].pop("sha256")
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="film cast metadata"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize("lane", tuple(FILM_CASTS))
def test_schema_v3_proof_rejects_a_tampered_checked_cast_checksum(tmp_path: Path, lane: str) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_tampered_cast")
    manifest, casts = write_film_proof(tmp_path)
    with casts[lane].open("a", encoding="utf-8") as stream:
        stream.write(json.dumps([FILM_DURATION_RANGES[lane][1], "o", "tampered"]) + "\n")

    with pytest.raises(ValueError, match="cast checksum"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize("lane", tuple(FILM_COMMANDS))
def test_schema_v3_proof_requires_exact_public_command_catalog(tmp_path: Path, lane: str) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_commands")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["commands"][lane][0] = "public command intentionally changed"
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="command catalog"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize(
    ("lane", "command"),
    [(lane, command) for lane, commands in FILM_COMMANDS.items() for command in commands],
)
def test_schema_v3_checked_films_require_each_exact_public_command(
    tmp_path: Path, lane: str, command: str
) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_cast_commands")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    write_film_cast(
        casts[lane],
        lane=lane,
        text=film_cast_text(lane).replace(f"$ {command}", "$ command intentionally omitted"),
    )
    refresh_film_cast_hash(data, lane, casts[lane])
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="missing command"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize("lane", tuple(FILM_CASTS))
def test_schema_v3_proof_rejects_internal_rpc_driver_in_every_checked_film(tmp_path: Path, lane: str) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_internal_command")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    write_film_cast(
        casts[lane],
        lane=lane,
        text=film_cast_text(lane) + "$ uv run python ci/run-provider-linting-rpcs.py\n",
    )
    refresh_film_cast_hash(data, lane, casts[lane])
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="internal proof command"):
        verify_films(verifier, manifest, casts)


def test_schema_v3_opentofu_film_rejects_direct_provider_evidence(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_native_only")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    write_film_cast(
        casts["opentofu"],
        lane="opentofu",
        text=film_cast_text("opentofu") + f"$ {DIRECT_RPC_COMMAND}\nDirect provider validation: 7/7 cases\n",
    )
    refresh_film_cast_hash(data, "opentofu", casts["opentofu"])
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="direct provider evidence"):
        verify_films(verifier, manifest, casts)


def test_schema_v3_opentofu_film_requires_the_pinned_beta_version(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_beta_version")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    write_film_cast(
        casts["opentofu"],
        lane="opentofu",
        text=film_cast_text("opentofu").replace("OpenTofu v1.13.0-beta1\n", ""),
    )
    refresh_film_cast_hash(data, "opentofu", casts["opentofu"])
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="exact OpenTofu version"):
        verify_films(verifier, manifest, casts)


def test_schema_v3_opentofu_film_rejects_a_hash_refreshed_beta10_version(tmp_path: Path) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_beta10")
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    write_film_cast(
        casts["opentofu"],
        lane="opentofu",
        text=film_cast_text("opentofu").replace("OpenTofu v1.13.0-beta1\n", "OpenTofu v1.13.0-beta10\n"),
    )
    refresh_film_cast_hash(data, "opentofu", casts["opentofu"])
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="exact OpenTofu version"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize(
    ("lane", "timestamp"),
    [
        ("opentofu", 29),
        ("opentofu", 37),
        ("direct", 32),
        ("direct", 40),
        ("walkthrough", 35),
        ("walkthrough", 41),
    ],
)
def test_schema_v3_proof_rejects_out_of_range_film_duration(
    tmp_path: Path, lane: str, timestamp: float
) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_duration")
    manifest, casts = write_film_proof(tmp_path)
    write_film_cast(casts[lane], lane=lane, timestamp=timestamp)
    data = film_manifest_for(casts)
    write_film_manifest(manifest, data)

    with pytest.raises(ValueError, match="duration"):
        verify_films(verifier, manifest, casts)


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ("byte", "direct cast checksum"),
        ("duration", "direct cast duration"),
        ("command", "missing command from walkthrough recording"),
    ],
)
def test_schema_v3_verifier_cli_rejects_each_checked_film_mutation_independently(
    tmp_path: Path, mutation: str, expected_error: str
) -> None:
    """Exercise the public verifier command for independent v3 evidence changes."""
    manifest, casts = write_film_proof(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))

    if mutation == "byte":
        casts["direct"].write_bytes(casts["direct"].read_bytes() + b" ")
    elif mutation == "duration":
        write_film_cast(casts["direct"], lane="direct", timestamp=49)
        write_film_manifest(manifest, film_manifest_for(casts))
    else:
        write_film_cast(
            casts["walkthrough"],
            lane="walkthrough",
            text=film_cast_text("walkthrough").replace("$ soup --version", "$ command omitted"),
        )
        refresh_film_cast_hash(data, "walkthrough", casts["walkthrough"])
        write_film_manifest(manifest, data)

    result = subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
            str(manifest),
            str(casts["opentofu"]),
            str(casts["direct"]),
            str(casts["walkthrough"]),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert expected_error in result.stderr


@pytest.mark.parametrize(
    ("lane", "timestamp"),
    [
        ("opentofu", 30),
        ("opentofu", 36),
        ("direct", 33),
        ("direct", 39),
        ("walkthrough", 36),
        ("walkthrough", 40),
    ],
)
def test_schema_v3_proof_accepts_inclusive_film_duration_boundaries(
    tmp_path: Path, lane: str, timestamp: float
) -> None:
    verifier = load_script(VERIFIER, "provider_linting_verifier_three_films_duration_boundaries")
    manifest, casts = write_film_proof(tmp_path)
    write_film_cast(casts[lane], lane=lane, timestamp=timestamp)
    write_film_manifest(manifest, film_manifest_for(casts))

    verify_films(verifier, manifest, casts)


@pytest.mark.parametrize(
    ("lane", "target"),
    [("opentofu", 34), ("direct", 37), ("walkthrough", 40)],
)
def test_pacer_preserves_ansi_wrapped_cast_bytes_and_lane_duration(
    tmp_path: Path, lane: str, target: float
) -> None:
    source = tmp_path / "source.cast"
    paced = tmp_path / "paced.cast"
    source_events: list[list[Any]] = [
        [0.1, "o", "\x1b[1;36m$ tofu vali"],
        [0.2, "o", "date\x1b[0m\r\n"],
        [0.3, "o", "\nLint summary:\nwarning: retain output ✓\n"],
        [0.4, "o", "PASS: provider validation\n"],
    ]
    write_cast_events(source, source_events)

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", lane, str(source), str(paced)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    paced_events = [json.loads(line) for line in paced.read_text(encoding="utf-8").splitlines()[1:]]
    source_bytes = b"".join(event[2].encode("utf-8") for event in source_events)
    paced_bytes = b"".join(event[2].encode("utf-8") for event in paced_events)
    timestamps = [event[0] for event in paced_events]

    assert json.loads(paced.read_text(encoding="utf-8").splitlines()[0]) == json.loads(
        source.read_text(encoding="utf-8").splitlines()[0]
    )
    assert paced_bytes == source_bytes
    assert all(event[2].endswith("\n") for event in paced_events)
    assert timestamps == sorted(timestamps)
    assert timestamps[-1] == target
    assert timestamps[1] - timestamps[0] > timestamps[2] - timestamps[1]
    assert timestamps[2] - timestamps[1] > 0
    assert timestamps[3] - timestamps[2] > 0
    lower, upper = FILM_DURATION_RANGES[lane]
    assert lower <= timestamps[-1] <= upper


@pytest.mark.parametrize(
    ("header_version", "events", "error"),
    [
        (3, [[0.1, "o", "not supported\n"]], "unsupported asciinema cast version"),
        (2, [[0.1, "i", "keystrokes"]], "cast has no output events"),
        (2, [[0.1, "o", "\udcff"]], "output event payload is not valid UTF-8"),
    ],
)
def test_pacer_rejects_unsafe_cast_inputs(
    tmp_path: Path, header_version: int, events: list[list[Any]], error: str
) -> None:
    source = tmp_path / "source.cast"
    paced = tmp_path / "paced.cast"
    write_cast_events(source, events)
    rewrite_cast_header(source, version=header_version)

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", "opentofu", str(source), str(paced)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert error in completed.stderr
    assert not paced.exists()


def test_pacer_rejects_an_unknown_lane(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(PACER),
            "--lane",
            "not-a-lane",
            str(tmp_path / "in"),
            str(tmp_path / "out"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "invalid choice" in completed.stderr


def test_pacer_preserves_a_literal_unicode_line_separator_in_output(tmp_path: Path) -> None:
    source = tmp_path / "source.cast"
    paced = tmp_path / "paced.cast"
    source_events = [[0.1, "o", "first\u2028second\n"]]
    write_cast_events(source, source_events)
    source.write_text(source.read_text(encoding="utf-8").replace("\\u2028", "\u2028"), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", "opentofu", str(source), str(paced)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    paced_events = [json.loads(line) for line in paced.read_text(encoding="utf-8").split("\n")[1:] if line]
    assert b"".join(event[2].encode("utf-8") for event in paced_events) == b"first\xe2\x80\xa8second\n"


def test_pacer_rejects_a_surrogate_header_without_overwriting_its_input(tmp_path: Path) -> None:
    source = tmp_path / "source.cast"
    write_cast_events(source, [[0.1, "o", "safe source\n"]])
    lines = source.read_text(encoding="utf-8").splitlines()
    header = json.loads(lines[0])
    header["title"] = "\udcff"
    source.write_text("\n".join([json.dumps(header), *lines[1:]]) + "\n", encoding="utf-8")
    original = source.read_bytes()

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", "opentofu", str(source), str(source)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "cast header contains invalid UTF-8" in completed.stderr
    assert source.read_bytes() == original
    assert source.read_bytes()


def test_pacer_rejects_an_unrepresentably_large_timestamp(tmp_path: Path) -> None:
    source = tmp_path / "source.cast"
    paced = tmp_path / "paced.cast"
    write_cast_events(source, [[int("9" * 400), "o", "line\n"]])

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", "opentofu", str(source), str(paced)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "invalid timestamp" in completed.stderr
    assert "OverflowError" not in completed.stderr
    assert not paced.exists()


def test_pacer_preserves_input_event_order_after_complete_output_lines(tmp_path: Path) -> None:
    source = tmp_path / "source.cast"
    paced = tmp_path / "paced.cast"
    write_cast_events(
        source,
        [[0.1, "o", "first\n"], [0.2, "o", "second\n"], [0.3, "i", "input"]],
    )

    completed = subprocess.run(
        [sys.executable, str(PACER), "--lane", "opentofu", str(source), str(paced)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    paced_events = [json.loads(line) for line in paced.read_text(encoding="utf-8").splitlines()[1:]]
    assert [(event[1], event[2]) for event in paced_events] == [
        ("o", "first\n"),
        ("o", "second\n"),
        ("i", "input"),
    ]


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


def test_film_generator_rejects_invalid_walkthrough_without_overwriting_output(tmp_path: Path) -> None:
    generator = load_script(GENERATOR, "provider_linting_film_generator_atomic_output")
    _manifest, casts = write_film_proof(tmp_path)
    write_film_cast(
        casts["walkthrough"],
        lane="walkthrough",
        timestamp=40,
        text=film_cast_text("walkthrough").replace("$ soup --version\n", ""),
    )
    binary = tmp_path / "dist" / "linux_amd64" / "terraform-provider-pyvider_v0.5.0"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"packaged provider")
    provenance = tmp_path / "dist" / "provider-linting-build-provenance.json"
    provenance.write_text(
        json.dumps(
            {
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
    output = tmp_path / "provider-linting-proof.json"
    sentinel = b"preserve this existing proof exactly\n"
    output.write_bytes(sentinel)

    with pytest.raises(ValueError, match="missing command from walkthrough recording"):
        generator.generate_film_proof(
            opentofu_cast_path=casts["opentofu"],
            direct_cast_path=casts["direct"],
            walkthrough_cast_path=casts["walkthrough"],
            build_provenance_path=provenance,
            output_path=output,
            provider_version="0.5.0",
            opentofu_archive="tofu_1.13.0-beta1_linux_amd64.zip",
            opentofu_archive_sha256="6" * 64,
            generated_at="2026-09-14T07:00:00Z",
            ci_environment={},
        )

    assert output.read_bytes() == sentinel


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
    assert "provider-linting-direct.cast" in recorder
    assert "provider-linting-walkthrough.cast" in recorder
    assert "--opentofu-cast" in recorder and "--direct-rpc-cast" in recorder
    assert "flavor pack" not in opentofu_demo + direct_rpc_demo + recorder
    assert "provider_linting_proof:" in workflow
    assert "pyvider_ref:" not in workflow
    assert "components_ref:" not in workflow
    assert "provider-linux_amd64" in workflow
    assert "actions/download-artifact" in workflow
    assert "ci/build-provider-linting-stack.py" in workflow
    assert "test-conformance-binary" in workflow
    assert "test-linting-opentofu-binary" in workflow
    assert "provider-linting-proof" in workflow
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in workflow
    assert "grep -Fxq 'OpenTofu v1.13.0-beta1'" in recorder
    assert "grep -Fxq 'OpenTofu v1.13.0-beta1'" in workflow
    assert "uv tool install --refresh tofusoup==0.8.2" in workflow

    proof_job = workflow.split("  provider-linting-proof:", 1)[1].split("\n  summary:", 1)[0]
    assert "provider-linting-proof.json" in proof_job
    assert "provider-linting-opentofu.cast" in proof_job
    assert "provider-linting-direct.cast" in proof_job
    assert "            provider-linting-opentofu.cast" in proof_job
    assert "            provider-linting-direct.cast" in proof_job
    assert "            provider-linting-walkthrough.cast" in proof_job
    assert "            provider-linting.cast" not in proof_job
    assert "ci/build-provider-linting-stack.py" not in proof_job
    assert ".stack/pyvider" not in proof_job
    assert ".stack/pyvider-components" not in proof_job


def test_recording_scripts_preserve_all_public_films_without_the_private_driver() -> None:
    scripts = {
        "opentofu": (ROOT / "ci" / "provider-linting-demo.sh").read_text(encoding="utf-8"),
        "direct": (ROOT / "ci" / "provider-linting-direct-rpc-demo.sh").read_text(encoding="utf-8"),
        "walkthrough": (ROOT / "ci" / "provider-linting-walkthrough.sh").read_text(encoding="utf-8"),
    }
    recorder = (ROOT / "ci" / "record-provider-linting.sh").read_text(encoding="utf-8")

    for lane, commands in FILM_COMMANDS.items():
        for command in commands:
            assert command in scripts[lane]
        assert "run-provider-linting-rpcs.py" not in scripts[lane]
        assert f"provider-linting-{lane}.raw.cast" in recorder
        assert f"provider-linting-{lane}.cast" in recorder
        assert f"--lane {lane}" in recorder

    assert "provider-linting-walkthrough.sh" in recorder
    assert "pace-provider-linting-cast.py" in recorder
    assert "retime-cast.py" not in recorder
    assert "run-provider-linting-rpcs.py" not in recorder


def test_public_recording_commands_have_a_real_blank_line_before_them() -> None:
    scripts = {
        "opentofu": (ROOT / "ci" / "provider-linting-demo.sh").read_text(encoding="utf-8"),
        "direct": (ROOT / "ci" / "provider-linting-direct-rpc-demo.sh").read_text(encoding="utf-8"),
        "walkthrough": (ROOT / "ci" / "provider-linting-walkthrough.sh").read_text(encoding="utf-8"),
    }

    public_commands = {
        "opentofu": ["tofu version", *OPENTOFU_COMMANDS],
        "direct": [DIRECT_RPC_COMMAND],
        "walkthrough": WALKTHROUGH_COMMANDS,
    }

    for lane, commands in public_commands.items():
        for command in commands:
            assert f"printf '\\n'\nshow_command '{command}'" in scripts[lane]


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
        [sys.executable, "ci/record-to-cast.py", str(legacy_cast), "printf", "legacy-proof"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(legacy_cast.read_text(encoding="utf-8").splitlines()[0])["title"] == (
        "pyvider conformance suite"
    )
    subprocess.run(
        [sys.executable, "ci/retime-cast.py", str(legacy_cast), str(retimed_cast), "15"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(retimed_cast.read_text(encoding="utf-8").splitlines()[0])["title"] == (
        "pyvider conformance suite"
    )
