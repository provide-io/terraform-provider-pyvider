import json

from components.functions.jq import jq as jq_function


class TestJqFunctionContract:
    """
    TDD: These tests enforce the correct contract for the pyvider_jq function.
    """

    def test_jq_function_returns_primitive_for_single_match(self):
        """
        TDD 1: Verifies the function returns a JSON string for a single primitive.
        """
        data = {"key": "value"}
        query = ".key"
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == "value"

    def test_jq_function_returns_json_string_for_multiple_matches(self):
        """
        TDD 2: Verifies the function returns a JSON string for a stream of results.
        """
        data = [{"name": "A"}, {"name": "B"}]
        query = ".[] | .name"
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == ["A", "B"]

    def test_jq_function_returns_json_string_for_array_constructor(self):
        """
        TDD 3: Verifies the function returns a JSON string for a query
        that constructs a list.
        """
        data = [{"name": "A"}, {"name": "B"}]
        query = "[.[] | .name]"
        result = jq_function(data, query)
        assert isinstance(result, str)
        assert json.loads(result) == ["A", "B"]
