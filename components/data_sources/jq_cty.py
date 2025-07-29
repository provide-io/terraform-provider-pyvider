# pyvider/components/data_sources/jq_cty.py
import json
from typing import Any, cast

import attrs

from pyvider.conversion import cty_to_native
from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_dyn, a_str, s_data_source
from pyvider.telemetry import logger

from ..helpers.jq_cty_processor import JqCtyProcessor


@attrs.define(frozen=True)
class JqCtyConfig:
    json_input: str
    query: str

@attrs.define(frozen=True)
class JqCtyState:
    json_input: str
    query: str
    result: Any

@register_data_source("pyvider_jq_cty")
class JqCtyDataSource(BaseDataSource["pyvider_jq_cty", JqCtyState, JqCtyConfig]):
    config_class = JqCtyConfig
    state_class = JqCtyState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source({
            "json_input": a_str(required=True),
            "query": a_str(required=True),
            "result": a_dyn(computed=True),
        })

    async def read(self, ctx: ResourceContext) -> JqCtyState:
        config = cast(JqCtyConfig, ctx.config)
        if not config:
            raise DataSourceError("Configuration is missing.")

        logger.debug("⚙️ JQ-CTY 📞 Data source 'pyvider_jq_cty' read called", query=config.query)

        try:
            parsed_json = json.loads(config.json_input)
        except json.JSONDecodeError as e:
            raise DataSourceError(f"Invalid JSON in 'json_input': {e}") from e

        try:
            result_cty_value = JqCtyProcessor.execute(config.query, parsed_json)
            logger.debug("⚙️ JQ-CTY ✅ Data source query successful", result_type=str(result_cty_value.type))

            # Adhere to the framework contract. Convert the CtyValue to a
            # native Python object before returning it in the state object.
            native_result = cty_to_native(result_cty_value)

            return JqCtyState(
                json_input=config.json_input,
                query=config.query,
                result=native_result
            )
        except Exception as e:
            raise DataSourceError(f"Error processing jq query: {e}") from e

    async def delete(self, ctx: ResourceContext): pass
