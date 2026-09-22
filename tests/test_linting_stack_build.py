# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the public-artifact provider linting build."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
from types import ModuleType
from typing import Any
import zipfile

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "ci" / "build-provider-linting-stack.py"
PYVIDER_SHA = "1" * 40
COMPONENTS_SHA = "2" * 40


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def project_repo(parent: Path, files: dict[str, str]) -> Path:
    repo = parent / "provider"
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


def provider_repo(tmp_path: Path) -> Path:
    return project_repo(
        tmp_path,
        {
            "pyproject.toml": (
                '[project]\nname="provider"\n'
                'dependencies=["pyvider>=0.7", "pyvider-components>=0.7"]\n'
                '[tool.uv.sources]\npyvider={path="../pyvider"}\n'
                '[tool.flavor]\noutput_path="dist/terraform-provider-pyvider"\n'
            ),
            "uv.lock": 'version = 1\nrevision = 3\nrequires-python = ">=3.11"\n',
            "VERSION": "0.6.0\n",
            "marker.txt": "archived provider\n",
        },
    )


def initialized_repo(tmp_path: Path) -> Path:
    return project_repo(tmp_path, {"tracked.txt": "clean\n"})


def load_build_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_provider_linting_stack", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_locked_public_dependencies(cwd: Path) -> None:
    (cwd / "uv.lock").write_text(
        """version = 1
revision = 3
requires-python = ">=3.11"

[[package]]
name = "pyvider"
version = "0.8.1"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "pyvider-components"
version = "0.8.0"
source = { registry = "https://pypi.org/simple" }
""",
        encoding="utf-8",
    )


