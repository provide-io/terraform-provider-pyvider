#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Build the provider from exact clean Pyvider and component revisions."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from contextlib import suppress
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from typing import IO, Any, Protocol

import tomli_w


class CommandRunner(Protocol):
    def __call__(self, command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]: ...


class HashDigest(Protocol):
    def update(self, data: bytes, /) -> None: ...


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


def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
    """Reap a subprocess, terminating it first when it is still running."""
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def _close_pipe(stream: IO[bytes] | None) -> None:
    """Close a subprocess pipe without masking the pipeline's primary failure."""
    if stream is not None:
        with suppress(OSError):
            stream.close()


def _pump_archive_bytes(
    archive_process: subprocess.Popen[bytes],
    tar_process: subprocess.Popen[bytes],
    digest: HashDigest,
) -> tuple[int, int]:
    """Copy archive bytes between child pipes and return both exit codes."""
    if archive_process.stdout is None or tar_process.stdin is None:
        raise RuntimeError("archive pipeline did not expose required byte streams")
    archive_stdout = archive_process.stdout
    tar_stdin = tar_process.stdin
    for chunk in iter(lambda: archive_stdout.read(1024 * 1024), b""):
        digest.update(chunk)
        tar_stdin.write(chunk)
    archive_stdout.close()
    tar_stdin.close()
    return archive_process.wait(), tar_process.wait()


def materialize_revision(source: Path, revision: str, destination: Path) -> str:
    """Stream one Git archive into tar while hashing the exact archive bytes."""
    destination.mkdir(parents=True)
    digest = hashlib.sha256()
    archive_process: subprocess.Popen[bytes] | None = None
    tar_process: subprocess.Popen[bytes] | None = None
    succeeded = False
    try:
        archive_process = subprocess.Popen(
            ["git", "archive", revision],
            cwd=source,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        tar_process = subprocess.Popen(
            ["tar", "-x", "-C", str(destination)],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        archive_returncode, tar_returncode = _pump_archive_bytes(
            archive_process,
            tar_process,
            digest,
        )
        if archive_returncode:
            raise subprocess.CalledProcessError(archive_returncode, archive_process.args)
        if tar_returncode:
            raise subprocess.CalledProcessError(tar_returncode, tar_process.args)
        succeeded = True
        return digest.hexdigest()
    except BrokenPipeError:
        if tar_process is not None:
            failed_tar_returncode = tar_process.poll()
            if failed_tar_returncode not in (None, 0):
                raise subprocess.CalledProcessError(failed_tar_returncode, tar_process.args) from None
        raise
    finally:
        _close_pipe(None if archive_process is None else archive_process.stdout)
        _close_pipe(None if tar_process is None else tar_process.stdin)
        _stop_process(tar_process)
        _stop_process(archive_process)
        if not succeeded:
            shutil.rmtree(destination, ignore_errors=True)


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


def publish_outputs_atomically(
    publications: list[tuple[Path, Path]],
    *,
    staging_directory: Path,
) -> None:
    """Publish staged files with provenance last and roll back partial replacement."""
    backups = staging_directory / "backups"
    backups.mkdir()
    saved: dict[Path, Path] = {}
    for index, (_, destination) in enumerate(publications):
        if destination.exists():
            backup = backups / str(index)
            shutil.copy2(destination, backup)
            saved[destination] = backup

    published: list[Path] = []
    try:
        for staged, destination in publications:
            os.replace(staged, destination)  # noqa: PTH105 - explicit atomic replacement
            published.append(destination)
    except Exception:
        for destination in reversed(published):
            saved_backup = saved.get(destination)
            if saved_backup is None:
                destination.unlink(missing_ok=True)
            else:
                os.replace(saved_backup, destination)  # noqa: PTH105 - explicit atomic rollback
        raise


def build_stack(
    *,
    provider_repository: Path,
    pyvider_source: Path,
    components_source: Path,
    output_dir: Path,
    command_runner: CommandRunner = _run_command,
) -> dict[str, Any]:
    """Build the coordinated provider stack in a disposable source tree."""
    provider_sha = inspect_source(provider_repository, label="provider")
    pyvider_sha = inspect_source(pyvider_source, label="Pyvider")
    components_sha = inspect_source(components_source, label="pyvider-components")

    with tempfile.TemporaryDirectory(prefix="provider-linting-build-") as temporary:
        context = Path(temporary) / "provider"
        provider_archive_sha = materialize_revision(provider_repository, provider_sha, context)
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

        built_psp = context / "dist" / "terraform-provider-pyvider.psp"
        version = (context / "VERSION").read_text(encoding="utf-8").strip()
        suffix = ".exe" if platform.system().lower().startswith("win") else ""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_psp = output_dir / built_psp.name
        output_binary = output_dir / current_platform() / f"terraform-provider-pyvider_v{version}{suffix}"
        output_binary.parent.mkdir(parents=True, exist_ok=True)
        provenance_path = output_dir / "provider-linting-build-provenance.json"
        with tempfile.TemporaryDirectory(prefix=".provider-linting-stage-", dir=output_dir) as staging:
            staging_directory = Path(staging)
            staged_psp = staging_directory / output_psp.name
            staged_binary = staging_directory / output_binary.relative_to(output_dir)
            staged_binary.parent.mkdir(parents=True)
            shutil.copy2(built_psp, staged_psp)
            shutil.copy2(built_psp, staged_binary)
            staged_binary.chmod(staged_binary.stat().st_mode | 0o111)

            psp_sha = sha256_file(staged_psp)
            binary_sha = sha256_file(staged_binary)
            provenance: dict[str, Any] = {
                "schema_version": 1,
                "provider_repository_head": provider_sha,
                "provider_repository_archive_sha256": provider_archive_sha,
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
                # Retain it semantically unchanged as parsed above, and separately
                # prove local builds by inventorying the package's wheels slot.
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
            staged_provenance = staging_directory / provenance_path.name
            staged_provenance.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            publish_outputs_atomically(
                [
                    (staged_psp, output_psp),
                    (staged_binary, output_binary),
                    (staged_provenance, provenance_path),
                ],
                staging_directory=staging_directory,
            )

    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyvider-source", type=Path, required=True)
    parser.add_argument("--components-source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        build_stack(
            provider_repository=Path(__file__).absolute().parents[1],
            pyvider_source=arguments.pyvider_source,
            components_source=arguments.components_source,
            output_dir=arguments.output_dir,
        )
    except json.JSONDecodeError:
        print("error: coordinated provider build failed", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        # Build tools and parsers can expose temporary/internal paths. Keep the
        # CLI boundary concise while leaving KeyboardInterrupt/SystemExit alone.
        print("error: coordinated provider build failed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
