# pyvider/components/functions/jq_cty.py
from typing import Any

from pyvider.cty.conversion import cty_to_native
from pyvider.exceptions import FunctionError
from pyvider.hub import register_function
from pyvider.telemetry import logger

from ..helpers.jq_cty_processor import JqCtyProcessor


@register_function(
    name="pyvider_jq_cty",
    summary="Processes a data structure and returns a native CTY value.",
    description="Applies a jq query to the given input data. Returns a native CTY value (list, object, etc.) directly.",
    param_descriptions={
        "input_data": "The data structure to process.",
        "query": "The jq query string to apply.",
    },
)
def jq_cty(input_data: Any, query: str) -> Any:
    """Applies a jq query and returns a native Python object."""
    logger.debug("⚙️ JQ-CTY 📞 Function 'pyvider_jq_cty' called")
    if not isinstance(query, str) or not query:
        raise FunctionError("The 'query' argument must be a non-empty string.")

    result_cty = JqCtyProcessor.execute(query, input_data)

    # Adhere to the framework contract: convert the CtyValue to a native Python object.
    return cty_to_native(result_cty)
