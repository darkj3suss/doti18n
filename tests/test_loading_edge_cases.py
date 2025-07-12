import unittest
import os
import shutil

from tests import (
    BaseLocaleTest,
    TEST_LOCALES_DIR,
    LocaleData,
    LOGGER_LOCALE_DATA
)


class TestLoadingEdgeCases(BaseLocaleTest):
    """Tests for edge cases during LocaleData loading."""
    def test_directory_not_found(self):
        """Test that LocaleData handles the localization directory not being found."""
        if os.path.exists(TEST_LOCALES_DIR):
            shutil.rmtree(TEST_LOCALES_DIR)

        with self.assertLogsFor(LOGGER_LOCALE_DATA, level='ERROR') as log_cm:
            locales = LocaleData(TEST_LOCALES_DIR, 'en')
        self.assertIn(f"Localization directory '{TEST_LOCALES_DIR}' not found.", log_cm.output[0])
        self.assertEqual(locales.loaded_locales, [])
        self.assertEqual(locales['en'].some_key, None)
        locales = None


if __name__ == '__main__':
    unittest.main()
