#
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Provider functions and data sources over the packaged binary.

These are not new in v6.11, but they share the msgpack boundary with
everything that is, and a function's declared return type is the one place
where a serialization mistake surfaces as a wrong *value* rather than an
error.
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

FILE_INFO = "pyvider_file_info"


async def call(provider: TfPluginProvider, name: str, *arguments: object) -> pb.CallFunction.Response:
    # The generated gRPC stub is untyped, so the await returns Any. Naming the
    # type here is what makes the helper's annotation mean something.
    response: pb.CallFunction.Response = await provider.stub.CallFunction(
        pb.CallFunction.Request(name=name, arguments=[pack(a) for a in arguments])
    )
    return response


async def test_get_functions_publishes_signatures(provider: TfPluginProvider) -> None:
    """A function with no published signature cannot be called from HCL."""
    response = await provider.stub.GetFunctions(pb.GetFunctions.Request())

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert {"add", "upper", "length"} <= set(response.functions)


async def test_function_signature_matches_the_schema_response(provider: TfPluginProvider) -> None:
    """GetFunctions and GetProviderSchema must not disagree about arity."""
    assert provider.schema is not None
    response = await provider.stub.GetFunctions(pb.GetFunctions.Request())

    for name, signature in response.functions.items():
        assert len(signature.parameters) == len(provider.schema.functions[name].parameters)


async def test_calling_a_numeric_function_returns_a_number(provider: TfPluginProvider) -> None:
    response = await call(provider, "add", 2, 3)

    assert not response.HasField("error"), response.error.text
    assert unpack(response.result) == 5


async def test_calling_a_string_function_returns_a_string(provider: TfPluginProvider) -> None:
    response = await call(provider, "upper", "conformance")

    assert not response.HasField("error"), response.error.text
    assert unpack(response.result) == "CONFORMANCE"


async def test_calling_a_collection_function_returns_a_number(provider: TfPluginProvider) -> None:
    response = await call(provider, "length", ["a", "b", "c"])

    assert not response.HasField("error"), response.error.text
    assert unpack(response.result) == 3


async def test_division_by_zero_matches_terraform_semantics(provider: TfPluginProvider) -> None:
    """`1/0` is +Inf here because that is what Terraform itself answers.

    Measured against OpenTofu's `terraform console`, and pyvider-cty agrees;
    raising an error instead would make the provider's arithmetic disagree with
    the language it is embedded in. Pinned because "divide by zero must error"
    is the intuitive-but-wrong expectation.
    """
    response = await call(provider, "divide", 1, 0)

    assert not response.HasField("error"), response.error.text
    assert unpack(response.result) == float("inf")


async def test_calling_an_unknown_function_reports_an_error(provider: TfPluginProvider) -> None:
    response = await call(provider, "pyvider_no_such_function")

    assert response.HasField("error")


async def test_validate_data_source_config_accepts_a_valid_config(
    provider: TfPluginProvider, tmp_path: Path
) -> None:
    response = await provider.stub.ValidateDataResourceConfig(
        pb.ValidateDataResourceConfig.Request(type_name=FILE_INFO, config=pack({"path": str(tmp_path)}))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)


async def test_unknown_data_source_type_reports_a_diagnostic(provider: TfPluginProvider) -> None:
    response = await provider.stub.ValidateDataResourceConfig(
        pb.ValidateDataResourceConfig.Request(type_name="pyvider_no_such_data_source", config=pack({}))
    )

    found = errors(response.diagnostics)
    assert found
    assert "pyvider_no_such_data_source" in diagnostic_text(found)


async def test_read_data_source_returns_computed_values(provider: TfPluginProvider, tmp_path: Path) -> None:
    """The data source must actually inspect the filesystem, not echo config."""
    target = tmp_path / "inspected.txt"
    target.write_text("twelve bytes", encoding="utf-8")

    response = await provider.stub.ReadDataSource(
        pb.ReadDataSource.Request(type_name=FILE_INFO, config=pack({"path": str(target)}))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    state = unpack(response.state)
    assert state["exists"] is True
    assert state["is_file"] is True
    assert state["size"] == len("twelve bytes")


async def test_read_data_source_reports_an_absent_path(provider: TfPluginProvider, tmp_path: Path) -> None:
    """An absent file is a fact to report, not an error to raise."""
    response = await provider.stub.ReadDataSource(
        pb.ReadDataSource.Request(type_name=FILE_INFO, config=pack({"path": str(tmp_path / "missing.txt")}))
    )

    assert not errors(response.diagnostics), diagnostic_text(response.diagnostics)
    assert unpack(response.state)["exists"] is False


async def test_stop_provider_answers_before_shutting_down(spawn_provider: Any) -> None:
    """StopProvider must return a response, not die mid-call.

    Stopping the gRPC server cancels every call in flight, so a handler that
    awaits its own shutdown never gets to answer and the caller sees
    UNAVAILABLE -- which is exactly what a crashed plugin looks like. Terraform
    calls this on interrupt, and needs to distinguish the two.

    Uses its own provider process: running it against the shared session fixture
    would stop the server every other test depends on.
    """
    victim = await spawn_provider()

    response = await victim.stub.StopProvider(pb.StopProvider.Request())

    assert not response.Error


# 🧪🔌🔚
