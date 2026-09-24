# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""The local server the http_api examples run against, and its wrapper."""

from __future__ import annotations

from collections.abc import Iterator
from email.message import Message
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "ci" / "http_api_stub.py"
WRAPPER = ROOT / "ci" / "with-http-api-stub.sh"


@pytest.fixture
def base_url(tmp_path: Path) -> Iterator[str]:
    url_file = tmp_path / "url"
    process = subprocess.Popen([sys.executable, str(STUB), "--url-file", str(url_file)])
    try:
        deadline = time.monotonic() + 10
        while not url_file.exists():
            assert process.poll() is None, "stub exited before it was ready"
            assert time.monotonic() < deadline, "stub not ready"
            time.sleep(0.05)
        yield url_file.read_text(encoding="utf-8").strip()
    finally:
        process.terminate()
        process.wait(timeout=10)


def request(
    url: str, method: str = "GET", headers: dict[str, str] | None = None, body: bytes | None = None
) -> tuple[int, Message, bytes]:
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def test_it_listens_on_loopback_on_a_free_port(base_url: str) -> None:
    assert base_url.startswith("http://127.0.0.1:")
    assert not base_url.endswith(":0")


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_each_echo_path_answers_its_method(base_url: str, method: str) -> None:
    status, headers, body = request(f"{base_url}/{method.lower()}?a=1", method, {"X-Probe": "yes"})
    assert status == 200
    assert headers["Content-Type"] == "application/json"
    payload = json.loads(body)
    assert payload["args"] == {"a": "1"}
    assert payload["headers"]["X-Probe"] == "yes"


def test_an_echo_path_refuses_another_method(base_url: str) -> None:
    status, _, _ = request(f"{base_url}/post", "GET")
    assert status == 405


def test_a_json_body_is_echoed_parsed(base_url: str) -> None:
    status, _, body = request(
        f"{base_url}/post", "POST", {"Content-Type": "application/json"}, json.dumps({"k": "v"}).encode()
    )
    assert status == 200
    assert json.loads(body)["json"] == {"k": "v"}


def test_options_lists_the_methods(base_url: str) -> None:
    status, headers, _ = request(f"{base_url}/get", "OPTIONS")
    assert status == 200
    assert "PATCH" in headers["Allow"]


def test_delay_is_capped(base_url: str) -> None:
    started = time.monotonic()
    status, _, _ = request(f"{base_url}/delay/3")
    assert status == 200
    assert time.monotonic() - started < 3


def test_bearer_needs_a_token(base_url: str) -> None:
    assert request(f"{base_url}/bearer")[0] == 401
    status, _, body = request(f"{base_url}/bearer", headers={"Authorization": "Bearer abc"})
    assert status == 200
    assert json.loads(body) == {"authenticated": True, "token": "abc"}


@pytest.mark.parametrize("code", [401, 404, 500])
def test_status_returns_that_code(base_url: str, code: int) -> None:
    assert request(f"{base_url}/status/{code}")[0] == code


def test_the_json_api_paths(base_url: str) -> None:
    status, _, body = request(f"{base_url}/users/1")
    assert status == 200
    assert json.loads(body)["id"] == 1
    status, _, body = request(f"{base_url}/posts?userId=1")
    posts = json.loads(body)
    assert status == 200 and posts and all(post["userId"] == 1 for post in posts)
    assert posts[0]["title"]


def test_an_unknown_path_is_a_404(base_url: str) -> None:
    assert request(f"{base_url}/nothing-here")[0] == 404


def test_the_wrapper_points_both_variables_at_the_server_and_stops_it() -> None:
    probe = (
        "import os, urllib.request;"
        "a = os.environ['TF_VAR_api_base_url']; j = os.environ['TF_VAR_json_api_base_url'];"
        "assert a == j and a.startswith('http://127.0.0.1:');"
        "urllib.request.urlopen(a + '/get', timeout=10).read();"
        "print(a)"
    )
    result = subprocess.run(
        ["bash", str(WRAPPER), sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "TF_VAR_api_base_url": "", "TF_VAR_json_api_base_url": ""},
    )
    served = result.stdout.strip()
    # Once the wrapper returns, nothing is listening there any more.
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(served + "/get", timeout=2)


def test_the_wrapper_passes_the_command_exit_status_through() -> None:
    result = subprocess.run(["bash", str(WRAPPER), "sh", "-c", "exit 7"], capture_output=True, text=True)
    assert result.returncode == 7


def test_starting_does_not_resolve_a_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    # HTTPServer.server_bind calls socket.getfqdn, a reverse DNS lookup that
    # can outlast the wrapper's readiness timeout on a macOS runner. The stub
    # binds loopback by address and never needs the name.
    import socket

    sys.path.insert(0, str(STUB.parent))
    try:
        import http_api_stub
    finally:
        sys.path.remove(str(STUB.parent))

    def refuse(*_: object) -> str:
        raise AssertionError("getfqdn called")

    monkeypatch.setattr(socket, "getfqdn", refuse)
    server = http_api_stub.make_server()
    try:
        assert server.server_address[0] == http_api_stub.HOST
    finally:
        server.server_close()
