import json
import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag

from complex_rest_dtcd_supergraph.converters import Converter, Dumper, Loader

from .misc import sort_payload

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / "data"


class TestLoader(SimpleTestCase):
    loader = Loader()


class TestDumper:
    pass


class TestConverter(SimpleTestCase):
    def _check_load_dump(self, data):
        sort_payload(data)
        converter = Converter()
        subgraph = converter.load(data)
        exported = converter.dump(subgraph)
        sort_payload(exported)
        # TODO log difference like in api test suite
        self.assertEqual(exported, data)

    def _check_load_dump_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self._check_load_dump(data)

    # def test_load_dump_small(self):
    #     self._check_load_dump_from_json(DATA_DIR / "graph-sample-small.json")

    # def test_load_dump_n25_e25(self):
    #     self._check_load_dump_from_json(DATA_DIR / "n25_e25.json")

    # def test_load_dump_n50_e25(self):
    #     self._check_load_dump_from_json(DATA_DIR / "n50_e25.json")

    # def test_load_dump_large(self):
    #     self._check_load_dump_from_json(DATA_DIR / "graph-sample-large.json")


if __name__ == "__main__":
    unittest.main()
