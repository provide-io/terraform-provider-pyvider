# pyvider/components/test_suite/nested_data_test.py
# Comprehensive test suite to isolate CTY nested data issues
from decimal import Decimal
import hashlib
import json
from typing import Any, cast

import attrs

from pyvider.cty import CtyValue
from pyvider.cty.conversion import cty_to_native
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import FunctionError
from pyvider.hub import register_function, register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.schema import (
    PvsSchema,
    a_bool,
    a_dyn,
    a_map,
    a_num,
    a_obj,
    a_str,
    b_list,
    s_data_source,
    s_resource,
)

# =============================================================================
# Level 1: Simple Map Test (should work)
# =============================================================================

@attrs.define(frozen=True)
class SimpleMapConfig:
    input_data: dict[str, str] | None = None

@attrs.define(frozen=True)
class SimpleMapState:
    input_data: dict[str, str]
    processed_data: dict[str, str]
    data_hash: str

@register_data_source("pyvider_simple_map_test")
class SimpleMapDataSource(BaseDataSource["pyvider_simple_map_test", SimpleMapState, SimpleMapConfig]):
    config_class = SimpleMapConfig
    state_class = SimpleMapState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source(attributes={
            "input_data": a_map(a_str(), optional=True, description="Simple string map input"),
            "processed_data": a_map(a_str(), computed=True, description="Processed string map"),
            "data_hash": a_str(computed=True, description="Hash of processed data"),
        })

    async def read(self, ctx: ResourceContext) -> SimpleMapState:
        config = cast(SimpleMapConfig, ctx.config)
        input_data = config.input_data or {}
        processed_data = {k: v.upper() for k, v in input_data.items()}
        data_hash = hashlib.sha256(json.dumps(processed_data, sort_keys=True).encode()).hexdigest()

        return SimpleMapState(
            input_data=input_data,
            processed_data=processed_data,
            data_hash=data_hash
        )


# =============================================================================
# Level 2: Mixed Type Map Test
# =============================================================================

@attrs.define(frozen=True)
class MixedMapConfig:
    input_data: dict[str, Any] | None = None

@attrs.define(frozen=True)
class MixedMapState:
    input_data: dict[str, Any]
    processed_data: dict[str, Any]
    data_hash: str

@register_data_source("pyvider_mixed_map_test")
class MixedMapDataSource(BaseDataSource["pyvider_mixed_map_test", MixedMapState, MixedMapConfig]):
    config_class = MixedMapConfig
    state_class = MixedMapState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source(attributes={
            "input_data": a_dyn(optional=True, description="Mixed type map input"),
            "processed_data": a_dyn(computed=True, description="Processed mixed map"),
            "data_hash": a_str(computed=True, description="Hash of processed data"),
        })

    async def read(self, ctx: ResourceContext) -> MixedMapState:
        config = cast(MixedMapConfig, ctx.config)
        input_data = config.input_data or {}

        processed_data = {}
        if isinstance(input_data, dict):
            for k, v in input_data.items():
                if isinstance(v, str):
                    processed_data[k] = v.upper()
                elif isinstance(v, (int, float, Decimal)):
                    processed_data[k] = v + 1
                else:
                    processed_data[k] = v
        else:
            processed_data = {"error": "Input data was not a map as expected.", "received_type": type(input_data).__name__}

        data_hash = hashlib.sha256(json.dumps(processed_data, sort_keys=True, default=str).encode()).hexdigest()

        return MixedMapState(
            input_data=input_data,
            processed_data=processed_data,
            data_hash=data_hash
        )


# =============================================================================
# Level 3: Structured Object Test (well-defined nesting)
# =============================================================================

@attrs.define(frozen=True)
class StructuredObjectConfig:
    config_name: str
    metadata: dict[str, str] | None = None

@attrs.define(frozen=True)
class StructuredObjectState:
    config_name: str
    metadata: dict[str, str]
    generated_config: dict[str, Any]
    summary: dict[str, Any]

