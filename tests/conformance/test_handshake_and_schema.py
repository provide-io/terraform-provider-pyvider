#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Handshake, protocol negotiation, and the discovery RPCs.

Everything else in this suite depends on these passing, so they assert the
things that would otherwise produce confusing downstream failures: that the
negotiated protocol really is 6, that the transport is what the handshake
advertised, and that the two discovery RPCs agree about what exists.
"""

from __future__ import annotations

import pytest
from tofusoup.tfplugin import TfPluginProvider, errors

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: The provider process, its gRPC channel, and every stub call must share the
#: loop the session-scoped fixture created them on. Without this the default
#: loop-per-test hands each test a channel bound to an already-closed loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")

#: The v6.11 features this branch exists to deliver, and the demo components
#: registered for each. Discovery must surface all of them.
EXPECTED_ACTIONS = {"pyvider_echo", "pyvider_failing_action", "pyvider_wait_for_file"}
EXPECTED_LIST_RESOURCES = {"pyvider_secret_note", "pyvider_directory_entry"}
EXPECTED_STATE_STORES = {"pyvider_filesystem_store"}


async def test_negotiates_protocol_six(provider: TfPluginProvider) -> None:
    """A v6.11 provider must land on protocol 6, not fall back to 1.

    The default when nothing is offered is version 1, so this catches a
    provider that ignored PLUGIN_PROTOCOL_VERSIONS entirely.
    """
    assert provider.protocol_version == 6


async def test_serves_over_the_advertised_transport(provider: TfPluginProvider) -> None:
    """The handshake names a transport and the channel must actually use it."""
    assert provider.transport in {"unix", "tcp"}


async def test_server_capabilities_are_advertised_on_get_provider_schema(
    provider: TfPluginProvider,
) -> None:
    """Terraform reads these flags from GetProviderSchema, nowhere else.

    GetMetadata carries the same flags but the proto marks that RPC unused, so
    advertising them only there means MoveResourceState and
    GenerateResourceConfig are implemented and never called.
    """
    assert provider.schema is not None
    capabilities = provider.schema.server_capabilities

    assert capabilities.plan_destroy is True
    assert capabilities.get_provider_schema_optional is True
    assert capabilities.move_resource_state is True
    assert capabilities.generate_resource_config is True


async def test_schema_response_carries_no_errors(provider: TfPluginProvider) -> None:
    """A schema built with error diagnostics is not a usable schema."""
    assert provider.schema is not None
    assert not errors(provider.schema.diagnostics)


async def test_action_schemas_are_published(provider: TfPluginProvider) -> None:
    """Actions are new in v6.11 and must appear as ActionSchema entries."""
    assert provider.schema is not None
    assert set(provider.schema.action_schemas) >= EXPECTED_ACTIONS


async def test_list_resource_schemas_are_published(provider: TfPluginProvider) -> None:
    """List resources are new in v6.11 and drive `terraform query`."""
    assert provider.schema is not None
    assert set(provider.schema.list_resource_schemas) >= EXPECTED_LIST_RESOURCES


async def test_state_store_schemas_are_published(provider: TfPluginProvider) -> None:
    """State stores are new in v6.11 and are selected in the terraform block."""
    assert provider.schema is not None
    assert set(provider.schema.state_store_schemas) >= EXPECTED_STATE_STORES


async def test_action_schema_declares_its_attributes(provider: TfPluginProvider) -> None:
    """An action with no attributes cannot be configured from HCL."""
    assert provider.schema is not None
    echo = provider.schema.action_schemas["pyvider_echo"]
    names = {a.name for a in echo.schema.block.attributes}

    assert {"message", "path", "repeat", "defer"} <= names


async def test_metadata_and_schema_agree(provider: TfPluginProvider) -> None:
    """A type in GetMetadata with no schema is a type Terraform cannot use.

    The two RPCs are built from separate code paths, so they can drift; when
    they do, the failure surfaces far downstream as a missing schema.
    """
    assert provider.schema is not None
    metadata = await provider.stub.GetMetadata(pb.GetMetadata.Request())

    assert {a.type_name for a in metadata.actions} == set(provider.schema.action_schemas)
    assert {r.type_name for r in metadata.list_resources} == set(provider.schema.list_resource_schemas)
    assert {s.type_name for s in metadata.state_stores} == set(provider.schema.state_store_schemas)
    assert {r.type_name for r in metadata.resources} == set(provider.schema.resource_schemas)
    assert {d.type_name for d in metadata.data_sources} == set(provider.schema.data_source_schemas)


async def test_metadata_repeats_the_server_capabilities(provider: TfPluginProvider) -> None:
    """terraform-plugin-mux reads the flags here; the two must not disagree."""
    assert provider.schema is not None
    metadata = await provider.stub.GetMetadata(pb.GetMetadata.Request())

    assert metadata.server_capabilities.plan_destroy == provider.schema.server_capabilities.plan_destroy
    assert (
        metadata.server_capabilities.move_resource_state
        == provider.schema.server_capabilities.move_resource_state
    )


async def test_provider_config_validates(provider: TfPluginProvider) -> None:
    """ValidateProviderConfig runs before configure and must accept the block."""
    response = await provider.stub.ValidateProviderConfig(
        pb.ValidateProviderConfig.Request(config=provider.provider_config())
    )

    assert not errors(response.diagnostics)


# 🧪🔌🔚
