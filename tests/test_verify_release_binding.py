# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Post-publish binding of a downloaded release to its build and proof.

A release directory is flat: the platform zips, the proof files, and the build
provenance sit side by side. The provenance names its binary relative to its
own directory (`linux_amd64/terraform-provider-pyvider_v<version>`), as it was
in the build's dist/. The v0.6.0 verification resolved that path against the
release directory instead and failed on a correct release; these tests pin the
layout a real `gh release download` produces.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "ci" / "verify-release-binding.py"
VERSION = "9.9.9"
SHA = "a" * 40
BINARY = f"terraform-provider-pyvider_v{VERSION}"


def write_release(released: Path, *, binary: bytes = b"provider") -> None:
    released.mkdir()
    with zipfile.ZipFile(released / f"terraform-provider-pyvider_{VERSION}_linux_amd64.zip", "w") as archive:
        archive.writestr(BINARY, binary)
    digest = hashlib.sha256(b"provider").hexdigest()
    candidate = {"platform": "linux_amd64", "archive": f"terraform-provider-pyvider_{VERSION}_linux_amd64.zip"}
    dependencies = {
        "pyvider": {"commit": "b" * 40, "sha256": "c" * 64},
        "pyvider-components": {"commit": "d" * 40, "sha256": "e" * 64},
    }
    (released / "provider-linting-build-provenance.json").write_text(
        json.dumps(
            {
                "provider_repository_head": SHA,
                "release_candidate": candidate,
                "artifacts": {
                    "binary": {"path": f"linux_amd64/{BINARY}", "platform": "linux_amd64", "sha256": digest}
                },
                "dependencies": dependencies,
            }
        ),
        encoding="utf-8",
    )
    (released / "provider-linting-proof.json").write_text(
        json.dumps(
            {
                "components": {
                    "terraform-provider-pyvider": {"sha": SHA, "version": VERSION},
                    "pyvider": {"sha": "b" * 40, "wheel_sha256": "c" * 64},
                    "pyvider-components": {"sha": "d" * 40, "wheel_sha256": "e" * 64},
                },
                "provider_binary": {"sha256": digest, "platform": "linux_amd64"},
                "release_candidate": candidate,
            }
        ),
        encoding="utf-8",
    )


def bind(released: Path, sha: str = SHA) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(released), VERSION, sha],
        capture_output=True,
        text=True,
        check=False,
    )


def test_binding_accepts_the_flat_layout_a_release_download_produces(tmp_path: Path) -> None:
    released = tmp_path / "released"
    write_release(released)

    result = bind(released)

    assert result.returncode == 0, result.stderr
    binary = Path(result.stdout.strip())
    assert binary == (released / "dist" / "linux_amd64" / BINARY).resolve()
    assert binary.read_bytes() == b"provider"
    assert (released / "dist" / "provider-linting-build-provenance.json").is_file()


def test_binding_rejects_a_release_built_from_another_commit(tmp_path: Path) -> None:
    released = tmp_path / "released"
    write_release(released)

    assert bind(released, sha="f" * 40).returncode != 0


def test_binding_rejects_a_binary_that_does_not_match_its_provenance(tmp_path: Path) -> None:
    released = tmp_path / "released"
    write_release(released, binary=b"tampered")

    assert bind(released).returncode != 0


@pytest.mark.parametrize("dependency", ["pyvider", "pyvider-components"])
def test_binding_rejects_a_proof_that_names_other_dependency_wheels(tmp_path: Path, dependency: str) -> None:
    released = tmp_path / "released"
    write_release(released)
    proof_path = released / "provider-linting-proof.json"
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    proof["components"][dependency]["wheel_sha256"] = "0" * 64
    proof_path.write_text(json.dumps(proof), encoding="utf-8")

    assert bind(released).returncode != 0


def test_released_proof_rerun_reads_the_released_provenance() -> None:
    """The checkout has no dist/, so the Makefile's default provenance path is absent."""
    rerun = (ROOT / "ci" / "rerun-released-proof.sh").read_text(encoding="utf-8")

    assert 'PYVIDER_LINTING_PROVENANCE="${RELEASED}/dist/provider-linting-build-provenance.json"' in rerun


def test_release_and_manual_verification_share_one_workflow() -> None:
    import yaml  # type: ignore[import-untyped]

    release = yaml.safe_load((ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8"))
    verify = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "verify-release.yml").read_text(encoding="utf-8")
    )
    job = release["jobs"]["verify-release-proof"]

    assert job["uses"] == "./.github/workflows/verify-release.yml"
    assert job["needs"] == ["validate-build", "release"]
    triggers = verify[True] if True in verify else verify["on"]
    assert {"workflow_call", "workflow_dispatch"} <= set(triggers)


def test_verify_workflow_never_hides_a_failure_inside_an_echo() -> None:
    """`echo "x=$(cmd)"` exits 0 when cmd fails; only an assignment fails the step."""
    import re

    workflow = (ROOT / ".github" / "workflows" / "verify-release.yml").read_text(encoding="utf-8")

    assert not re.search(r"echo [^\n]*\$\(", workflow)
