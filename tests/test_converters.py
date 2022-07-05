import json
import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag

from complex_rest_dtcd_supergraph.converters import Converter, Dumper, Loader

from .misc import generate_data, sort_payload
from .misc import KEYS, LABELS, TYPES, SCHEMA

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / "data"
N = 30  # deprecated


class TestLoader(SimpleTestCase):
    loader = Loader(SCHEMA)

    def test_load_data(self):
        data = {
            "name": "amy",
            "online": True,
            "address": ["bob", "dan"],
            "layout": {"x": 0, "y": 0},
        }

        tree = self.loader._load_data(data)
        self.assertEqual(len(tree.subgraph.nodes), 2)
        self.assertEqual(len(tree.subgraph.relationships), 1)
        self.assertTrue(tree.root.has_label(LABELS["data"]))

    def test_load_entity(self):
        data = {
            "name": "amy",
            "online": True,
            "address": ["bob", "dan"],
            "layout": {"x": 0, "y": 0},
        }
        tree = self.loader._load_entity(data)
        self.assertEqual(len(tree.subgraph.nodes), 3)
        self.assertEqual(len(tree.subgraph.relationships), 2)
        self.assertTrue(tree.root.has_label(LABELS["entity"]))
        self.assertIn(TYPES["has_data"], tree.subgraph.types())

    def test_load_vertex(self):
        data = {
            "name": "amy",
            "primitiveID": "abc",
            "online": True,
            "address": ["bob", "dan"],
            "layout": {"x": 0, "y": 0},
        }
        tree = self.loader._load_vertex(data)
        self.assertEqual(len(tree.subgraph.nodes), 3)
        self.assertEqual(len(tree.subgraph.relationships), 2)
        self.assertTrue(tree.root.has_label(LABELS["node"]))
        key = KEYS["yfiles_id"]
        self.assertIn(key, tree.root)
        self.assertEqual(tree.root[key], "abc")

    def test_load_edge(self):
        data = {
            "sourceNode": "amy",
            "sourcePort": "o1",
            "targetNode": "bob",
            "targetPort": "i1",
        }
        tree = self.loader._load_edge(data)
        self.assertEqual(len(tree.subgraph.nodes), 2)
        self.assertEqual(len(tree.subgraph.relationships), 1)
        self.assertTrue(tree.root.has_label(LABELS["edge"]))
        # TODO replace hard-coded stuff
        self.assertIn("sourceNode", tree.root)
        self.assertIn("sourcePort", tree.root)
        self.assertIn("targetNode", tree.root)
        self.assertIn("targetPort", tree.root)
        self.assertEqual(tree.root["sourceNode"], "amy")
        self.assertEqual(tree.root["sourcePort"], "o1")
        self.assertEqual(tree.root["targetNode"], "bob")
        self.assertEqual(tree.root["targetPort"], "i1")

    def test_load(self):
        data = generate_data()["data"]
        subgraph = self.loader.load(data)
        self.assertEqual(len(subgraph.nodes), 17)
        self.assertEqual(len(subgraph.relationships), 16)

    def test_load_from_json(self):
        with open(DATA_DIR / "graph-sample-small.json") as f:
            data = json.load(f)

        subgraph = self.loader.load(data)
        self.assertEqual(len(subgraph.nodes), 19)
        self.assertEqual(len(subgraph.relationships), 18)


class TestDumper:
    def test_dump(self):
        d = generate_data()
        data = d["data"]
        sort_payload(data)
        subgraph = d["subgraph"]
        dumper = Dumper(SCHEMA)
        exported = dumper.dump(subgraph)
        sort_payload(exported)
        self.assertEqual(exported, data)


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

    def test_load_dump_small(self):
        self._check_load_dump_from_json(DATA_DIR / "graph-sample-small.json")

    def test_load_dump_n25_e25(self):
        self._check_load_dump_from_json(DATA_DIR / "n25_e25.json")

    def test_load_dump_n50_e25(self):
        self._check_load_dump_from_json(DATA_DIR / "n50_e25.json")

    @unittest.skip("py2neo bug")
    @tag("slow")
    def test_load_dump_many_times(self):
        with open(DATA_DIR / "graph-sample-small.json") as f:
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
        self._check_load_dump_from_json(DATA_DIR / "graph-sample-large.json")

    @unittest.skip("py2neo bug")
    @tag("slow")
    def test_load_dump_large_many_times(self):
        with open(DATA_DIR / "graph-sample-large.json") as f:
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
