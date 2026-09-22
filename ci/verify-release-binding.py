#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Bind a downloaded release to the build and proof it was published from.

Usage: ci/verify-release-binding.py <released-dir> <version> <release-target-sha>

A `gh release download` directory is flat. The build provenance names its
binary relative to its own directory, as it sat in the build's dist/, so the
linux_amd64 archive is unpacked into <released-dir>/dist/linux_amd64 and the
provenance copied beside it before the path is resolved. On success this
prints the verified binary path, which the proof re-run then executes.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
from typing import Any
import zipfile

_HELPER = Path(__file__).resolve().parent / "provider-linting-artifact-path.py"


def _verified_binary_path(provenance: Path) -> Path:
    spec = importlib.util.spec_from_file_location("provider_linting_artifact_path", _HELPER)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {_HELPER.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path: Path = module.verified_binary_path(provenance)
    return path


def _load(path: Path) -> dict[str, Any]:
    loaded: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path.name} must be an object")
    return loaded


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bind(released: Path, version: str, release_target_sha: str) -> Path:
    dist = released / "dist"
    unpacked = dist / "linux_amd64"
    unpacked.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(released / f"terraform-provider-pyvider_{version}_linux_amd64.zip") as archive:
        archive.extractall(unpacked)
    provenance = dist / "provider-linting-build-provenance.json"
    shutil.copyfile(released / "provider-linting-build-provenance.json", provenance)

    build = _load(provenance)
    proof = _load(released / "provider-linting-proof.json")
    binary = _verified_binary_path(provenance)
    binary.chmod(0o755)

    _require(
        build.get("provider_repository_head") == release_target_sha, "build is not from the release commit"
    )
    _require(build["release_candidate"]["platform"] == "linux_amd64", "build proved another platform")
    _require(
        proof["components"]["terraform-provider-pyvider"]["sha"] == release_target_sha,
        "proof is not from the release commit",
    )
    _require(
        proof["provider_binary"]["sha256"] == build["artifacts"]["binary"]["sha256"],
        "proof and build name different binaries",
    )
    _require(proof["provider_binary"]["platform"] == "linux_amd64", "proof names another platform")
    _require(
        proof["release_candidate"] == build["release_candidate"], "proof and build name different archives"
    )
    for name in ("pyvider", "pyvider-components"):
        dependency = build["dependencies"][name]
        component = proof["components"][name]
        _require(component["sha"] == dependency["commit"], f"{name} commit differs between proof and build")
        _require(
            component["wheel_sha256"] == dependency["sha256"], f"{name} wheel differs between proof and build"
        )
    return binary


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    released, version, release_target_sha = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    try:
        print(bind(released, version, release_target_sha))
    except (OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
