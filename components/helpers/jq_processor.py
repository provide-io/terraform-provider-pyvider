from decimal import Decimal
import json
from typing import Any

import jq as jq_library

from pyvider.cty.conversion import cty_to_native
from pyvider.exceptions import FunctionError
from pyvider.telemetry import logger


class DecimalAwareJSONEncoder(json.JSONEncoder):
    """A JSON encoder that can handle Decimal objects."""
    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super().default(o)

class JqProcessor:
    """A reusable helper to encapsulate the JQ processing logic."""
    @staticmethod
    def execute(query: str, input_data: Any) -> Any:
        """
        Executes a JQ query and returns the result.
        """
        logger.debug("⚙️ JQ ✅ Applying jq query", query=query)
        try:
            # Always convert the input data (which might be a CtyValue)
            # to a native Python object before JSON serialization.
            native_data = cty_to_native(input_data)
            json_input_text = json.dumps(native_data, cls=DecimalAwareJSONEncoder)

            # Always use .all() for consistent behavior. This is more robust
            # than trying to guess the query's output structure.
            results = jq_library.all(query, text=json_input_text)

            # If the query was intended to produce a single value (like '.key'),
            # jq.all() will return a list with one item. We unwrap it here
            # to provide the most intuitive result to the user.
            # If the query produces a stream of results, they remain in a list.
            return results[0] if len(results) == 1 else results
        except Exception as e:
            logger.error("⚙️ JQ ❌ JQ processing failed", error=str(e), exc_info=True)
            raise FunctionError(f"jq query failed: {e}") from e
