import unittest

from tests import BaseLocaleTest


# noinspection PyArgumentEqualDefault
class TestFallback(BaseLocaleTest):
    """Tests for the default locale fallback mechanism."""

    def test_key_only_in_default(self):
        self.create_locale_file('en', {'only_in_en': 'English only'})
        self.create_locale_file('ru', {'ru_key': 'Russian key'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].only_in_en, 'English only')

    def test_key_only_in_current(self):
        self.create_locale_file('en', {'en_key': 'English key'})
        self.create_locale_file('ru', {'only_in_ru': 'Russian only'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].only_in_ru, 'Russian only')

    def test_key_in_both_prefers_current(self):
        self.create_locale_file('en', {'key_in_both': 'English version'})
        self.create_locale_file('ru', {'key_in_both': 'Russian version'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].key_in_both, 'Russian version')

    def test_nested_key_only_in_default(self):
        self.create_locale_file('en', {'nested': {'item': 'English item'}})
        self.create_locale_file('ru', {'other_root': 'value'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].nested.item, 'English item')

    def test_nested_key_in_both_prefers_current(self):
        self.create_locale_file('en', {'nested': {'item': 'English item', 'shared': 'English'}})
        self.create_locale_file('ru', {'nested': {'item': 'Russian item', 'ru_only': 'Russian'}})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].nested.item, 'Russian item')
        self.assertEqual(locales['ru'].nested.shared, 'English')

    def test_list_item_fallback(self):
        self.create_locale_file('en',
                                {'items': [{'name': 'Apple', 'desc': 'Sweet'}, {'name': 'Banana', 'desc': 'Yellow'}]})
        self.create_locale_file('ru', {'items': [{'name': 'Яблоко'}, {'name': 'Банан'}]})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].items[0].name, 'Яблоко')
        self.assertEqual(locales['ru'].items[0].desc, 'Sweet')
        self.assertEqual(locales['ru'].items[1].name, 'Банан')
        self.assertEqual(locales['ru'].items[1].desc, 'Yellow')

    def test_list_fallback_entire_list(self):
        self.create_locale_file('en', {'list_only_in_en': ['a', 'b']})
        self.create_locale_file('ru', {'ru_item': 'stuff'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].list_only_in_en[0], 'a')
        self.assertEqual(locales['ru'].list_only_in_en[1], 'b')

    def test_fallback_chain_dict_list_dict(self):
        self.create_locale_file('en', {
            'section': {
                'items': [
                    {'detail': 'English detail 1'},
                    {'detail': 'English detail 2'}
                ]
            }
        })
        self.create_locale_file('ru', {
            'section': {
                'items': [
                    {'id': 1},
                    {'id': 2}
                ]
            }
        })
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].section.items[0].id, 1)
        self.assertEqual(locales['ru'].section.items[0].detail, 'English detail 1')

    def test_plural_fallback_template(self):
        self.create_locale_file('en', {
            'apples': {
                'one': '1 English apple',
                'other': '{count} English apples'
            }
        })
        self.create_locale_file('ru', {
            'apples': {
                'one': '1 Русское яблоко',
            }
        })
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].apples(1), '1 Русское яблоко')
        self.assertEqual(locales['ru'].apples(3), '3 English apples')
        self.assertEqual(locales['ru'].apples(10), '10 English apples')
        self.assertEqual(locales['ru'].apples(25), '25 English apples')


if __name__ == '__main__':
    unittest.main()
