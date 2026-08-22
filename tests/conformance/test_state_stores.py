#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The v6.11 pluggable state-store RPCs.

A state store is where Terraform keeps state, so the bar is higher than "the
calls return without error": a lock must actually exclude a second holder, and
a chunked write must reassemble byte-for-byte. Both are asserted here through
the packaged binary, including across two separate provider processes.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from tofusoup.tfplugin import TfPluginProvider, diagnostic_text, errors, pack

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: The provider process, its gRPC channel, and every stub call must share the
#: loop the session-scoped fixture created them on. Without this the default
#: loop-per-test hands each test a channel bound to an already-closed loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")

STORE = "pyvider_filesystem_store"

#: Small enough that a modest payload spans several chunks, so the chunking
#: path is genuinely exercised rather than degenerating to a single write.
CLIENT_CHUNK_SIZE = 8


def store_config(path: Path) -> Any:
    return pack({"path": str(path)})


async def configure_store(provider: TfPluginProvider, path: Path) -> pb.ConfigureStateStore.Response:
    # The generated gRPC stub is untyped, so the await returns Any. Naming the
    # type here is what makes the helper's annotation mean something.
    response: pb.ConfigureStateStore.Response = await provider.stub.ConfigureStateStore(
        pb.ConfigureStateStore.Request(
            type_name=STORE,
            config=store_config(path),
            capabilities=pb.StateStoreClientCapabilities(chunk_size=CLIENT_CHUNK_SIZE),
        )
    )
    return response


async def write_state(
    provider: TfPluginProvider, state_id: str, payload: bytes, chunk_size: int
) -> pb.WriteStateBytes.Response:
    """Stream a payload in chunks the way Terraform Core does."""

    async def chunks() -> AsyncIterator[pb.WriteStateBytes.RequestChunk]:
        total = len(payload)
        first = True
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = pb.WriteStateBytes.RequestChunk(
                bytes=payload[start:end],
                total_length=total,
                range=pb.StateRange(start=start, end=end),
            )
            if first:
                # meta rides on the first chunk only
                chunk.meta.CopyFrom(pb.RequestChunkMeta(type_name=STORE, state_id=state_id))
                first = False
            yield chunk

    response: pb.WriteStateBytes.Response = await provider.stub.WriteStateBytes(chunks())
    return response


async def read_state(provider: TfPluginProvider, state_id: str) -> tuple[bytes, list[Any]]:
    """Reassemble a chunked read back into the original payload."""
    buffer = bytearray()
    diagnostics: list[Any] = []
    async for response in provider.stub.ReadStateBytes(
        pb.ReadStateBytes.Request(type_name=STORE, state_id=state_id)
    ):
        buffer.extend(response.bytes)
        diagnostics.extend(response.diagnostics)
    return bytes(buffer), diagnostics


async def test_validate_accepts_a_configured_path(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateStateStoreConfig(
        pb.ValidateStateStore.Request(type_name=STORE, config=store_config(tmp_path / "states"))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_validate_rejects_a_missing_path(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateStateStoreConfig(
        pb.ValidateStateStore.Request(type_name=STORE, config=pack({"path": None}))
    )

    assert errors(response.diagnostics)


async def test_unknown_state_store_falls_back_to_the_default_backend(
    provider: TfPluginProvider,
) -> None:
    """State stores deliberately differ from actions and list resources here.

    Those two reject an unregistered type name with a diagnostic. A state store
    instead resolves through ``StateStoreManager``, which builds the
    environment-configured default backend for any name it does not recognise,
    so validation succeeds. Terraform validates the ``state_store`` block
    against ``state_store_schemas`` before it ever calls this RPC, so an
    unknown name is not reachable from a real CLI run — but the asymmetry is
    deliberate and worth pinning rather than discovering later.
    """
    response = await provider.stub.ValidateStateStoreConfig(
        pb.ValidateStateStore.Request(type_name="pyvider_not_a_store", config=pack({}))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_configure_negotiates_a_chunk_size(provider: TfPluginProvider, tmp_path: Path) -> None:
    """The plugin chooses the chunk size; Core only suggests one."""
    response = await configure_store(provider, tmp_path / "chunked")

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert response.capabilities.chunk_size > 0


async def test_lock_write_read_unlock_round_trip(provider: TfPluginProvider, tmp_path: Path) -> None:
    """The full sequence a Terraform apply performs against a state store."""
    root = tmp_path / "roundtrip"
    await configure_store(provider, root)
    payload = b'{"version":4,"serial":7,"lineage":"conformance"}'

    lock = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="prod", operation="apply")
    )
    assert not errors(lock.diagnostics), diagnostic_text(lock.diagnostics)
    assert lock.lock_id

    written = await write_state(provider, "prod", payload, CLIENT_CHUNK_SIZE)
    assert not errors(written.diagnostics), diagnostic_text(written.diagnostics)

    read_back, diagnostics = await read_state(provider, "prod")
    assert not errors(diagnostics), diagnostic_text(diagnostics)
    assert read_back == payload

    unlock = await provider.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="prod", lock_id=lock.lock_id)
    )
    assert not errors(unlock.diagnostics), diagnostic_text(unlock.diagnostics)


