import json
import unittest
from pathlib import Path

from django.test import SimpleTestCase

from complex_rest_dtcd_supergraph.structures import Content

from .misc import load_data, sort_payload

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / "data"


# TODO tests for import/export: Primitive, Port, Vertex, Group, Edge


class TestContent(SimpleTestCase):
    content = Content

    def _check_from_dict_to_dict(self, data):
        sort_payload(data)
        content = Content.from_dict(data)
        exported = self.content.to_dict(content)
        sort_payload(exported)
        self.assertEqual(exported, data)

    def test_from_dict(self):
        data = load_data(DATA_DIR / "basic.json")
        content = Content.from_dict(data)

        self.assertEqual(len(content.vertices), 2)
        self.assertEqual(len(content.ports), 2)
        self.assertEqual(len(content.edges), 1)
        self.assertEqual(len(content.groups), 0)

    def test_to_dict(self):
        # TODO
        pass

    def _check_from_dict_to_dict_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self._check_from_dict_to_dict(data)

    def test_from_dict_to_dict_small(self):
        self._check_from_dict_to_dict_from_json(DATA_DIR / "graph-sample-small.json")

    def test_from_dict_to_dict_n25_e25(self):
        self._check_from_dict_to_dict_from_json(DATA_DIR / "n25_e25.json")

    def test_from_dict_to_dict_n50_e25(self):
        self._check_from_dict_to_dict_from_json(DATA_DIR / "n50_e25.json")

    def test_from_dict_to_dict_large(self):
        self._check_from_dict_to_dict_from_json(DATA_DIR / "graph-sample-large.json")


if __name__ == "__main__":
    unittest.main()
