#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The v6.11 list-resource RPCs: ValidateListResourceConfig and ListResource.

ListResource is a server-streaming RPC backing `terraform query`. The parts
worth proving over a real socket are the ones a single-process unit test can
fake: that results stream with identity attached, that `limit` actually stops
the stream, and that `include_resource_object` is honoured rather than ignored.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from tofusoup.tfplugin import TfPluginProvider, diagnostic_text, errors, pack, unpack

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: The provider process, its gRPC channel, and every stub call must share the
#: loop the session-scoped fixture created them on. Without this the default
#: loop-per-test hands each test a channel bound to an already-closed loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")

DIRECTORY_ENTRY = "pyvider_directory_entry"


def directory_config(path: Path, suffix: str | None = None, include_hidden: bool | None = None) -> Any:
    return pack({"path": str(path), "suffix": suffix, "include_hidden": include_hidden})


async def collect(provider: TfPluginProvider, request: pb.ListResource.Request) -> list[pb.ListResource.Event]:
    return [event async for event in provider.stub.ListResource(request)]


def identities(events: list[pb.ListResource.Event]) -> list[dict[str, Any]]:
    return [unpack(e.identity.identity_data) for e in events if e.HasField("identity")]


def populated_dir(root: Path) -> Path:
    """A directory with a predictable, sorted set of files."""
    root.mkdir(parents=True, exist_ok=True)
    for name in ("alpha.txt", "beta.txt", "gamma.log", ".hidden.txt"):
        (root / name).write_text(name, encoding="utf-8")
    (root / "subdir").mkdir(exist_ok=True)
    return root


async def test_validate_accepts_a_well_formed_config(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateListResourceConfig(
        pb.ValidateListResourceConfig.Request(type_name=DIRECTORY_ENTRY, config=directory_config(tmp_path))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_validate_rejects_a_missing_required_attribute(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateListResourceConfig(
        pb.ValidateListResourceConfig.Request(
            type_name=DIRECTORY_ENTRY,
            config=pack({"path": None, "suffix": None, "include_hidden": None}),
        )
    )

    assert errors(response.diagnostics)


async def test_validate_rejects_a_non_directory(provider: TfPluginProvider, tmp_path: Path) -> None:
    """The list resource validates its own config, not just its schema."""
    target = tmp_path / "a-file.txt"
    target.write_text("not a directory", encoding="utf-8")

    response = await provider.stub.ValidateListResourceConfig(
        pb.ValidateListResourceConfig.Request(type_name=DIRECTORY_ENTRY, config=directory_config(target))
    )

    assert errors(response.diagnostics)


async def test_unknown_list_resource_type_reports_a_diagnostic(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateListResourceConfig(
        pb.ValidateListResourceConfig.Request(type_name="pyvider_not_a_list", config=pack({}))
    )

    found = errors(response.diagnostics)
    assert found
    assert "pyvider_not_a_list" in diagnostic_text(found)


async def test_streams_one_event_per_matching_entry(provider: TfPluginProvider, tmp_path: Path) -> None:
    """Non-files, subdirectories, and dotfiles are excluded by default."""
    root = populated_dir(tmp_path / "listing")

    events = await collect(
        provider, pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root))
    )

    names = [Path(i["path"]).name for i in identities(events)]
    assert names == ["alpha.txt", "beta.txt", "gamma.log"]


async def test_identity_is_attached_to_every_result(provider: TfPluginProvider, tmp_path: Path) -> None:
    """Identity is how Terraform addresses a listed object; it cannot be empty."""
    root = populated_dir(tmp_path / "identity")

    events = await collect(
        provider, pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root))
    )

    assert events
    for event in events:
        assert event.HasField("identity")
        assert unpack(event.identity.identity_data)["path"]
        assert event.display_name


async def test_suffix_filter_is_applied(provider: TfPluginProvider, tmp_path: Path) -> None:
    root = populated_dir(tmp_path / "filtered")

    events = await collect(
        provider,
        pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root, suffix=".log")),
    )

    names = [Path(i["path"]).name for i in identities(events)]
    assert names == ["gamma.log"]


async def test_include_hidden_widens_the_listing(provider: TfPluginProvider, tmp_path: Path) -> None:
    root = populated_dir(tmp_path / "hidden")

    events = await collect(
        provider,
        pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root, include_hidden=True)),
    )

    names = [Path(i["path"]).name for i in identities(events)]
    assert ".hidden.txt" in names


async def test_limit_stops_the_stream(provider: TfPluginProvider, tmp_path: Path) -> None:
    """`limit` is a hard stop, not a hint. Terraform stops reading at it."""
    root = populated_dir(tmp_path / "limited")

    events = await collect(
        provider,
        pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root), limit=2),
    )

    assert len(events) == 2


async def test_resource_object_is_omitted_unless_requested(provider: TfPluginProvider, tmp_path: Path) -> None:
    """Sending the full object unasked wastes bandwidth on every query."""
    root = populated_dir(tmp_path / "no-object")

    events = await collect(
        provider, pb.ListResource.Request(type_name=DIRECTORY_ENTRY, config=directory_config(root))
    )

    assert events
    assert not any(e.HasField("resource_object") for e in events)


async def test_resource_object_is_included_when_requested(provider: TfPluginProvider, tmp_path: Path) -> None:
    root = populated_dir(tmp_path / "with-object")

    events = await collect(
        provider,
        pb.ListResource.Request(
            type_name=DIRECTORY_ENTRY, config=directory_config(root), include_resource_object=True
        ),
    )

    assert events
    for event in events:
        assert event.HasField("resource_object")
        obj = unpack(event.resource_object)
        assert obj["name"]
        assert obj["size_bytes"] is not None


async def test_a_list_resource_type_should_match_a_managed_resource_type(
    provider: TfPluginProvider,
) -> None:
    """Terraform resolves a list block's identity via a *managed* resource type.

    `terraform query` looks the identity schema up under the list block's type
    name in its cached provider schema, and that lookup only covers managed
    resources -- it never calls GetResourceIdentitySchemas at all. A list
    resource with no managed counterpart therefore fails the whole query with
    "Identity schema not found for resource type ...", no matter what the
    provider publishes. Measured on Terraform 1.17.0-alpha20260812.

    `pyvider_secret_note` satisfies this (its list resource borrows the managed
    resource's schemas via `resource_type=`); `pyvider_directory_entry` does
    not, and is usable at the protocol level only.
    """
    assert provider.schema is not None

    borrowed = "pyvider_secret_note"
    assert borrowed in provider.schema.list_resource_schemas
    assert borrowed in provider.schema.resource_schemas, (
        "a list resource Terraform can query must share its name with a managed resource"
    )

    # Pinned as the known CLI-level gap rather than silently tolerated.
    assert DIRECTORY_ENTRY in provider.schema.list_resource_schemas
    assert DIRECTORY_ENTRY not in provider.schema.resource_schemas


async def test_absent_directory_lists_nothing_without_erroring(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """A directory that does not exist yet is an empty result, not a failure."""
    events = await collect(
        provider,
        pb.ListResource.Request(
            type_name=DIRECTORY_ENTRY, config=directory_config(tmp_path / "never-created")
        ),
    )

    assert events == []


# 🧪🔌🔚
