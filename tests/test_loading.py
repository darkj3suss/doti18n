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
        locales = None  # Explicitly dereference

    def test_empty_directory(self):
        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='WARNING') as log_cm:
            locales = self.get_locale_data('en')
        log_output = "\n".join(log_cm.output)
        self.assertIn(f"No localization files found or successfully loaded from '{TEST_LOCALES_DIR}'.", log_output)
        self.assertEqual(locales.loaded_locales, [])
        self.assertIsInstance(locales['en'], locales['en'].__class__)
        self.assertEqual(locales['en'].some_key, None)
        locales = None  # Explicitly dereference   

    def test_invalid_yaml_file(self):
        invalid_yaml_content = "key: value\n- list item"  # Invalid YAML
        filepath = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_yaml_content)

        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='ERROR') as log_cm:
            locales = self.get_locale_data('en')
        log_output = "\n".join(log_cm.output)
        self.assertIn("Error parsing YAML file", log_output)
        self.assertNotIn('en', locales.loaded_locales)
        locales = None  # Explicitly dereference

    def test_file_with_non_dict_root(self):
        list_root_content = yaml.dump(['item1', 'item2'], allow_unicode=True)
        filepath_list = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        with open(filepath_list, 'w', encoding='utf-8') as f:
            f.write(list_root_content)

        string_root_content = yaml.dump("just a string", allow_unicode=True)
        filepath_string = os.path.join(TEST_LOCALES_DIR, 'ru.yaml')
        with open(filepath_string, 'w', encoding='utf-8') as f:
            f.write(string_root_content)

        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='CRITICAL') as log_cm:
            locales = self.get_locale_data('en')

        log_output = "\n".join(log_cm.output)
        self.assertIn("Default locale file for 'en.yaml/.yml' not found or root is not a dictionary", log_output)

        self.assertNotIn('en', locales.loaded_locales)
        self.assertNotIn('ru', locales.loaded_locales)

        self.assertEqual(locales['en'].some_key, None)
        self.assertEqual(locales['ru'].some_key, None)
        locales = None  # Explicitly dereference

    def test_default_locale_file_missing(self):
        en_filepath = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        if os.path.exists(en_filepath):
            os.remove(en_filepath)

        self.create_locale_file('ru', {'key_ru': 'value_ru'})

        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='CRITICAL') as log_cm:
            locales = self.get_locale_data('en')

        log_output = "\n".join(log_cm.output)
        self.assertIn("Default locale file for 'en.yaml/.yml' not found or root is not a dictionary", log_output)
        self.assertIn('ru', locales.loaded_locales)

        self.assertEqual(locales['en'].some_key, None)
        self.assertEqual(locales['ru'].key_ru, 'value_ru')
        locales = None  # Explicitly dereference

    def test_default_locale_file_with_invalid_root(self):
        list_root_content = yaml.dump(['item1', 'item2'], allow_unicode=True)
        filepath_list = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        with open(filepath_list, 'w', encoding='utf-8') as f:
            f.write(list_root_content)

        self.create_locale_file('ru', {'key_ru': 'value_ru'})

        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='CRITICAL') as log_cm:
            locales = self.get_locale_data('en')

        log_output = "\n".join(log_cm.output)
        self.assertIn("Default locale file for 'en.yaml/.yml' not found or root is not a dictionary", log_output)
        self.assertNotIn('en', locales.loaded_locales)
        self.assertIn('ru', locales.loaded_locales)

        self.assertEqual(locales['en'].some_key, None)
        self.assertEqual(locales['ru'].key_ru, 'value_ru')
        locales = None  # Explicitly dereference

    def test_locale_code_case_insensitivity_loading(self):
        # setUp creates en.yaml, remove it
        en_filepath = os.path.join(TEST_LOCALES_DIR, 'en.yaml')
        if os.path.exists(en_filepath):
            os.remove(en_filepath)

        # Create files with different casing
        self.create_locale_file('EN', {'key_en': 'value_en'})
        self.create_locale_file('ru-RU', {'key_ru': 'value_ru'})
        self.create_locale_file('fr', {'key_fr': 'value_fr'})

        locales = self.get_locale_data('en')
        loaded = sorted(locales.loaded_locales)
        self.assertEqual(loaded, ['en', 'fr', 'ru-ru'])
        self.assertEqual(len(locales.loaded_locales), 3)  # Expect 3, not 2 now
        self.assertEqual(locales['en'].key_en, 'value_en')
        self.assertEqual(locales['ru-ru'].key_ru, 'value_ru')
        self.assertEqual(locales['fr'].key_fr, 'value_fr')
        self.assertEqual(locales['EN'].key_en, 'value_en')
        self.assertEqual(locales['ru-RU'].key_ru, 'value_ru')
        locales = None  # Explicitly dereference


if __name__ == '__main__':
    unittest.main()
