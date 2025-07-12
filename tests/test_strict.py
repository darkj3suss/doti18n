import unittest

from tests import BaseLocaleTest
from src.doti18n.wrapped import LocaleNamespace, LocaleList


class TestStrict(BaseLocaleTest):
    """Tests for strict mode behavior (exceptions on missing keys/indices)."""

    def test_missing_key_raises_attributeerror(self):
        self.create_locale_file('en', {'existing': 'value'})
        locales = self.get_locale_data(strict=True)
        self.assertRaisesAttributeError(
            "Strict mode error: Key/index path 'non_existent_key' not found",
            locales['en'].__getattr__,
            'non_existent_key'
        )
        locales = None

    def test_missing_nested_key_raises_attributeerror(self):
        self.create_locale_file('en', {'nested': {'existing': 'value'}})
        locales = self.get_locale_data(strict=True)
        namespace = locales['en'].nested
        self.assertIsInstance(namespace, LocaleNamespace)
        self.assertRaisesAttributeError(
            "Strict mode error: Key/index path 'nested.non_existent_key' not found",
            namespace.__getattr__,
            'non_existent_key'
        )
        locales = None

    def test_missing_index_raises_indexerror(self):
        self.create_locale_file('en', {'items': ['a', 'b']})
        locales = self.get_locale_data(strict=True)
        with self.assertRaises(IndexError) as cm:
            _ = locales['en'].items[2]
        self.assertIn("Strict mode error: Index 2 out of bounds for list at path 'items'", str(cm.exception))

    def test_calling_namespace_raises_typeerror(self):
        self.create_locale_file('en', {'nested': {'item': 'value'}})
        locales = self.get_locale_data(strict=True)
        namespace = locales['en'].nested
        self.assertIsInstance(namespace, LocaleNamespace)
        with self.assertRaises(TypeError) as cm:
            namespace()
        self.assertIn("object at path 'nested' is not callable", str(cm.exception))

    def test_calling_list_raises_typeerror(self):
        self.create_locale_file('en', {'items': ['a']})
        locales = self.get_locale_data(strict=True)
        item_list = locales['en'].items
        self.assertIsInstance(item_list, LocaleList)
        with self.assertRaises(TypeError) as cm:
            item_list()
        self.assertIn("object at path 'items' is not callable", str(cm.exception))

    def test_plural_missing_form_raises_attributeerror(self):
        self.create_locale_file('en', {'items': {'one': 'one item'}})
        locales = self.get_locale_data(strict=True)
        with self.assertRaises(AttributeError) as cm:
            locales['en'].items(2)
        self.assertIn("Failed to find plural template for key 'items' (form 'other', count 2)", str(cm.exception))

    def test_plural_missing_format_placeholder_raises_valueerror(self):
        self.create_locale_file('en', {'greeting': {'one': 'Hello', 'other': 'Hello {name}'}})
        locales = self.get_locale_data(strict=True)
        with self.assertRaises(ValueError) as cm:
            locales['en'].greeting(5)
        self.assertIn("Formatting error for plural key 'greeting' (form 'other'): Missing placeholder 'name'",
                      str(cm.exception))


if __name__ == '__main__':
    unittest.main()
