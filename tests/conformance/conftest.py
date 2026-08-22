#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Fixtures for driving this repo's packaged provider.

Everything provider-specific lives here: where `make build` leaves the binary,
and the environment it needs. The driver itself is `tofusoup.tfplugin`, which
knows nothing about pyvider.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
import os
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from tofusoup.tfplugin import TfPluginProvider, base_env, start_provider

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: Terraform version the harness claims to be. 1.14+ is the first line that
#: drives list resources, so it is the honest thing to report.
CLAIMED_TERRAFORM_VERSION = "1.14.9"

#: Where `make build` leaves the packaged provider.
VERSION = (Path(__file__).resolve().parents[2] / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_PSP = (
    Path(__file__).resolve().parents[2] / "dist" / "darwin_arm64" / f"terraform-provider-pyvider_v{VERSION}"
)


def psp_path() -> Path:
    return Path(os.environ.get("PYVIDER_CONFORMANCE_PSP", str(DEFAULT_PSP)))


def child_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """The environment this provider needs to serve its full surface.

    The v6.11 demo components are registered `test_only`, and a provider schema
    is computed before ConfigureProvider runs, so the environment is the only
    signal that can reveal them in time.
    """
    env = {
        "PYVIDER_TESTMODE": "true",
        "PYVIDER_LOG_LEVEL": os.environ.get("PYVIDER_CONFORMANCE_LOG_LEVEL", "ERROR"),
    }
    if extra:
        env.update(extra)
    return base_env(env)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark the whole suite: it launches a real process and is not quick."""
    for item in items:
        item.add_marker(pytest.mark.conformance)


@pytest.fixture(scope="session")
def packaged_provider_path() -> Path:
    """Skip rather than fail when the provider has not been built.

    Set PYVIDER_CONFORMANCE_REQUIRED=1 in CI so a missing build is a failure
    instead of a silently green run that tested nothing.
    """
    path = psp_path()
    if not path.exists():
        message = f"packaged provider not found at {path}; run `make build`"
        if os.environ.get("PYVIDER_CONFORMANCE_REQUIRED"):
            pytest.fail(message)
        pytest.skip(message)
    return path


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def provider(packaged_provider_path: Path) -> AsyncIterator[TfPluginProvider]:
    """A configured provider process shared by the whole session.

    The RPC order mirrors Terraform's: schema first, then configure. Doing it in
    that order is part of what is under test -- the schema is computed once, at
    the moment it is first requested.
    """
    session = await start_provider(packaged_provider_path, env=child_env())
    try:
        session.schema = await session.stub.GetProviderSchema(pb.GetProviderSchema.Request())
        await session.stub.ConfigureProvider(
            pb.ConfigureProvider.Request(
                terraform_version=CLAIMED_TERRAFORM_VERSION,
                config=session.provider_config(),
                client_capabilities=pb.ClientCapabilities(
                    deferral_allowed=True,
                    write_only_attributes_allowed=True,
                ),
            )
        )
        yield session
    finally:
        await session.stop()


@pytest_asyncio.fixture(loop_scope="session")
async def spawn_provider(packaged_provider_path: Path) -> AsyncIterator[Callable[..., Any]]:
    """Start extra provider processes, e.g. to contend for a state-store lock."""
    started: list[TfPluginProvider] = []

    async def _spawn(**extra_env: str) -> TfPluginProvider:
        session = await start_provider(packaged_provider_path, env=child_env(extra_env or None))
        session.schema = await session.stub.GetProviderSchema(pb.GetProviderSchema.Request())
        await session.stub.ConfigureProvider(
            pb.ConfigureProvider.Request(
                terraform_version=CLAIMED_TERRAFORM_VERSION,
                config=session.provider_config(),
            )
        )
        started.append(session)
        return session

    try:
        yield _spawn
    finally:
        for session in started:
            await session.stop()


# 🧪🔌🔚
