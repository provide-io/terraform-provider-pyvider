# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""The release stages exactly what the build uploaded, where it uploaded it.

upload-artifact stores each path relative to the paths' least common ancestor,
so `dist/provider-linting-build-provenance.json` arrives under `dist/` while the
casts arrive at the artifact root. A release that reads every proof file from
the root fails on the first real run. These tests build the artifact tree from
build-provider.yml's own upload list, so the two cannot drift apart silently.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import subprocess

import pytest
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
BUILD_WORKFLOW = ROOT / ".github" / "workflows" / "build-provider.yml"
STAGE_SCRIPT = ROOT / "ci" / "stage-release-assets.sh"
VERSION = "9.9.9"
TARGETS = ("linux_amd64", "linux_arm64", "darwin_amd64", "darwin_arm64", "windows_amd64")
PROOF_ASSETS = (
    "provider-linting-proof.json",
    "provider-linting-opentofu.cast",
    "provider-linting-direct.cast",
    "provider-linting-walkthrough.cast",
    "provider-linting-build-provenance.json",
)


def proof_upload_paths() -> list[PurePosixPath]:
    """The `path:` list of the step that uploads the provider-linting-proof artifact."""
    workflow = yaml.safe_load(BUILD_WORKFLOW.read_text(encoding="utf-8"))
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if step.get("with", {}).get("name") == "provider-linting-proof":
                return [
                    PurePosixPath(line.strip()) for line in step["with"]["path"].splitlines() if line.strip()
                ]
    raise AssertionError("build-provider.yml uploads no provider-linting-proof artifact")


def artifact_layout(paths: list[PurePosixPath]) -> list[PurePosixPath]:
    """Mirror upload-artifact: store each path relative to the least common ancestor."""
    ancestor = PurePosixPath(os.path.commonpath([str(path.parent) for path in paths]) or ".")
    return [path.relative_to(ancestor) for path in paths]


def fake_build_artifacts(artifacts: Path) -> None:
    for target in TARGETS:
        archive = artifacts / f"provider-{target}" / f"terraform-provider-pyvider_{VERSION}_{target}.zip"
        archive.parent.mkdir(parents=True)
        archive.write_bytes(target.encode())
    for relative in artifact_layout(proof_upload_paths()):
        stored = artifacts / "provider-linting-proof" / relative
        stored.parent.mkdir(parents=True, exist_ok=True)
        stored.write_text(relative.name, encoding="utf-8")


def stage(artifacts: Path, release: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(STAGE_SCRIPT), str(artifacts), str(release), VERSION],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_build_uploads_every_proof_asset_the_release_publishes() -> None:
    assert sorted(path.name for path in proof_upload_paths()) == sorted(PROOF_ASSETS)


def test_release_stages_the_artifact_layout_the_build_uploads(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    release = tmp_path / "release"
    fake_build_artifacts(artifacts)

    result = stage(artifacts, release)

    assert result.returncode == 0, result.stderr
    assert sorted(path.name for path in release.iterdir()) == sorted(
        [
            *PROOF_ASSETS,
            *(f"terraform-provider-pyvider_{VERSION}_{target}.zip" for target in TARGETS),
            f"terraform-provider-pyvider_{VERSION}_manifest.json",
        ]
    )
    for name in PROOF_ASSETS:
        assert (release / name).read_text(encoding="utf-8") == name


@pytest.mark.parametrize("missing", ["provider-linting-build-provenance.json", "windows_amd64"])
def test_release_staging_refuses_an_incomplete_build(tmp_path: Path, missing: str) -> None:
    artifacts = tmp_path / "artifacts"
    fake_build_artifacts(artifacts)
    for path in artifacts.rglob("*"):
        if path.is_file() and missing in path.name:
            path.unlink()

    result = stage(artifacts, tmp_path / "release")

    assert result.returncode != 0
