import os
from typing import (
    Dict,
    Optional,
    Any,
    List
)

import yaml
from .locale_translator import LocaleTranslator
import logging


logger = logging.getLogger(__name__)


class LocaleData:
    """
    Manages the loading of all localization files and provides access to LocaleTranslator instances.

    Supports a 'strict' mode which is passed to created LocaleTranslator instances.
    """

    def __init__(self, locales_dir: str, default_locale: str = 'en', strict: bool = False):
        """
        Initializes the LocaleData manager.

        Loads all YAML localization files from the specified directory.

        :param locales_dir: The path to the directory containing YAML locale files.
        :type locales_dir: str
        :param default_locale: The code of the default locale. Defaults to 'en'.
        :type default_locale: str
        :param strict: If `True`, all created LocaleTranslator instances will be in strict mode.
                       If `False` (default), they will be in non-strict mode.
        :type strict: bool
        """

        self.logger = logger
        self.locales_dir = locales_dir
        self.default_locale = default_locale.lower()
        self._strict = strict
        # Dictionary to store raw loaded data: normalized_locale_code -> data (or None)
        self._raw_translations: Dict[str, Optional[Dict[str, Any]]] = {}
        # Cache for LocaleTranslator instances: normalized_locale_code -> LocaleTranslator
        self._locale_translators_cache: Dict[str, LocaleTranslator] = {}
        self._load_all_translations()

    def _load_all_translations(self):
        """Loads all YAML localization files from the directory."""
        if not os.path.exists(self.locales_dir):
            self.logger.error(f"Localization directory '{self.locales_dir}' not found.")
            return

        loaded_any = False
        for filename in os.listdir(self.locales_dir):
            if filename.lower().endswith((".yaml", ".yml")):
                locale_code_raw = os.path.splitext(filename)[0]
                locale_code_normalized = locale_code_raw.lower()
                filepath = os.path.join(self.locales_dir, filename)
                try:
                    with open(filepath, encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        # Store the loaded data under the normalized locale code.
                        # If the loaded data is not a dictionary at the root, store None.
                        self._raw_translations[locale_code_normalized] = data if isinstance(data, dict) else None
                        loaded_any = True
                    self.logger.info(f"Loaded locale data for: '{locale_code_normalized}' from '{filename}'")
                except FileNotFoundError:
                    self.logger.error(f"Locale file '{filepath}' not found during load.")
                except yaml.YAMLError as e:
                    self.logger.error(f"Error parsing YAML file '{filepath}': {e}")
                except Exception as e:
                    self.logger.error(f"Unknown error loading '{filepath}': {e}", exc_info=True)

        if not loaded_any:
            self.logger.warning(f"No localization files found or successfully loaded from '{self.locales_dir}'.")

        default_data = self._raw_translations.get(self.default_locale)
        if not isinstance(default_data, dict):
            if self.default_locale not in self._raw_translations:
                self._raw_translations[self.default_locale] = None  # Ensure entry exists
            elif not isinstance(default_data, dict):
                self._raw_translations[self.default_locale] = None  # None if not a dict

            self.logger.critical(
                f"Default locale file for '{self.default_locale}.yaml/.yml' not found or root is not a dictionary "
                f"({type(default_data).__name__ if default_data is not None else 'NoneType'}). "
                "Fallback to the default locale will be limited or impossible."
            )

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
