import json
from pathlib import Path
from typing import Any

import pytest

# Component imports
from components.functions.jq_cty import jq_cty as jq_cty_function
from pyvider.conversion import marshal, unmarshal
from pyvider.cty import CtyDynamic, CtyList, CtyString, CtyValue
from pyvider.protocols.tfprotov6.handlers import CallFunctionHandler

# Framework imports for simulating the full lifecycle
import pyvider.protocols.tfprotov6.protobuf as pb

# Define the path to the test data relative to the project root
TF_DATA_PATH = Path("components/tf/advanced_jq_test")

@pytest.fixture(scope="module")
def personnel_data() -> dict[str, Any]:
    return json.loads((TF_DATA_PATH / "personnel_records.json").read_text())

class TestJqWireProtocol:
    """
    These tests verify the full contract of the JQ components.
    """

    def test_jq_cty_function_returns_native_value(self, personnel_data: dict):
        """
        Verifies that the JQ function returns a native Python list, not a CtyValue.
        """
        query = "[.records[].name]"
        result = jq_cty_function(personnel_data, query)
        assert isinstance(result, list)
        assert result == ["Dr. Evelyn Reed", "Dr. Jian Chen", "Maria Rosa"]

    @pytest.mark.asyncio
    async def test_full_lifecycle_with_corrected_function(self, personnel_data: dict):
        """
        This lifecycle test now passes because the function returns a native list,
        and the framework correctly validates and marshals it.
        """
        raw_args = [personnel_data, "[.records[].name]"]

        marshalled_arg1 = marshal(raw_args[0], schema=CtyDynamic())
        marshalled_arg2 = marshal(raw_args[1], schema=CtyString())

        request = pb.CallFunction.Request(
            name="pyvider_jq_cty",
            arguments=[marshalled_arg1, marshalled_arg2]
        )

        response = await CallFunctionHandler(request, context=None)

        assert not response.error.text, f"Handler returned an error: {response.error.text}"

        # The function's return type is dynamic, so we unmarshal against CtyDynamic.
        result_cty = unmarshal(response.result, schema=CtyDynamic())

        # The corrected CtyDynamic.validate ensures the result is a single,
        # correctly-typed CtyValue.
        assert isinstance(result_cty, CtyValue)
        assert isinstance(result_cty.type, CtyList)
        assert result_cty.type.element_type.equal(CtyString())

        from pyvider.conversion import cty_to_native
        native_result = cty_to_native(result_cty)
        assert native_result == ["Dr. Evelyn Reed", "Dr. Jian Chen", "Maria Rosa"]
