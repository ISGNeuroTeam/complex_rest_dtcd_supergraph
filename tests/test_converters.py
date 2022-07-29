import json
import unittest
from pathlib import Path

from django.test import SimpleTestCase

from complex_rest_dtcd_supergraph.converters import GraphDataConverter

from .misc import load_data, sort_payload

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / "data"


class TestGraphDataConverter(SimpleTestCase):
    converter = GraphDataConverter()

    def _check_to_content_to_data(self, data):
        sort_payload(data)
        content = self.converter.to_content(data)
        exported = self.converter.to_data(content)
        sort_payload(exported)
        self.assertEqual(exported, data)

    def test_to_content(self):
        data = load_data(DATA_DIR / "basic.json")
        content = self.converter.to_content(data)

        self.assertEqual(len(content.vertices), 2)
        self.assertEqual(len(content.ports), 2)
        self.assertEqual(len(content.edges), 1)
        self.assertEqual(len(content.groups), 0)

    def test_to_data(self):
        # TODO
        pass

    def _check_to_content_to_data_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self._check_to_content_to_data(data)

    def test_to_content_to_data_small(self):
        self._check_to_content_to_data_from_json(DATA_DIR / "graph-sample-small.json")

    def test_to_content_to_data_n25_e25(self):
        self._check_to_content_to_data_from_json(DATA_DIR / "n25_e25.json")

    def test_to_content_to_data_n50_e25(self):
        self._check_to_content_to_data_from_json(DATA_DIR / "n50_e25.json")

    def test_to_content_to_data_large(self):
        self._check_to_content_to_data_from_json(DATA_DIR / "graph-sample-large.json")


if __name__ == "__main__":
    unittest.main()
