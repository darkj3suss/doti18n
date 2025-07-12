import unittest

from tests import (
    BaseLocaleTest,
    LOGGER_LOCALE_TRANSLATOR
)
from src.doti18n.wrapped import (
    LocaleNamespace,
    LocaleList,
    NoneWrapper
)


# noinspection PyArgumentEqualDefault,PyUnusedLocal
class TestNonStrict(BaseLocaleTest):
    """Tests for non-strict mode behavior (returns None and logs warnings)."""

    def test_missing_key_returns_none_and_warns(self):
        self.create_locale_file('en', {'existing': 'value'})
        locales = self.get_locale_data(strict=False)
        with self.assertLogsFor(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value = locales['en'].non_existent_key
        self.assertEqual(value, None)
        log_output = "\n".join(log_cm.output)
        self.assertIn("key/index path 'non_existent_key' not found in translations", log_output)
        locales = None

    def test_missing_nested_key_returns_none_and_warns(self):
        self.create_locale_file('en', {'nested': {'existing': 'value'}})
        locales = self.get_locale_data(strict=False)
        with self.assertLogsFor(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value = locales['en'].nested.non_existent_key
        self.assertEqual(value, None)
        log_output = "\n".join(log_cm.output)
        self.assertIn("key/index path 'nested.non_existent_key' not found in translations", log_output)
        locales = None

    def test_none_wrapper_instance(self):
        self.create_locale_file('en', {})
        locales = self.get_locale_data(strict=False)

        value1 = locales['en'].missing_key
        self.assertIsInstance(value1, NoneWrapper)
        self.assertEqual(value1._path, 'missing_key')

        value2 = locales['en'].missing_key.another_one
        self.assertIsInstance(value2, NoneWrapper)
        self.assertEqual(value2._path, 'missing_key.another_one')

        value3 = locales['en'].missing_key.another_one.yet_another
        self.assertIsInstance(value3, NoneWrapper)
        self.assertEqual(value3._path, 'missing_key.another_one.yet_another')

    def test_none_wrapper_chain_access(self):
        self.create_locale_file('en', {})
        locales = self.get_locale_data(strict=False)
        with self.assertLogs(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value = locales['en'].missing.key

        self.assertEqual(None, value)
        log_output = "\n".join(log_cm.output)
        expected_log_substring = "Locale 'en': key/index path 'missing' not found in translations"
        self.assertIn(expected_log_substring, log_output)

    def test_calling_namespace_raises_typeerror(self):
        self.create_locale_file('en', {'nested': {'item': 'value'}})
        locales = self.get_locale_data(strict=False)
        namespace = locales['en'].nested
        self.assertIsInstance(namespace, LocaleNamespace)
        with self.assertRaises(TypeError):
            namespace()

    def test_calling_list_raises_typeerror(self):
        self.create_locale_file('en', {'items': ['a']})
        locales = self.get_locale_data(strict=False)
        item_list = locales['en'].items
        self.assertIsInstance(item_list, LocaleList)
        with self.assertRaises(TypeError):
            item_list()

    def test_plural_missing_form_returns_none_and_warns(self):
        self.create_locale_file('en', {'items': {'one': 'one item'}})
        locales = self.get_locale_data(strict=False)
        with self.assertRaises(AttributeError) as cm:
            locales['en'].items(2)
        self.assertIn("Failed to find plural template for key 'items' (form 'other', count 2)", str(cm.exception))

    def test_plural_missing_format_placeholder_raises_valueerror(self):
        self.create_locale_file('en', {'greeting': {'one': 'Hello', 'other': 'Hello {name}'}})
        locales = self.get_locale_data(strict=False)
        with self.assertRaises(ValueError) as cm:
            locales['en'].greeting(5)
        self.assertIn("Formatting error for plural key 'greeting' (form 'other'): Missing placeholder 'name'",
                      str(cm.exception))


if __name__ == '__main__':
    unittest.main()
