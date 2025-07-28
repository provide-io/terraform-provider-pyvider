# components/functions/string_manipulation.py
from typing import Any

from pyvider.exceptions import FunctionError
from pyvider.hub import register_function

# Import the canonical tostring function for consistent type conversion.
from .type_conversion_functions import tostring


@register_function(
    name="upper",
    summary="Converts a string to uppercase.",
    param_descriptions={"input_str": "The string to convert."},
)
def upper(input_str: str | None) -> str | None:
    """Converts a string to uppercase. Returns null for null input."""
    if input_str is None:
        return None
    return input_str.upper()


@register_function(
    name="lower",
    summary="Converts a string to lowercase.",
    param_descriptions={"input_str": "The string to convert."},
)
def lower(input_str: str | None) -> str | None:
    """Converts a string to lowercase. Returns null for null input."""
    if input_str is None:
        return None
    return input_str.lower()


@register_function(
    name="format",
    summary="Formats a string using positional arguments.",
    param_descriptions={
        "template": "The format string (e.g., 'Hello {0}').",
        "values": "A list of values to insert into the template.",
    },
)
def format_str(template: str | None, values: list[Any] | None) -> str | None:
    """Formats a string using positional placeholders. Returns null if template is null."""
    if template is None:
        return None
    value_list = values or []
    try:
        # Use the canonical `tostring` to ensure booleans are 'true'/'false'.
        str_values = [tostring(v) for v in value_list]
        return template.format(*str_values)
    except IndexError as e:
        raise FunctionError(f"Formatting failed: not enough values for template '{template}'.") from e


@register_function(
    name="join",
    summary="Joins list elements with a delimiter.",
    param_descriptions={
        "delimiter": "The string to insert between elements.",
        "strings": "The list of elements to join.",
    },
)
def join(delimiter: str | None, strings: list[Any] | None) -> str | None:
    """Joins list elements with a delimiter. Returns null if the list is null."""
    if strings is None:
        return None
    delimiter_str = delimiter or ""
    # Use the canonical `tostring` to ensure booleans are 'true'/'false'.
    return delimiter_str.join(map(tostring, strings))


@register_function(
    name="split",
    summary="Splits a string by a delimiter.",
    param_descriptions={
        "delimiter": "The delimiter string to split by.",
        "string": "The string to split.",
    },
)
def split(delimiter: str | None, string: str | None) -> list[str] | None:
    """Splits a string by a delimiter. Returns null if the string is null."""
    if string is None:
        return None
    delimiter_str = delimiter or ""
    # Align with Terraform's behavior: splitting an empty string yields an empty list.
    if not string:
        return []
    return string.split(delimiter_str)


@register_function(
    name="replace",
    summary="Replaces occurrences of a substring.",
    param_descriptions={
        "string": "The input string.",
        "search": "The substring to search for.",
        "replacement": "The string to replace occurrences with.",
    },
)
def replace(string: str | None, search: str | None, replacement: str | None) -> str | None:
    """Replaces all occurrences of a substring. Returns null if the input string is null."""
    if string is None:
        return None
    return string.replace(search or "", replacement or "")
