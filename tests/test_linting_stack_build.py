# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the coordinated provider-linting stack build."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tomllib
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "ci" / "build-provider-linting-stack.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def initialized_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Test Author")
    (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "initial")
    return repo


def project_repo(parent: Path, name: str, files: dict[str, str]) -> Path:
    repo = parent / name
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Test Author")
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    return repo


def fake_stack_repositories(tmp_path: Path) -> tuple[Path, Path, Path]:
    provider = project_repo(
        tmp_path,
        "provider",
        {
            "pyproject.toml": (
                '[project]\nname = "provider"\n\n'
                '[tool.flavor]\noutput_path = "dist/terraform-provider-pyvider"\n\n'
                "[tool.flavor.build]\n"
            ),
            "uv.lock": "original lock\n",
            "VERSION": "1.2.3\n",
        },
    )
    pyvider = project_repo(tmp_path, "pyvider", {"pyproject.toml": '[project]\nname = "pyvider"\n'})
    components = project_repo(
        tmp_path,
        "components",
        {"pyproject.toml": '[project]\nname = "pyvider-components"\n'},
    )
    return provider, pyvider, components


def successful_build_runner(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    if "pack" in command:
        (cwd / "dist").mkdir()
        (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
    if "extract" in command:
        wheel = cwd / "pyvider-0.7.0-py3-none-any.whl"
        wheel.write_bytes(b"wheel")
        with tarfile.open(cwd / command[-1], "w:gz") as stream:
            stream.add(wheel, arcname=f"wheels/{wheel.name}")
    if "inspect" in command and "--provenance" in command:
        output = '{"provenance":{"packages":[]}}'
    elif "inspect" in command:
        output = '{"slots":[{"index":2,"name":"wheels"}]}'
    else:
        output = ""
    return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")


def load_build_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_provider_linting_stack", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_script_is_importable() -> None:
    module = load_build_module()

    assert callable(module.main)


def test_missing_source_repository_is_rejected(tmp_path: Path) -> None:
    module = load_build_module()

    with pytest.raises(ValueError, match="source repository does not exist"):
        module.inspect_source(tmp_path / "absent", label="Pyvider")


def test_non_git_source_repository_is_rejected(tmp_path: Path) -> None:
    module = load_build_module()
    source = tmp_path / "source"
    source.mkdir()

    with pytest.raises(ValueError, match="not a Git repository"):
        module.inspect_source(source, label="Pyvider")


def test_dirty_source_repository_is_rejected(tmp_path: Path) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    (source / "tracked.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(ValueError, match="has uncommitted changes"):
        module.inspect_source(source, label="Pyvider")


def test_clean_source_resolves_head_revision(tmp_path: Path) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)

    assert module.inspect_source(source, label="Pyvider") == git(source, "rev-parse", "HEAD")


def test_build_rejects_a_missing_provider_repository(tmp_path: Path) -> None:
    module = load_build_module()
    pyvider = project_repo(tmp_path, "pyvider", {"tracked.txt": "clean\n"})
    components = project_repo(tmp_path, "components", {"tracked.txt": "clean\n"})

    with pytest.raises(ValueError, match="provider source repository does not exist"):
        module.build_stack(
            provider_repository=tmp_path / "missing-provider",
            pyvider_source=pyvider,
            components_source=components,
            output_dir=tmp_path / "output",
        )


def test_build_rejects_a_non_git_provider_repository(tmp_path: Path) -> None:
    module = load_build_module()
    provider = tmp_path / "provider"
    provider.mkdir()
    pyvider = project_repo(tmp_path, "pyvider", {"tracked.txt": "clean\n"})
    components = project_repo(tmp_path, "components", {"tracked.txt": "clean\n"})

    with pytest.raises(ValueError, match="provider source is not a Git repository"):
        module.build_stack(
            provider_repository=provider,
            pyvider_source=pyvider,
            components_source=components,
            output_dir=tmp_path / "output",
        )


def test_build_rejects_a_dirty_provider_repository(tmp_path: Path) -> None:
    module = load_build_module()
    provider, pyvider, components = fake_stack_repositories(tmp_path)
    (provider / "VERSION").write_text("dirty\n", encoding="utf-8")

    def must_not_build(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        raise AssertionError(f"dirty provider reached build command {command!r} in {cwd}")

    with pytest.raises(ValueError, match="provider source repository has uncommitted changes"):
        module.build_stack(
            provider_repository=provider,
            pyvider_source=pyvider,
            components_source=components,
            output_dir=tmp_path / "output",
            command_runner=must_not_build,
        )


def test_source_revision_is_materialized_by_git_archive(tmp_path: Path) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    revision = git(source, "rev-parse", "HEAD")
    expected_archive = subprocess.run(
        ["git", "archive", revision], cwd=source, check=True, capture_output=True
    ).stdout
    (source / "tracked.txt").write_text("new revision\n", encoding="utf-8")
    git(source, "add", "tracked.txt")
    git(source, "commit", "-m", "new revision")
    destination = tmp_path / "build" / "_stack" / "pyvider"

    archive_sha = module.materialize_revision(source, revision, destination)

    assert (destination / "tracked.txt").read_text(encoding="utf-8") == "clean\n"
    assert not (destination / ".git").exists()
    assert archive_sha == hashlib.sha256(expected_archive).hexdigest()


def test_git_archive_stdout_is_piped_through_hash_capture_into_tar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    revision = git(source, "rev-parse", "HEAD")
    destination = tmp_path / "materialized"
    real_popen = subprocess.Popen
    processes: list[subprocess.Popen[Any]] = []
    calls: list[dict[str, Any]] = []

    def observing_popen(*args: Any, **kwargs: Any) -> subprocess.Popen[Any]:
        calls.append(kwargs)
        process = real_popen(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(module.subprocess, "Popen", observing_popen)

    module.materialize_revision(source, revision, destination)

    assert len(processes) == 2
    assert calls[0]["stdout"] is subprocess.PIPE
    assert calls[1]["stdin"] is subprocess.PIPE
    assert all(process.poll() is not None for process in processes)


def test_materialize_removes_partial_destination_when_archive_spawn_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    destination = tmp_path / "materialized"

    def fail_spawn(*args: Any, **kwargs: Any) -> subprocess.Popen[Any]:
        raise OSError("archive spawn sentinel")

    monkeypatch.setattr(module.subprocess, "Popen", fail_spawn)

    with pytest.raises(OSError, match="archive spawn sentinel"):
        module.materialize_revision(source, "HEAD", destination)

    assert not destination.exists()


def test_materialize_stops_archive_when_tar_spawn_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    destination = tmp_path / "materialized"

    class ArchiveProcess:
        def __init__(self) -> None:
            self.args = ["git", "archive", "HEAD"]
            self.stdout = io.BytesIO(b"archive")
            self.returncode: int | None = None
            self.terminated = False
            self.waited = False

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.terminated = True
            self.returncode = -15

        def wait(self, timeout: float | None = None) -> int:
            self.waited = True
            self.returncode = 0 if self.returncode is None else self.returncode
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

    archive = ArchiveProcess()
    calls = 0

    def spawn(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            return archive
        raise OSError("tar spawn sentinel")

    monkeypatch.setattr(module.subprocess, "Popen", spawn)

    with pytest.raises(OSError, match="tar spawn sentinel"):
        module.materialize_revision(source, "HEAD", destination)

    assert archive.terminated
    assert archive.waited
    assert not destination.exists()


def test_materialize_stops_children_and_cleans_destination_on_broken_pipe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    destination = tmp_path / "materialized"

    class BrokenWriter:
        def write(self, data: bytes) -> int:
            raise BrokenPipeError("write sentinel")

        def close(self) -> None:
            pass

    class Process:
        def __init__(
            self,
            args: list[str],
            *,
            stdout: io.BytesIO | None,
            stdin: Any,
        ) -> None:
            self.args = args
            self.stdout = stdout
            self.stdin = stdin
            self.returncode: int | None = None
            self.terminated = False
            self.waited = False

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.terminated = True
            self.returncode = -15

        def wait(self, timeout: float | None = None) -> int:
            self.waited = True
            self.returncode = 0 if self.returncode is None else self.returncode
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

    archive = Process(["git", "archive", "HEAD"], stdout=io.BytesIO(b"archive"), stdin=None)
    tar = Process(["tar", "-x"], stdout=io.BytesIO(), stdin=BrokenWriter())
    processes = [archive, tar]

    def spawn(*args: Any, **kwargs: Any) -> Process:
        if not processes:
            raise AssertionError("materialization spawned an external capture process")
        return processes.pop(0)

    monkeypatch.setattr(module.subprocess, "Popen", spawn)

    with pytest.raises(BrokenPipeError, match="write sentinel"):
        module.materialize_revision(source, "HEAD", destination)

    assert archive.waited
    assert tar.waited
    assert not destination.exists()


def test_materialize_cleans_destination_when_git_archive_exits_nonzero(tmp_path: Path) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    destination = tmp_path / "materialized"

    with pytest.raises(subprocess.CalledProcessError):
        module.materialize_revision(source, "missing-revision", destination)

    assert not destination.exists()


def test_materialize_cleans_destination_and_reaps_children_when_tar_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    source = initialized_repo(tmp_path)
    destination = tmp_path / "materialized"
    real_popen = subprocess.Popen
    processes: list[subprocess.Popen[Any]] = []

    def fail_tar(command: list[str], **kwargs: Any) -> subprocess.Popen[Any]:
        actual = ["/usr/bin/false"] if command[0] == "tar" else command
        process = real_popen(actual, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(module.subprocess, "Popen", fail_tar)

    with pytest.raises(subprocess.CalledProcessError):
        module.materialize_revision(source, "HEAD", destination)

    assert all(process.poll() is not None for process in processes)
    assert not destination.exists()


def test_local_sources_are_injected_only_into_build_context(tmp_path: Path) -> None:
    module = load_build_module()
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    original = b'[project]\nname = "provider"\n\n[tool.flavor.build]\nexclude = ["dist"]\n'
    (checkout / "pyproject.toml").write_bytes(original)
    context = tmp_path / "context"
    context.mkdir()
    (context / "pyproject.toml").write_bytes(original)

    module.inject_local_sources(context / "pyproject.toml")

    assert (checkout / "pyproject.toml").read_bytes() == original
    generated = tomllib.loads((context / "pyproject.toml").read_text(encoding="utf-8"))
    assert generated["tool"]["uv"]["sources"] == {
        "pyvider": {"path": "_stack/pyvider"},
        "pyvider-components": {"path": "_stack/pyvider-components"},
    }
    assert generated["tool"]["flavor"]["build"]["dependencies"] == [
        "_stack/pyvider",
        "_stack/pyvider-components",
    ]


def test_build_uses_an_isolated_archived_context(tmp_path: Path) -> None:
    module = load_build_module()
    provider = project_repo(
        tmp_path,
        "provider",
        {
            "pyproject.toml": '[project]\nname = "provider"\n\n[tool.flavor.build]\n',
            "uv.lock": "original lock\n",
            "VERSION": "1.2.3\n",
            "provider-marker": "from provider head\n",
        },
    )
    pyvider = project_repo(tmp_path, "pyvider", {"pyvider-marker": "archived pyvider\n"})
    components = project_repo(tmp_path, "components", {"components-marker": "archived components\n"})

    class ContextObserved(RuntimeError):
        pass

    def observe(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        assert command == ["uv", "lock"]
        assert (cwd / "provider-marker").read_text(encoding="utf-8") == "from provider head\n"
        assert (cwd / "_stack" / "pyvider" / "pyvider-marker").is_file()
        assert (cwd / "_stack" / "pyvider-components" / "components-marker").is_file()
        assert not (cwd / ".git").exists()
        raise ContextObserved

    with pytest.raises(ContextObserved):
        module.build_stack(
            provider_repository=provider,
            pyvider_source=pyvider,
            components_source=components,
            output_dir=tmp_path / "output",
            command_runner=observe,
        )


def test_build_runs_lock_pack_and_provenance_inspection(tmp_path: Path) -> None:
    module = load_build_module()
    provider = project_repo(
        tmp_path,
        "provider",
        {
            "pyproject.toml": (
                '[project]\nname = "provider"\n\n'
                '[tool.flavor]\noutput_path = "dist/terraform-provider-pyvider"\n\n'
                "[tool.flavor.build]\n"
            ),
            "uv.lock": "original lock\n",
            "VERSION": "1.2.3\n",
        },
    )
    pyvider = project_repo(tmp_path, "pyvider", {"pyproject.toml": '[project]\nname = "pyvider"\n'})
    components = project_repo(
        tmp_path,
        "components",
        {"pyproject.toml": '[project]\nname = "pyvider-components"\n'},
    )
    original_pyproject = (provider / "pyproject.toml").read_bytes()
    original_lock = (provider / "uv.lock").read_bytes()
    commands: list[list[str]] = []

    def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if "pack" in command:
            (cwd / "dist").mkdir()
            (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
        if "extract" in command:
            wheel = cwd / "pyvider-0.7.0-py3-none-any.whl"
            wheel.write_bytes(b"wheel")
            with tarfile.open(cwd / command[-1], "w:gz") as stream:
                stream.add(wheel, arcname=f"wheels/{wheel.name}")
        if "inspect" in command and "--provenance" in command:
            output = '{"provenance":{"packages":[]}}'
        elif "inspect" in command:
            output = '{"slots":[{"index":2,"name":"wheels"}]}'
        else:
            output = ""
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    module.build_stack(
        provider_repository=provider,
        pyvider_source=pyvider,
        components_source=components,
        output_dir=tmp_path / "output",
        command_runner=run,
    )

    assert commands == [
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
        [
            "uv",
            "run",
            "flavor",
            "extract",
            "--force",
            "dist/terraform-provider-pyvider.psp",
            "2",
            "dist/provider-linting-wheels.tar.gz",
        ],
    ]
    assert (provider / "pyproject.toml").read_bytes() == original_pyproject
    assert (provider / "uv.lock").read_bytes() == original_lock


def test_build_copies_psp_and_versioned_binary(tmp_path: Path) -> None:
    module = load_build_module()
    provider, pyvider, components = fake_stack_repositories(tmp_path)

    def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        if "pack" in command:
            (cwd / "dist").mkdir()
            (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
        if "extract" in command:
            wheel = cwd / "pyvider-0.7.0-py3-none-any.whl"
            wheel.write_bytes(b"wheel")
            with tarfile.open(cwd / command[-1], "w:gz") as stream:
                stream.add(wheel, arcname=f"wheels/{wheel.name}")
        if "inspect" in command and "--provenance" in command:
            output = '{"provenance":{"packages":[]}}'
        elif "inspect" in command:
            output = '{"slots":[{"index":2,"name":"wheels"}]}'
        else:
            output = ""
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    output = tmp_path / "output"
    module.build_stack(
        provider_repository=provider,
        pyvider_source=pyvider,
        components_source=components,
        output_dir=output,
        command_runner=run,
    )

    psp = output / "terraform-provider-pyvider.psp"
    binary = output / module.current_platform() / "terraform-provider-pyvider_v1.2.3"
    assert psp.read_bytes() == b"provider package"
    assert binary.read_bytes() == b"provider package"
    assert binary.stat().st_mode & 0o111
    assert not (output / "_stack").exists()


def test_failed_atomic_publication_rolls_back_artifacts_and_cleans_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    provider, pyvider, components = fake_stack_repositories(tmp_path)
    output = tmp_path / "output"
    binary = output / module.current_platform() / "terraform-provider-pyvider_v1.2.3"
    psp = output / "terraform-provider-pyvider.psp"
    provenance = output / "provider-linting-build-provenance.json"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"old binary")
    psp.write_bytes(b"old psp")
    provenance.write_bytes(b"old provenance")
    real_replace = os.replace
    published: list[Path] = []

    def fail_binary_publication(source: Path, destination: Path) -> None:
        published.append(Path(destination))
        if Path(destination) == binary:
            raise OSError("publication sentinel")
        real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_binary_publication)

    with pytest.raises(OSError, match="publication sentinel"):
        module.build_stack(
            provider_repository=provider,
            pyvider_source=pyvider,
            components_source=components,
            output_dir=output,
            command_runner=successful_build_runner,
        )

    assert psp.read_bytes() == b"old psp"
    assert binary.read_bytes() == b"old binary"
    assert provenance.read_bytes() == b"old provenance"
    assert provenance not in published
    assert not any("provider-linting-stage" in path.name for path in output.rglob("*"))


def test_build_writes_complete_provenance(tmp_path: Path) -> None:
    module = load_build_module()
    provider, pyvider, components = fake_stack_repositories(tmp_path)
    inspection = {
        "provenance": {
            "packages": [
                {"name": "pyvider", "version": "0.8.dev0"},
                {"name": "pyvider-components", "version": "0.8.dev0"},
            ]
        }
    }

    def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        if "pack" in command:
            (cwd / "dist").mkdir()
            (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
        if "extract" in command:
            wheel = cwd / "pyvider-0.7.0-py3-none-any.whl"
            wheel.write_bytes(b"wheel")
            with tarfile.open(cwd / command[-1], "w:gz") as stream:
                stream.add(wheel, arcname=f"wheels/{wheel.name}")
        if "inspect" in command and "--provenance" in command:
            output = json.dumps(inspection)
        elif "inspect" in command:
            output = '{"slots":[{"index":2,"name":"wheels"}]}'
        else:
            output = ""
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    output = tmp_path / "output"
    result = module.build_stack(
        provider_repository=provider,
        pyvider_source=pyvider,
        components_source=components,
        output_dir=output,
        command_runner=run,
    )

    provenance_path = output / "provider-linting-build-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert result == provenance
    assert provenance["schema_version"] == 1
    assert provenance["provider_repository_head"] == git(provider, "rev-parse", "HEAD")
    provider_archive = subprocess.run(
        ["git", "archive", "HEAD"],
        cwd=provider,
        check=True,
        capture_output=True,
    ).stdout
    assert provenance["provider_repository_archive_sha256"] == hashlib.sha256(provider_archive).hexdigest()
    assert provenance["sources"] == {
        "pyvider": {
            "sha": git(pyvider, "rev-parse", "HEAD"),
            "archive_sha256": hashlib.sha256(
                subprocess.run(["git", "archive", "HEAD"], cwd=pyvider, check=True, capture_output=True).stdout
            ).hexdigest(),
        },
        "pyvider-components": {
            "sha": git(components, "rev-parse", "HEAD"),
            "archive_sha256": hashlib.sha256(
                subprocess.run(
                    ["git", "archive", "HEAD"], cwd=components, check=True, capture_output=True
                ).stdout
            ).hexdigest(),
        },
    }
    assert provenance["commands"] == [
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
        [
            "uv",
            "run",
            "flavor",
            "extract",
            "--force",
            "dist/terraform-provider-pyvider.psp",
            "2",
            "dist/provider-linting-wheels.tar.gz",
        ],
    ]
    assert provenance["flavor_inspection"] == inspection
    assert provenance["flavor_package_inspection"] == {"slots": [{"index": 2, "name": "wheels"}]}
    assert provenance["packaged_wheels"] == ["pyvider-0.7.0-py3-none-any.whl"]
    expected_sha = hashlib.sha256(b"provider package").hexdigest()
    assert provenance["artifacts"] == {
        "psp": {
            "path": "terraform-provider-pyvider.psp",
            "sha256": expected_sha,
        },
        "binary": {
            "path": f"{module.current_platform()}/terraform-provider-pyvider_v1.2.3",
            "sha256": expected_sha,
        },
    }
    assert provenance["platform"] == module.current_platform()
    assert provenance["generated_at"].endswith("Z")
    assert sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()) == [
        f"{module.current_platform()}/terraform-provider-pyvider_v1.2.3",
        "provider-linting-build-provenance.json",
        "terraform-provider-pyvider.psp",
    ]


def test_packaged_wheel_inventory_names_local_distributions(tmp_path: Path) -> None:
    module = load_build_module()
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    for filename in (
        "pyvider-0.7.0-py3-none-any.whl",
        "pyvider_components-0.7.2-py3-none-any.whl",
        "attrs-25.4.0-py3-none-any.whl",
    ):
        (wheels / filename).write_bytes(b"wheel")
    archive = tmp_path / "wheels.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(wheels, arcname="wheels")

    assert module.packaged_wheel_inventory(archive) == [
        "attrs-25.4.0-py3-none-any.whl",
        "pyvider-0.7.0-py3-none-any.whl",
        "pyvider_components-0.7.2-py3-none-any.whl",
    ]


def test_packaged_wheel_inventory_accepts_flavorpacks_decompressed_tar(tmp_path: Path) -> None:
    module = load_build_module()
    wheel = tmp_path / "pyvider-0.7.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")
    archive = tmp_path / "wheels.slot"
    with tarfile.open(archive, "w:") as stream:
        stream.add(wheel, arcname=f"wheels/{wheel.name}")

    assert module.packaged_wheel_inventory(archive) == [wheel.name]


def test_build_provenance_inventories_flavorpack_wheels_slot(tmp_path: Path) -> None:
    module = load_build_module()
    provider, pyvider, components = fake_stack_repositories(tmp_path)

    def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        if "pack" in command:
            (cwd / "dist").mkdir()
            (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
        if "extract" in command:
            wheel_root = cwd / "wheel-fixture"
            wheel_root.mkdir()
            for filename in (
                "pyvider-0.7.0-py3-none-any.whl",
                "pyvider_components-0.7.2-py3-none-any.whl",
            ):
                (wheel_root / filename).write_bytes(b"wheel")
            with tarfile.open(cwd / command[-1], "w:gz") as stream:
                stream.add(wheel_root, arcname="wheels")
        if "inspect" in command and "--provenance" in command:
            output = '{"builder":"flavor-python"}'
        elif "inspect" in command:
            output = '{"slots":[{"index":2,"name":"wheels"}]}'
        else:
            output = ""
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    output = tmp_path / "output"
    provenance = module.build_stack(
        provider_repository=provider,
        pyvider_source=pyvider,
        components_source=components,
        output_dir=output,
        command_runner=run,
    )

    assert provenance["flavor_inspection"] == {"builder": "flavor-python"}
    assert provenance["flavor_package_inspection"] == {"slots": [{"index": 2, "name": "wheels"}]}
    assert provenance["packaged_wheels"] == [
        "pyvider-0.7.0-py3-none-any.whl",
        "pyvider_components-0.7.2-py3-none-any.whl",
    ]


def test_build_cli_requires_both_source_repositories() -> None:
    module = load_build_module()

    with pytest.raises(SystemExit) as raised:
        module.main([])

    assert raised.value.code == 2


def test_build_cli_reports_actionable_validation_errors(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_build_module()

    def fail_validation(**kwargs: Any) -> dict[str, Any]:
        raise ValueError("Pyvider source repository is dirty: /user/source")

    monkeypatch.setattr(module, "build_stack", fail_validation)

    result = module.main(
        [
            "--pyvider-source",
            "/user/source",
            "--components-source",
            "/user/components",
            "--output-dir",
            "/user/output",
        ]
    )

    assert result == 2
    assert capsys.readouterr().err == "error: Pyvider source repository is dirty: /user/source\n"


@pytest.mark.parametrize(
    "failure",
    [
        pytest.param(
            subprocess.CalledProcessError(1, ["uv", "/private/internal/project"], stderr="secret"),
            id="command",
        ),
        pytest.param(FileNotFoundError("missing /private/internal/tool"), id="missing-tool"),
        pytest.param(json.JSONDecodeError("secret /private/internal/json", "not-json", 0), id="json"),
        pytest.param(tarfile.ReadError("secret /private/internal/archive"), id="tar"),
    ],
)
def test_build_cli_sanitizes_unexpected_failures(
    failure: Exception,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_build_module()

    def fail_build(**kwargs: Any) -> dict[str, Any]:
        raise failure

    monkeypatch.setattr(module, "build_stack", fail_build)

    result = module.main(
        [
            "--pyvider-source",
            "/user/source",
            "--components-source",
            "/user/components",
            "--output-dir",
            "/user/output",
        ]
    )

    assert result == 2
    assert capsys.readouterr().err == "error: coordinated provider build failed\n"


def test_make_build_target_refuses_missing_pyvider_source() -> None:
    result = subprocess.run(
        ["make", "build-linting-stack", "PYVIDER_SOURCE=", "COMPONENTS_SOURCE="],
        cwd=SCRIPT.parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "PYVIDER_SOURCE is required" in result.stderr


def test_make_build_target_refuses_missing_components_source(tmp_path: Path) -> None:
    pyvider = initialized_repo(tmp_path)

    result = subprocess.run(
        [
            "make",
            "build-linting-stack",
            f"PYVIDER_SOURCE={pyvider}",
            "COMPONENTS_SOURCE=",
        ],
        cwd=SCRIPT.parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "COMPONENTS_SOURCE is required" in result.stderr


def test_conformance_binary_target_is_a_no_rebuild_dry_run(tmp_path: Path) -> None:
    binary = tmp_path / "terraform-provider-pyvider_v1.2.3"
    binary.write_bytes(b"provider")

    result = subprocess.run(
        [
            "make",
            "-n",
            "test-conformance-binary",
            f"PYVIDER_CONFORMANCE_PSP={binary}",
            "MAKE=:",
        ],
        cwd=SCRIPT.parents[1],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "flavor pack" not in result.stdout
    assert "make build" not in result.stdout
    assert f'ci/warm-workenv.sh "{binary}"' in result.stdout
    assert 'PYVIDER_CONFORMANCE_REQUIRED=1 PYVIDER_CONFORMANCE_PSP="' in result.stdout
