import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from .errors import DefaultLocaleNotLoadedError, LocaleNotLoadedError, UnexpectedMultiLocaleError
from .loaders import Loader
from .locale_translator import LocaleTranslator
from .utils import _deep_merge

logger = logging.getLogger(__name__)


class LocaleData:
    """
    Manages the loading of all localization files and provides access to LocaleTranslator instances.

    Supports a 'strict' mode which is passed to created LocaleTranslator instances.
    """

    def __init__(self, locales_dir: str, default_locale: str = "en", strict: bool = False, preload: bool = True):
        """
        Initialize the LocaleData manager.

        :param locales_dir: The path to the directory containing YAML locale files.
        :param default_locale: The code of the default locale. (default: 'en')
        :param strict: If `True`, all created LocaleTranslator instances will be in strict mode.
                       That means that where you've gotten warnings before, you'll get exceptions.
                       (default: False).
        :param preload: If `True`, load all translations at initialization.
                        Not recommended to use with large locale directories.
                        Instead, you can use LocaleData.get("filename") to load individual locale.
                        (default: True)
        """
        self.locales_dir = locales_dir
        self.default_locale = default_locale.lower()
        self._logger = logger
        self._loader = Loader(strict)
        self._strict = strict
        self._raw_translations: Dict[str, Optional[Dict[str, Any]]] = {}
        self._locale_translators_cache: Dict[str, LocaleTranslator] = {}
        if preload:
            self._load_all_translations()

    def _load_all_translations(self):
        if not os.path.exists(self.locales_dir):
            self._throw(f"Locale directory '{self.locales_dir}' does not exist.", FileNotFoundError)
            return

        for filename in os.listdir(self.locales_dir):
            data = self._loader.load(os.path.join(self.locales_dir, filename))
            self._process_data(data)

        if not any(self._raw_translations.values()):
            self._throw(
                f"No localization files found or successfully loaded from '{self.locales_dir}'.", LocaleNotLoadedError
            )

        default_data = self._raw_translations.get(self.default_locale)
        if not isinstance(default_data, dict):
            if self.default_locale not in self._raw_translations:
                self._raw_translations[self.default_locale] = None  # Ensure entry exists
            elif not isinstance(default_data, dict):
                self._raw_translations[self.default_locale] = None  # None if not a dict

            self._throw(
                f"Default locale was not found or root is not a dictionary "
                f"({type(default_data).__name__ if default_data is not None else 'NoneType'}). "
                "Fallback to the default locale will be limited or impossible.",
                DefaultLocaleNotLoadedError,
            )

    def _process_data(self, data: Union[Dict[str, Any], List[Tuple[str, Dict[str, Any]]]]):
        if isinstance(data, dict):
            _deep_merge(data, self._raw_translations)

        elif isinstance(data, list):
            for locale_code, data in data:
                if locale_code in self._raw_translations:
                    _deep_merge(data, self._raw_translations[locale_code])
                else:
                    self._raw_translations[locale_code] = data

    def __getitem__(self, locale_code: str) -> LocaleTranslator:
        """
        Return the LocaleTranslator object for the specified locale code.

        Uses a cache to avoid creating multiple translator instances for the
        same locale. Normalizes the locale code to lowercase. The 'strict'
        setting of this LocaleData instance is passed to the translator.

        :param locale_code: The code of the desired locale (e.g., 'en', 'FR').
        :return: The LocaleTranslator instance for the requested locale.
        """
        normalized_locale_code = locale_code.lower()
        if normalized_locale_code in self._locale_translators_cache:
            return self._locale_translators_cache[normalized_locale_code]

        current_locale_data = self._raw_translations.get(normalized_locale_code)
        default_locale_data = self._raw_translations.get(self.default_locale)

        translator = LocaleTranslator(
            normalized_locale_code, current_locale_data, default_locale_data, self.default_locale, strict=self._strict
        )

        self._locale_translators_cache[normalized_locale_code] = translator
        return translator

    def __contains__(self, locale_code: str) -> bool:
        """
        Check if a locale with the given code was successfully loaded with a dictionary root.

        Normalizes the locale code to lowercase for the check.

        :param locale_code: The locale code to check (e.g., 'en', 'fr').
        :return: True if the locale was loaded and its root is a dictionary, False otherwise.
        """
        normalized_locale_code = locale_code.lower()
        return isinstance(self._raw_translations.get(normalized_locale_code), dict)

    @property
    def loaded_locales(self) -> List[str]:
        """
        Return a list of normalized locale codes that have been successfully loaded.

        :return: A list of normalized locale codes (e.g., ['en', 'fr']).
        :rtype: List[str]
        """
        return [code for code, data in self._raw_translations.items() if isinstance(data, dict)]

    def get_translation(self, locale_code: str, default: Any = None) -> Union[Optional[LocaleTranslator], Any]:
        """
        Retrieve or create a `LocaleTranslator` instance for the specified locale.

        If the LocaleTranslator is already cached, it will return the cached instance. Otherwise, it ensures
        the locale data is loaded, validates the existence of a default locale, and creates a
        new `LocaleTranslator` instance. If the default locale is not loaded or valid, it logs
        an error and returns the provided default value.

        :param locale_code: The code representing the desired locale, provided as a string.
        :param default: An optional fallback value to be returned in case a locale cannot be
            resolved or the default locale is not loaded properly.
        :return: An instance of LocaleTranslator for the specified locale or the fallback
            default value.
        """
        locale_code = locale_code.lower()
        if locale_code in self._locale_translators_cache:
            return self._locale_translators_cache[locale_code]

        self._ensure_locale_loaded(locale_code)

        if locale_code != self.default_locale:
            self._ensure_locale_loaded(self.default_locale)

        locale_data = self._raw_translations.get(locale_code, None)
        if not locale_data:
            self._throw(
                f"Locale was not found or root is not a dictionary "
                f"({type(locale_data).__name__ if locale_data is not None else 'NoneType'}). ",
                LocaleNotLoadedError,
            )

        default_data = self._raw_translations.get(self.default_locale, None)
        if not default_data:
            self._throw(
                f"Default locale was not found or root is not a dictionary "
                f"({type(default_data).__name__ if default_data is not None else 'NoneType'}). "
                "Fallback to the default locale will be limited or impossible.",
                DefaultLocaleNotLoadedError,
            )
            return default

        _t = LocaleTranslator(locale_code, locale_data, default_data, self.default_locale, strict=self._strict)
        self._locale_translators_cache[locale_code] = _t
        return _t

    def _ensure_locale_loaded(self, locale_code: str):
        locale_code = locale_code.lower()
        if locale_code in self._locale_translators_cache:
            return None

        found_path = None
        for extension in self._loader.SUPPORTED_EXTENSIONS:
            filepath = os.path.join(self.locales_dir, f"{locale_code}{extension}")
            if os.path.exists(filepath):
                found_path = filepath
                break

        if not found_path:
            return self._throw(
                f"Locale file for locale: '{locale_code}' not found or have not supported extension.", FileNotFoundError
            )

        data = self._loader.load(found_path)
        if isinstance(data, list):
            return self._throw(
                f"Locale file at path '{found_path}' contains multiple locales.", UnexpectedMultiLocaleError
            )

        else:
            return self._process_data(data)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR):
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return None
