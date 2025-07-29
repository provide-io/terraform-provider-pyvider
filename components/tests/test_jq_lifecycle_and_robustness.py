import json
from pathlib import Path
from typing import Any

import pytest

from components.data_sources.jq_cty import JqCtyDataSource
from pyvider.conversion import marshal, unmarshal
from pyvider.protocols.tfprotov6.handlers import ReadDataSourceHandler
import pyvider.protocols.tfprotov6.protobuf as pb

TF_DATA_PATH = Path("components/tf/advanced_jq_test")

@pytest.fixture(scope="module")
def full_system_data() -> dict[str, Any]:
    return {
        "personnel": json.loads((TF_DATA_PATH / "personnel_records.json").read_text()),
        "schematics": json.loads((TF_DATA_PATH / "project_apollo_schematics.json").read_text()),
        "supply_chain": json.loads((TF_DATA_PATH / "supply_chain_database.json").read_text()),
        "materials": json.loads((TF_DATA_PATH / "materials_properties.json").read_text()),
        "test_logs": json.loads((TF_DATA_PATH / "test_and_validation_logs.json").read_text()),
    }

@pytest.fixture(scope="module")
def master_audit_query() -> str:
    return (TF_DATA_PATH / "master_audit_v3.jq").read_text()

class TestJqLifecycleAndRobustness:
    @pytest.mark.asyncio
    async def test_data_source_full_lifecycle(self, full_system_data: dict, master_audit_query: str):
        ds_schema = JqCtyDataSource.get_schema()
        raw_config = {
            "json_input": json.dumps(full_system_data),
            "query": master_audit_query,
        }
        marshalled_config = marshal(raw_config, schema=ds_schema.block)
        request = pb.ReadDataSource.Request(
            type_name="pyvider_jq_cty",
            config=marshalled_config
        )
        response = await ReadDataSourceHandler(request, context=None)

        # Assert that the handler, which now works correctly,
        # returns no diagnostics.
        assert not response.diagnostics, f"Handler returned diagnostics: {response.diagnostics}"

        result_cty = unmarshal(response.state, schema=ds_schema.block)
        from pyvider.conversion import cty_to_native
        final_result = cty_to_native(result_cty)

        assert isinstance(final_result["result"], list)
        assert len(final_result["result"]) > 0
        assert "part_name" in final_result["result"][0]
        assert final_result["result"][0]["part_name"] == "Qubit Capacitor Array"
