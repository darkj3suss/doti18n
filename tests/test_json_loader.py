import os
import json

from src.doti18n.loaders.json_loader import JsonLoader
from src.doti18n.utils import _EMPTY_FILE
from tests import BaseLocaleTest, TEST_LOCALES_DIR


class TestJsonLoader(BaseLocaleTest):
    def setUp(self):
        super().setUp()
        self.loader = JsonLoader()

    def test_json_loader_valid_file(self):
        path = os.path.join(TEST_LOCALES_DIR, "en.json")
        data = {"key": "value"}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        loaded = self.loader.load(path)
        self.assertIsInstance(loaded, dict)
        self.assertIn("key", list(list(loaded.values())[0].keys()))

    def test_json_loader_empty_file(self):
        path = os.path.join(TEST_LOCALES_DIR, "empty.json")
        with open(path, "w", encoding="utf-8"):
            pass
        result = self.loader.load(path)
        self.assertIsNone(result)

    def test_json_loader_invalid_json(self):
        path = os.path.join(TEST_LOCALES_DIR, "broken.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{not json}")
        result = self.loader.load(path)
        self.assertIsNone(result)

    def test_json_loader_file_not_found(self):
        result = self.loader.load(os.path.join(TEST_LOCALES_DIR, "absolutely_no_such_file.json"))
        self.assertIsNone(result)
