from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Union,
)

from ..utils import _NOT_FOUND

if TYPE_CHECKING:
    import doti18n


class NamespaceWrapper:
    """
    Represent a nested namespace of localizations accessible via dot notation.

    This class is used internally by LocaleTranslator to provide access
    to nested structures like `messages.status.online`.
    """

    __slots__ = ("_path", "_translator")

    def __init__(self, path: List[Union[str, int]], translator: "doti18n.LocaleTranslator"):
        """Initialize a LocaleNamespace."""
        self._path = path
        self._translator = translator

    def __getattr__(self, name: str) -> Any:
        """Handle attribute access (e.g., `messages.greeting`)."""
        path = self._path + [name]
        return self._translator._resolve_value_by_path(path)

    def __call__(self, *args, **kwargs) -> Any:
        """Handle attempts to call the object (e.g., `messages.greeting()`)."""
        full_key_path = ".".join(map(str, self._path)) if self._path else "root"
        raise TypeError(f"'{type(self).__name__}' object at path '{full_key_path}' is not callable. ")

    def __repr__(self) -> str:
        """Return string representation of the namespace for debugging."""
        path_str = ".".join(map(str, self._path)) if self._path else "root"
        return (
            f"<LocaleNamespace['{self._translator.locale_code}'] at path '{path_str}' "
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
            yield self._translator._get_value_by_path(self._path + [key])[0]

    def __len__(self):
        """Return the length of the namespace."""
        data, _ = self._translator._get_value_by_path(self._path)
        return len(data)

    def __reversed__(self):
        """Reverse the iteration order."""
        return reversed(tuple(self.__iter__()))

    def get(self, name: str) -> Any:
        """Symbolic alias for __getattr__."""
        return self._translator._resolve_value_by_path(self._path + [name])
