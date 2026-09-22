# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the pinned OpenTofu experimental-lint installer."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import zipfile

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "ci" / "install-opentofu-experimental.sh"
ROOT = SCRIPT.parents[1]
VERSION = "1.13.0-rc1"


def host_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{system}_{architecture}"


def fake_release(tmp_path: Path, *, checksum: str | None = None) -> tuple[Path, Path]:
    release = tmp_path / "release"
    release.mkdir()
    archive_name = f"tofu_{VERSION}_{host_platform()}.zip"
    archive = release / archive_name
    tofu = tmp_path / "tofu"
    tofu.write_text("#!/bin/sh\nprintf 'OpenTofu v1.13.0-rc1\\n'\n", encoding="utf-8")
    tofu.chmod(0o755)
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.write(tofu, arcname="tofu")
    digest = checksum or hashlib.sha256(archive.read_bytes()).hexdigest()
    (release / f"tofu_{VERSION}_SHA256SUMS").write_text(
        f"{'0' * 64}  tofu_{VERSION}_unrelated.zip\n{digest}  {archive_name}\n",
        encoding="utf-8",
    )
    return release, archive


def run_installer(release: Path, cache: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(SCRIPT),
            "--version",
            VERSION,
            "--cache-dir",
            str(cache),
            "--release-base-url",
            release.as_uri(),
        ],
        capture_output=True,
        text=True,
    )


def test_installer_selects_host_archive_verifies_it_and_prints_binary(tmp_path: Path) -> None:
    release, archive = fake_release(tmp_path)
    cache = tmp_path / "cache"

    result = run_installer(release, cache)

    expected = cache / VERSION / host_platform() / "tofu"
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{expected}\n"
    assert expected.is_file()
    assert os.access(expected, os.X_OK)
    assert subprocess.run([expected, "version"], check=True, capture_output=True, text=True).stdout == (
        "OpenTofu v1.13.0-rc1\n"
    )
    assert hashlib.sha256(archive.read_bytes()).hexdigest() in result.stderr


def test_installer_rejects_a_checksum_mismatch(tmp_path: Path) -> None:
    release, _ = fake_release(tmp_path, checksum="f" * 64)

    result = run_installer(release, tmp_path / "cache")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "FAILED" in result.stderr


def test_installer_is_pinned_and_uses_verified_curl_downloads() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'PINNED_VERSION="1.13.0-rc1"' in source
    assert "curl --fail --location" in source
    assert "shasum -a 256 -c" in source
    assert "latest" not in source.lower()


