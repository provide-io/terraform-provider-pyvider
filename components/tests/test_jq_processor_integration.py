from decimal import Decimal
import json

import pytest

from components.functions.jq import jq as jq_function
from components.helpers.jq_processor import JqProcessor
from pyvider.exceptions import FunctionError


class TestJqComponentIntegration:
    def test_processor_handles_list_wrapped_dict(self):
        list_wrapped_data = [{"key": "value", "items": [1, 2]}]
        query = ".[0].key"
        # THE FIX: The processor correctly returns the primitive.
        result = JqProcessor.execute(query, list_wrapped_data)
        assert result == "value"

    def test_jq_function_handles_decimal_type(self):
        native_input = {"price": Decimal("99.99")}
        query = "{ new_price: .price * 2 }"
        result_json_string = jq_function(native_input, query)
        assert isinstance(result_json_string, str)
        decoded_result = json.loads(result_json_string)
        assert "new_price" in decoded_result
        assert decoded_result["new_price"] == 199.98

    def test_jq_function_fails_gracefully_on_invalid_query(self):
        data = {"key": "value"}
        invalid_query = ".[}"
        with pytest.raises(FunctionError) as exc_info:
            jq_function(data, invalid_query)
        assert "jq query failed" in str(exc_info.value)
