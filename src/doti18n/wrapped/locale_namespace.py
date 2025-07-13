import logging
from typing import (
    List,
    Any,
    Union,
    TYPE_CHECKING,
)
from ..utils import _NOT_FOUND
from .string_wrapper import StringWrapper
if TYPE_CHECKING:
    import doti18n


logger = logging.getLogger(__name__)


class LocaleNamespace:
    """
    Represents a nested namespace of localizations accessible via dot notation.

    This class is used internally by LocaleTranslator to provide access
    to nested YAML structures like `messages.status.online`.
    """

    def __init__(self, path: List[Union[str, int]], translator: 'doti18n.LocaleTranslator'):
        """
        Initializes a LocaleNamespace.

        :param path: The list of keys representing the path to this namespace.
        :type path: List[str]
        :param translator: The LocaleTranslator instance this namespace belongs to.
        :type translator: LocaleTranslator
        """

        self._path = path
        self._translator = translator

    def __getattr__(self, name: str) -> Any:
        """
        Handles attribute access (e.g., `messages.greeting`).

        This method constructs the new path and delegates the value resolution
        to the associated LocaleTranslator. The behavior (return None/log warning
        or raise exception) is determined by the translator's `strict` setting.

        :param name: The attribute name (the next key in the path).
        :type name: str
        :return: The resolved value, which could be a string, another
                 LocaleNamespace, a plural handler callable, or None (in non-strict mode).
        :rtype: Any
        :raises AttributeError: If the key is not found and the translator is in strict mode.
        """

        new_path = self._path + [name]
        return self._translator._resolve_value_by_path(new_path)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handles attempts to call the object (e.g., `messages.greeting()`).

        This raises a TypeError because LocaleNamespace objects represent
        namespaces or simple values, not callable functions (unless it's
        a plural handler returned by `__getattr__` for a plural dict).

        :raises TypeError: If the LocaleNamespace object is called.
        """

        full_key_path = '.'.join(map(str, self._path)) if self._path else "root"
        raise TypeError(
            f"'{type(self).__name__}' object at path '{full_key_path}' is not callable. "
            f"It represents a localization namespace or a simple value. "
            f"Access nested keys using dot notation (e.g., .title) or format plural keys (e.g., .apples(5))."
        )

    def __repr__(self) -> str:
        path_str = '.'.join(map(str, self._path)) if self._path else "root"
        return (
            f"<LocaleNamespace at path '{path_str}' for '{self._translator.locale_code}' "
            f"(strict={self._translator._strict})>"
        )

    def __str__(self) -> str:
        return self._path[-1]

    def __contains__(self, name: str | StringWrapper) -> bool:
        if not isinstance(name, str):
            raise TypeError(f"Expected a string, got {type(name).__name__}")

        data = self._translator._get_value_by_path(self._path + [name])
        if data[0] is _NOT_FOUND:
            return False

        return True

    def __iter__(self):
        data, _ = self._translator._get_value_by_path(self._path)
        for key in data:
            if isinstance(data.get(key), dict):
                yield LocaleNamespace(self._path + [key], self._translator)
            else:
                yield key

    def __len__(self):
        data, _ = self._translator._get_value_by_path(self._path)
        return len(data)

    def __reversed__(self):
        return reversed(list(self.__iter__()))

    def get(self, name: str, default: Any = None) -> Any:
        """
        Retrieve the value of an attribute by name. If the attribute does not exist
        or evaluates to a falsy value, the specified default value will be returned.

        :param name: The name of the attribute to retrieve.
        :type name: str
        :param default: The value returned if the attribute does not exist or is falsy.
        :type default: Any
        :return: The value of the specified attribute or the default value.
        :rtype: Any
        """
        data = self.__getattr__(name)
        return data if data else default

    def to_list(self):
        return list(self.__iter__())

    def to_set(self):
        return set(self.__iter__())

    def to_tuple(self):
        return tuple(self.__iter__())

    def to_dict(self):
        data, _ = self._translator._get_value_by_path(self._path)
        return {key: LocaleNamespace(self._path + [key], self._translator) if isinstance(value, dict) else value for key, value in data.items()}