def test_installer_requires_an_explicit_cache_directory(tmp_path: Path) -> None:
    release, _ = fake_release(tmp_path)

    result = subprocess.run(
        [str(SCRIPT), "--version", VERSION, "--release-base-url", release.as_uri()],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--cache-dir is required" in result.stderr


def test_installer_requires_the_explicit_pinned_version(tmp_path: Path) -> None:
    release, _ = fake_release(tmp_path)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--release-base-url",
            release.as_uri(),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--version 1.13.0-rc1 is required" in result.stderr


@pytest.mark.parametrize("version", ["latest", "1.12.0", "1.13.0"])
def test_installer_rejects_any_unpinned_version(tmp_path: Path, version: str) -> None:
    release, _ = fake_release(tmp_path)
    result = subprocess.run(
        [
            str(SCRIPT),
            "--version",
            version,
            "--cache-dir",
            str(tmp_path / "cache"),
            "--release-base-url",
            release.as_uri(),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "only OpenTofu 1.13.0-rc1 is supported" in result.stderr


def test_concurrent_installers_atomically_publish_one_verified_binary(tmp_path: Path) -> None:
    release, _ = fake_release(tmp_path)
    cache = tmp_path / "cache"
    command = [
        str(SCRIPT),
        "--version",
        VERSION,
        "--cache-dir",
        str(cache),
        "--release-base-url",
        release.as_uri(),
    ]

    processes = [
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)
    ]
    completed = [(*process.communicate(), process.returncode) for process in processes]

    expected = cache / VERSION / host_platform() / "tofu"
    assert all(returncode == 0 for _, _, returncode in completed)
    assert {stdout for stdout, _, _ in completed} == {f"{expected}\n"}
    assert subprocess.run([expected, "version"], check=True, capture_output=True, text=True).stdout == (
        "OpenTofu v1.13.0-rc1\n"
    )
    assert list(cache.glob(".install-*")) == []


def test_failed_extraction_preserves_an_existing_verified_binary(tmp_path: Path) -> None:
    release, archive = fake_release(tmp_path)
    cache = tmp_path / "cache"
    installed = run_installer(release, cache)
    binary = Path(installed.stdout.strip())
    before = binary.read_bytes()
    archive.write_bytes(b"not a zip archive")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (release / f"tofu_{VERSION}_SHA256SUMS").write_text(
        f"{digest}  {archive.name}\n",
        encoding="utf-8",
    )

    failed = run_installer(release, cache)

    assert failed.returncode != 0
    assert binary.read_bytes() == before
    assert os.access(binary, os.X_OK)
    assert list(cache.glob(".install-*")) == []


def test_opentofu_make_target_requires_an_explicit_provider_binary() -> None:
    result = subprocess.run(
        ["make", "test-linting-opentofu-binary", "PYVIDER_CONFORMANCE_PSP="],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "PYVIDER_CONFORMANCE_PSP is required" in result.stderr


def test_opentofu_make_target_requires_build_provenance(tmp_path: Path) -> None:
    binary = tmp_path / "terraform-provider-pyvider_v0.5.0"
    binary.write_bytes(b"provider")
    missing = tmp_path / "missing-provenance.json"

    result = subprocess.run(
        [
            "make",
            "test-linting-opentofu-binary",
            f"PYVIDER_CONFORMANCE_PSP={binary}",
            f"PYVIDER_LINTING_PROVENANCE={missing}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert f"missing build provenance: {missing}" in result.stderr


def test_opentofu_make_target_rejects_a_binary_outside_the_build_provenance(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "terraform-provider-pyvider_v0.5.0"
    binary.write_bytes(b"unreviewed provider")
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps({"artifacts": {"binary": {"sha256": hashlib.sha256(b"reviewed").hexdigest()}}}),
        encoding="utf-8",
    )
    cache = tmp_path / "opentofu-cache"

    result = subprocess.run(
        [
            "make",
            "test-linting-opentofu-binary",
            f"PYVIDER_CONFORMANCE_PSP={binary}",
            f"PYVIDER_LINTING_PROVENANCE={provenance}",
            f"OPENTOFU_LINTING_CACHE_DIR={cache}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "provider binary checksum does not match build provenance" in result.stderr
    assert not cache.exists()


def test_opentofu_make_target_is_a_no_rebuild_dry_run(tmp_path: Path) -> None:
    binary = tmp_path / "terraform-provider-pyvider_v0.5.0"
    binary.write_bytes(b"provider")
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps({"artifacts": {"binary": {"sha256": hashlib.sha256(b"provider").hexdigest()}}}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "make",
            "-n",
            "test-linting-opentofu-binary",
            f"PYVIDER_CONFORMANCE_PSP={binary}",
            f"PYVIDER_LINTING_PROVENANCE={provenance}",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "flavor pack" not in result.stdout
    assert "make build" not in result.stdout
    assert "ci/install-opentofu-experimental.sh --cache-dir" in result.stdout
    assert "--version 1.13.0-rc1" in result.stdout
    assert "OpenTofu v1.13.0-rc1" in result.stdout
    assert "tests/e2e/test_provider_linting_opentofu.py" in result.stdout
    assert "PYVIDER_OPENTOFU_BINARY=" in result.stdout
    assert str(provenance) in result.stdout
