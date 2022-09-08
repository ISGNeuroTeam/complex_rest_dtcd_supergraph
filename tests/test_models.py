import neomodel

from rest_auth.models import User

from complex_rest_dtcd_supergraph import settings  # sets up neo4j settings
from complex_rest_dtcd_supergraph.models.auth import (
    KeyChain,
    RoleModelCoveredMixin,
)

from .misc import APITestCase
from .test_views import Neo4jTestCaseMixin


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
