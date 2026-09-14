#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Drive every provider configuration-validation RPC for lint proof."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
from typing import Any

from tofusoup.tfplugin import TfPluginProvider, base_env, pack, start_provider

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb

EXPECTED_RPCS = {
    ("provider", "pyvider"),
    ("resource", "pyvider_local_directory"),
    ("data_source", "pyvider_http_api"),
    ("ephemeral_resource", "pyvider_lease"),
    ("list_resource", "pyvider_file_content"),
    ("action", "pyvider_wait_for_file"),
    ("state_store", "pyvider_filesystem_store"),
}
RULE_CATALOG = {
    "provide-io/pyvider:insecure-tls": (
        "TLS certificate verification is disabled",
        ("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:world-writable-directory": (
        "Directory permissions are world-writable",
        ("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:insecure-http": (
        "HTTP API uses an unencrypted connection",
        ("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:long-lived-lease": (
        "Lease lifetime exceeds one hour",
        ("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
    "provide-io/pyvider:include-hidden-files": (
        "File listing includes hidden files",
        ("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:long-action-timeout": (
        "Action timeout exceeds five minutes",
        ("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
    "provide-io/pyvider:relative-state-store-path": (
        "State store path is relative",
        ("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
}


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


async def validate_failing_action_fixture(session: TfPluginProvider) -> dict[str, Any]:
    """Drive the existing test-only action whose lint hook deliberately raises."""
    if session.schema is None:
        raise RuntimeError("fetch the provider schema before driving validation RPCs")
    action_name = "pyvider_failing_action"
    response = await session.stub.ValidateActionConfig(
        pb.ValidateActionConfig.Request(
            type_name=action_name,
            config=schema_config(
                session.schema.action_schemas[action_name].schema,
                {"message": "semantically-valid"},
            ),
        )
    )
    return {
        "kind": "failing_action_fixture",
        "name": action_name,
        "diagnostics": list(response.diagnostics),
    }


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


def _expected_summaries(selector: str) -> set[str]:
    include = {
        token.strip() for token in selector.split(",") if token.strip() and not token.strip().startswith("!")
    }
    exclude = {
        token.strip()[1:]
        for token in selector.split(",")
        if token.strip().startswith("!") and len(token.strip()) > 1
    }

    def enabled(rule: str, groups: tuple[str, ...]) -> bool:
        if rule in include:
            return True
        if rule in exclude:
            return False
        if include.intersection(groups):
            return True
        if exclude.intersection(groups):
            return False
        return "all" in include

    return {f"{summary} ({rule})" for rule, (summary, groups) in RULE_CATALOG.items() if enabled(rule, groups)}


def assert_expected_catalog(results: list[dict[str, Any]], selector: str) -> None:
    """Refuse a proof unless all RPCs and every selected diagnostic are present."""
    observed_rpcs = {(result["kind"], result["name"]) for result in results}
    if observed_rpcs != EXPECTED_RPCS:
        raise ValueError(
            f"RPC catalog mismatch: expected {sorted(EXPECTED_RPCS)!r}, observed {sorted(observed_rpcs)!r}"
        )
    observed_summaries = [diagnostic.summary for result in results for diagnostic in result["diagnostics"]]
    if not observed_summaries:
        raise ValueError(f"provider lint proof returned no diagnostics for selector {selector!r}")
    expected_summaries = _expected_summaries(selector)
    if len(observed_summaries) != len(expected_summaries) or set(observed_summaries) != expected_summaries:
        raise ValueError(
            "diagnostic catalog mismatch: "
            f"expected {sorted(expected_summaries)!r}, observed {sorted(observed_summaries)!r}"
        )


@contextmanager
def silence_client_stderr() -> Iterator[None]:
    """Keep proof output machine-readable while the RPC client logs verbosely."""
    sys.stderr.flush()
    saved_stderr = os.dup(2)
    try:
        with Path(os.devnull).open("w", encoding="utf-8") as sink:
            os.dup2(sink.fileno(), 2)
            yield
    finally:
        sys.stderr.flush()
        os.dup2(saved_stderr, 2)
        os.close(saved_stderr)


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
        assert_expected_catalog(results, selector)
        return [
            diagnostic_record(result, diagnostic) for result in results for diagnostic in result["diagnostics"]
        ]
    finally:
        await session.stop()


def main() -> int:
    args = parse_args()
    if not args.binary.is_file():
        print(f"error: provider binary does not exist: {args.binary}", file=sys.stderr)
        return 2
    try:
        with silence_client_stderr():
            records = asyncio.run(run(args.binary, args.selector, Path.cwd()))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for record in records:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
