#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The ephemeral resource RPCs over the packaged binary.

Ephemeral resources carry private state between three separate RPCs, and that
state crosses the msgpack boundary and an encryption step every time. A resource
that works in-process can still lose it here, and the symptom -- a renew or
close that quietly acts on the wrong lease -- is invisible without checking the
side effect.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from tofusoup.tfplugin import TfPluginProvider, diagnostic_text, errors, pack

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: The provider process, its gRPC channel, and every stub call must share the
#: loop the session-scoped fixture created them on. Without this the default
#: loop-per-test hands each test a channel bound to an already-closed loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")

LEASE = "pyvider_lease"


def lease_config(name: str, path: Path, ttl_seconds: int | None = None) -> Any:
    return pack(
        {
            "name": name,
            "path": str(path),
            "ttl_seconds": ttl_seconds,
            "lease_id": None,
            "expires_at": None,
        }
    )


async def open_lease(provider: TfPluginProvider, name: str, path: Path) -> Any:
    return await provider.stub.OpenEphemeralResource(
        pb.OpenEphemeralResource.Request(type_name=LEASE, config=lease_config(name, path))
    )


async def test_ephemeral_schema_is_published(provider: TfPluginProvider) -> None:
    """An ephemeral resource absent from the schema cannot be used at all."""
    assert provider.schema is not None
    assert LEASE in provider.schema.ephemeral_resource_schemas

    names = {a.name for a in provider.schema.ephemeral_resource_schemas[LEASE].block.attributes}
    assert {"name", "path", "ttl_seconds", "lease_id", "expires_at"} <= names


async def test_validate_accepts_a_well_formed_config(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateEphemeralResourceConfig(
        pb.ValidateEphemeralResourceConfig.Request(
            type_name=LEASE, config=lease_config("alpha", tmp_path / "a.lease")
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_validate_rejects_a_non_positive_ttl(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateEphemeralResourceConfig(
        pb.ValidateEphemeralResourceConfig.Request(
            type_name=LEASE, config=lease_config("alpha", tmp_path / "a.lease", ttl_seconds=0)
        )
    )

    assert errors(response.diagnostics)


async def test_unknown_ephemeral_type_reports_a_diagnostic(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateEphemeralResourceConfig(
        pb.ValidateEphemeralResourceConfig.Request(type_name="pyvider_no_such_ephemeral", config=pack({}))
    )

    assert errors(response.diagnostics)


async def test_open_takes_the_lease_and_returns_a_deadline(provider: TfPluginProvider, tmp_path: Path) -> None:
    """A success that did not take the lease is the failure worth catching."""
    target = tmp_path / "opened.lease"

    response = await open_lease(provider, "alpha", target)

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert target.exists()
    assert response.renew_at.seconds > 0
    assert response.private, "no private state: renew and close cannot identify the lease"


async def test_renew_survives_the_private_state_round_trip(provider: TfPluginProvider, tmp_path: Path) -> None:
    """Private state crosses the wire encrypted; renew must still resolve it."""
    target = tmp_path / "renewed.lease"
    opened = await open_lease(provider, "alpha", target)

    renewed = await provider.stub.RenewEphemeralResource(
        pb.RenewEphemeralResource.Request(type_name=LEASE, private=opened.private)
    )

    assert not errors(renewed.diagnostics), diagnostic_text(renewed.diagnostics)
    assert renewed.renew_at.seconds > 0
    assert "renewed" in target.read_text(encoding="utf-8")


async def test_repeated_renewals_accumulate_across_the_boundary(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """Each renewal must build on the previous one's returned private state.

    If the round trip drops the counter, every renewal writes #1 and the loss is
    silent -- the RPCs all still succeed.
    """
    target = tmp_path / "many.lease"
    opened = await open_lease(provider, "alpha", target)

    private = opened.private
    for _ in range(3):
        renewed = await provider.stub.RenewEphemeralResource(
            pb.RenewEphemeralResource.Request(type_name=LEASE, private=private)
        )
        private = renewed.private

    lines = [line for line in target.read_text(encoding="utf-8").splitlines() if "renewed" in line]
    assert [line.rsplit("#", 1)[-1] for line in lines] == ["1", "2", "3"]


async def test_close_releases_the_lease(provider: TfPluginProvider, tmp_path: Path) -> None:
    target = tmp_path / "closed.lease"
    opened = await open_lease(provider, "alpha", target)

    response = await provider.stub.CloseEphemeralResource(
        pb.CloseEphemeralResource.Request(type_name=LEASE, private=opened.private)
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert not target.exists(), "close left the lease behind"


async def test_the_full_lifecycle_leaves_nothing_behind(provider: TfPluginProvider, tmp_path: Path) -> None:
    """open -> renew -> close, the sequence a real Terraform run performs."""
    target = tmp_path / "lifecycle.lease"

    opened = await open_lease(provider, "alpha", target)
    renewed = await provider.stub.RenewEphemeralResource(
        pb.RenewEphemeralResource.Request(type_name=LEASE, private=opened.private)
    )
    closed = await provider.stub.CloseEphemeralResource(
        pb.CloseEphemeralResource.Request(type_name=LEASE, private=renewed.private)
    )

    assert not errors(closed.diagnostics), diagnostic_text(closed.diagnostics)
    assert not target.exists()


# 🧪🔌🔚
