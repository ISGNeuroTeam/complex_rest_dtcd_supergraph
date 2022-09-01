"""
Node classes from neomodel.
"""

import logging
from typing import List, Tuple, Union

from neomodel import (
    db,
    JSONProperty,
    Relationship,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)
from neomodel.contrib import SemiStructuredNode

from rest_auth.authorization import auth_covered_method
from rest_auth.models import IAuthCovered, KeyChainModel, User
from rest_auth.models.base_auth_covered import log as auth_logger

from . import management
from ..settings import PLUGIN_NAME
from ..settings import ROLE_MODEL_ACTION_NAMES as ACTION_NAMES
from .relations import EdgeRel, RELATION_TYPES


logger = logging.getLogger(PLUGIN_NAME)


# type aliases
# this depends on front-end team and what they use as IDs
CustomUniqueIdProperty = StringProperty  # TODO better validation for IDs?


class AbstractPrimitive(SemiStructuredNode):
    """Abstract entity.

    May contain nested metadata in its `meta_` property, as well as
    ad-hoc properties not defined here.

    We assume that ad-hoc properties are user-defined valid Neo4j
    properties. Invalid ones are stored in `meta_`.
    """

    __abstract_node__ = True

    # TODO more properties? created/modified on, owner, etc?
    uid = CustomUniqueIdProperty(unique_index=True, required=True)
    meta_ = JSONProperty()


class Port(AbstractPrimitive):
    """A vertex port.

    An output port connects to an input port via the edge relationship.
    """

    neighbor = Relationship("Port", RELATION_TYPES.edge, model=EdgeRel)


class Vertex(AbstractPrimitive):
    """A vertex coming from Y-files.

    Vertices have ports, through which they connect to other vertices.
    """

    # TODO explicit input and output ports?
    ports = RelationshipTo(Port, RELATION_TYPES.default)

    def delete(self, cascade=True):
        """Delete this vertex.

        If cascade is enabled, also delete all connected ports.
        """

        if cascade:
            self.clear()

        return super().delete()

    def clear(self):
        """Delete all connected ports."""

        for port in self.ports.all():
            port.delete()


class Group(AbstractPrimitive):
    """A group is a container for vertices or other groups.

    Front-end needs it to group objects. Currently it has no backend use.
    """


class Container(IAuthCovered, StructuredNode):
    """A container for the content.

    May include vertices and groups.
    """

    uid = UniqueIdProperty()
    name = StringProperty(max_length=255, required=True)  # TODO settings

    vertices = RelationshipTo(Vertex, RELATION_TYPES.contains)
    groups = RelationshipTo(Group, RELATION_TYPES.contains)

    def delete(self, cascade=True):
        """Delete this container.

        If cascade is enabled, delete all related vertices and groups in
        a cascading fashion.
        """

        if cascade:
            self.clear()

        return super().delete()

    @auth_covered_method(ACTION_NAMES.clear)
    def clear(self):
        """Delete all related vertices and groups in a cascading fashion."""

        for vertex in self.vertices.all():
            vertex.delete(cascade=True)

        for group in self.groups.all():
            group.delete()

    @property
    def edges(self) -> List[Tuple[Port, EdgeRel, Port]]:
        """Return a list of tuples (start, edge, end) inside this container."""

        q = (
            f"MATCH (this) WHERE id(this)={self.id} "
            "MATCH (this) -- (:Vertex) "
            f"  -- (src:Port) -[r:{RELATION_TYPES.edge}]-> (dst:Port) "
            "MATCH (dst)  -- (:Vertex) -- (this) "
            "RETURN src, r, dst"
        )
        results, _ = db.cypher_query(q, resolve_objects=True)

        return [(r[0], r[1], r[2]) for r in results]

    @auth_covered_method(ACTION_NAMES.read)
    def read_content(self):
        """Query and return the content of this container."""

        return management.Reader.read(self)

    @auth_covered_method(ACTION_NAMES.replace)
    def replace_content(self, new_content):
        """Replace the content of this container."""

        # content pre-conditions (referential integrity within the content):
        # - for each edge, start (output) & end (input) ports exist in content
        # - for each vertex, all ports exist in content
        management.Deprecator.delete_difference(self, new_content)
        # TODO does not replace old properties
        # TODO possible clashes between structured and user-defined properties
        result = management.Merger.merge(new_content)
        # TODO leaves existing connections to different containers
        management.reconnect_to_container(self, result.vertices, result.groups)

    def reconnect_to_content(self, container):
        """Reconnect to the content of a given container."""

        management.reconnect_to_container(self, container.vertices, container.groups)

    # ------------------------------------------------------------------
    # Role model interface
    # see rest_auth.models.AuthCoveredModel for info
    # ------------------------------------------------------------------
    @property
    def keychain(self) -> Union[KeyChainModel, None]:
        """Look up and return the keychain if it exists, None otherwise."""

        logger.info("Keychain lookup from %s", self)

        # TODO switch to normal interface
        # if self.keychain_id is not None:
        #     try:
        #         return KeyChainModel.objects.get(pk=self.keychain_id)
        #     except KeyChainModel.DoesNotExist:
        #         # TODO better error handling?
        #         auth_logger.error(f'Not found KeyChain with id = {self.keychain_id}')

        return None

    @keychain.setter
    def keychain(self, keychain: KeyChainModel):
        # self.keychain_id = keychain.pk
        # self.save()
        pass

    @property
    def owner(self) -> Union[User, None]:
        """Look up and return the owner if it exists, None otherwise."""

        logger.info("Owner lookup from %s", self)

        # if self.owner_id is not None:
        #     try:
        #         return User.objects.get(pk=self.owner_id)
        #     except User.DoesNotExist:
        #         # TODO better error handling?
        #         auth_logger.error(f'Not found owner with id = {self.owner_id}')

        return None

    @owner.setter
    def owner(self, user: User):
        # self.owner_id = user.pk
        # self.save()
        pass


class Fragment(Container):
    """Fragment is a container for primitives.

    A fragment may include vertices and groups.
    We use fragments to partition the graph into regions for security
    control and ease of work.
    """


class Root(Container):
    """A root is a collection of fragments and content.

    Roots partition global Neo4j graph into non-overlapping subgraphs."""

    fragments = RelationshipTo(Fragment, RELATION_TYPES.contains)

    def delete(self, cascade=True):
        """Delete this root.

        Deletes all related fragments, vertices and groups in a cascading
        fashion.
        """

        if cascade:
            self.clear()

        return super().delete(cascade=False)

    def clear(self, content_only=False):
        """Delete all related fragments, vertices and groups in a cascading fashion.

        If `content_only` is True, then only delete the content:
        vertices and groups.
        """

        super().clear()

        if content_only:
            return

        for fragment in self.fragments.all():
            fragment.delete(cascade=False)  # already cleared related content
