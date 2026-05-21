import logging
from typing import TYPE_CHECKING, Any, SupportsIndex, overload

if TYPE_CHECKING:
    import doti18n


class ListWrapper(list):
    """
    Represent a nested list of localizations accessible via index notation.

    This class is used internally by LocaleTranslator to provide access
    to nested structures like `locale["en"].list[0].item`.
    """

    __slots__ = ("_data", "_path", "_translator", "_strict", "_logger")

    def __init__(self, data: list[Any], path: list[str | int], translator: "doti18n.LocaleTranslator"):
        """Initialize a LocaleList."""
        self._data = data
        self._path = path
        self._logger = logging.getLogger(f"{self.__class__.__name__}[{repr(translator.locale_code)}]")
        self._translator = translator
        self._strict = translator._strict
        super().__init__(data)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> Any: ...

    @overload
    def __getitem__(self, index: slice, /) -> list[Any]: ...

    def __getitem__(self, index: SupportsIndex | slice, /) -> Any:
        """Construct a path and delegate resolution to the LocaleTranslator."""
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._data))
            return [self._translator._resolve_value_by_path(self._path + [idx]) for idx in range(start, stop, step)]

        try:
            idx = index.__index__()
        except AttributeError:
            raise TypeError(f"index must be SupportsIndex or slice, not {type(index).__name__}")
        else:
            return self._translator._resolve_value_by_path(self._path + [idx])

    def __iter__(self):
        """Iterate over the elements of the list."""
        for index, item in enumerate(self._data):
            path = self._path + [index]
            yield self._translator._resolve_value_by_path(path)

    def __call__(self, *args, **kwargs) -> Any:
        """Handle attempts to call the object (e.g., `list()`)."""
        full_path = ".".join(map(str, self._path)) if self._path else "root"
        raise TypeError(
            f"'{type(self).__name__}' object at path '{full_path}' is not callable. "
            f"Access list items using index notation (e.g., [0], [1])."
        )

    def __str__(self) -> str:
        """Return string representation of the path."""
        return ".".join(map(str, self._path))

    def __repr__(self) -> str:
        """Return string representation of the namespace for debugging."""
        path_str = ".".join(map(str, self._path)) if self._path else "root"
        return (
            f"<LocaleList at path '{path_str}' for '{self._translator.locale_code}' "
            f"len={len(self._data)} data={repr(self._data)}>"
        )
