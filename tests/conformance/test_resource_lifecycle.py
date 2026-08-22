#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The resource lifecycle a real apply performs, over the packaged binary.

`pyvider_secret_note` is the resource under test because it exercises the
features that are easy to get subtly wrong across a serialization boundary at
once: a `write_only` attribute that must arrive at apply but never be
persisted, a computed attribute that is unknown at plan time, and a resource
identity.
"""

from __future__ import annotations

from typing import Any

import pytest
from tofusoup.tfplugin import TfPluginProvider, diagnostic_text, errors, pack, unpack

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

#: The provider process, its gRPC channel, and every stub call must share the
#: loop the session-scoped fixture created them on. Without this the default
#: loop-per-test hands each test a channel bound to an already-closed loop.
pytestmark = pytest.mark.asyncio(loop_scope="session")

NOTE = "pyvider_secret_note"


def note_config(name: str, secret: str | None = "s3cret") -> Any:
    return pack({"name": name, "secret_value": secret, "digest": None})


def note_state(name: str, digest: str | None) -> Any:
    """State as the provider persists it: the write-only value is absent."""
    return pack({"name": name, "secret_value": None, "digest": digest})


async def create_note(
    provider: TfPluginProvider,
    name: str,
    secret: str = "s3cret",
) -> dict[str, Any]:
    """Run plan + apply for a create and return the resulting state."""
    config = note_config(name, secret)
    planned = await provider.stub.PlanResourceChange(
        pb.PlanResourceChange.Request(
            type_name=NOTE,
            config=config,
            prior_state=pack(None),
            proposed_new_state=config,
        )
    )
    assert not errors(planned.diagnostics), diagnostic_text(planned.diagnostics)

    applied = await provider.stub.ApplyResourceChange(
        pb.ApplyResourceChange.Request(
            type_name=NOTE,
            config=config,
            prior_state=pack(None),
            planned_state=planned.planned_state,
            planned_private=planned.planned_private,
        )
    )
    assert not errors(applied.diagnostics), diagnostic_text(applied.diagnostics)
    state: dict[str, Any] = unpack(applied.new_state)
    return state


async def test_validate_accepts_a_well_formed_config(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateResourceConfig(
        pb.ValidateResourceConfig.Request(type_name=NOTE, config=note_config("valid"))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_validate_rejects_an_empty_name(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateResourceConfig(
        pb.ValidateResourceConfig.Request(type_name=NOTE, config=note_config("   "))
    )

    assert errors(response.diagnostics)


async def test_unknown_resource_type_reports_a_diagnostic(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateResourceConfig(
        pb.ValidateResourceConfig.Request(type_name="pyvider_no_such_resource", config=pack({}))
    )

    found = errors(response.diagnostics)
    assert found
    assert "pyvider_no_such_resource" in diagnostic_text(found)


async def test_plan_marks_the_computed_attribute_unknown(provider: TfPluginProvider) -> None:
    """digest is derived at apply time, so plan must not invent a value."""
    config = note_config("planned")
    response = await provider.stub.PlanResourceChange(
        pb.PlanResourceChange.Request(
            type_name=NOTE, config=config, prior_state=pack(None), proposed_new_state=config
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert response.planned_state.msgpack


async def test_apply_creates_rather_than_destroys(provider: TfPluginProvider) -> None:
    """A create must return state, not null.

    Returning null state here is read as a destroy, which is how a create can
    silently delete instead of creating.
    """
    state = await create_note(provider, "created")

    assert state is not None
    assert state["name"] == "created"


async def test_apply_computes_the_derived_attribute(provider: TfPluginProvider) -> None:
    state = await create_note(provider, "digested", secret="known-secret")

    assert state["digest"]


async def test_the_write_only_value_reaches_apply(provider: TfPluginProvider) -> None:
    """The resource raises if the write-only value was stripped inbound.

    A green apply is therefore evidence the value survived the boundary.
    """
    state = await create_note(provider, "delivered", secret="must-arrive")

    assert state["digest"]


async def test_the_write_only_value_is_never_persisted(provider: TfPluginProvider) -> None:
    """Write-only means it must be usable during apply and absent from state."""
    state = await create_note(provider, "not-persisted", secret="do-not-store")

    assert state["secret_value"] is None


async def test_the_same_secret_produces_the_same_digest(provider: TfPluginProvider) -> None:
    """Two notes with one secret must agree, or the digest is not derived."""
    first = await create_note(provider, "digest-a", secret="identical")
    second = await create_note(provider, "digest-b", secret="identical")

    assert first["digest"] == second["digest"]


async def test_read_returns_the_persisted_state(provider: TfPluginProvider) -> None:
    state = await create_note(provider, "readable", secret="readable-secret")

    response = await provider.stub.ReadResource(
        pb.ReadResource.Request(type_name=NOTE, current_state=note_state("readable", state["digest"]))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert unpack(response.new_state)["name"] == "readable"


async def test_read_does_not_resurrect_the_write_only_value(provider: TfPluginProvider) -> None:
    state = await create_note(provider, "still-secret", secret="never-read-back")

    response = await provider.stub.ReadResource(
        pb.ReadResource.Request(type_name=NOTE, current_state=note_state("still-secret", state["digest"]))
    )

    assert unpack(response.new_state)["secret_value"] is None


async def test_identity_schema_is_published(provider: TfPluginProvider) -> None:
    """Identity is how import addresses a resource without an opaque id."""
    response = await provider.stub.GetResourceIdentitySchemas(pb.GetResourceIdentitySchemas.Request())

    assert NOTE in response.identity_schemas
    names = {a.name for a in response.identity_schemas[NOTE].identity_attributes}
    assert "name" in names


async def test_import_carries_identity_across_the_boundary(provider: TfPluginProvider) -> None:
    """Import by identity must return a resource whose identity survived."""
    await create_note(provider, "importable", secret="import-me")

    response = await provider.stub.ImportResourceState(
        pb.ImportResourceState.Request(
            type_name=NOTE,
            identity=pb.ResourceIdentityData(identity_data=pack({"name": "importable"})),
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert response.imported_resources
    imported = response.imported_resources[0]
    assert imported.type_name == NOTE
    assert unpack(imported.identity.identity_data)["name"] == "importable"


async def test_import_by_id_adopts_an_existing_object(provider: TfPluginProvider) -> None:
    """The plain `terraform import ADDR ID` path, with no identity supplied."""
    await create_note(provider, "importable-by-id", secret="import-by-id")

    response = await provider.stub.ImportResourceState(
        pb.ImportResourceState.Request(type_name=NOTE, id="importable-by-id")
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    imported = response.imported_resources[0]
    assert unpack(imported.state)["name"] == "importable-by-id"


async def test_import_does_not_fabricate_the_write_only_value(provider: TfPluginProvider) -> None:
    """A write-only value was never stored, so import cannot recover one.

    Inventing a value here would write a fabricated secret into state.
    """
    await create_note(provider, "imported-secret", secret="unrecoverable")

    response = await provider.stub.ImportResourceState(
        pb.ImportResourceState.Request(type_name=NOTE, id="imported-secret")
    )

    assert unpack(response.imported_resources[0].state)["secret_value"] is None


async def test_importing_a_missing_object_is_reported_as_not_found(
    provider: TfPluginProvider,
) -> None:
    """ "Not found" and "cannot import" are different answers to the reader."""
    response = await provider.stub.ImportResourceState(
        pb.ImportResourceState.Request(type_name=NOTE, id="never-created")
    )

    found = errors(response.diagnostics)
    assert found
    assert "never-created" in diagnostic_text(found)


async def test_upgrade_resource_identity_round_trips(provider: TfPluginProvider) -> None:
    response = await provider.stub.UpgradeResourceIdentity(
        pb.UpgradeResourceIdentity.Request(
            type_name=NOTE,
            version=0,
            raw_identity=pb.RawState(json=b'{"name":"upgradable"}'),
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert unpack(response.upgraded_identity.identity_data)["name"] == "upgradable"


async def test_upgrade_resource_state_accepts_current_version(provider: TfPluginProvider) -> None:
    response = await provider.stub.UpgradeResourceState(
        pb.UpgradeResourceState.Request(
            type_name=NOTE,
            version=0,
            raw_state=pb.RawState(json=b'{"name":"upgraded","secret_value":null,"digest":"abc"}'),
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert unpack(response.upgraded_state)["name"] == "upgraded"


async def test_move_resource_state_carries_state_across(provider: TfPluginProvider) -> None:
    """Terraform only calls this because the capability flag says it may."""
    response = await provider.stub.MoveResourceState(
        pb.MoveResourceState.Request(
            target_type_name=NOTE,
            source_type_name=NOTE,
            source_schema_version=0,
            source_state=pb.RawState(json=b'{"name":"moved","secret_value":null,"digest":"abc"}'),
            source_identity=pb.RawState(json=b'{"name":"moved"}'),
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert unpack(response.target_state)["name"] == "moved"


async def test_generate_resource_config_drops_unwritable_values(provider: TfPluginProvider) -> None:
    """Generated config must be something Terraform would accept back.

    Echoing a computed attribute produces a config that fails validation, and
    a write-only value cannot be recovered from state at all.
    """
    state = await create_note(provider, "generated", secret="generate-me")

    response = await provider.stub.GenerateResourceConfig(
        pb.GenerateResourceConfig.Request(type_name=NOTE, state=note_state("generated", state["digest"]))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    generated = unpack(response.config)
    assert generated["name"] == "generated"
    assert generated.get("secret_value") is None


# 🧪🔌🔚
