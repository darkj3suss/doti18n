import unittest
import os
import shutil
import yaml
import logging
from typing import Union

logging.basicConfig(level=logging.WARNING)

try:
    from src.doti18n import LocaleData, LocaleTranslator
    from src.doti18n.wrapped import LocaleNamespace, LocaleList, PluralWrapper
except ImportError:
    # Fallback if running tests in a way that src.doti18n isn't in sys.path
    # This part might need adjustment based on *exactly* how you run tests.
    # Running 'python -m unittest discover -s tests' from the project root often works
    print("Warning: Could not import src.doti18n directly. Attempting sys.path manipulation.")
    import sys

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    try:
        from src.doti18n import LocaleData, LocaleTranslator
        from src.doti18n.wrapped import LocaleNamespace, LocaleList, PluralWrapper
    except ImportError as e:
        print(f"Fatal Error: Could not import src.doti18n even with sys.path adjustment: {e}")
        # Optionally, exit or raise the error
        raise e

LOGGER_LOCALE_DATA = 'src.doti18n.locale_data'
LOGGER_LOCALE_TRANSLATOR = 'src.doti18n.locale_translator'
LOGGER_UTILS = 'src.doti18n.utils'
LOGGER_WRAPPED_LIST = 'src.doti18n.wrapped.locale_list'
LOGGER_WRAPPED_NAMESPACE = 'src.doti18n.wrapped.locale_namespace'
LOGGER_WRAPPED_PLURAL = 'src.doti18n.wrapped.plural_handler_wrapper'

TEST_LOCALES_DIR = os.path.join(os.path.dirname(__file__), 'test_locales')


class BaseLocaleTest(unittest.TestCase):
    """Base class for localization tests handling temporary locale directory."""

    @classmethod
    def setUpClass(cls):
        """Create and clear a temporary directory for locale files before each test class."""
        if os.path.exists(TEST_LOCALES_DIR):
            shutil.rmtree(TEST_LOCALES_DIR, ignore_errors=True)
        os.makedirs(TEST_LOCALES_DIR)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory after each test class."""
        try:
            if os.path.exists(TEST_LOCALES_DIR):
                shutil.rmtree(TEST_LOCALES_DIR)
        except OSError as e:
            print(f"\nWarning: Could not remove test directory {TEST_LOCALES_DIR}: {e}")

    def create_locale_file(self, locale_code: str, data: dict):
        """Helper to create a YAML locale file in the temporary directory."""
        os.makedirs(TEST_LOCALES_DIR, exist_ok=True)
        filepath = os.path.join(TEST_LOCALES_DIR, f"{locale_code}.yaml")
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def get_locale_data(self, default_locale='en', strict=False) -> LocaleData:
        """Helper to create LocaleData instance."""
        return LocaleData(TEST_LOCALES_DIR, default_locale=default_locale, strict=strict)

    def assertLogsFor(self, logger_name: str, level: Union[int, str]):
        """Helper to assert logs against a specific logger and level."""
        return self.assertLogs(logger_name, level=level)

    def assertRaisesAttributeError(self, msg_substring: str, callable_obj, *args, **kwargs):
        """Asserts AttributeError is raised and its message contains a substring."""
        with self.assertRaises(AttributeError) as cm:
            callable_obj(*args, **kwargs)
        self.assertIn(msg_substring, str(cm.exception))

    def assertRaisesIndexError(self, msg_substring: str, callable_obj, *args, **kwargs):
        """Asserts IndexError is raised and its message contains a substring."""
        with self.assertRaises(IndexError) as cm:
            callable_obj(*args, **kwargs)
        self.assertIn(msg_substring, str(cm.exception))

    def assertRaisesTypeError(self, msg_substring: str, callable_obj, *args, **kwargs):
        """Asserts TypeError is raised and its message contains a substring."""
        with self.assertRaises(TypeError) as cm:
            callable_obj(*args, **kwargs)
        self.assertIn(msg_substring, str(cm.exception))


__all__ = [
    "BaseLocaleTest",
    "TEST_LOCALES_DIR",
    "LocaleData",
    "LocaleTranslator",
    "LocaleNamespace",
    "LocaleList",
    "PluralWrapper",
    "LOGGER_LOCALE_DATA",
    "LOGGER_LOCALE_TRANSLATOR",
    "LOGGER_UTILS",
    "LOGGER_WRAPPED_LIST",
    "LOGGER_WRAPPED_NAMESPACE",
    "LOGGER_WRAPPED_PLURAL",
]
