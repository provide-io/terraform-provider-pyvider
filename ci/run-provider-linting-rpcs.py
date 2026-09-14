#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Drive every provider configuration-validation RPC for lint proof."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from tofusoup.tfplugin import TfPluginProvider, base_env, pack, start_provider

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb


def schema_config(schema: pb.Schema, overrides: dict[str, Any]) -> pb.DynamicValue:
    """Shape a config from the schema returned by the running provider."""
    values: dict[str, Any] = {attribute.name: None for attribute in schema.block.attributes}
    values.update(overrides)
    return pack(values)


async def validate_configurations(session: TfPluginProvider, working_directory: Path) -> list[dict[str, Any]]:
    """Drive lint-triggering validation requests against one provider process."""
    if session.schema is None:
        raise RuntimeError("fetch the provider schema before driving validation RPCs")
    provider = await session.stub.ValidateProviderConfig(
        pb.ValidateProviderConfig.Request(
            config=schema_config(
                session.schema.provider,
                {"api_insecure_skip_verify": True},
            )
        )
    )
    resource_name = "pyvider_local_directory"
    resource = await session.stub.ValidateResourceConfig(
        pb.ValidateResourceConfig.Request(
            type_name=resource_name,
            config=schema_config(
                session.schema.resource_schemas[resource_name],
                {
                    "path": str(working_directory / "world-writable"),
                    "permissions": "0o777",
                },
            ),
        )
    )
    data_source_name = "pyvider_http_api"
    data_source = await session.stub.ValidateDataResourceConfig(
        pb.ValidateDataResourceConfig.Request(
            type_name=data_source_name,
            config=schema_config(
                session.schema.data_source_schemas[data_source_name],
                {
                    "url": "http://127.0.0.1/provider-lint-proof",
                    "method": "GET",
                    "headers": {},
                    "timeout": 30,
                },
            ),
        )
    )
    ephemeral_name = "pyvider_lease"
    ephemeral = await session.stub.ValidateEphemeralResourceConfig(
        pb.ValidateEphemeralResourceConfig.Request(
            type_name=ephemeral_name,
            config=schema_config(
                session.schema.ephemeral_resource_schemas[ephemeral_name],
                {
                    "name": "provider-lint-proof",
                    "path": str(working_directory / "proof.lease"),
                    "ttl_seconds": 3601,
                },
            ),
        )
    )
    list_name = "pyvider_file_content"
    list_resource = await session.stub.ValidateListResourceConfig(
        pb.ValidateListResourceConfig.Request(
            type_name=list_name,
            config=schema_config(
                session.schema.list_resource_schemas[list_name],
                {
                    "path": str(working_directory),
                    "include_hidden": True,
                },
            ),
        )
    )
    action_name = "pyvider_wait_for_file"
    action = await session.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(
            type_name=action_name,
            config=schema_config(
                session.schema.action_schemas[action_name].schema,
                {
                    "path": str(working_directory / "eventually-created"),
                    "timeout_seconds": 301,
                },
            ),
        )
    )
    state_store_name = "pyvider_filesystem_store"
    state_store = await session.stub.ValidateStateStoreConfig(
        pb.ValidateStateStore.Request(
            type_name=state_store_name,
            config=schema_config(
                session.schema.state_store_schemas[state_store_name],
                {"path": "relative-state-store"},
            ),
        )
    )
    return [
        {"kind": "provider", "name": "pyvider", "diagnostics": list(provider.diagnostics)},
        {"kind": "resource", "name": resource_name, "diagnostics": list(resource.diagnostics)},
        {
            "kind": "data_source",
            "name": data_source_name,
            "diagnostics": list(data_source.diagnostics),
        },
        {
            "kind": "ephemeral_resource",
            "name": ephemeral_name,
            "diagnostics": list(ephemeral.diagnostics),
        },
        {
            "kind": "list_resource",
            "name": list_name,
            "diagnostics": list(list_resource.diagnostics),
        },
        {"kind": "action", "name": action_name, "diagnostics": list(action.diagnostics)},
        {
            "kind": "state_store",
            "name": state_store_name,
            "diagnostics": list(state_store.diagnostics),
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--selector", required=True)
    parser.add_argument("--format", choices=("json-lines",), required=True)
    return parser.parse_args()


def diagnostic_record(result: dict[str, Any], diagnostic: pb.Diagnostic) -> dict[str, Any]:
    """Convert one wire diagnostic into a stable JSON-lines proof record."""
    return {
        "attribute": [step.attribute_name for step in diagnostic.attribute.steps],
        "detail": diagnostic.detail,
        "kind": result["kind"],
        "name": result["name"],
        "severity": pb.Diagnostic.Severity.Name(diagnostic.severity).lower(),
        "summary": diagnostic.summary,
    }


async def run(binary: Path, selector: str, working_directory: Path) -> list[dict[str, Any]]:
    """Launch the packaged provider and collect all validation diagnostics."""
    session: TfPluginProvider = await start_provider(
        binary,
        env=base_env(
            {
                "PYVIDER_TESTMODE": "true",
                "PYVIDER_LOG_LEVEL": "ERROR",
                "PYVIDER_LINT": selector,
            }
        ),
    )
    try:
        session.schema = await session.stub.GetProviderSchema(pb.GetProviderSchema.Request())
        await session.stub.ConfigureProvider(
            pb.ConfigureProvider.Request(
                terraform_version="1.14.9",
                config=schema_config(session.schema.provider, {}),
            )
        )
        results = await validate_configurations(session, working_directory)
        return [
            diagnostic_record(result, diagnostic) for result in results for diagnostic in result["diagnostics"]
        ]
    finally:
        await session.stop()


def main() -> int:
    args = parse_args()
    records = asyncio.run(run(args.binary, args.selector, Path.cwd()))
    for record in records:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
