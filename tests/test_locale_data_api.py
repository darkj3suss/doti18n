import unittest
import os
import yaml

from tests import (
    TEST_LOCALES_DIR,
    BaseLocaleTest
)
from src.doti18n import LocaleTranslator


# noinspection PyArgumentEqualDefault
class TestLocaleDataApi(BaseLocaleTest):
    """Tests for the public API of the LocaleData class."""

    def test_getitem_returns_translator_and_caches(self):
        self.create_locale_file('en', {'key': 'value'})
        locales = self.get_locale_data('en')
        translator1 = locales['en']
        translator2 = locales['en']

        self.assertIsInstance(translator1, LocaleTranslator)
        self.assertIs(translator1, translator2)
        translator_non_existent = locales['fr']
        self.assertIsInstance(translator_non_existent, LocaleTranslator)
        self.assertEqual(translator_non_existent.some_key, None)

    # noinspection PyTypeChecker
    def test_contains(self):
        self.create_locale_file('en', {'key': 'value'})
        self.create_locale_file('ru', {'key': 'value'})
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)

        locales = self.get_locale_data('en')

        self.assertIn('en', locales)
        self.assertIn('ru', locales)
        self.assertNotIn('fr', locales)
        self.assertNotIn('invalid', locales)
        self.assertIn('EN', locales)
        self.assertIn('Ru', locales)

    def test_loaded_locales_property(self):
        self.create_locale_file('en', {'key': 'value'})
        self.create_locale_file('ru', {'key': 'value'})
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)

        locales = self.get_locale_data('en')
        loaded = sorted(locales.loaded_locales)
        self.assertEqual(loaded, ['en', 'ru'])

    def test_get_method(self):
        self.create_locale_file('en', {'key': 'value'})
        locales = self.get_locale_data('en')
        translator = locales.get('en')
        self.assertIsInstance(translator, LocaleTranslator)
        self.assertEqual(translator.key, 'value')
        translator_none = locales.get('fr')
        self.assertIsNone(translator_none)
        default_value = "default"
        value_with_default = locales.get('fr', default_value)
        self.assertEqual(value_with_default, default_value)
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)
        locales = self.get_locale_data('en')
        self.assertNotIn('invalid', locales)
        value_invalid = locales.get('invalid', default_value)
        self.assertEqual(value_invalid, default_value)


if __name__ == '__main__':
    unittest.main()