@register_data_source("pyvider_structured_object_test")
class StructuredObjectDataSource(BaseDataSource["pyvider_structured_object_test", StructuredObjectState, StructuredObjectConfig]):
    config_class = StructuredObjectConfig
    state_class = StructuredObjectState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source(attributes={
            "config_name": a_str(required=True),
            "metadata": a_map(a_str(), optional=True),
            "generated_config": a_obj(
                attributes={
                    "name": a_str(), "version": a_str(), "enabled": a_bool(),
                    "settings": a_map(a_str()), "numeric_settings": a_map(a_num()),
                },
                computed=True
            ),
            "summary": a_obj(
                attributes={
                    "total_keys": a_num(), "has_metadata": a_bool(), "config_hash": a_str(),
                    "nested_info": a_obj({"created_at": a_str(), "level": a_num()}),
                },
                computed=True
            ),
        })

    async def read(self, ctx: ResourceContext) -> StructuredObjectState:
        config = cast(StructuredObjectConfig, ctx.config)
        metadata = config.metadata or {}
        generated_config = {
            "name": config.config_name, "version": "1.0.0", "enabled": True,
            "settings": {k: f"processed_{v}" for k, v in metadata.items()},
            "numeric_settings": {f"num_{k}": len(v) for k, v in metadata.items()},
        }
        summary = {
            "total_keys": len(metadata), "has_metadata": bool(metadata),
            "config_hash": hashlib.sha256(config.config_name.encode()).hexdigest()[:8],
            "nested_info": {"created_at": "2025-06-24T20:30:00Z", "level": 2},
        }
        return StructuredObjectState(
            config_name=config.config_name, metadata=metadata,
            generated_config=generated_config, summary=summary
        )


# =============================================================================
# Level 4: Nested Resource Test
# =============================================================================

@attrs.define(frozen=True)
class NestedResourceConfig:
    resource_name: str
    configuration: dict[str, Any] | None = None
    nested_configs: list[dict[str, Any]] | None = None

@attrs.define(frozen=True)
class NestedResourceState:
    resource_name: str
    configuration: dict[str, Any] | None = None
    nested_configs: list[dict[str, Any]] | None = None
    processed_data: dict[str, Any] | None = attrs.field(default=None)
    resource_id: str | None = attrs.field(default=None)
    exists: bool | None = attrs.field(default=None)

@register_resource("pyvider_nested_resource_test")
class NestedResourceTest(BaseResource["pyvider_nested_resource_test", NestedResourceState, NestedResourceConfig]):
    config_class = NestedResourceConfig
    state_class = NestedResourceState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource(
            attributes={
                "resource_name": a_str(required=True),
                "configuration": a_dyn(optional=True, description="Dynamic configuration map"),
                "processed_data": a_dyn(computed=True, description="Processed configuration data"),
                "resource_id": a_str(computed=True),
                "exists": a_bool(computed=True),
            },
            block_types=[
                b_list(
                    "nested_configs",
                    attributes={
                        "service": a_str(required=True),
                        "port": a_num(required=True),
                        "protocol": a_str(required=True),
                        "ssl_enabled": a_bool(optional=True),
                    },
                    description="List of structured configuration maps"
                )
            ]
        )

    async def plan(self, ctx: ResourceContext) -> tuple[NestedResourceState | None, None]:
        config_cty = cast(CtyValue, ctx.config_cty)
        planned_state_data = cty_to_native(config_cty)

        processed_data = {
            "main_config": planned_state_data.get("configuration", {}),
            "nested_count": len(planned_state_data.get("nested_configs", [])),
        }

        planned_state_data["processed_data"] = processed_data
        planned_state_data["resource_id"] = f"resource_{planned_state_data.get('resource_name')}"
        planned_state_data["exists"] = True

        return self.state_class(**planned_state_data), None

    async def apply(self, ctx: ResourceContext) -> tuple[NestedResourceState | None, None]:
        return ctx.planned_state, None
    async def read(self, ctx: ResourceContext) -> NestedResourceState | None: return ctx.state
    async def delete(self, ctx: ResourceContext): pass


# =============================================================================
# Level 5: Complex Function Test (returns nested data)
# =============================================================================

@register_function(name="pyvider_nested_data_processor")
def nested_data_processor(input_json: str, processing_mode: str = "analyze") -> str:
    try:
        input_data = json.loads(input_json) if input_json else {}
    except json.JSONDecodeError as e:
        raise FunctionError(f"Invalid JSON provided to input_json: {e}") from e

    result = {
        "original_data": input_data,
        "summary": {
            "mode": processing_mode,
        }
    }
    if processing_mode == "analyze":
        result["summary"]["total_keys"] = len(input_data)

    return json.dumps(result, default=str)
