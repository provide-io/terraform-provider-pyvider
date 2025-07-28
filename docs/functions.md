---
page_title: "Pyvider Provider: Functions"
description: |-
  Documentation for the utility functions provided by the Pyvider provider.
---

# Utility Functions

The Pyvider provider includes a rich set of utility functions for data manipulation, similar to a standard library.

## Collection Functions

*   `length(collection)`: Returns the number of elements in a list or map, or characters in a string.
*   `contains(list, element)`: Returns `true` if a list contains the given element.
*   `lookup(map, key, [default])`: Retrieves a value from a map by key. If the key is not found, returns the default value or raises an error if no default is provided.

## String Functions

*   `upper(string)`: Converts a string to uppercase.
*   `lower(string)`: Converts a string to lowercase.
*   `format(template, values)`: Formats a string using positional placeholders (e.g., `format("Hello, {0}!", ["World"])`).
*   `join(delimiter, list)`: Joins the elements of a list into a single string with the given delimiter.
*   `split(delimiter, string)`: Splits a string by a delimiter into a list of strings.
*   `replace(string, search, replacement)`: Replaces all occurrences of a substring.

## Numeric Functions

*   `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`: Basic arithmetic operations.
*   `min(list)`, `max(list)`, `sum(list)`: Aggregate functions for lists of numbers.
*   `round(number, [precision])`: Rounds a number to a given number of decimal places.

## Type Conversion Functions

*   `tostring(value)`: Explicitly converts any value to its string representation, ensuring booleans become `"true"` or `"false"`.
