import logging
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Union,
)

from ..utils import _NOT_FOUND

if TYPE_CHECKING:
    import doti18n


logger = logging.getLogger(__name__)


class LocaleNamespace:
    """
    Represent a nested namespace of localizations accessible via dot notation.

    This class is used internally by LocaleTranslator to provide access
    to nested YAML structures like `messages.status.online`.
    """

    __slots__ = ("_path", "_translator")

    def __init__(self, path: List[Union[str, int]], translator: "doti18n.LocaleTranslator"):
        """
        Initialize a LocaleNamespace.

        :param path: The list of keys representing the path to this namespace.
        :param translator: The LocaleTranslator instance this namespace belongs to.
        :type translator: LocaleTranslator
        """
        self._path = path
        self._translator = translator

    def __getattr__(self, name: str) -> Any:
        """
        Handle attribute access (e.g., `messages.greeting`).

        This method constructs the new path and delegates the value resolution
        to the associated LocaleTranslator. The behavior (return None/log warning
        or raise exception) is determined by the translator's `strict` setting.

        :param name: The attribute name (the next key in the path).
        :return: The resolved value, which could be a string, another
                 LocaleNamespace, a plural handler callable, or None (in non-strict mode).
        :raises AttributeError: If the key is not found and the translator is in strict mode.
        """
        new_path = self._path + [name]
        return self._translator._resolve_value_by_path(new_path)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handle attempts to call the object (e.g., `messages.greeting()`).

        This raises a TypeError because LocaleNamespace objects represent
        namespaces or simple values, not callable functions (unless it's
        a plural handler returned by `__getattr__` for a plural dict).

        :raises TypeError: If the LocaleNamespace object is called.
        """
        full_key_path = ".".join(map(str, self._path)) if self._path else "root"
        raise TypeError(
            f"'{type(self).__name__}' object at path '{full_key_path}' is not callable. "
            f"It represents a localization namespace or a simple value. "
            f"Access nested keys using dot notation (e.g., .title) or format plural keys (e.g., .apples(5))."
        )

    def __repr__(self) -> str:
        """Return string representation of the namespace for debugging."""
        path_str = ".".join(map(str, self._path)) if self._path else "root"
        return (
            f"<LocaleNamespace at path '{path_str}' for '{self._translator.locale_code}' "
            f"(strict={self._translator._strict})>"
        )

    def __str__(self) -> str:
        """Return stirng representation of the namespace."""
        return ".".join(map(str, self._path))

    def __contains__(self, name: str) -> bool:
        """Check if a key exists in the namespace."""
        if not isinstance(name, str):
            raise TypeError(f"Expected a string, got {type(name).__name__}")

        data = self._translator._get_value_by_path(self._path + [name])
        if data[0] is _NOT_FOUND:
            return False

        return True

    def __iter__(self):
        """Iterate over the keys in the namespace."""
        data, _ = self._translator._get_value_by_path(self._path)
        for key in data:
            if isinstance(data.get(key), dict):
                yield LocaleNamespace(self._path + [key], self._translator)
            else:
                yield key

    def __len__(self):
        """Return the length of the namespace."""
        data, _ = self._translator._get_value_by_path(self._path)
        return len(data)

    def __reversed__(self):
        """Reverse the iteration order."""
        return reversed(list(self.__iter__()))

    def get(self, name: str) -> Any:
        """Symbolic alias for __getattr__."""
        return self._resolve_value_by_path([name])

    def to_list(self):
        """Convert the namespace to a list."""
        return list(self.__iter__())

    def to_set(self):
        """Convert the namespace to a set."""
        return set(self.__iter__())

    def to_tuple(self):
        """Convert the namespace to a tuple."""
        return tuple(self.__iter__())

    def to_dict(self):
        """Convert the namespace to a dictionary."""
        data, _ = self._translator._get_value_by_path(self._path)
        return {
            key: LocaleNamespace(self._path + [key], self._translator) if isinstance(value, dict) else value
            for key, value in data.items()
        }
