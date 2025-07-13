import os
from typing import (
    Any,
    List,
    Optional,
    Dict,
    Union
)


_NOT_FOUND = object()
_EMPTY_FILE = object()


def _is_plural_dict(data: Any) -> bool:
    """
    Checks if the given object resembles a dictionary for plural forms.

    This is a heuristic check. It considers an object a plural dictionary
    if it's a dictionary and contains at least one key from the CLDR plural
    categories ('zero', 'one', 'two', 'few', 'many', 'other') with a
    string value.
    """

    if not isinstance(data, dict):
        return False

    plural_keys = {'zero', 'one', 'two', 'few', 'many', 'other'}
    return any(key in data and isinstance(data[key], str) for key in plural_keys)


def _get_value_by_path_single(path: List[Union[str, int]], data: Optional[Dict[str, Any]]) -> Any:
    """
    Helper method to retrieve a value by path only from a given dictionary.

    Supports paths containing both dictionary keys (str) and list indices (int).
    Returns the value found (including None if it's an explicit value),
    or returns a special 'not found' indicator if the path segment does not exist
    or traversal fails. A simple `None` return cannot distinguish these.
    Let's use a sentinel value or raise a specific internal exception.
    Using a sentinel is cleaner as this is an internal helper.
    """

    if data is None or not isinstance(data, dict):
        return _NOT_FOUND if path else data  # Return data itself if path is empty

    value = data
    for i, key_or_index in enumerate(path):
        if isinstance(value, dict):
            if not isinstance(key_or_index, str):
                return _NOT_FOUND  # Expected string key for dict
            if key_or_index not in value:
                return _NOT_FOUND  # Key not found in dict

            next_value = value.get(key_or_index)
            if i < len(path) - 1:
                if not isinstance(next_value, (dict, list)):
                    return _NOT_FOUND
                value = next_value
            else:
                return next_value

        elif isinstance(value, list):
            if not isinstance(key_or_index, int):
                return _NOT_FOUND
            if not (0 <= key_or_index < len(value)):
                return _NOT_FOUND

            next_value = value[key_or_index]
            if i < len(path) - 1:
                if not isinstance(next_value, (dict, list)):
                    return _NOT_FOUND
                value = next_value
            else:
                # This is the last element, return the actual value (could be None)
                return next_value

        else:
            return _NOT_FOUND  # Cannot traverse through non-collection type

    # Return the initial data if path was empty
    return data


def _get_locale_code(filename: str) -> str:
    locale_code_raw = os.path.splitext(filename)[0]
    locale_code_normalized = locale_code_raw.lower()
    return locale_code_normalized


def _deep_merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
            _deep_merge(value, destination[key])
        else:
            destination[key] = value


__all__ = [
    "_NOT_FOUND",
    "_EMPTY_FILE",
    "_get_value_by_path_single",
    "_is_plural_dict",
    "_get_locale_code",
    "_deep_merge"
]
