import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag
from py2neo import Graph

from complex_rest_dtcd_supergraph import settings
from complex_rest_dtcd_supergraph.models import Fragment
from complex_rest_dtcd_supergraph.exceptions import FragmentIsNotBound
from complex_rest_dtcd_supergraph.managers import (
    FragmentManager,
    ContentManager,
)


TEST_DIR = Path(__file__).resolve().parent
# service settings for Neo4j operations
KEYS = settings.SCHEMA["keys"]
LABELS = settings.SCHEMA["labels"]
TYPES = settings.SCHEMA["types"]
# connection to Neo4j db
GRAPH = Graph(
    settings.NEO4J["uri"],
    settings.NEO4J["name"],
    auth=(settings.NEO4J["user"], settings.NEO4J["password"]),
)


@tag("neo4j")
class TestFragmentManager(SimpleTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        GRAPH.delete_all()  # clear the db
        cls.manager = FragmentManager(GRAPH)

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def tearDown(self) -> None:
        GRAPH.delete_all()

    def test_all(self):
        # empty
        fragments = self.manager.all()
        self.assertEqual(len(fragments), 0)

        # some fragments
        f1 = Fragment(name="amy")
        f2 = Fragment(name="bob")
        f3 = Fragment(name="cloe")
        self.manager.save(f1, f2, f3)
        fragments = self.manager.all()
        self.assertEqual(len(fragments), 3)
        self.assertEqual(set(f.name for f in fragments), {"amy", "bob", "cloe"})

    def test_get(self):
        # non-existent fragment
        f = self.manager.get(42)
        self.assertIsNone(f)

        # real fragment
        orig = Fragment(name="amy")
        self.manager.save(orig)
        fromdb = self.manager.get(orig.__primaryvalue__)
        self.assertEqual(fromdb, orig)

    def test_save(self):
        # TODO same as get test???
        orig = Fragment(name="amy")
        self.manager.save(orig)
        fromdb = self.manager._repo.get(Fragment, orig.__primaryvalue__)
        self.assertEqual(fromdb, orig)

    def test_remove(self):
        orig = Fragment(name="amy")
        self.manager.save(orig)
        self.manager.remove(orig)
        fromdb = self.manager.get(orig.__primaryvalue__)
        self.assertIsNone(fromdb)


@tag("neo4j")
class TestContentManager(SimpleTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        GRAPH.delete_all()  # clear the db

        # create default fragment
        cls.fragment_manager = FragmentManager(GRAPH)
        cls.fragment = Fragment(name="sales")
        cls.fragment_manager.save(cls.fragment)

        cls.content_manager = ContentManager(GRAPH)

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def tearDown(self) -> None:
        GRAPH.delete_all()

    def test_get_invalid_fragment(self):
        # unbound fragment
        f = Fragment(name="unbound")
        with self.assertRaises(FragmentIsNotBound):
            self.content_manager.read(f)

        # TODO fragment from different graph?

    def test_get_empty_content(self):
        # all content
        subgraph = self.content_manager.read()
        self.assertEqual(len(subgraph.nodes), 0)
        self.assertEqual(len(subgraph.relationships), 0)

        # content of a fragment
        subgraph = self.content_manager.read(self.fragment)
        self.assertEqual(len(subgraph.nodes), 0)
        self.assertEqual(len(subgraph.relationships), 0)

    # TODO how to efficiently construct data for tests?
    # TODO construction of data for main methods is finicky


if __name__ == "__main__":
    unittest.main()
