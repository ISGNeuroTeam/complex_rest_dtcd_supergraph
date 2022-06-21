import configparser
import json
import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag

from complex_rest_dtcd_supergraph.converters import Converter

from ..fixtures import sort_payload


# path to tests/ dir
TEST_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = TEST_DIR / "fixtures"
DATA_DIR = TEST_DIR / "data"
# testing config
config = configparser.ConfigParser()
config.read(TEST_DIR / "config.ini")
N = config["general"].getint("num_iter")


class TestConverter(SimpleTestCase):
    def _check_load_dump(self, data):
        sort_payload(data)
        converter = Converter()
        subgraph = converter.load(data)
        exported = converter.dump(subgraph)
        sort_payload(exported)
        self.assertEqual(data, exported)

    def _check_load_dump_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self._check_load_dump(data)

    def test_load_dump_small(self):
        self._check_load_dump_from_json(FIXTURES_DIR / "graph-sample-small.json")

    def test_load_dump_n25_e25(self):
        self._check_load_dump_from_json(DATA_DIR / "n25_e25.json")

    def test_load_dump_n50_e25(self):
        self._check_load_dump_from_json(DATA_DIR / "n50_e25.json")

    @unittest.skip("py2neo bug")
    @tag("slow")
    def test_load_dump_many_times(self):
        with open(FIXTURES_DIR / "graph-sample-small.json") as f:
            data = json.load(f)
        sort_payload(data)

        ok = True

        # TODO settings for number of iterations
        for _ in range(N):
            converter = Converter()
            subgraph = converter.load(data)
            converter = Converter()
            exported = converter.dump(subgraph)
            sort_payload(exported)
            if data != exported:
                ok = False
                break

        self.assertTrue(ok)

    def test_load_dump_large(self):
        self._check_load_dump_from_json(FIXTURES_DIR / "graph-sample-large.json")

    @unittest.skip("py2neo bug")
    @tag("slow")
    def test_load_dump_large_many_times(self):
        with open(FIXTURES_DIR / "graph-sample-large.json") as f:
            data = json.load(f)
        sort_payload(data)

        for i in range(N):
            converter = Converter()
            subgraph = converter.load(data)
            exported = converter.dump(subgraph)
            sort_payload(exported)
            self.assertEqual(data, exported, msg=f"Lap {i}")

    # TODO add tests through DB: duplicated edges


if __name__ == "__main__":
    unittest.main()
