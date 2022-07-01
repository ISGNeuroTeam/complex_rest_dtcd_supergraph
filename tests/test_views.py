import configparser
import json
import unittest
from pathlib import Path

from django.urls import reverse
from django.test import Client, tag
from rest_framework import status
from rest_framework.test import APISimpleTestCase

from .misc import generate_data, sort_payload


TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / "data"
# testing config
config = configparser.ConfigParser()
config.read(TEST_DIR / "config.ini")
USE_DB = config["general"].getboolean("use_db")
URL_RESET = reverse("supergraph:reset")  # post here resets the db
CLIENT = Client()


def reset_db():
    CLIENT.post(URL_RESET)


class Neo4jTestCaseMixin:
    """A mixin for API tests of a Neo4j-based endpoint.

    Adds calls to reset the database on class setup and on teardowns of each test.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # clean db on start
        reset_db()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def tearDown(self) -> None:
        # clean after each test
        reset_db()


@unittest.skipUnless(USE_DB, "use_db=False")
@tag("neo4j")
class TestFragmentListView(Neo4jTestCaseMixin, APISimpleTestCase):
    url = reverse("supergraph:fragments")

    def test_post(self):
        response = self.client.post(self.url, data={"name": "sales"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        fragment = response.data["fragment"]
        self.assertIn("id", fragment)
        self.assertEqual(fragment["name"], "sales")

    def test_get(self):
        names = {"hr", "marketing", "sales"}
        for name in names:
            self.client.post(self.url, data={"name": name}, format="json")
        response = self.client.get(self.url)
        data = response.data
        fragments = data["fragments"]
        self.assertEqual({f["name"] for f in fragments}, names)


@unittest.skipUnless(USE_DB, "use_db=False")
@tag("neo4j")
class TestFragmentDetailView(Neo4jTestCaseMixin, APISimpleTestCase):
    def setUp(self) -> None:
        # default fragment
        response = self.client.post(
            reverse("supergraph:fragments"),
            data={"name": "sales"},
            format="json",
        )
        self.fragment = response.data["fragment"]
        self.pk = self.fragment["id"]
        self.url = reverse("supergraph:fragment-detail", args=(self.pk,))

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fragment = response.data["fragment"]
        self.assertEqual(fragment["id"], self.pk)
        self.assertEqual(fragment["name"], "sales")

    def test_put(self):
        data = {"name": "marketing"}
        response = self.client.put(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # get detail back with the same pk
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fragment = response.data["fragment"]
        self.assertEqual(fragment["name"], "marketing")

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@unittest.skip("deprecated")
@unittest.skipUnless(USE_DB, "use_db=False")
@tag("neo4j")
class TestNeo4jGraphView(APISimpleTestCase):
    @classmethod
    def setUpClass(cls):
        cls.url_fragments = reverse("supergraph:fragments")
        cls.url_reset = reverse("supergraph:reset")
        cls.data = generate_data()["data"]
        sort_payload(cls.data)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # create a fragment
        response = self.client.post(
            self.url_fragments, data={"name": "sales"}, format="json"
        )
        self.fragment_id = int(response.data["fragment"]["id"])
        self.url_graph = reverse("supergraph:fragment-graph", args=(self.fragment_id,))

    def tearDown(self):
        # clear Neo4j
        self.client.post(self.url_reset)

    def _put(self, data):
        """Shortcut to upload graph data to pre-created fragment."""

        sort_payload(data)
        response = self.client.put(self.url_graph, data={"graph": data}, format="json")
        return response

    def _check_put(self, data):
        response = self._put(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def _get(self):
        """Shortcut to read graph data from pre-created fragment."""

        response = self.client.get(self.url_graph, format="json")
        return response

    def _check_get(self):
        response = self._get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("graph", response.data)
        return response

    def _check_put_get(self, data):
        self._check_put(data)
        freshdata = self._check_get().data["graph"]
        sort_payload(freshdata)
        self.assertEqual(freshdata, data)

    def _check_put_get_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self._check_put_get(data)

    def test_put_get(self):
        self._check_put_get(self.data)

    def test_put_get_duplicated_edges(self):
        data = {
            "nodes": [{"primitiveID": "france"}, {"primitiveID": "spain"}],
            "edges": [
                {
                    "sourceNode": "france",
                    "targetNode": "spain",
                    "sourcePort": "lyon",
                    "targetPort": "barcelona",
                },
                {
                    "sourceNode": "france",
                    "targetNode": "spain",
                    "sourcePort": "paris",
                    "targetPort": "madrid",
                },
            ],
        }
        self._check_put_get(data)

    def test_put_get_basic(self):
        self._check_put_get_from_json(DATA_DIR / "basic.json")

    def test_put_get_basic_attributes(self):
        self._check_put_get_from_json(DATA_DIR / "basic-attributes.json")

    def test_put_get_basic_edges(self):
        self._check_put_get_from_json(DATA_DIR / "basic-edges.json")

    def test_put_get_basic_ports(self):
        self._check_put_get_from_json(DATA_DIR / "basic-ports.json")

    def test_put_get_basic_nested_attributes(self):
        self._check_put_get_from_json(DATA_DIR / "basic-nested-attributes.json")

    def test_put_get_basic_nested_edges(self):
        self._check_put_get_from_json(DATA_DIR / "basic-nested-edges.json")

    def test_put_get_basic_nested_ports(self):
        self._check_put_get_from_json(DATA_DIR / "basic-nested-ports.json")

    @tag("slow")
    def test_put_get_large(self):
        self._check_put_get_from_json(DATA_DIR / "graph-sample-large.json")

    def test_put_get_empty(self):
        self._check_put_get_from_json(DATA_DIR / "empty.json")

    @tag("slow")
    def test_put_get_n25_e25(self):
        self._check_put_get_from_json(DATA_DIR / "n25_e25.json")

    @tag("slow")
    def test_put_get_n50_e25(self):
        self._check_put_get_from_json(DATA_DIR / "n50_e25.json")


if __name__ == "__main__":
    unittest.main()
