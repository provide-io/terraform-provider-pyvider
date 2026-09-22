#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Build one provider release candidate from public PyPI dependencies."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import suppress
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess  # nosec B404
import sys
import tarfile
import tempfile
import tomllib
from typing import IO, Any, Protocol
import zipfile

import tomli_w

PYPI_REGISTRY = "https://pypi.org/simple"
PUBLIC_PROJECTS = {
    "pyvider": "provide-io/pyvider",
    "pyvider-components": "provide-io/pyvider-components",
}
PROOF_OUTPUTS = frozenset(
    {
        "provider-linting-direct.cast",
        "provider-linting-opentofu.cast",
        "provider-linting-walkthrough.cast",
        "tutorial-part7-provider-linting.cast",
        "provider-linting-proof.json",
    }
)


class CommandRunner(Protocol):
    def __call__(self, command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]: ...


class HashDigest(Protocol):
    def update(self, data: bytes, /) -> None: ...


TagResolver = Callable[[str, str], str]


def current_platform() -> str:
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{platform.system().lower()}_{architecture}"


BUILD_COMMANDS = [
    ["uv", "lock", "--refresh"],
    ["uv", "run", "flavor", "keygen", "--out-dir", "keys"],
    [
        "uv",
        "run",
        "flavor",
        "pack",
        "--output",
        "dist/terraform-provider-pyvider.psp",
        "--private-key",
        "keys/flavor-private.key",
        "--public-key",
        "keys/flavor-public.key",
    ],
    [
        "uv",
        "run",
        "flavor",
        "inspect",
        "--json",
        "--provenance",
        "dist/terraform-provider-pyvider.psp",
    ],
    ["uv", "run", "flavor", "inspect", "--json", "dist/terraform-provider-pyvider.psp"],
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_source(path: Path, *, label: str, allowed_dirty: Iterable[str] = ()) -> str:
    """Return HEAD when a repository has no dirt outside an explicit allowlist."""
    if not path.exists():
        raise ValueError(f"{label} source repository does not exist: {path}")
    try:
        subprocess.run(  # nosec B603, B607
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"{label} source is not a Git repository: {path}") from exc
    lines = subprocess.run(  # nosec B603, B607
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.splitlines()
    allowed = set(allowed_dirty)
    dirty = set()
    for line in lines:
        candidate = line[3:]
        if " -> " in candidate:
            candidate = candidate.rsplit(" -> ", 1)[1]
        dirty.add(candidate.strip('"'))
    unexpected = sorted(dirty - allowed)
    if unexpected:
        raise ValueError(f"{label} source repository has unexpected dirty paths: {', '.join(unexpected)}")
    return subprocess.run(  # nosec B603, B607
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def inspect_provider_source(path: Path) -> str:
    """Allow the four generated proof outputs, but no other provider dirt."""
    return inspect_source(path, label="provider", allowed_dirty=PROOF_OUTPUTS)


def _requirement_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if match is None:
        raise ValueError(f"invalid project dependency: {requirement!r}")
    return match.group(1).lower().replace("_", "-")


def pin_public_lint_dependencies(path: Path, *, pyvider: str, components: str) -> None:
    """Pin the two lint packages and remove every disposable local uv source."""
    project: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    replacements = {
        "pyvider": f"pyvider=={pyvider}",
        "pyvider-components": f"pyvider-components=={components}",
    }
    dependencies = []
    seen: set[str] = set()
    for requirement in project["project"]["dependencies"]:
        name = _requirement_name(requirement)
        if name in replacements:
            dependencies.append(replacements[name])
            seen.add(name)
        else:
            dependencies.append(requirement)
    if seen != set(replacements):
        raise ValueError("provider project does not declare both lint dependencies")
    project["project"]["dependencies"] = dependencies
    project.get("tool", {}).get("uv", {}).pop("sources", None)
    path.write_text(tomli_w.dumps(project), encoding="utf-8")


def validate_registry_lock(path: Path, expected: Mapping[str, str]) -> None:
    """Require one exact PyPI registry record for every public proof input."""
    packages = tomllib.loads(path.read_text(encoding="utf-8")).get("package", [])
    for name, version in expected.items():
        matches = [item for item in packages if item.get("name") == name]
        if len(matches) != 1:
            raise ValueError(f"lock must contain exactly one {name} package")
        record = matches[0]
        if record.get("version") != version:
            raise ValueError(f"lock resolved {name} at an unexpected version")
        if record.get("source") != {"registry": PYPI_REGISTRY}:
            raise ValueError(f"lock resolved {name} from a non-registry source")


def wheel_records(archive: Path, expected: Mapping[str, str]) -> tuple[list[str], dict[str, dict[str, str]]]:
    """Inventory packed wheels and hash the exact public wheel members."""
    records: dict[str, dict[str, str]] = {}
    with tarfile.open(archive, "r:*") as stream:
        members = [member for member in stream.getmembers() if member.name.endswith(".whl")]
        inventory = sorted(Path(member.name).name for member in members)
        for distribution, version in expected.items():
            normalized = distribution.replace("-", "[_-]")
            pattern = re.compile(rf"{normalized}-{re.escape(version)}-.*\.whl\Z", re.IGNORECASE)
            matches = [member for member in members if pattern.fullmatch(Path(member.name).name)]
            if len(matches) != 1:
                raise ValueError(
                    f"package contains {len(matches)} {distribution} {version} wheels; expected one"
                )
            extracted = stream.extractfile(matches[0])
            if extracted is None:
                raise ValueError(f"cannot read packed {distribution} wheel")
            records[distribution] = {
                "wheel": Path(matches[0].name).name,
                "sha256": hashlib.sha256(extracted.read()).hexdigest(),
            }
    return inventory, records


def packaged_wheel_inventory(archive: Path) -> list[str]:
    with tarfile.open(archive, "r:*") as stream:
        return sorted(Path(member.name).name for member in stream.getmembers() if member.name.endswith(".whl"))


def resolve_github_tag_commit(repository: str, tag: str) -> str:
    result = subprocess.run(  # nosec B603, B607
        [
            "git",
            "ls-remote",
            f"https://github.com/{repository}.git",
            f"refs/tags/{tag}",
            f"refs/tags/{tag}^{{}}",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    refs = {line.split("\t", 1)[1]: line.split("\t", 1)[0] for line in result.stdout.splitlines()}
    commit = refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")
    if commit is None or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError(f"cannot resolve {repository} {tag} to a commit")
    return commit


def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
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
    if stream is not None:
        with suppress(OSError):
            stream.close()


def _pump_archive_bytes(
    archive_process: subprocess.Popen[bytes], tar_process: subprocess.Popen[bytes], digest: HashDigest
) -> tuple[int, int]:
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
    destination.mkdir(parents=True)
    digest = hashlib.sha256()
    archive_process: subprocess.Popen[bytes] | None = None
    tar_process: subprocess.Popen[bytes] | None = None
    succeeded = False
    try:
        archive_process = subprocess.Popen(  # nosec B603, B607
            ["git", "archive", revision], cwd=source, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        tar_process = subprocess.Popen(  # nosec B603, B607
            ["tar", "-x", "-C", str(destination)],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        archive_returncode, tar_returncode = _pump_archive_bytes(archive_process, tar_process, digest)
        if archive_returncode:
            raise subprocess.CalledProcessError(archive_returncode, archive_process.args)
        if tar_returncode:
            raise subprocess.CalledProcessError(tar_returncode, tar_process.args)
        succeeded = True
        return digest.hexdigest()
    finally:
        _close_pipe(None if archive_process is None else archive_process.stdout)
        _close_pipe(None if tar_process is None else tar_process.stdin)
        _stop_process(tar_process)
        _stop_process(archive_process)
        if not succeeded:
            shutil.rmtree(destination, ignore_errors=True)


def _run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    print(f"📦 {command}", file=sys.stderr)
    try:
        return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8")  # nosec B603, B607
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        raise


def publish_outputs_atomically(publications: list[tuple[Path, Path]], *, staging_directory: Path) -> None:
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
            os.replace(staged, destination)  # noqa: PTH105
            published.append(destination)
    except Exception:
        for destination in reversed(published):
            saved_backup = saved.get(destination)
            if saved_backup is None:
                destination.unlink(missing_ok=True)
            else:
                os.replace(saved_backup, destination)  # noqa: PTH105
        raise


def build_stack(
    *,
    provider_repository: Path,
    pyvider_version: str,
    components_version: str,
    output_dir: Path,
    command_runner: CommandRunner = _run_command,
    tag_resolver: TagResolver = resolve_github_tag_commit,
) -> dict[str, Any]:
    """Build a public-dependency provider release candidate in an archived tree."""
    provider_sha = inspect_provider_source(provider_repository)
    expected = {"pyvider": pyvider_version, "pyvider-components": components_version}
    with tempfile.TemporaryDirectory(prefix="provider-linting-build-") as temporary:
        context = Path(temporary) / "provider"
        provider_archive_sha = materialize_revision(provider_repository, provider_sha, context)
        pin_public_lint_dependencies(
            context / "pyproject.toml", pyvider=pyvider_version, components=components_version
        )
        command_runner(BUILD_COMMANDS[0], cwd=context)
        validate_registry_lock(context / "uv.lock", expected)
        command_runner(BUILD_COMMANDS[1], cwd=context)
        command_runner(BUILD_COMMANDS[2], cwd=context)
        inspection_result = command_runner(BUILD_COMMANDS[3], cwd=context)
        package_result = command_runner(BUILD_COMMANDS[4], cwd=context)
        package_inspection: dict[str, Any] = json.loads(package_result.stdout)
        wheels_slot = next(
            (slot for slot in package_inspection.get("slots", []) if slot.get("name") == "wheels"), None
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
        packaged_wheels, wheel_metadata = wheel_records(context / wheels_archive, expected)
        built_psp = context / "dist" / "terraform-provider-pyvider.psp"
        version = (context / "VERSION").read_text(encoding="utf-8").strip()
        target = current_platform()
        suffix = ".exe" if target.startswith("windows_") else ""
        output_dir.mkdir(parents=True, exist_ok=True)
        platform_dir = output_dir / target
        platform_dir.mkdir(parents=True, exist_ok=True)
        binary_name = f"terraform-provider-pyvider_v{version}{suffix}"
        archive_name = f"terraform-provider-pyvider_{version}_{target}.zip"
        output_psp = platform_dir / "terraform-provider-pyvider.psp"
        output_binary = platform_dir / binary_name
        output_archive = output_dir / archive_name
        provenance_path = output_dir / "provider-linting-build-provenance.json"
        with tempfile.TemporaryDirectory(prefix=".provider-linting-stage-", dir=output_dir) as staging:
            stage = Path(staging)
            staged_psp = stage / target / output_psp.name
            staged_binary = stage / target / binary_name
            staged_archive = stage / archive_name
            staged_psp.parent.mkdir(parents=True)
            shutil.copy2(built_psp, staged_psp)
            shutil.copy2(built_psp, staged_binary)
            staged_binary.chmod(staged_binary.stat().st_mode | 0o111)
            with zipfile.ZipFile(staged_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(staged_binary, binary_name)
            psp_sha = sha256_file(staged_psp)
            binary_sha = sha256_file(staged_binary)
            archive_sha = sha256_file(staged_archive)
            dependencies = {}
            for name, dependency_version in expected.items():
                dependencies[name] = {
                    "version": dependency_version,
                    "tag": f"v{dependency_version}",
                    "commit": tag_resolver(PUBLIC_PROJECTS[name], f"v{dependency_version}"),
                    "registry": PYPI_REGISTRY,
                    **wheel_metadata[name],
                }
            provenance: dict[str, Any] = {
                "schema_version": 2,
                "provider_repository_head": provider_sha,
                "provider_repository_archive_sha256": provider_archive_sha,
                "dependencies": dependencies,
                "release_candidate": {
                    "github_artifact": f"provider-{target}",
                    "archive": archive_name,
                    "platform": target,
                    "sha256": archive_sha,
                },
                "commands": [*BUILD_COMMANDS, extract_command],
                "flavor_inspection": json.loads(inspection_result.stdout),
                "flavor_package_inspection": package_inspection,
                "packaged_wheels": packaged_wheels,
                "artifacts": {
                    "psp": {"path": output_psp.relative_to(output_dir).as_posix(), "sha256": psp_sha},
                    "binary": {
                        "path": output_binary.relative_to(output_dir).as_posix(),
                        "platform": target,
                        "sha256": binary_sha,
                    },
                },
                "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            staged_provenance = stage / provenance_path.name
            staged_provenance.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            publish_outputs_atomically(
                [
                    (staged_psp, output_psp),
                    (staged_binary, output_binary),
                    (staged_archive, output_archive),
                    (staged_provenance, provenance_path),
                ],
                staging_directory=stage,
            )
    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider-repository", type=Path, default=Path(__file__).absolute().parents[1])
    parser.add_argument("--pyvider-version", required=True)
    parser.add_argument("--components-version", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        build_stack(
            provider_repository=arguments.provider_repository,
            pyvider_version=arguments.pyvider_version,
            components_version=arguments.components_version,
            output_dir=arguments.output_dir,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        print("error: coordinated provider build failed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
