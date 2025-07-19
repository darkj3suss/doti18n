import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from .utils import (
    _NOT_FOUND,
    _get_value_by_path_single,
    _is_plural_dict,
)
from .wrapped import (
    LocaleList,
    LocaleNamespace,
    NoneWrapper,
    PluralWrapper,
    StringWrapper,
)

logger = logging.getLogger(__name__)
try:
    from babel import Locale
except ImportError:
    logger.warning("Babel is not installed. Library working can be unstable (especially plural forms).")

    if not TYPE_CHECKING:

        class Locale:
            """Stub Locale class."""

            def __init__(self, *args, **kwargs):
                """
                Initialize the stub Locale class.

                The stub plural_form implementation is very basic.
                A more robust dummy might be needed depending on usage,
                but 'other' is the most common fallback.
                """
                pass

            def plural_form(self, *args, **kwargs):
                """Stub plural_form function."""
                # Always return 'other' as a fallback without Babel
                return "other"


class LocaleTranslator:
    """
    Translator for localization data for a specific locale.

    Supports a 'strict' mode where missing keys raise exceptions.
    """

    def __init__(
        self,
        locale_code: str,
        current_locale_data: Optional[Dict[str, Any]],
        default_locale_data: Optional[Dict[str, Any]],
        default_locale_code: str,
        strict: bool = False,
    ):
        """
        Initialize a LocaleTranslator.

        :param locale_code: The code of the locale this translator handles (e.g., 'en.yml', 'fr').
        :type locale_code: str
        :param current_locale_data: The raw localization data (as a dictionary) for the current locale.
                                    Can be None if the locale file was not found or invalid.
        :type current_locale_data: Optional[Dict[str, Any]]
        :param default_locale_data: The raw localization data (as a dictionary) for the default locale.
                                    Can be None if the default locale file was not found or invalid.
        :type default_locale_data: Optional[Dict[str, Any]]
        :param default_locale_code: The code of the default locale.
        :type default_locale_code: str
        :param strict: If True, accessing a non-existent key will raise AttributeError.
                       If False (default), it returns None and logs a warning.
        :type strict: bool
        """
        self.locale_code = locale_code
        self._logger = logger
        self._current_locale_data = current_locale_data if isinstance(current_locale_data, dict) else {}
        self._default_locale_data = default_locale_data if isinstance(default_locale_data, dict) else {}
        self._default_locale_code = default_locale_code
        self._strict = strict

    def _get_value_by_path(self, path: List[Union[str, int]]) -> Tuple[Any, Optional[str]]:
        """
        Retrieve the value at the given path.

        First, checking the current locale first, then the default locale.
        Return the value found and the locale code where it was found.
        Uses _NOT_FOUND sentinel if the path does not exist in either locale.

        :param path: The list of keys/indices representing as a path (e.g., ['messages', 'hi'] or ['page', 0, 'title']).
        :type path: List[Union[str, int]] # Обновить docstring
        :return: A tuple containing the value (Any) and the locale code (Optional[str])
                 where the value was found. Returns (None, None) if not found.
        :rtype: Tuple[Any, Optional[str]]
        """
        value_from_current = _get_value_by_path_single(path, self._current_locale_data)
        if value_from_current is not _NOT_FOUND:  # Check against sentinel
            return value_from_current, self.locale_code

        value_from_default = _get_value_by_path_single(path, self._default_locale_data)
        if value_from_default is not _NOT_FOUND:  # Check against sentinel
            self._logger.warning(
                f"Fallback for key '{'.'.join(list(map(str, path)))}' "
                f"from '{self.locale_code}' "
                f"to '{self._default_locale_code}'"
            )
            return value_from_default, self._default_locale_code

        # If sentinel returned from both, the path was not found
        return _NOT_FOUND, None  # Return sentinel and None locale code

    def _get_plural_form_key(self, count: int, locale_code: Optional[str]) -> str:
        """
        Determine the plural form key based on a number and locale code.

        :param count: The number for which to determine the plural form.
        :type count: int
        :param locale_code: The locale code to use for plural rules. If None,
                            uses the translator's current locale code.
        :type locale_code: Optional[str]
        :return: The plural form key (e.g., 'one', 'few', 'many', 'other').
                 Returns 'other' as a fallback in case of errors.
        :rtype: str
        """
        target_locale_code = locale_code if locale_code else self.locale_code
        try:
            # Babel's Locale expects underscores for territory (e.g., en_US)
            locale_obj = Locale(target_locale_code.replace("-", "_"))
            plural_rule_func = locale_obj.plural_form
            return plural_rule_func(abs(count))
        except Exception as e:
            self._logger.warning(
                f"Babel failed to get plural rule function or category for count {abs(count)} "
                f"and locale '{target_locale_code}': {e}. Falling back to 'other'.",
                exc_info=True,
            )
            return "other"

    def _get_plural_template(
        self,
        path: List[Union[str, int]],
        count: int,
        current_plural_dict: Dict[str, Any],
        current_plural_locale_code: Optional[str],
    ) -> Optional[str]:
        """
        Retrieve the plural template string based on the count and locale rules.

        Searche first in the provided plural dictionary, then in the default locale's
        corresponding plural dictionary. Returns the template string or None.

        :param path: The full path to the plural dictionary.
        :type path: List[str]
        :param count: The number used to determine the plural form.
        :type count: int
        :param current_plural_dict: The plural dictionary found in the current locale
                                    (or the first locale where it was found).
        :type current_plural_dict: Dict[str, Any]
        :param current_plural_locale_code: The locale code where `current_plural_dict` was found.
                                         Used for getting the plural form key.
        :type current_plural_locale_code: Optional[str]
        :return: The template string for the determined plural form, or the 'other' form,
                 or None if no suitable template is found in either locale.
        :rtype: Optional[str]
        """
        form_key = self._get_plural_form_key(count, current_plural_locale_code)
        template = current_plural_dict.get(form_key)
        if template is None:
            template = current_plural_dict.get("other")

        if template is None:
            default_plural_dict = _get_value_by_path_single(path, self._default_locale_data)
            if (
                default_plural_dict is not None
                and isinstance(default_plural_dict, dict)
                and _is_plural_dict(default_plural_dict)
            ):
                template = default_plural_dict.get(form_key)
                if template is None:
                    template = default_plural_dict.get("other")

        return template if isinstance(template, str) else None

    def _handle_resolved_value(self, value: Any, path: List[Union[str, int]], found_locale_code: Optional[str]) -> Any:
        """
        Process the value obtained from _get_value_by_path.

        Assumes the value is NOT the _NOT_FOUND sentinel.
        Logs a warning if an explicit None value is found.

        :param value: The value retrieved by _get_value_by_path.
        :type value: Any
        :param path: The full path used to retrieve the value.
        :type path: List[Union[str, int]] # Обновить docstring
        :param found_locale_code: The locale code where the value was found.
        :type found_locale_code: Optional[str]
        :return: The processed value or handler.
        :rtype: Any
        :raises ValueError: If formatting a plural string fails.
        :raises AttributeError: If a template for a plural form is not a string.
        """
        if isinstance(value, str):
            return StringWrapper(value)
        elif isinstance(value, dict):
            if _is_plural_dict(value):
                full_path = ".".join(map(str, path))
                return PluralWrapper(
                    func=self._create_plural_handler(path, value, found_locale_code),
                    path=full_path,
                    strict=self._strict,
                )
            else:
                return LocaleNamespace(path, self)
        elif isinstance(value, list):
            return LocaleList(value, path, self)
        else:
            # Always return the raw simple value (int, float, bool, or the explicit None)
            return value

    def _create_plural_handler(
        self, path: List[Union[str, int]], plural_dict: Dict[str, Any], found_locale_code: Optional[str]
    ) -> Callable:
        """Create the callable plural handler."""

        def plural_handler(count: int, **kwargs) -> str:
            """
            Return handler for plural localization keys.

            Format the appropriate plural template based on the count.
            """
            if not isinstance(count, int):
                raise TypeError(
                    f"Plural handler for key '{'.'.join(map(str, path))}' "
                    f"requires an integer count, not {type(count).__name__}"
                )

            template = self._get_plural_template(path, count, plural_dict, found_locale_code)

            full_key_path_str = ".".join(map(str, path))
            if template is None:
                form_key = self._get_plural_form_key(count, found_locale_code)
                raise AttributeError(
                    f"Failed to find plural template for key '{full_key_path_str}' "
                    f"(form '{form_key}', count {count}) in locale '{found_locale_code or self.locale_code}' "
                    f"or default '{self._default_locale_code}'."
                )

            format_args = {"count": count}
            format_args.update(kwargs)
            try:
                return template.format(**format_args)
            except KeyError as e:
                form_key = self._get_plural_form_key(count, found_locale_code)
                raise ValueError(
                    f"Formatting error for plural key '{full_key_path_str}' (form '{form_key}'): "
                    f"Missing placeholder {e} in template '{template}'"
                )
            except AttributeError:
                form_key = self._get_plural_form_key(count, found_locale_code)
                raise ValueError(f"Error: Template for key '{full_key_path_str}' form '{form_key}' is not a string.")

        return plural_handler

    def _resolve_value_by_path(self, path: List[Union[str, int]]) -> Any:
        """
        Retrieve and process a value given its full path.

        Used by LocaleNamespace, LocaleList, and the Translator itself. Handles the
        strict/non-strict behavior for missing keys/indices.

        :param path: The list of keys/indices represents the full path.
        :type path: List[Union[str, int]] # Обновить docstring
        :return: The resolved value or handler.
        :rtype: Any
        :raises AttributeError: If the key path is not found (for str keys) and self._strict is True.
        :raises IndexError: If an index path is out of bounds (for int indices) and self._strict is True.
        """
        # FIXME: bug with pycharm debugger
        # I noticed that in the debugger pycharm somthing tries to get the `shape` key.
        # If you have any ideas how to fix this instead of such a crutch - I'm waiting for your pull-requests.
        # Keep the crutch as it was in the original code, though its placement might need review.
        if path and path[0] == "shape":
            return None

        value, found_locale_code = self._get_value_by_path(path)

        if value is _NOT_FOUND:
            full_key_path = ".".join(map(str, path))
            if self._strict:
                if path and isinstance(path[-1], int):
                    raise IndexError(
                        f"Locale '{self.locale_code}': Index out of bounds or path invalid "
                        f"for path '{full_key_path}' "
                        f"(looked in current '{self.locale_code}' and default '{self._default_locale_code}')."
                    )
                else:
                    raise AttributeError(
                        f"Locale '{self.locale_code}': Strict mode error: Key/index path '{full_key_path}' not found "
                        f"in translations (including default '{self._default_locale_code}')."
                    )
            else:
                logger.warning(
                    f"Locale '{self.locale_code}': key/index path '{full_key_path}' not found "
                    f"in translations (including default '{self._default_locale_code}'). None will be returned."
                )
                return NoneWrapper(self.locale_code, full_key_path)

        # If the value is *not* the sentinel, it means _get_value_by_path found *something*
        return self._handle_resolved_value(value, path, found_locale_code)

    def __getattr__(self, name: str) -> Any:
        """
        Handle attribute access for the top level (e.g., `data['en.yml'].messages`).

        Delegates the resolution to `_resolve_value_by_path` unless the attribute
        exists in the object's attributes.

        :param name: The attribute name (the first key in the path).
        :type name: str
        :return: The resolved value, which could be a string, LocaleNamespace,
                 LocaleList, plural handler, or None.
        :rtype: Any
        """
        if name in dir(self):
            return object.__getattribute__(self, name)

        return self._resolve_value_by_path([name])

    def __iter__(self):
        """Return an iterator for the current locale data."""
        return iter(self._current_locale_data)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handle attempts to call the LocaleTranslator object directly.

        This is not supported, access keys via dot notation.

        :raises TypeError: If the LocaleTranslator object is called.
        """
        raise TypeError(
            f"'{type(self).__name__}' object is not callable directly. "
            "Access keys using dot notation (e.g., .greeting, .apples(5))."
        )

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return f"<LocaleTranslator for '{self.locale_code}' (strict={self._strict})>"

    def __repr__(self) -> str:
        """Return string representation of the translator for debugging."""
        return self.__str__()
