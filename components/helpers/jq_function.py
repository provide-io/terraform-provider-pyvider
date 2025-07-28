# pyvider/components/functions/jq_function.py
from typing import Any

from pyvider.exceptions import FunctionError
from pyvider.hub import register_function
from pyvider.telemetry import logger

# Import the shared logic from its new, neutral location.
from ..helpers.jq_processor import JqProcessor


@register_function(
    name="pyvider_jq",
    summary="Processes a data structure with a jq query.",
    description="Applies a jq query to the given input data. Returns complex types (lists, objects) as a JSON string, which should be decoded with `jsondecode()`.",
    param_descriptions={
        "input_data": "The data structure to process.",
        "query": "The jq query string to apply.",
    },
)
def jq(input_data: Any, query: str) -> Any:
    """Applies a jq query to the given data."""
    logger.debug("⚙️ JQ 📞 Function 'pyvider_jq' called")
    if not isinstance(query, str) or not query:
        raise FunctionError("The 'query' argument must be a non-empty string.")

    # Delegate all logic to the shared processor.
    return JqProcessor.execute(query, input_data)
