import json

import pytest

from components.data_sources.jq_cty import JqCtyConfig, JqCtyDataSource, JqCtyState
from pyvider.resources.context import ResourceContext


@pytest.mark.asyncio
async def test_jq_cty_data_source_with_problematic_input():
    problematic_json_input = json.dumps([{"message": "hello from list"}])
    query = ".[0].message"
    config = JqCtyConfig(json_input=problematic_json_input, query=query)
    ctx = ResourceContext(config=config)
    data_source = JqCtyDataSource()
    state = await data_source.read(ctx)

    assert isinstance(state, JqCtyState)
    # THE FIX: The `read` method now returns a native Python string.
    assert state.result == "hello from list"
