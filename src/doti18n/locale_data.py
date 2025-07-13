import os
from typing import (
    Dict,
    Optional,
    Any,
    List,
    Union,
    Tuple
)

from .locale_translator import LocaleTranslator
import logging
from .loaders import Loader
from .utils import (
    _EMPTY_FILE,
    _get_locale_code, _deep_merge
)


logger = logging.getLogger(__name__)


class LocaleData:
    """
    Manages the loading of all localization files and provides access to LocaleTranslator instances.

    Supports a 'strict' mode which is passed to created LocaleTranslator instances.
    """

    def __init__(
            self,
            locales_dir: str,
            default_locale: str = 'en',
            strict: bool = False,
            strict_file_load: bool = False,
            preload: bool = True
    ):
        """
        Initializes the LocaleData manager.
        :param locales_dir: The path to the directory containing YAML locale files.
        :type locales_dir: str
        :param default_locale: The code of the default locale. (default: 'en')
        :type default_locale: str
        :param strict: If `True`, all created LocaleTranslator instances will be in strict mode.
                       That means that where you've gotten warnings before, you'll get exceptions.
                       (default: False).
        :type strict: bool
        :param strict_file_load: If `True`, Loader will not try to guess the file type
                                 if the file has an unspecified extension.
                                 (default: False).
        :type strict_file_load: bool
        :param preload: If `True`, load all translations at initialization.
                        Not recommended to use with large locale directories.
                        Instead, you can use LocaleData.get("filename") to load individual locale.
                        (default: True)
        :type preload: bool
        """

        self.locales_dir = locales_dir
        self.default_locale = default_locale.lower()
        self._logger = logger
        self._loader = Loader(strict_file_load)
        self._strict = strict
        self._raw_translations: Dict[str, Optional[Dict[str, Any]]] = {}
        self._locale_translators_cache: Dict[str, LocaleTranslator] = {}
        if preload:
            self._load_all_translations()

    def _load_all_translations(self):
        if not os.path.exists(self.locales_dir):
            msg = f"Localization directory '{self.locales_dir}' not found."
            if self._strict:
                raise FileNotFoundError(msg)
            else:
                self._logger.error(msg)
                return

        for filename in os.listdir(self.locales_dir):
            data = self._loader.load(os.path.join(self.locales_dir, filename))
            self._process_data(data)

        if not any(self._raw_translations.values()):
            self._logger.warning(f"No localization files found or successfully loaded from '{self.locales_dir}'.")

        default_data = self._raw_translations.get(self.default_locale)
        if not isinstance(default_data, dict):
            if self.default_locale not in self._raw_translations:
                self._raw_translations[self.default_locale] = None  # Ensure entry exists
            elif not isinstance(default_data, dict):
                self._raw_translations[self.default_locale] = None  # None if not a dict

            self._logger.warning(
                f"Default locale was not found or root is not a dictionary "
                f"({type(default_data).__name__ if default_data is not None else 'NoneType'}). "
                "Fallback to the default locale will be limited or impossible."
            )

    def _process_data(self, data: Union[Tuple, Dict, List]):
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
        Returns the LocaleTranslator object for the specified locale code.

        Uses a cache to avoid creating multiple translator instances for the
        same locale. Normalizes the locale code to lowercase. The 'strict'
        setting of this LocaleData instance is passed to the translator.

        :param locale_code: The code of the desired locale (e.g., 'en', 'FR').
        :type locale_code: str
        :return: The LocaleTranslator instance for the requested locale.
        :rtype: LocaleTranslator
        """

        normalized_locale_code = locale_code.lower()
        if normalized_locale_code in self._locale_translators_cache:
            return self._locale_translators_cache[normalized_locale_code]

        current_locale_data = self._raw_translations.get(normalized_locale_code)
        default_locale_data = self._raw_translations.get(self.default_locale)

        translator = LocaleTranslator(
            normalized_locale_code,
            current_locale_data,
            default_locale_data,
            self.default_locale,
            strict=self._strict
        )

        self._locale_translators_cache[normalized_locale_code] = translator
        return translator

    def __contains__(self, locale_code: str) -> bool:
        """
        Checks if a locale with the given code was successfully loaded with a dictionary root.
        Normalizes the locale code to lowercase for the check.

        :param locale_code: The locale code to check (e.g., 'en', 'fr').
        :type locale_code: str
        :return: True if the locale was loaded and its root is a dictionary, False otherwise.
        :rtype: bool
        """

        normalized_locale_code = locale_code.lower()
        return isinstance(self._raw_translations.get(normalized_locale_code), dict)

    @property
    def loaded_locales(self) -> List[str]:
        """
        Returns a list of normalized locale codes that were successfully loaded
        with a dictionary root.

        :return: A list of normalized locale codes (e.g., ['en', 'fr']).
        :rtype: List[str]
        """

        return [code for code, data in self._raw_translations.items() if isinstance(data, dict)]

    def get(self, locale_code: str, default: Optional[LocaleTranslator] = None) -> Optional[LocaleTranslator]:
        """
        Returns the LocaleTranslator for the specified locale, or a default value
        if the locale was not successfully loaded (e.g., file not found or root not a dictionary).

        Normalizes the locale code. The 'strict' setting of this LocaleData instance
        is used if a translator is created.

        :param locale_code: The code of the desired locale.
        :type locale_code: str
        :param default: The value to return if the locale is not found or invalid.
                        Defaults to None.
        :type default: Optional[LocaleTranslator]
        :return: The LocaleTranslator instance or the default value.
        :rtype: Optional[LocaleTranslator]
        """

        normalized_locale_code = locale_code.lower()
        if normalized_locale_code in self:
            return self[normalized_locale_code]
        else:
            return default

    def load_translation(self, filename: str) -> Optional[LocaleTranslator]:
        """
        Loads a translation from the specified locale file and returns a LocaleTranslator instance
        if the translation is successfully processed. This method checks if the translation is
        already cached, loads data from the file, processes the translation, and handles warnings
        related to defaults in locale data.

        The method raises errors if the locale file is empty, the data cannot be loaded, or the
        format of the locale file is invalid (e.g., contains multiple locales).

        :param filename: The name of the locale file to be loaded.
        :type filename: str

        :return: A LocaleTranslator instance for the given locale, or None if not available.
        :rtype: Optional[LocaleTranslator]

        :raises ValueError: If the locale file is empty, data cannot be loaded, or the format
            contains multiple locales.
        """

        locale_code = _get_locale_code(filename)
        if locale_code in self._locale_translators_cache:
            return self._locale_translators_cache[locale_code]

        filepath = os.path.join(self.locales_dir, filename)
        data = self._loader.load(filepath)

        if data is _EMPTY_FILE:
            if self._strict:
                raise ValueError(f"Locale file '{filename}' was epmty.")
            else:
                self._logger.warning(f"Locale file '{filename}' was epmty.")
        
        if not data:
            if self._strict:
                raise ValueError(f"Data from locale file '{filename}' not loaded")
            else:
                self._logger.warning(f"Data from locale file '{filename}' not loaded")

        if isinstance(data, list):
            raise ValueError(
                f"Locale file '{filename}' contains multiple locales.\n"
                f"It's not possible to use it for LocaleTranslator.\n"
                f"Instead of this, use preload=True in LocaleData, and use .get() method"
            )

        if data:
            self._process_data(data)

        default_data = self._raw_translations.get(self.default_locale)
        if not default_data:
            self._logger.warning(
                f"Default locale was not found or root is not a dictionary "
                f"({type(default_data).__name__ if default_data is not None else 'NoneType'}). "
                "Fallback to the default locale will be limited or impossible."
            )

        return LocaleTranslator(
            locale_code,
            self._raw_translations.get(locale_code),
            self._raw_translations.get(self.default_locale),
            self.default_locale,
            strict=self._strict
        )

