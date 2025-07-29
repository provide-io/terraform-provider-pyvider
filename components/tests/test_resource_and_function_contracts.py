import json

from components.functions.jq import jq as jq_function


class TestResourceAndFunctionContracts:
    def test_jq_function_returns_json_string_for_list_output(self):
        query = ".items[].name" # This query streams results
        data = {"items": [{"name": "one"}, {"name": "two"}]}
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == ["one", "two"]

    def test_jq_function_handles_array_constructor(self):
        query = "[.items[].name]" # This query constructs a list
        data = {"items": [{"name": "one"}, {"name": "two"}]}
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == ["one", "two"]
