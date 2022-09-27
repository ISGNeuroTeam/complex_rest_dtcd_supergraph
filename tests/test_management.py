import unittest
from pathlib import Path
from types import SimpleNamespace

from django.test import SimpleTestCase, tag

from complex_rest_dtcd_supergraph import settings  # sets up neo4j settings
from complex_rest_dtcd_supergraph.models import management

from .factories import (
    ContainerFactory,
    GroupFactory,
    PortFactory,
    VertexFactory,
)
from .test_views import Neo4jTestCaseMixin


TEST_DIR = Path(__file__).resolve().parent


def create_graph():
    g = SimpleNamespace()

    # container A
    g.c0 = ContainerFactory(name="A").save()
    # vertices
    g.v0 = VertexFactory().save()
    g.v1 = VertexFactory().save()
    # ports
    g.p0 = PortFactory().save()
    g.p1 = PortFactory().save()
    # groups
    g.g0 = GroupFactory().save()
    # relations: port -[edge]-> port
    g.e_inside = g.p0.neighbor.connect(g.p1, dict(meta_="eggs"))
    # relations: vertex --> port
    g.v0.ports.connect(g.p0)
    g.v1.ports.connect(g.p1)
    # relations: container --> vertex
    g.c0.vertices.connect(g.v0)
    g.c0.vertices.connect(g.v1)
    # relations: container --> group
    g.c0.groups.connect(g.g0)

    # container B
    g.c1 = ContainerFactory(name="B").save()
    g.v_other = VertexFactory().save()
    g.p_other = PortFactory().save()
    g.v_other.ports.connect(g.p_other)
    g.c1.vertices.connect(g.v_other)

    # cross-container relation
    g.e_outside = g.p1.neighbor.connect(g.p_other, dict(meta_="spam"))

    return g


@tag("neo4j")
class TestReader(Neo4jTestCaseMixin, SimpleTestCase):
    def setUp(self) -> None:
        self.g = create_graph()

    def test_read(self):
        # TODO assert meta attrs are equal
        content = management.Reader.read(self.g.c0)
        self.assertEqual(len(content.vertices), 2)
        self.assertEqual(
            {x.uid for x in content.vertices},
            {self.g.v0.uid, self.g.v1.uid},
        )
        self.assertEqual(len(content.ports), 2)
        self.assertEqual(
            {x.uid for x in content.ports},
            {self.g.p0.uid, self.g.p1.uid},
        )
        self.assertEqual(len(content.groups), 1)
        self.assertEqual(
            {x.uid for x in content.groups},
            {self.g.g0.uid},
        )
        self.assertEqual(len(content.edges), 1)
        edge = content.edges[0]
        self.assertEqual(edge.meta, self.g.e_inside.meta_)


@tag("neo4j")
class TestDeprecator(Neo4jTestCaseMixin, SimpleTestCase):
    def test_delete_difference_edges(self):
        # TODO
        pass

    def test_delete_difference_ports(self):
        # TODO
        pass

    def test_delete_difference_vertices(self):
        # TODO
        pass


@tag("neo4j")
class TestMerger(Neo4jTestCaseMixin, SimpleTestCase):
    # TODO
    pass


if __name__ == "__main__":
    unittest.main()
