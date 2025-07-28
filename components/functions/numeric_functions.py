# components/functions/numeric_functions.py

from pyvider.exceptions import FunctionError
from pyvider.hub import register_function


@register_function(
    name="add",
    summary="Adds two numbers.",
    description="Adds the two numeric arguments.",
    param_descriptions={"a": "The first number.", "b": "The second number."},
)
def add(a: int | float | None, b: int | float | None) -> int | float | None:
    """Adds two numbers. If any argument is null, the result is null."""
    if a is None or b is None:
        return None
    try:
        result = a + b
        return int(result) if isinstance(result, float) and result.is_integer() else result
    except TypeError as e:
        raise FunctionError(f"Invalid argument types for addition: {e}") from e


@register_function(
    name="subtract",
    summary="Subtracts two numbers.",
    description="Subtracts the second number from the first.",
    param_descriptions={"a": "The number to subtract from.", "b": "The number to subtract."},
)
def subtract(a: int | float | None, b: int | float | None) -> int | float | None:
    """Subtracts two numbers. If any argument is null, the result is null."""
    if a is None or b is None:
        return None
    try:
        result = a - b
        return int(result) if isinstance(result, float) and result.is_integer() else result
    except TypeError as e:
        raise FunctionError(f"Invalid argument types for subtraction: {e}") from e


@register_function(
    name="multiply",
    summary="Multiplies two numbers.",
    description="Multiplies the two numeric arguments.",
    param_descriptions={"a": "The first number.", "b": "The second number."},
)
def multiply(a: int | float | None, b: int | float | None) -> int | float | None:
    """Multiplies two numbers. If any argument is null, the result is null."""
    if a is None or b is None:
        return None
    try:
        result = a * b
        return int(result) if isinstance(result, float) and result.is_integer() else result
    except TypeError as e:
        raise FunctionError(f"Invalid argument types for multiplication: {e}") from e


@register_function(
    name="divide",
    summary="Divides two numbers.",
    description="Divides the first number by the second.",
    param_descriptions={"a": "The numerator.", "b": "The denominator."},
)
def divide(a: int | float | None, b: int | float | None) -> int | float | None:
    """Divides the first number by the second. If any argument is null, the result is null."""
    if a is None or b is None:
        return None
    if b == 0:
        raise FunctionError("Division by zero.")
    try:
        result = a / b
        return int(result) if isinstance(result, float) and result.is_integer() else result
    except TypeError as e:
        raise FunctionError(f"Invalid argument types for division: {e}") from e


@register_function(
    name="min",
    summary="Finds the minimum value in a list of numbers.",
    description="Returns the minimum value from a list of numbers.",
    param_descriptions={"numbers": "A list of numbers."},
)
def min_value(numbers: list[int | float] | None) -> int | float | None:
    """Finds the minimum value in a list of numbers. Returns null for null input."""
    if numbers is None:
        return None
    if not numbers:
        raise FunctionError("min() requires at least one number.")
    return min(numbers)


@register_function(
    name="max",
    summary="Finds the maximum value in a list of numbers.",
    description="Returns the maximum value from a list of numbers.",
    param_descriptions={"numbers": "A list of numbers."},
)
def max_value(numbers: list[int | float] | None) -> int | float | None:
    """Finds the maximum value in a list of numbers. Returns null for null input."""
    if numbers is None:
        return None
    if not numbers:
        raise FunctionError("max() requires at least one number.")
    return max(numbers)


@register_function(
    name="sum",
    summary="Calculates the sum of a list of numbers.",
    description="Returns the sum of a list of numbers. Returns 0 for an empty list.",
    param_descriptions={"numbers": "A list of numbers to sum."},
)
def sum_list(numbers: list[int | float] | None) -> int | float | None:
    """Calculates the sum of a list of numbers. Returns null for null input."""
    if numbers is None:
        return None
    result = sum(numbers)
    return int(result) if isinstance(result, float) and result.is_integer() else result


@register_function(
    name="round",
    summary="Rounds a number to a specified precision.",
    description="Rounds a number to a given number of decimal places (default is 0).",
    param_descriptions={
        "number": "The number to round.",
        "precision": "The number of decimal places to round to.",
    },
)
def round_number(number: int | float | None, precision: int | None = 0) -> int | float | None:
    """Rounds a number to a specified precision. Returns null for null input."""
    if number is None or precision is None:
        return None
    try:
        int_precision = int(precision)
        return round(number, int_precision)
    except TypeError as e:
        raise FunctionError(f"Invalid argument types for round: {e}") from e
