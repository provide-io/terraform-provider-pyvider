#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""A local stand-in for the services the `pyvider_http_api` examples call.

The examples default to the public httpbin.org and JSONPlaceholder, so a test
run that uses them depends on two third parties' uptime and latency -- a slow
httpbin.org is what made the `delay/3` example flaky. They take their base URLs
from `var.api_base_url` and `var.json_api_base_url`, so a run can point them
here instead: `ci/with-http-api-stub.sh` starts this server and exports
`TF_VAR_api_base_url` / `TF_VAR_json_api_base_url`.

It answers the paths the examples use, in the shape they read:

- httpbin: `/get`, `/post`, `/put`, `/patch`, `/delete` (each echoing args,
  headers, url and body), `/delay/<n>`, `/bearer`, `/status/<code>`, and
  `OPTIONS` on any of them;
- JSONPlaceholder: `/users/<id>` and `/posts?userId=<id>`.

Standard library only, so a runner needs nothing installed. It binds an
ephemeral port and writes its base URL to `--url-file` once it is listening,
which is how the wrapper knows it is ready.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import socketserver
import sys
import time
from urllib.parse import parse_qs, urlsplit

# Loopback only: nothing outside this machine should reach a test fixture.
HOST = "127.0.0.1"
# 0 asks the OS for a free port, so nothing is hardcoded and parallel runs
# cannot collide.
PORT = 0
# `/delay/<n>` is capped well under the examples' 10-second timeout: the point
# is to exercise a slow response, not to make the run slow.
MAX_DELAY_SECONDS = 1.0

ECHO_METHODS = {"/get": "GET", "/post": "POST", "/put": "PUT", "/patch": "PATCH", "/delete": "DELETE"}

USER: dict[str, object] = {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "address": {
        "street": "Kulas Light",
        "suite": "Apt. 556",
        "city": "Gwenborough",
        "zipcode": "92998-3874",
        "geo": {"lat": "-37.3159", "lng": "81.1496"},
    },
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
        "name": "Romaguera-Crona",
        "catchPhrase": "Multi-layered client-server neural-net",
        "bs": "harness real-time e-markets",
    },
}

POSTS: list[dict[str, object]] = [
    {"userId": 1, "id": 1, "title": "sunt aut facere repellat provident", "body": "quia et suscipit"},
    {"userId": 1, "id": 2, "title": "qui est esse", "body": "est rerum tempore vitae"},
]

Query = dict[str, list[str]]


class Handler(BaseHTTPRequestHandler):
    """Routes one request to the httpbin- or JSONPlaceholder-shaped answer."""

    server_version = "pyvider-http-api-stub"

    def log_message(self, format: str, *args: object) -> None:
        # Quiet: the run's own output is what matters, and stir captures it.
        return

    def _send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_empty(self, status: int, **headers: str) -> None:
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _read_body(self) -> str:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length).decode("utf-8", "replace") if length else ""

    def _echo(self, query: Query) -> dict[str, object]:
        data = self._read_body()
        try:
            parsed: object = json.loads(data) if data else None
        except ValueError:
            parsed = None
        return {
            "args": {key: values[0] if len(values) == 1 else values for key, values in query.items()},
            "headers": dict(self.headers.items()),
            "origin": self.client_address[0],
            "url": f"http://{self.headers.get('Host', HOST)}{self.path}",
            "data": data,
            "json": parsed,
        }

    def _echo_method(self, path: str, query: Query) -> bool:
        expected = ECHO_METHODS.get(path)
        if expected is None:
            return False
        allowed = {expected, "HEAD"} if expected == "GET" else {expected}
        if self.command in allowed:
            self._send_json(200, self._echo(query))
        else:
            self._send_json(405, {"error": f"{path} accepts {expected}"})
        return True

    def _delay(self, path: str, query: Query) -> bool:
        match = re.fullmatch(r"/delay/(\d+(?:\.\d+)?)", path)
        if match is None:
            return False
        time.sleep(min(float(match.group(1)), MAX_DELAY_SECONDS))
        self._send_json(200, self._echo(query))
        return True

    def _bearer(self, path: str, query: Query) -> bool:
        if path != "/bearer":
            return False
        authorization = self.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            self._send_json(200, {"authenticated": True, "token": authorization[len("Bearer ") :]})
        else:
            self._send_json(401, {"authenticated": False})
        return True

    def _status(self, path: str, query: Query) -> bool:
        match = re.fullmatch(r"/status/(\d{3})", path)
        if match is None:
            return False
        self._send_empty(int(match.group(1)))
        return True

    def _user(self, path: str, query: Query) -> bool:
        match = re.fullmatch(r"/users/(\d+)", path)
        if match is None:
            return False
        if int(match.group(1)) == USER["id"]:
            self._send_json(200, USER)
        else:
            self._send_json(404, {})
        return True

    def _posts(self, path: str, query: Query) -> bool:
        if path != "/posts":
            return False
        wanted = query.get("userId")
        self._send_json(200, [post for post in POSTS if wanted is None or str(post["userId"]) == wanted[0]])
        return True

    def _route(self) -> None:
        split = urlsplit(self.path)
        path, query = split.path, parse_qs(split.query)
        if self.command == "OPTIONS":
            self._send_empty(200, Allow="GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS")
            return
        for answer in (self._echo_method, self._delay, self._bearer, self._status, self._user, self._posts):
            if answer(path, query):
                return
        self._send_json(404, {"error": f"no stub for {self.command} {path}"})

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _route


class StubServer(ThreadingHTTPServer):
    """A threading HTTP server that does not look up its own hostname.

    `HTTPServer.server_bind` sets `server_name` from `socket.getfqdn`, a
    reverse DNS lookup that can outlast the wrapper's readiness timeout on a
    macOS CI runner -- the server is alive but has not finished binding. This
    binds loopback by address and never uses the name.
    """

    def server_bind(self) -> None:
        socketserver.TCPServer.server_bind(self)
        self.server_name = HOST
        self.server_port = self.server_address[1]


def make_server() -> StubServer:
    """The stub, bound to a free loopback port."""
    return StubServer((HOST, PORT), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--url-file", required=True, type=Path, help="where to write the base URL once listening"
    )
    args = parser.parse_args(argv)

    server = make_server()
    port = server.server_address[1]
    # Written only after bind, so the file's existence means "ready".
    tmp = args.url_file.with_suffix(args.url_file.suffix + ".tmp")
    tmp.write_text(f"http://{HOST}:{port}\n", encoding="utf-8")
    tmp.replace(args.url_file)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
