from typing import Any

from pyvider.exceptions import FunctionError
from pyvider.hub import register_function


@register_function(
    name="length",
    summary="Returns the length of a given list, map, or string.",
    param_descriptions={
        "collection": "The list, map, or string to determine the length of.",
    },
)
def length(collection: list | dict | str | None) -> int | None:
    """Returns the number of elements in a list/map or characters in a string."""
    if collection is None:
        return None
    return len(collection)

@register_function(
    name="contains",
    summary="Checks if a list contains a given element.",
    param_descriptions={
        "list_to_check": "The list to check for the element.",
        "element": "The element to look for.",
    },
)
def contains(list_to_check: list[Any] | None, element: Any) -> bool | None:
    """Returns true if a given list contains the given element value. Returns null if the list is null."""
    if list_to_check is None:
        return None
    return element in list_to_check

@register_function(
    name="lookup",
    summary="Performs a dynamic lookup into a map.",
    param_descriptions={
        "map_to_search": "The map to search for the key.",
        "key": "The key to look up in the map.",
        "default": "A default value to return if the key is not found. If omitted, an error is raised.",
    },
)
def lookup(map_to_search: dict[str, Any] | None, key: str, default: Any | None = None) -> Any:
    """Looks up a key in a map, returning null if the map is null, or a default value if the key is not found."""
    if map_to_search is None:
        return None

    if key in map_to_search:
        return map_to_search[key]

    if default is not None:
        return default

    raise FunctionError(f"Invalid key for map lookup: key \"{key}\" does not exist in the map.")
