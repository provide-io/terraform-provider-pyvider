#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Drive every provider configuration-validation RPC for lint proof."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, NamedTuple

from tofusoup.tfplugin import TfPluginProvider, base_env, pack, start_provider

from pyvider.protocols.tfprotov6.protobuf import tfplugin6_pb2 as pb


class LintContract(NamedTuple):
    kind: str
    name: str
    summary: str
    detail: str
    attribute: str
    groups: tuple[str, ...]


RULE_CATALOG = {
    "provide-io/pyvider:insecure-tls": LintContract(
        kind="provider",
        name="pyvider",
        summary="TLS certificate verification is disabled",
        detail=(
            "Skipping TLS certificate verification may be intentional for local development, "
            "but it permits man-in-the-middle attacks. Set api_insecure_skip_verify to false "
            "for safer connections. Suppress with !provide-io/pyvider:insecure-tls."
        ),
        attribute="api_insecure_skip_verify",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:world-writable-directory": LintContract(
        kind="resource",
        name="pyvider_local_directory",
        summary="Directory permissions are world-writable",
        detail=(
            "World-writable permissions may be intentional for a shared scratch directory, "
            "but any local user can modify its contents. Remove the POSIX other-write bit "
            "(for example, set permissions to 0o755) for a safer directory. Suppress with "
            "!provide-io/pyvider:world-writable-directory."
        ),
        attribute="permissions",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:insecure-http": LintContract(
        kind="data_source",
        name="pyvider_http_api",
        summary="HTTP API uses an unencrypted connection",
        detail=(
            "Plain HTTP may be intentional for a local endpoint, but request data can be "
            "intercepted or changed. Set url to an https:// address for a safer connection. "
            "Suppress with !provide-io/pyvider:insecure-http."
        ),
        attribute="url",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:long-lived-lease": LintContract(
        kind="ephemeral_resource",
        name="pyvider_lease",
        summary="Lease lifetime exceeds one hour",
        detail=(
            "A lease longer than one hour may be intentional for lengthy operations, but "
            "long-lived ephemeral values remain usable for longer if exposed. Set ttl_seconds "
            "to 3600 or less for a safer lease. Suppress with "
            "!provide-io/pyvider:long-lived-lease."
        ),
        attribute="ttl_seconds",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
    "provide-io/pyvider:include-hidden-files": LintContract(
        kind="list_resource",
        name="pyvider_file_content",
        summary="File listing includes hidden files",
        detail=(
            "Including hidden files may be intentional for configuration discovery, but it "
            "can expose secrets or metadata. Set include_hidden to false for safer listings. "
            "Suppress with !provide-io/pyvider:include-hidden-files."
        ),
        attribute="include_hidden",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:security"),
    ),
    "provide-io/pyvider:long-action-timeout": LintContract(
        kind="action",
        name="pyvider_wait_for_file",
        summary="Action timeout exceeds five minutes",
        detail=(
            "A timeout longer than five minutes may be intentional for slow prerequisites, "
            "but it can leave Terraform waiting for an unresponsive action. Set "
            "timeout_seconds to 300 or less for a safer timeout. Suppress with "
            "!provide-io/pyvider:long-action-timeout."
        ),
        attribute="timeout_seconds",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
    "provide-io/pyvider:relative-state-store-path": LintContract(
        kind="state_store",
        name="pyvider_filesystem_store",
        summary="State store path is relative",
        detail=(
            "A relative state store path may be intentional for a self-contained workspace, "
            "but it depends on the provider process's working directory. Set path to an "
            "absolute path for safer, predictable state storage. Suppress with "
            "!provide-io/pyvider:relative-state-store-path."
        ),
        attribute="path",
        groups=("provide-io/pyvider:all", "provide-io/pyvider:reliability"),
    ),
}
EXPECTED_RPCS = {(contract.kind, contract.name) for contract in RULE_CATALOG.values()}


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


def diagnostic_record(
    result: dict[str, Any], diagnostic: pb.Diagnostic, provider_sha256: str
) -> dict[str, Any]:
    """Convert one wire diagnostic into a stable JSON-lines proof record."""
    summary_rule = diagnostic.summary.rsplit(" (", 1)
    if len(summary_rule) != 2 or not summary_rule[1].endswith(")"):
        raise ValueError(f"diagnostic summary has no rule ID: {diagnostic.summary!r}")
    kind = {
        "data_source": "data-source",
        "ephemeral_resource": "ephemeral",
        "list_resource": "list",
        "state_store": "state-store",
    }.get(result["kind"], result["kind"])
    attribute = [step.attribute_name for step in diagnostic.attribute.steps]
    if len(attribute) != 1:
        raise ValueError(f"diagnostic attribute is not top-level: {diagnostic.summary!r}")
    return {
        "attribute": attribute[0],
        "kind": kind,
        "observed_via": "tofusoup",
        "provider_sha256": provider_sha256,
        "rule_id": summary_rule[1][:-1],
        "severity": pb.Diagnostic.Severity.Name(diagnostic.severity).lower(),
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

    return {
        f"{contract.summary} ({rule})"
        for rule, contract in RULE_CATALOG.items()
        if enabled(rule, contract.groups)
    }


def assert_expected_catalog(results: list[dict[str, Any]], selector: str) -> None:
    """Refuse a proof unless all RPCs and every selected diagnostic are present."""
    observed_rpcs = {(result["kind"], result["name"]) for result in results}
    if observed_rpcs != EXPECTED_RPCS:
        raise ValueError(
            f"RPC catalog mismatch: expected {sorted(EXPECTED_RPCS)!r}, observed {sorted(observed_rpcs)!r}"
        )
    contracts_by_summary = {
        f"{contract.summary} ({rule})": contract for rule, contract in RULE_CATALOG.items()
    }
    for result in results:
        for diagnostic in result["diagnostics"]:
            if diagnostic.severity != pb.Diagnostic.WARNING:
                raise ValueError(f"diagnostic severity mismatch for {diagnostic.summary!r}")
            contract = contracts_by_summary.get(diagnostic.summary)
            if contract is not None and (result["kind"], result["name"]) != (
                contract.kind,
                contract.name,
            ):
                raise ValueError(f"diagnostic RPC ownership mismatch for {diagnostic.summary!r}")
            if contract is not None and diagnostic.detail != contract.detail:
                raise ValueError(f"diagnostic detail mismatch for {diagnostic.summary!r}")
            attribute = [step.attribute_name for step in diagnostic.attribute.steps]
            if contract is not None and attribute != [contract.attribute]:
                raise ValueError(f"diagnostic attribute mismatch for {diagnostic.summary!r}")
    observed_summaries = [diagnostic.summary for result in results for diagnostic in result["diagnostics"]]
    if not observed_summaries:
        raise ValueError(f"provider lint proof returned no diagnostics for selector {selector!r}")
    expected_summaries = _expected_summaries(selector)
    if len(observed_summaries) != len(expected_summaries) or set(observed_summaries) != expected_summaries:
        raise ValueError(
            "diagnostic catalog mismatch: "
            f"expected {sorted(expected_summaries)!r}, observed {sorted(observed_summaries)!r}"
        )


def assert_no_bootstrap_diagnostics(responses: dict[str, list[pb.Diagnostic]]) -> None:
    """Reject schema/configuration diagnostics before collecting lint proof."""
    for rpc, diagnostics in responses.items():
        if diagnostics:
            raise ValueError(f"{rpc} bootstrap diagnostics were not empty")


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
        schema_response = await session.stub.GetProviderSchema(pb.GetProviderSchema.Request())
        session.schema = schema_response
        configure_response = await session.stub.ConfigureProvider(
            pb.ConfigureProvider.Request(
                terraform_version="1.14.9",
                config=schema_config(session.schema.provider, {}),
            )
        )
        assert_no_bootstrap_diagnostics(
            {
                "GetProviderSchema": list(schema_response.diagnostics),
                "ConfigureProvider": list(configure_response.diagnostics),
            }
        )
        results = await validate_configurations(session, working_directory)
        assert_expected_catalog(results, selector)
        provider_sha256 = hashlib.sha256(binary.read_bytes()).hexdigest()
        return [
            diagnostic_record(result, diagnostic, provider_sha256)
            for result in results
            for diagnostic in result["diagnostics"]
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
    except Exception:
        # This is the CLI trust boundary: provider launch, handshake, and RPC
        # failures may contain internal paths or tracebacks. BaseException is
        # intentionally not caught so KeyboardInterrupt/SystemExit still work.
        print(f"error: provider proof failed for binary: {args.binary}", file=sys.stderr)
        return 2
    for record in records:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
