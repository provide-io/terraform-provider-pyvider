#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The v6.11 action RPCs: ValidateActionConfig, PlanAction, InvokeAction.

Actions run outside any resource lifecycle, and InvokeAction is a *stream*:
progress events followed by exactly one completed event. The completed event
is what tells Terraform the action is over, so its presence matters as much on
the failure path as on the happy one.
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

ECHO = "pyvider_echo"
FAILING = "pyvider_failing_action"


def echo_config(
    path: Path, message: str = "hello", repeat: int | None = None, defer: bool | None = None
) -> Any:
    return pack({"message": message, "path": str(path), "repeat": repeat, "defer": defer})


async def invoke(provider: TfPluginProvider, request: pb.InvokeAction.Request) -> list[pb.InvokeAction.Event]:
    """Drain an InvokeAction stream into a list of events."""
    return [event async for event in provider.stub.InvokeAction(request)]


def progress_messages(events: list[pb.InvokeAction.Event]) -> list[str]:
    return [e.progress.message for e in events if e.WhichOneof("type") == "progress"]


def completed(events: list[pb.InvokeAction.Event]) -> list[pb.InvokeAction.Event]:
    return [e for e in events if e.WhichOneof("type") == "completed"]


async def test_validate_accepts_a_well_formed_config(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(type_name=ECHO, config=echo_config(tmp_path / "note.txt"))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_validate_rejects_a_missing_required_attribute(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """A config the action declares invalid must come back as an error.

    Silently accepting it would move the failure into invoke, where the side
    effect may already have happened.
    """
    response = await provider.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(
            type_name=ECHO,
            config=pack({"message": None, "path": str(tmp_path / "n.txt"), "repeat": None, "defer": None}),
        )
    )

    assert errors(response.diagnostics)


async def test_validate_rejects_an_out_of_range_value(provider: TfPluginProvider, tmp_path: Path) -> None:
    response = await provider.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(type_name=ECHO, config=echo_config(tmp_path / "n.txt", repeat=0))
    )

    assert errors(response.diagnostics)


async def test_unknown_action_type_is_an_error_not_a_silent_success(provider: TfPluginProvider) -> None:
    """An unregistered type must produce a diagnostic naming it."""
    response = await provider.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(type_name="pyvider_not_a_real_action", config=pack({}))
    )

    found = errors(response.diagnostics)
    assert found
    assert "pyvider_not_a_real_action" in diagnostic_text(found)


async def test_plan_reports_the_intended_side_effect(provider: TfPluginProvider, tmp_path: Path) -> None:
    """The action warns about what it will touch, and plan must carry that."""
    target = tmp_path / "planned.txt"
    response = await provider.stub.PlanAction(
        pb.PlanAction.Request(action_type=ECHO, config=echo_config(target))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert str(target) in diagnostic_text(response.diagnostics)


async def test_plan_defers_when_the_client_allows_it(provider: TfPluginProvider, tmp_path: Path) -> None:
    """A deferral is only legal when the client offered to accept one.

    And only for one reason. Terraform refuses any other from PlanAction --
    "An action can only be deferred due to an unknown provider configuration"
    (internal/plugin6/grpc_provider.go:1951-1957) -- and the error branch there
    does not return, so a wrong reason both defers and fails the run.
    """
    response = await provider.stub.PlanAction(
        pb.PlanAction.Request(
            action_type=ECHO,
            config=echo_config(tmp_path / "deferred.txt", defer=True),
            client_capabilities=pb.ClientCapabilities(deferral_allowed=True),
        )
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert response.HasField("deferred")
    assert response.deferred.reason == pb.Deferred.PROVIDER_CONFIG_UNKNOWN


async def test_plan_refuses_to_defer_when_the_client_did_not_offer(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """Deferring at a client that cannot handle it must be a loud error.

    Returning an un-deferred success instead would silently run the action the
    provider just said was not ready.
    """
    response = await provider.stub.PlanAction(
        pb.PlanAction.Request(
            action_type=ECHO,
            config=echo_config(tmp_path / "deferred.txt", defer=True),
            client_capabilities=pb.ClientCapabilities(deferral_allowed=False),
        )
    )

    assert not response.HasField("deferred")
    assert errors(response.diagnostics)


async def test_invoke_streams_progress_then_exactly_one_completed(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """The stream shape is the contract: N progress events, then one completed."""
    target = tmp_path / "invoked.txt"
    events = await invoke(
        provider, pb.InvokeAction.Request(action_type=ECHO, config=echo_config(target, repeat=3))
    )

    assert len(completed(events)) == 1
    assert events[-1].WhichOneof("type") == "completed"
    assert len(progress_messages(events)) >= 3


async def test_invoke_performs_the_side_effect(provider: TfPluginProvider, tmp_path: Path) -> None:
    """A green completed event is not evidence on its own; check the file.

    The action's whole reason for writing to disk is that the result can be
    verified independently of what the RPC claims.
    """
    target = tmp_path / "written.txt"
    events = await invoke(
        provider,
        pb.InvokeAction.Request(action_type=ECHO, config=echo_config(target, message="conformance", repeat=2)),
    )

    assert not errors(completed(events)[0].completed.diagnostics)
    assert target.exists()
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert all(line.endswith("conformance") for line in lines)


async def test_failing_action_still_sends_a_completed_event(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    """A mid-stream failure must terminate the stream properly.

    Without a completed event Terraform waits on an action that already died.
    """
    events = await invoke(
        provider,
        pb.InvokeAction.Request(action_type=FAILING, config=echo_config(tmp_path / "fail.txt")),
    )

    finals = completed(events)
    assert len(finals) == 1
    assert errors(finals[0].completed.diagnostics)


async def test_invoking_an_unknown_action_reports_a_diagnostic(provider: TfPluginProvider) -> None:
    events = await invoke(
        provider,
        pb.InvokeAction.Request(action_type="pyvider_missing_action", config=pack({})),
    )

    finals = completed(events)
    assert len(finals) == 1
    assert errors(finals[0].completed.diagnostics)


# 🧪🔌🔚
