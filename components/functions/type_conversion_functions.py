from typing import Any

from pyvider.hub import register_function


@register_function(
    name="tostring",
    summary="Explicitly converts a value to a string.",
    param_descriptions={"value": "The value to convert to a string."},
)
def tostring(value: Any | None) -> str | None:
    """Converts its argument to a string value."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