def successful_runner(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    if command[:3] == ["uv", "lock", "--refresh"]:
        write_locked_public_dependencies(cwd)
    elif "pack" in command:
        (cwd / "dist").mkdir(exist_ok=True)
        (cwd / "dist" / "terraform-provider-pyvider.psp").write_bytes(b"provider package")
    elif "extract" in command:
        wheel_root = cwd / "wheel-fixture"
        wheel_root.mkdir()
        (wheel_root / "pyvider-0.8.1-py3-none-any.whl").write_bytes(b"pyvider wheel")
        (wheel_root / "pyvider_components-0.8.0-py3-none-any.whl").write_bytes(b"components wheel")
        with tarfile.open(cwd / command[-1], "w:gz") as stream:
            stream.add(wheel_root, arcname="wheels")
    if "inspect" in command and "--provenance" in command:
        output = '{"builder":"flavor-python"}'
    elif "inspect" in command:
        output = '{"slots":[{"index":2,"name":"wheels"}]}'
    else:
        output = ""
    return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")


def resolve_tag(repository: str, tag: str) -> str:
    assert tag == ("v0.8.1" if repository.endswith("/pyvider") else "v0.8.0")
    return PYVIDER_SHA if repository.endswith("/pyvider") else COMPONENTS_SHA


def test_build_script_is_importable() -> None:
    assert callable(load_build_module().main)


def test_missing_and_non_git_provider_are_rejected(tmp_path: Path) -> None:
    module = load_build_module()
    with pytest.raises(ValueError, match="does not exist"):
        module.inspect_provider_source(tmp_path / "missing")
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(ValueError, match="not a Git repository"):
        module.inspect_provider_source(plain)


def test_unexpected_provider_dirt_is_rejected(tmp_path: Path) -> None:
    module = load_build_module()
    provider = provider_repo(tmp_path)
    (provider / "VERSION").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected dirty paths: VERSION"):
        module.inspect_provider_source(provider)


def test_source_revision_is_materialized_by_git_archive(tmp_path: Path) -> None:
    module = load_build_module()
    source = provider_repo(tmp_path)
    revision = git(source, "rev-parse", "HEAD")
    archived = subprocess.run(["git", "archive", revision], cwd=source, check=True, capture_output=True).stdout
    destination = tmp_path / "materialized"

    digest = module.materialize_revision(source, revision, destination)

    assert (destination / "marker.txt").read_text(encoding="utf-8") == "archived provider\n"
    assert not (destination / ".git").exists()
    assert digest == hashlib.sha256(archived).hexdigest()


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
        def __init__(self, args: list[str], *, stdout: io.BytesIO | None, stdin: Any) -> None:
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

    with pytest.raises((subprocess.CalledProcessError, BrokenPipeError)):
        module.materialize_revision(source, "HEAD", destination)

    assert all(process.poll() is not None for process in processes)
    assert not destination.exists()


def test_registry_lock_rejects_path_git_url_editable_and_duplicate_sources(tmp_path: Path) -> None:
    module = load_build_module()
    lock = tmp_path / "uv.lock"
    expected = {"pyvider": "0.8.1", "pyvider-components": "0.8.0"}
    for source in (
        '{ path = "../pyvider" }',
        '{ git = "https://github.com/provide-io/pyvider" }',
        '{ url = "https://example.invalid/pyvider.whl" }',
        '{ editable = "../pyvider" }',
    ):
        lock.write_text(
            f"""[[package]]\nname="pyvider"\nversion="0.8.1"\nsource={source}\n"""
            '[[package]]\nname="pyvider-components"\nversion="0.8.0"\n'
            'source={registry="https://pypi.org/simple"}\n',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="non-registry source"):
            module.validate_registry_lock(lock, expected)
    lock.write_text(
        '[[package]]\nname="pyvider"\nversion="0.8.1"\nsource={registry="https://pypi.org/simple"}\n'
        '[[package]]\nname="pyvider"\nversion="0.8.1"\nsource={registry="https://pypi.org/simple"}\n'
        '[[package]]\nname="pyvider-components"\nversion="0.8.0"\n'
        'source={registry="https://pypi.org/simple"}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="exactly one pyvider package"):
        module.validate_registry_lock(lock, expected)


def test_wheel_records_hash_exact_packed_bytes_and_require_one_match(tmp_path: Path) -> None:
    module = load_build_module()
    root = tmp_path / "wheels"
    root.mkdir()
    pyvider = root / "pyvider-0.8.1-py3-none-any.whl"
    components = root / "pyvider_components-0.8.0-py3-none-any.whl"
    pyvider.write_bytes(b"pyvider wheel")
    components.write_bytes(b"components wheel")
    archive = tmp_path / "wheels.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(root, arcname="wheels")

    inventory, records = module.wheel_records(archive, {"pyvider": "0.8.1", "pyvider-components": "0.8.0"})

    assert inventory == [pyvider.name, components.name]
    assert records["pyvider"] == {
        "wheel": pyvider.name,
        "sha256": hashlib.sha256(b"pyvider wheel").hexdigest(),
    }
    assert records["pyvider-components"]["sha256"] == hashlib.sha256(b"components wheel").hexdigest()
    with pytest.raises(ValueError, match=r"pyvider 0\.7\.0 wheels"):
        module.wheel_records(archive, {"pyvider": "0.7.0"})


def test_build_writes_schema_v2_public_provenance_and_release_archive(tmp_path: Path) -> None:
    module = load_build_module()
    provider = provider_repo(tmp_path)
    output = tmp_path / "output"

    provenance = module.build_stack(
        provider_repository=provider,
        pyvider_version="0.8.1",
        components_version="0.8.0",
        output_dir=output,
        command_runner=successful_runner,
        tag_resolver=resolve_tag,
    )

    assert provenance["schema_version"] == 2
    assert provenance["provider_repository_head"] == git(provider, "rev-parse", "HEAD")
    assert provenance["dependencies"]["pyvider"] == {
        "version": "0.8.1",
        "tag": "v0.8.1",
        "commit": PYVIDER_SHA,
        "registry": "https://pypi.org/simple",
        "wheel": "pyvider-0.8.1-py3-none-any.whl",
        "sha256": hashlib.sha256(b"pyvider wheel").hexdigest(),
    }
    assert provenance["dependencies"]["pyvider-components"]["commit"] == COMPONENTS_SHA
    platform = module.current_platform()
    binary = output / platform / "terraform-provider-pyvider_v0.6.0"
    archive = output / f"terraform-provider-pyvider_0.6.0_{platform}.zip"
    assert binary.read_bytes() == b"provider package"
    assert provenance["artifacts"]["binary"]["platform"] == platform
    assert provenance["release_candidate"] == {
        "github_artifact": f"provider-{platform}",
        "archive": archive.name,
        "platform": platform,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    with zipfile.ZipFile(archive) as packed:
        assert packed.namelist() == ["terraform-provider-pyvider_v0.6.0"]
        assert packed.read(packed.namelist()[0]) == b"provider package"
    commands = json.dumps(provenance["commands"])
    assert ["uv", "run", "flavor", "keygen", "--out-dir", "keys"] in provenance["commands"]
    pack_command = next(
        command for command in provenance["commands"] if command[:4] == ["uv", "run", "flavor", "pack"]
    )
    assert pack_command[-4:] == [
        "--private-key",
        "keys/flavor-private.key",
        "--public-key",
        "keys/flavor-public.key",
    ]
    assert "editable" not in commands
    assert "_stack" not in commands
    assert "git+" not in commands
    assert json.loads((output / "provider-linting-build-provenance.json").read_text()) == provenance


def test_build_leaves_checkout_inputs_unchanged(tmp_path: Path) -> None:
    module = load_build_module()
    provider = provider_repo(tmp_path)
    original_project = (provider / "pyproject.toml").read_bytes()
    original_lock = (provider / "uv.lock").read_bytes()

    module.build_stack(
        provider_repository=provider,
        pyvider_version="0.8.1",
        components_version="0.8.0",
        output_dir=tmp_path / "output",
        command_runner=successful_runner,
        tag_resolver=resolve_tag,
    )

    assert (provider / "pyproject.toml").read_bytes() == original_project
    assert (provider / "uv.lock").read_bytes() == original_lock


def test_failed_atomic_publication_rolls_back_existing_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    provider = provider_repo(tmp_path)
    output = tmp_path / "output"
    platform = module.current_platform()
    binary = output / platform / "terraform-provider-pyvider_v0.6.0"
    psp = output / platform / "terraform-provider-pyvider.psp"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"old binary")
    psp.write_bytes(b"old psp")
    real_replace = os.replace

    def fail_binary(source: Path, destination: Path) -> None:
        if Path(destination) == binary:
            raise OSError("publication sentinel")
        real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_binary)
    with pytest.raises(OSError, match="publication sentinel"):
        module.build_stack(
            provider_repository=provider,
            pyvider_version="0.8.1",
            components_version="0.8.0",
            output_dir=output,
            command_runner=successful_runner,
            tag_resolver=resolve_tag,
        )
    assert psp.read_bytes() == b"old psp"
    assert binary.read_bytes() == b"old binary"


def test_cli_requires_public_versions_and_passes_provider_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_module()
    captured: dict[str, Any] = {}
    monkeypatch.setattr(module, "build_stack", lambda **kwargs: captured.update(kwargs) or {})

    assert (
        module.main(
            [
                "--provider-repository",
                str(tmp_path),
                "--pyvider-version",
                "0.8.1",
                "--components-version",
                "0.8.0",
                "--output-dir",
                str(tmp_path / "dist"),
            ]
        )
        == 0
    )
    assert captured["provider_repository"] == tmp_path
    assert captured["pyvider_version"] == "0.8.1"
    with pytest.raises(SystemExit):
        module.main(["--output-dir", str(tmp_path)])


@pytest.mark.parametrize(
    "failure",
    [subprocess.CalledProcessError(1, ["uv"]), FileNotFoundError("missing"), tarfile.ReadError("bad")],
)
def test_cli_sanitizes_unexpected_failures(
    failure: Exception, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_build_module()

    def fail(**kwargs: Any) -> dict[str, Any]:
        raise failure

    monkeypatch.setattr(module, "build_stack", fail)
    result = module.main(
        [
            "--pyvider-version",
            "0.8.1",
            "--components-version",
            "0.8.0",
            "--output-dir",
            "/safe/output",
        ]
    )
    assert result == 2
    assert capsys.readouterr().err == "error: coordinated provider build failed\n"


def test_make_build_target_uses_only_public_coordinates() -> None:
    text = (SCRIPT.parents[1] / "Makefile").read_text(encoding="utf-8")
    target = text.split("build-linting-stack:", 1)[1].split(".PHONY: build-all", 1)[0]
    assert "--pyvider-version 0.8.1" in target
    assert "--components-version 0.8.0" in target
    assert "PYVIDER_SOURCE" not in target
    assert "COMPONENTS_SOURCE" not in target


def test_conformance_binary_target_is_a_no_rebuild_dry_run(tmp_path: Path) -> None:
    binary = tmp_path / "terraform-provider-pyvider_v0.6.0"
    binary.write_bytes(b"provider")
    result = subprocess.run(
        ["make", "-n", "test-conformance-binary", f"PYVIDER_CONFORMANCE_PSP={binary}", "MAKE=:"],
        cwd=SCRIPT.parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "flavor pack" not in result.stdout
    assert f'ci/warm-workenv.sh "{binary}"' in result.stdout