async def test_a_payload_larger_than_the_chunk_size_survives_intact(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """Chunk reassembly is the part most likely to silently corrupt state."""
    await configure_store(provider, tmp_path / "large")
    payload = bytes(range(256)) * 40  # 10 KiB of non-repeating byte values

    lock = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="big", operation="apply")
    )
    await write_state(provider, "big", payload, CLIENT_CHUNK_SIZE)
    read_back, _ = await read_state(provider, "big")
    await provider.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="big", lock_id=lock.lock_id)
    )

    assert read_back == payload


async def test_get_states_lists_what_was_written(provider: TfPluginProvider, tmp_path: Path) -> None:
    await configure_store(provider, tmp_path / "listing")

    for state_id in ("alpha", "beta"):
        lock = await provider.stub.LockState(
            pb.LockState.Request(type_name=STORE, state_id=state_id, operation="apply")
        )
        await write_state(provider, state_id, b"{}", CLIENT_CHUNK_SIZE)
        await provider.stub.UnlockState(
            pb.UnlockState.Request(type_name=STORE, state_id=state_id, lock_id=lock.lock_id)
        )

    response = await provider.stub.GetStates(pb.GetStates.Request(type_name=STORE))

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert {"alpha", "beta"} <= set(response.state_id)


async def test_delete_state_removes_it(provider: TfPluginProvider, tmp_path: Path) -> None:
    await configure_store(provider, tmp_path / "deletion")

    lock = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="doomed", operation="apply")
    )
    await write_state(provider, "doomed", b"{}", CLIENT_CHUNK_SIZE)
    await provider.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="doomed", lock_id=lock.lock_id)
    )

    deleted = await provider.stub.DeleteState(pb.DeleteState.Request(type_name=STORE, state_id="doomed"))
    assert not errors(deleted.diagnostics), diagnostic_text(deleted.diagnostics)

    remaining = await provider.stub.GetStates(pb.GetStates.Request(type_name=STORE))
    assert "doomed" not in set(remaining.state_id)


async def test_a_second_process_cannot_take_a_held_lock(
    provider: TfPluginProvider, spawn_provider: Any, tmp_path: Path
) -> None:
    """The lock must exclude a genuinely separate OS process.

    Two threads in one process can be excluded by a Python lock that would do
    nothing for the real case: two `terraform apply` runs on one machine.
    """
    root = tmp_path / "contended"
    await configure_store(provider, root)

    other = await spawn_provider()
    await configure_store(other, root)

    held = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="shared", operation="apply")
    )
    assert held.lock_id

    contender = await other.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="shared", operation="apply")
    )

    try:
        assert errors(contender.diagnostics), "a second process took a lock that was already held"
        assert not contender.lock_id
    finally:
        await provider.stub.UnlockState(
            pb.UnlockState.Request(type_name=STORE, state_id="shared", lock_id=held.lock_id)
        )


async def test_a_released_lock_can_be_retaken_by_another_process(
    provider: TfPluginProvider, spawn_provider: Any, tmp_path: Path
) -> None:
    """Exclusion that never releases is a deadlock, not a lock."""
    root = tmp_path / "released"
    await configure_store(provider, root)

    other = await spawn_provider()
    await configure_store(other, root)

    first = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="handover", operation="apply")
    )
    await provider.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="handover", lock_id=first.lock_id)
    )

    second = await other.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="handover", operation="apply")
    )

    assert not errors(second.diagnostics), diagnostic_text(second.diagnostics)
    assert second.lock_id

    await other.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="handover", lock_id=second.lock_id)
    )


async def test_state_written_by_one_process_is_visible_to_another(
    provider: TfPluginProvider, spawn_provider: Any, tmp_path: Path
) -> None:
    """Durability is the whole point: state must outlive the writing process.

    This also proves flavorpack passes PYVIDER_* through to the packaged
    binary, since both processes resolve the same directory from config.
    """
    root = tmp_path / "durable"
    await configure_store(provider, root)
    payload = b'{"written_by":"first_process"}'

    lock = await provider.stub.LockState(
        pb.LockState.Request(type_name=STORE, state_id="shared_state", operation="apply")
    )
    await write_state(provider, "shared_state", payload, CLIENT_CHUNK_SIZE)
    await provider.stub.UnlockState(
        pb.UnlockState.Request(type_name=STORE, state_id="shared_state", lock_id=lock.lock_id)
    )

    other = await spawn_provider()
    await configure_store(other, root)
    read_back, diagnostics = await read_state(other, "shared_state")

    assert not errors(diagnostics), diagnostic_text(diagnostics)
    assert read_back == payload


# 🧪🔌🔚
