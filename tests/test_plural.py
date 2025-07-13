import unittest

from tests import BaseLocaleTest
from src.doti18n.wrapped import PluralWrapper


# noinspection PyArgumentEqualDefault
class TestPluralForms(BaseLocaleTest):
    """Tests for plural form handling."""

    def test_english_plurals(self):
        self.create_locale_file('en', {
            'apples': {'one': 'You have {count} apple.', 'other': 'You have {count} apples.'},
            'mice': {'one': '1 mouse', 'other': '{count} mice'},
            'greeting': 'Hello'
        })
        locales = self.get_locale_data('en')

        self.assertEqual(locales['en'].apples(0), 'You have 0 apples.')
        self.assertEqual(locales['en'].apples(1), 'You have 1 apple.')
        self.assertEqual(locales['en'].apples(2), 'You have 2 apples.')
        self.assertEqual(locales['en'].apples(5), 'You have 5 apples.')

        self.assertEqual(locales['en'].mice(1), '1 mouse')
        self.assertEqual(locales['en'].mice(3), '3 mice')

    def test_russian_plurals(self):
        self.create_locale_file('ru', {
            'apples': {
                'one': 'У вас {count} яблоко.',
                'few': 'У вас {count} яблока.',
                'many': 'У вас {count} яблок.',
                'other': 'У вас {count} яблок (остальные).'
            },
            'guests': {
                'one': 'Пришел {count} гость.',
                'few': 'Пришло {count} гостя.',
                'many': 'Пришло {count} гостей.',
            }
        })
        locales = self.get_locale_data('ru')

        self.assertEqual(locales['ru'].apples(0), 'У вас 0 яблок.')  # many
        self.assertEqual(locales['ru'].apples(1), 'У вас 1 яблоко.')  # one
        self.assertEqual(locales['ru'].apples(2), 'У вас 2 яблока.')  # few
        self.assertEqual(locales['ru'].apples(3), 'У вас 3 яблока.')  # few
        self.assertEqual(locales['ru'].apples(4), 'У вас 4 яблока.')  # few
        self.assertEqual(locales['ru'].apples(5), 'У вас 5 яблок.')  # many
        self.assertEqual(locales['ru'].apples(10), 'У вас 10 яблок.')  # many
        self.assertEqual(locales['ru'].apples(21), 'У вас 21 яблоко.')  # one
        self.assertEqual(locales['ru'].apples(22), 'У вас 22 яблока.')  # few

        self.assertEqual(locales['ru'].guests(1), 'Пришел 1 гость.')  # one
        self.assertEqual(locales['ru'].guests(3), 'Пришло 3 гостя.')  # few
        self.assertEqual(locales['ru'].guests(11), 'Пришло 11 гостей.')  # many
        self.assertEqual(locales['ru'].guests(25), 'Пришло 25 гостей.')  # many

    def test_plural_with_extra_formatting_args(self):
        self.create_locale_file('en', {
            'items': {'one': 'You have {count} {item_name}.', 'other': 'You have {count} {item_name}s.'}
        })
        locales = self.get_locale_data('en')
        self.assertEqual(locales['en'].items(1, item_name='book'), 'You have 1 book.')
        self.assertEqual(locales['en'].items(5, item_name='book'), 'You have 5 books.')
        self.assertEqual(locales['en'].items(1, item_name='mouse'), 'You have 1 mouse.')
        self.assertEqual(locales['en'].items(5, item_name='mouse'), 'You have 5 mouses.')

    def test_nested_plural(self):
        self.create_locale_file('en', {
            'inventory': {'apples': {'one': '1 apple', 'other': '{count} apples'}}
        })
        locales = self.get_locale_data('en')
        self.assertEqual(locales['en'].inventory.apples(1), '1 apple')
        self.assertEqual(locales['en'].inventory.apples(7), '7 apples')
        self.assertIsInstance(locales['en'].inventory.apples, PluralWrapper)

    def test_plural_dict_value_type(self):
        self.create_locale_file('en', {'apples': {'one': 'apple', 'other': 'apples'}})
        locales = self.get_locale_data('en')
        handler = locales['en'].apples
        self.assertIsInstance(handler, PluralWrapper)
        self.assertTrue(callable(handler))


if __name__ == '__main__':
    unittest.main()
