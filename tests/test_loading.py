import time
import unittest
import os
import shutil
import yaml
import logging

from tests import (
    BaseLocaleTest,
    TEST_LOCALES_DIR,
    LOGGER_LOCALE_DATA
)


# noinspection PyArgumentEqualDefault,PyUnusedLocal
class TestLoading(BaseLocaleTest):
    """Tests for LocaleData file loading and initialization."""

    def setUp(self):
        """Create and clear the test locales directory before each test method."""
        if os.path.exists(TEST_LOCALES_DIR):
            try:
                shutil.rmtree(TEST_LOCALES_DIR, ignore_errors=True)
                # My pc need this delay for stable work of tests
                time.sleep(0.01)
            except OSError as e:
                logging.warning(f"Could not remove test directory {TEST_LOCALES_DIR} during setUp: {e}")

        os.makedirs(TEST_LOCALES_DIR, exist_ok=True)

    def test_load_valid_files(self):
        self.create_locale_file('en', {'key_en': 'value_en'})
        self.create_locale_file('ru', {'key_ru': 'value_ru'})
        locales = self.get_locale_data('en')
        self.assertIn('en', locales.loaded_locales)
        self.assertIn('ru', locales.loaded_locales)
        self.assertEqual(locales['en'].key_en, 'value_en')
        self.assertEqual(locales['ru'].key_ru, 'value_ru')
        locales = None

    def test_empty_directory(self):
        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='WARNING') as log_cm:
            locales = self.get_locale_data('en')
        log_output = "\n".join(log_cm.output)
        self.assertIn(f"No localization files found or successfully loaded from '{TEST_LOCALES_DIR}'.", log_output)
        self.assertEqual(locales.loaded_locales, [])
        self.assertIsInstance(locales['en'], locales['en'].__class__)
        self.assertEqual(locales['en'].some_key, None)
        locales = None

    def test_locale_code_case_insensitivity_loading(self):
        en_filepath = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        if os.path.exists(en_filepath):
            os.remove(en_filepath)

        self.create_locale_file('EN', {'key_en': 'value_en'})
        self.create_locale_file('ru-RU', {'key_ru': 'value_ru'})
        self.create_locale_file('fr', {'key_fr': 'value_fr'})

        locales = self.get_locale_data('en')
        loaded = sorted(locales.loaded_locales)
        self.assertEqual(loaded, ['en', 'fr', 'ru-ru'])
        self.assertEqual(len(locales.loaded_locales), 3)
        self.assertEqual(locales['en'].key_en, 'value_en')
        self.assertEqual(locales['ru-ru'].key_ru, 'value_ru')
        self.assertEqual(locales['fr'].key_fr, 'value_fr')
        self.assertEqual(locales['EN'].key_en, 'value_en')
        self.assertEqual(locales['ru-RU'].key_ru, 'value_ru')
        locales = None


if __name__ == '__main__':
    unittest.main()
