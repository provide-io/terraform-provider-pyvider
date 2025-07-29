from typing import Any

from pyvider.cty import CtyDynamic, CtyValue
from pyvider.exceptions import FunctionError
from pyvider.telemetry import logger

# Import the corrected, centralized processor
from .jq_processor import JqProcessor


class JqCtyProcessor:
    """
    Executes a JQ query and uses framework utilities to return a native CtyValue.
    """
    @staticmethod
    def execute(query: str, input_data: Any) -> CtyValue:
        """
        Executes a JQ query and converts the raw Python result to a CtyValue.
        """
        logger.debug("⚙️ JQ-CTY ✅ Applying jq query for native CTY output", query=query)

        try:
            final_raw_result = JqProcessor.execute(query, input_data)

            # Use the canonical entry point for converting raw data
            # into the Cty system. This now correctly handles all cases.
            return CtyDynamic().validate(final_raw_result)
        except Exception as e:
            logger.error("⚙️ JQ-CTY ❌ JQ processing failed", error=str(e), exc_info=True)
            if isinstance(e, FunctionError):
                raise
            raise FunctionError(f"jq query failed: {e}") from e
