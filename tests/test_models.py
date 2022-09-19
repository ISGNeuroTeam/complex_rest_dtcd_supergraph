import unittest
import uuid

import neomodel
from django.test import SimpleTestCase

from rest_auth.models import User

from complex_rest_dtcd_supergraph import settings  # sets up neo4j settings
from complex_rest_dtcd_supergraph.models import (
    Container,
    Fragment,
    Group,
    Port,
    Root,
    Vertex,
)
from complex_rest_dtcd_supergraph.models.auth import (
    KeyChain,
    RoleModelCoveredMixin,
)

from .misc import APITestCase
from .test_views import Neo4jTestCaseMixin


def genid():
    return uuid.uuid4().hex


class SampleNode(RoleModelCoveredMixin, neomodel.StructuredNode):
    # sample node for testing RM mixin
    uid = neomodel.UniqueIdProperty()


class TestRoleModelCoveredMixin(Neo4jTestCaseMixin, APITestCase):
    """Tests for RoleModelCoveredMixin interface."""

    def test_iterface_keychain(self):
        node = SampleNode().save()

        # by default, no keychain
        self.assertIsNone(node.keychain)

        # with keychain
        keychain = KeyChain.objects.create()
        node.keychain = keychain
        self.assertEqual(keychain, node.keychain)

        # invalid keychain
        node.keychain_id = keychain.pk - 1
        node.save()
        self.assertIsNone(node.keychain)

    def test_iterface_owner(self):
        node = SampleNode().save()

        # by default, no owner
        self.assertIsNone(node.owner)

        # with owner
        owner = User.objects.create_user(username="amy", password="pass")
        node.owner = owner
        self.assertEqual(owner, node.owner)

        # invalid owner
        node.owner_id = owner.pk + 1
        node.save()
        self.assertIsNone(node.owner)


class TestVertex(Neo4jTestCaseMixin, SimpleTestCase):
    def setUp(self) -> None:
        # prepare a vertex and 2 connected ports
        self.v = Vertex(uid=genid(), meta_="").save()
        self.p0 = Port(uid=genid(), meta_="").save()
        self.p1 = Port(uid=genid(), meta_="").save()
        self.v.ports.connect(self.p0)
        self.v.ports.connect(self.p1)

    def test_clear(self):
        self.v.clear()
        self.assertEqual(0, len(self.v.ports))
        self.assertEqual(0, len(Port.nodes))

    def test_delete(self):
        self.v.delete()
        self.assertEqual(0, len(Vertex.nodes))
        self.assertEqual(0, len(Port.nodes))


class TestContainer(Neo4jTestCaseMixin, SimpleTestCase):
    def test_edges(self):
        c = Container(name="container").save()
        v0 = Vertex(uid=genid(), meta_="").save()
        p0 = Port(uid=genid(), meta_="").save()
        v0.ports.connect(p0)
        c.vertices.connect(v0)
        v1 = Vertex(uid=genid(), meta_="").save()
        p1 = Port(uid=genid(), meta_="").save()
        v1.ports.connect(p1)
        c.vertices.connect(v1)
        e_inside = p0.neighbor.connect(p1, dict(meta_="eggs"))
        v_other = Vertex(uid=genid(), meta_="").save()
        p_other = Port(uid=genid(), meta_="").save()
        v_other.ports.connect(p_other)
        e_outside = p1.neighbor.connect(p_other, dict(meta_="spam"))
        # query the edges inside the container
        edges = c.edges
        # checks
        self.assertEqual(1, len(edges))  # only one relation inside the container
        start, rel, end = edges[0]
        self.assertEqual(p0, start)
        self.assertEqual(e_inside.id, rel.id)
        self.assertEqual(p1, end)

    def test_reconnect_to_container(self):
        c0 = Container(name="a").save()
        v = Vertex(uid=genid(), meta_="").save()
        c0.vertices.connect(v)
        c1 = Container(name="b").save()
        c1.reconnect_to_content(c0)
        self.assertEqual(c1.vertices.all(), c0.vertices.all())

    # FIXME
    @unittest.skip("protected via role model")
    def test_clear(self):
        c = Container(name="container").save()
        v = Vertex(uid=genid(), meta_="").save()
        g = Group(uid=genid(), meta_="").save()
        c.vertices.connect(v)
        c.groups.connect(g)
        c.clear()
        self.assertEqual(0, len(c.vertices))
        self.assertEqual(0, len(c.groups))

    # FIXME
    @unittest.skip("protected via role model")
    def test_delete(self):
        c = Container(name="container").save()
        v = Vertex(uid=genid(), meta_="").save()
        g = Group(uid=genid(), meta_="").save()
        c.vertices.connect(v)
        c.groups.connect(g)
        c.delete()
        self.assertEqual(0, len(Container.nodes))
        self.assertEqual(0, len(Vertex.nodes))
        self.assertEqual(0, len(Group.nodes))


# FIXME
@unittest.skip("protected via role model")
class TestFragment(Neo4jTestCaseMixin, SimpleTestCase):
    def test_delete_no_cascade(self):
        f = Fragment(name="fragment").save()
        v = Vertex(uid=genid(), meta_="").save()
        g = Group(uid=genid(), meta_="").save()
        f.vertices.connect(v)
        f.groups.connect(g)
        f.delete(cascade=False)
        self.assertEqual(0, len(Fragment.nodes))
        self.assertEqual(1, len(Vertex.nodes))
        self.assertEqual(1, len(Group.nodes))


# FIXME
@unittest.skip("protected via role model")
class TestRoot(Neo4jTestCaseMixin, SimpleTestCase):
    def setUp(self) -> None:
        self.r = Root(name="root").save()
        f = Fragment(name="fragment").save()
        v = Vertex(uid=genid(), meta_="").save()
        g = Group(uid=genid(), meta_="").save()
        f.vertices.connect(v)
        f.groups.connect(g)
        self.r.fragments.connect(f)
        self.r.vertices.connect(v)
        self.r.groups.connect(g)

    def test_clear(self):
        self.r.clear()
        self.assertEqual(0, len(Fragment.nodes))
        self.assertEqual(0, len(Vertex.nodes))
        self.assertEqual(0, len(Group.nodes))

    def test_clear_content_only(self):
        self.r.clear(content_only=True)
        self.assertEqual(1, len(Fragment.nodes))
        self.assertEqual(0, len(Vertex.nodes))
        self.assertEqual(0, len(Group.nodes))
