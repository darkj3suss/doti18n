import os
from typing import Any

_NOT_FOUND = object()


def _is_plural_dict(data: dict) -> bool:
    """
    Check if the given object resembles a dictionary for plural forms.

    This is a heuristic check. It considers an object a plural dictionary
    if it's a dictionary and contains at least one key from the CLDR plural
    categories ('zero', 'one', 'two', 'few', 'many', 'other') with a
    string value.
    """
    if not isinstance(data, dict):
        return False

    plural_keys = {"zero", "one", "two", "few", "many", "other"}
    return any(key in data and isinstance(data[key], str) for key in plural_keys)


def _get_value_by_path_single(path: list, data: list | dict | None) -> Any:
    """Retrieve a value by path from a single dictionary."""
    current_value = data

    for key_or_index in path:
        if isinstance(current_value, dict):
            if not isinstance(key_or_index, str) or key_or_index not in current_value:
                return _NOT_FOUND
            current_value = current_value[key_or_index]
            continue

        if isinstance(current_value, list):
            if not isinstance(key_or_index, int) or not (0 <= key_or_index < len(current_value)):
                return _NOT_FOUND
            current_value = current_value[key_or_index]
            continue

        return _NOT_FOUND

    return current_value


def _get_locale_code(filename: str) -> str:
    locale_code_raw = os.path.splitext(filename)[0]
    locale_code_normalized = locale_code_raw.lower()
    return locale_code_normalized


def _deep_merge(source: dict | None, destination: dict | None) -> None:
    if not isinstance(source, dict) or not isinstance(destination, dict):
        return

    for key, value in source.items():
        if key in destination and isinstance(value, dict) and isinstance(destination.get(key), dict):
            _deep_merge(value, destination.get(key))
        else:
            destination[key] = value


__all__ = [
    "_NOT_FOUND",
    "_get_value_by_path_single",
    "_is_plural_dict",
    "_get_locale_code",
    "_deep_merge",
]
