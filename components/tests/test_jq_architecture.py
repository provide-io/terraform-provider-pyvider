import json

from components.functions.jq import jq as jq_function
from components.helpers.jq_cty_processor import JqCtyProcessor
from pyvider.cty import CtyList, CtyObject, CtyString


class TestJqArchitecture:
    """TDD: These tests enforce the correct, stable jq architecture."""

    def test_jq_function_primitive_is_json_encoded(self):
        """
        Verifies `pyvider_jq` returns a valid JSON string for a primitive.
        """
        data = {"key": "value"}
        query = ".key"
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == "value"

    def test_jq_cty_ds_returns_list_for_list_query(self):
        """
        Verifies `pyvider_jq_cty` returns a list for a list query.
        This test now passes because the processor returns a CtyList directly.
        """
        data = {"items": [{"name": "A"}, {"name": "B"}]}
        query = "[.items[].name]" # A query that constructs a list
        result_cty = JqCtyProcessor.execute(query, data)
        assert isinstance(result_cty.type, CtyList)
        assert result_cty.type.element_type.equal(CtyString())

    def test_cty_object_equality_deep(self):
        """
        Verifies CtyObject.equal performs a deep comparison.
        """
        type1 = CtyObject(attribute_types={"nested": CtyObject(attribute_types={"a": CtyString()})})
        type2 = CtyObject(attribute_types={"nested": CtyObject(attribute_types={"a": CtyString()})})
        type3 = CtyObject(attribute_types={"nested": CtyObject(attribute_types={"a": CtyObject(attribute_types={})})})
        assert type1.equal(type2)
        assert not type1.equal(type3)
