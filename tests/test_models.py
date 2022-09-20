import unittest
import uuid

import neomodel
from django.test import SimpleTestCase, tag

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

from .factories import (
    ContainerFactory,
    FragmentFactory,
    GroupFactory,
    PortFactory,
    RootFactory,
    VertexFactory,
)
from .misc import APITestCase
from .test_views import Neo4jTestCaseMixin


class SampleNode(RoleModelCoveredMixin, neomodel.StructuredNode):
    # sample node for testing RM mixin
    uid = neomodel.UniqueIdProperty()


@tag("neo4j")
class TestRoleModelCoveredMixin(Neo4jTestCaseMixin, APITestCase):
    """Tests for RoleModelCoveredMixin interface."""

    def test_iterface_keychain(self):
        node = SampleNode().save()

        # by default, no keychain
        self.assertIsNone(node.keychain)

        # with keychain
        keychain = KeyChain.objects.create()
        node.keychain = keychain
        self.assertEqual(node.keychain, keychain)

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
        self.assertEqual(node.owner, owner)

        # invalid owner
        node.owner_id = owner.pk + 1
        node.save()
        self.assertIsNone(node.owner)


@tag("neo4j")
class TestVertex(Neo4jTestCaseMixin, SimpleTestCase):
    def setUp(self) -> None:
        # prepare a vertex and 2 connected ports
        self.v = VertexFactory().save()
        self.p0 = PortFactory().save()
        self.p1 = PortFactory().save()
        self.v.ports.connect(self.p0)
        self.v.ports.connect(self.p1)

    def test_clear(self):
        self.v.clear()
        self.assertEqual(len(self.v.ports), 0)
        self.assertEqual(len(Port.nodes), 0)

    def test_delete(self):
        self.v.delete()
        self.assertEqual(len(Vertex.nodes), 0)
        self.assertEqual(len(Port.nodes), 0)


@tag("neo4j")
class TestContainer(Neo4jTestCaseMixin, SimpleTestCase):
    def test_edges(self):
        c = ContainerFactory().save()
        v0 = VertexFactory().save()
        p0 = PortFactory().save()
        v0.ports.connect(p0)
        c.vertices.connect(v0)
        v1 = VertexFactory().save()
        p1 = PortFactory().save()
        v1.ports.connect(p1)
        c.vertices.connect(v1)
        e_inside = p0.neighbor.connect(p1, dict(meta_="eggs"))
        v_other = VertexFactory().save()
        p_other = PortFactory().save()
        v_other.ports.connect(p_other)
        e_outside = p1.neighbor.connect(p_other, dict(meta_="spam"))
        # query the edges inside the container
        edges = c.edges
        # checks
        self.assertEqual(len(edges), 1)  # only one relation inside the container
        start, rel, end = edges[0]
        self.assertEqual(start, p0)
        self.assertEqual(rel.id, e_inside.id)
        self.assertEqual(end, p1)

    def test_reconnect_to_container(self):
        c0 = ContainerFactory().save()
        v = VertexFactory().save()
        c0.vertices.connect(v)
        c1 = ContainerFactory().save()
        c1.reconnect_to_content(c0)
        self.assertEqual(c1.vertices.all(), c0.vertices.all())

    # FIXME
    @unittest.skip("protected via role model")
    def test_clear(self):
        c = ContainerFactory().save()
        v = VertexFactory().save()
        g = GroupFactory().save()
        c.vertices.connect(v)
        c.groups.connect(g)
        c.clear()
        self.assertEqual(len(c.vertices), 0)
        self.assertEqual(len(c.groups), 0)

    # FIXME
    @unittest.skip("protected via role model")
    def test_delete(self):
        c = ContainerFactory().save()
        v = VertexFactory().save()
        g = GroupFactory().save()
        c.vertices.connect(v)
        c.groups.connect(g)
        c.delete()
        self.assertEqual(len(Container.nodes), 0)
        self.assertEqual(len(Vertex.nodes), 0)
        self.assertEqual(len(Group.nodes), 0)


# FIXME
@unittest.skip("protected via role model")
@tag("neo4j")
class TestFragment(Neo4jTestCaseMixin, SimpleTestCase):
    def test_delete_no_cascade(self):
        f = FragmentFactory().save()
        v = VertexFactory().save()
        g = GroupFactory().save()
        f.vertices.connect(v)
        f.groups.connect(g)
        f.delete(cascade=False)
        self.assertEqual(len(Fragment.nodes), 0)
        self.assertEqual(len(Vertex.nodes), 1)
        self.assertEqual(len(Group.nodes), 1)


# FIXME
@unittest.skip("protected via role model")
@tag("neo4j")
class TestRoot(Neo4jTestCaseMixin, SimpleTestCase):
    def setUp(self) -> None:
        self.r = RootFactory().save()
        f = FragmentFactory().save()
        v = VertexFactory().save()
        g = GroupFactory().save()
        f.vertices.connect(v)
        f.groups.connect(g)
        self.r.fragments.connect(f)
        self.r.vertices.connect(v)
        self.r.groups.connect(g)

    def test_clear(self):
        self.r.clear()
        self.assertEqual(len(Fragment.nodes), 0)
        self.assertEqual(len(Vertex.nodes), 0)
        self.assertEqual(len(Group.nodes), 0)

    def test_clear_content_only(self):
        self.r.clear(content_only=True)
        self.assertEqual(len(Fragment.nodes), 1)
        self.assertEqual(len(Vertex.nodes), 0)
        self.assertEqual(len(Group.nodes), 0)
