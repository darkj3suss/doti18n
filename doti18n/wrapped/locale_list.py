import logging
from typing import TYPE_CHECKING, Any, List, SupportsIndex, Union, overload

if TYPE_CHECKING:
    import doti18n

logger = logging.getLogger(__name__)


class LocaleList(list):
    """
    Represent a nested list of localizations accessible via index notation.

    This class is used internally by LocaleTranslator to provide access
    to nested YAML structures like `locale["en"].list[0].item`.
    """

    def __init__(self, data: List[Any], path: List[Union[str, int]], translator: "doti18n.LocaleTranslator"):
        """
        Initialize a LocaleList.

        :param data: The actual list data from the localization.
        :type data: List[Any]
        :param path: The list of keys/indices representing the path to this list.
        :type path: List[Union[str, int]]
        :param translator: The LocaleTranslator instance this list belongs to.
        :type translator: LocaleTranslator
        """
        self._data = data
        self._path = path
        self._translator = translator
        self._strict = translator._strict
        super().__init__(data)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> Any: ...

    @overload
    def __getitem__(self, index: slice, /) -> list[Any]: ...

    def __getitem__(self, index: Union[SupportsIndex, slice], /) -> Any:
        """
        Construct a path and delegate resolution to the LocaleTranslator.

        :param index: The index to access in the list.
        :type index: int
        :return: The resolved value, which could be a string, another
                 LocaleNamespace, LocaleList, plural handler callable,
                 or None (in non-strict mode on error).
        :rtype: Any
        :raises IndexError: If the index is out of bounds and the translator is in strict mode.
        """
        if isinstance(index, slice):
            return super().__getitem__(index)

        if not isinstance(index, int):
            raise TypeError(
                f"List access for path '{'.'.join(map(str, self._path))}' "
                f"requires an integer index, not {type(index).__name__}"
            )

        if 0 <= index < len(self._data):
            new_path = self._path + [index]
            return self._translator._resolve_value_by_path(new_path)
        else:
            full_path_str = ".".join(map(str, self._path))
            if self._strict:
                raise IndexError(
                    f"Locale '{self._translator.locale_code}': Strict mode error: "
                    f"Index {index} out of bounds for list at path '{full_path_str}' (length {len(self._data)})."
                )
            else:
                logger.warning(
                    f"Locale '{self._translator.locale_code}': Index {index} out of bounds "
                    f"for list at path '{full_path_str}' (length {len(self._data)}). Returning None."
                )
                return None

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handle attempts to call the object (e.g., `mylist()`).

        Raises a TypeError because LocaleList objects represent
        lists/namespaces, not callable functions.

        :raises TypeError: If the LocaleList object is called.
        """
        full_key_path = ".".join(map(str, self._path)) if self._path else "root"
        raise TypeError(
            f"'{type(self).__name__}' object at path '{full_key_path}' is not callable. "
            f"Access list items using index notation (e.g., [0], [1])."
        )

    def __str__(self) -> str:
        """Return string representation of the list."""
        return str(self._data)

    def __repr__(self) -> str:
        """Return string representation of the namespace for debugging."""
        path_str = ".".join(map(str, self._path)) if self._path else "root"
        return (
            f"<LocaleList at path '{path_str}' for '{self._translator.locale_code}' "
            f"len={len(self._data)} data={repr(self._data)}>"
        )
