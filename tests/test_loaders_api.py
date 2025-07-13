import unittest
import os
import tempfile
import yaml
import json

from src.doti18n.loaders import Loader


class TestLoaderApi(unittest.TestCase):
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for fname in self.tempfiles:
            try:
                os.unlink(fname)
            except Exception:
                pass

    def test_loader_yaml_and_json(self):
        d = tempfile.mkdtemp()
        ymlfile = os.path.join(d, "en.yml")
        jsonfile = os.path.join(d, "en.json")
        with open(ymlfile, "w", encoding="utf-8") as f:
            yaml.dump({"hi": "yaml"}, f)
        with open(jsonfile, "w", encoding="utf-8") as f:
            json.dump({"hi": "json"}, f)
        self.tempfiles.extend([ymlfile, jsonfile])

        loader = Loader()
        loaded_yaml = loader.load(ymlfile)
        loaded_json = loader.load(jsonfile)
        self.assertIsInstance(loaded_yaml, dict)
        self.assertIsInstance(loaded_json, dict)
        self.assertIn("hi", list(loaded_yaml.values())[0])
        self.assertIn("hi", list(loaded_json.values())[0])

    def test_loader_warns_on_unknown_extension(self):
        d = tempfile.mkdtemp()
        unknownfile = os.path.join(d, "en.abc")
        with open(unknownfile, "w", encoding="utf-8") as f:
            f.write("123")
        self.tempfiles.append(unknownfile)

        loader = Loader(strict=True)
        try:
            loader.load(unknownfile)
        except Exception as e:
            self.assertTrue(type(e) is ValueError)

    def test_loader_guess_on_missing_extension(self):
        d = tempfile.mkdtemp()
        barefile = os.path.join(d, "en")
        with open(barefile, "w", encoding="utf-8") as f:
            yaml.dump({"key": "v"}, f)

        self.tempfiles.append(barefile)

        loader = Loader(strict=False)
        result = loader.load(barefile)
        self.assertIsInstance(result, dict)
