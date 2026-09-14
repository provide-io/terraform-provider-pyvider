#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Build the provider from exact clean Pyvider and component revisions."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
from typing import Any, Protocol

import tomli_w


class CommandRunner(Protocol):
    def __call__(self, command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]: ...


def current_platform() -> str:
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{platform.system().lower()}_{architecture}"


BUILD_COMMANDS = [
    ["uv", "lock"],
    ["uv", "run", "flavor", "pack"],
    [
        "uv",
        "run",
        "flavor",
        "inspect",
        "--json",
        "--provenance",
        "dist/terraform-provider-pyvider.psp",
    ],
    [
        "uv",
        "run",
        "flavor",
        "inspect",
        "--json",
        "dist/terraform-provider-pyvider.psp",
    ],
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def packaged_wheel_inventory(archive: Path) -> list[str]:
    """Return wheel filenames from Flavorpack's compressed wheels slot."""
    with tarfile.open(archive, "r:*") as stream:
        return sorted(Path(member.name).name for member in stream.getmembers() if member.name.endswith(".whl"))


def inspect_source(path: Path, *, label: str) -> str:
    """Return the clean Git revision selected for a source repository."""
    if not path.exists():
        raise ValueError(f"{label} source repository does not exist: {path}")
    try:
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"{label} source is not a Git repository: {path}") from exc
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise ValueError(f"{label} source repository has uncommitted changes: {path}")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def materialize_revision(source: Path, revision: str, destination: Path) -> str:
    """Extract one Git revision and return the SHA256 of its archive stream."""
    destination.mkdir(parents=True)
    with tempfile.NamedTemporaryFile(prefix="provider-linting-archive-") as captured:
        archive_process = subprocess.Popen(
            ["git", "archive", revision],
            cwd=source,
            stdout=subprocess.PIPE,
        )
        assert archive_process.stdout is not None
        capture_process = subprocess.Popen(
            ["tee", captured.name],
            stdin=archive_process.stdout,
            stdout=subprocess.PIPE,
        )
        archive_process.stdout.close()
        assert capture_process.stdout is not None
        tar_process = subprocess.Popen(
            ["tar", "-x", "-C", str(destination)],
            stdin=capture_process.stdout,
        )
        capture_process.stdout.close()
        tar_returncode = tar_process.wait()
        capture_returncode = capture_process.wait()
        archive_returncode = archive_process.wait()
        for process, returncode in (
            (archive_process, archive_returncode),
            (capture_process, capture_returncode),
            (tar_process, tar_returncode),
        ):
            if returncode:
                raise subprocess.CalledProcessError(returncode, process.args)

        return sha256_file(Path(captured.name))


def inject_local_sources(pyproject_path: Path) -> None:
    """Point one temporary provider project at the archived source trees."""
    project: dict[str, Any] = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    tool = project.setdefault("tool", {})
    uv = tool.setdefault("uv", {})
    uv["sources"] = {
        "pyvider": {"path": "_stack/pyvider"},
        "pyvider-components": {"path": "_stack/pyvider-components"},
    }
    flavor_build = tool.setdefault("flavor", {}).setdefault("build", {})
    flavor_build["dependencies"] = ["_stack/pyvider", "_stack/pyvider-components"]
    pyproject_path.write_text(tomli_w.dumps(project), encoding="utf-8")


def _run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def build_stack(
    *,
    provider_repository: Path,
    pyvider_source: Path,
    components_source: Path,
    output_dir: Path,
    command_runner: CommandRunner = _run_command,
) -> dict[str, Any]:
    """Build the coordinated provider stack in a disposable source tree."""
    pyvider_sha = inspect_source(pyvider_source, label="Pyvider")
    components_sha = inspect_source(components_source, label="pyvider-components")
    provider_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=provider_repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    with tempfile.TemporaryDirectory(prefix="provider-linting-build-") as temporary:
        context = Path(temporary) / "provider"
        materialize_revision(provider_repository, provider_sha, context)
        pyvider_archive_sha = materialize_revision(pyvider_source, pyvider_sha, context / "_stack" / "pyvider")
        components_archive_sha = materialize_revision(
            components_source,
            components_sha,
            context / "_stack" / "pyvider-components",
        )
        inject_local_sources(context / "pyproject.toml")
        command_runner(BUILD_COMMANDS[0], cwd=context)
        command_runner(BUILD_COMMANDS[1], cwd=context)
        inspection_result = command_runner(BUILD_COMMANDS[2], cwd=context)
        package_inspection_result = command_runner(BUILD_COMMANDS[3], cwd=context)
        package_inspection: dict[str, Any] = json.loads(package_inspection_result.stdout)
        wheels_slot = next(
            (slot for slot in package_inspection.get("slots", []) if slot.get("name") == "wheels"),
            None,
        )
        if wheels_slot is None:
            raise ValueError("Flavorpack package inspection did not expose a wheels slot")
        wheels_archive = Path("dist/provider-linting-wheels.tar.gz")
        extract_command = [
            "uv",
            "run",
            "flavor",
            "extract",
            "--force",
            "dist/terraform-provider-pyvider.psp",
            str(wheels_slot["index"]),
            wheels_archive.as_posix(),
        ]
        command_runner(extract_command, cwd=context)
        packaged_wheels = packaged_wheel_inventory(context / wheels_archive)

        output_dir.mkdir(parents=True, exist_ok=True)
        built_psp = context / "dist" / "terraform-provider-pyvider.psp"
        output_psp = output_dir / built_psp.name
        shutil.copy2(built_psp, output_psp)
        version = (context / "VERSION").read_text(encoding="utf-8").strip()
        suffix = ".exe" if platform.system().lower().startswith("win") else ""
        output_binary = output_dir / current_platform() / f"terraform-provider-pyvider_v{version}{suffix}"
        output_binary.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_psp, output_binary)
        output_binary.chmod(output_binary.stat().st_mode | 0o111)

        psp_sha = sha256_file(output_psp)
        binary_sha = sha256_file(output_binary)
        provenance: dict[str, Any] = {
            "schema_version": 1,
            "provider_repository_head": provider_sha,
            "sources": {
                "pyvider": {
                    "sha": pyvider_sha,
                    "archive_sha256": pyvider_archive_sha,
                },
                "pyvider-components": {
                    "sha": components_sha,
                    "archive_sha256": components_archive_sha,
                },
            },
            "commands": [*BUILD_COMMANDS, extract_command],
            "flavor_inspection": json.loads(inspection_result.stdout),
            # Flavorpack 0.5.3's --provenance JSON omits dependency names.
            # Retain it byte-for-byte as parsed above, and separately prove the
            # bundled local builds by inventorying the package's wheels slot.
            "flavor_package_inspection": package_inspection,
            "packaged_wheels": packaged_wheels,
            "artifacts": {
                "psp": {
                    "path": output_psp.relative_to(output_dir).as_posix(),
                    "sha256": psp_sha,
                },
                "binary": {
                    "path": output_binary.relative_to(output_dir).as_posix(),
                    "sha256": binary_sha,
                },
            },
            "platform": current_platform(),
            "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        provenance_path = output_dir / "provider-linting-build-provenance.json"
        provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyvider-source", type=Path, required=True)
    parser.add_argument("--components-source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        build_stack(
            provider_repository=Path(__file__).resolve().parents[1],
            pyvider_source=arguments.pyvider_source,
            components_source=arguments.components_source,
            output_dir=arguments.output_dir,
        )
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
