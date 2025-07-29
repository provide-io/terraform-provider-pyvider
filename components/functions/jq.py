import json
from typing import Any

from pyvider.exceptions import FunctionError
from pyvider.hub import register_function
from pyvider.telemetry import logger

# Import the corrected, centralized processor and its encoder
from ..helpers.jq_processor import DecimalAwareJSONEncoder, JqProcessor


@register_function(
    name="pyvider_jq",
    summary="Processes a data structure with a jq query.",
    description="Applies a jq query to the given input data. Returns a valid JSON string.",
    param_descriptions={
        "input_data": "The data structure to process.",
        "query": "The jq query string to apply.",
    },
)
def jq(input_data: Any, query: str) -> str:
    """
    Applies a jq query. ALWAYS returns a valid JSON string.
    """
    logger.debug("⚙️ JQ 📞 Function 'pyvider_jq' called")
    if not isinstance(query, str) or not query:
        raise FunctionError("The 'query' argument must be a non-empty string.")

    try:
        # 1. Get the native Python result from the centralized processor.
        native_result = JqProcessor.execute(query, input_data)

        # 2. Always serialize the native result to a JSON string. This enforces
        #    the contract that this function's output is consumable by
        #    Terraform's `jsondecode()`.
        return json.dumps(native_result, ensure_ascii=False, cls=DecimalAwareJSONEncoder)
    except Exception as e:
        logger.error("⚙️ JQ ❌ JQ processing failed", error=str(e), exc_info=True)
        if isinstance(e, FunctionError):
            raise
        raise FunctionError(f"jq query failed: {e}") from e
