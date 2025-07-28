# pyvider/components/data_sources/jq.py
import json
from typing import cast

import attrs

from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_str, s_data_source

from ..helpers.jq_processor import DecimalAwareJSONEncoder, JqProcessor


@attrs.define(frozen=True)
class JqConfig:
    json_input: str
    query: str


@attrs.define(frozen=True)
class JqState:
    json_input: str
    query: str
    result: str


@register_data_source("pyvider_jq")
class JqDataSource(BaseDataSource["pyvider_jq", JqState, JqConfig]):
    config_class = JqConfig
    state_class = JqState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source(
            {
                "json_input": a_str(required=True),
                "query": a_str(required=True),
                "result": a_str(computed=True),
            }
        )

    async def read(self, ctx: ResourceContext) -> JqState:
        config = cast(JqConfig, ctx.config)
        if not config:
            raise DataSourceError("Configuration is missing for pyvider_jq data source.")

        try:
            parsed_json = json.loads(config.json_input)
        except json.JSONDecodeError as e:
            raise DataSourceError(f"Invalid JSON in 'json_input': {e}") from e

        try:
            # The processor returns a native Python object.
            native_result = JqProcessor.execute(config.query, parsed_json)
            # The contract for this data source is to return a JSON string.
            result_str = json.dumps(native_result, cls=DecimalAwareJSONEncoder)

            return JqState(
                json_input=config.json_input,
                query=config.query,
                result=result_str
            )

        except Exception as e:
            raise DataSourceError(f"Error processing jq query: {e}") from e

    async def delete(self, ctx: ResourceContext): pass
