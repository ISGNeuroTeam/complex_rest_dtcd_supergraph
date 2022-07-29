"""
Node classes for neomodel.

The models here closely mirror classes from `structures` module.
"""

from typing import List, Tuple

from neomodel import (
    db,
    JSONProperty,
    Relationship,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)
from neomodel.contrib import SemiStructuredNode

from .relations import EdgeRel, RELATION_TYPES


# type aliases
CustomUniqueIdProperty = StringProperty  # TODO better validation for IDs


class AbstractPrimitive(SemiStructuredNode):
    """Abstract entity.

    May contain nested metadata in its `meta_` property, as well as
    ad-hoc properties not defined here.

    We assume that ad-hoc properties are user-defined valid Neo4j
    properties. Invalid ones are stored in `meta_`.
    """

    __abstract_node__ = True

    uid = CustomUniqueIdProperty(unique_index=True, required=True)
    meta_ = JSONProperty()


class Port(AbstractPrimitive):
    """A vertex port.

    An output port connects to an input port via the edge relationship.
    """

    neighbor = Relationship(
        "Port", RELATION_TYPES.edge, cardinality=ZeroOrOne, model=EdgeRel
    )


class Vertex(AbstractPrimitive):
    """A vertex coming from Y-files.

    Vertices have ports, through which they connect to other vertices.
    """

    # TODO explicit input and output ports?
    ports = Relationship(Port, RELATION_TYPES.default)

    def delete(self, cascade=True):
        """Delete this vertex.

        If cascade is enabled, also delete all connected ports.
        """

        if cascade:
            for port in self.ports.all():
                port.delete()

        return super().delete()


class Group(AbstractPrimitive):
    """A group is a container for vertices or other groups.

    Front-end needs it to group objects. Currently it has no backend use.
    """


class Fragment(StructuredNode):
    """Fragment is a container for primitives.

    A fragment may include vertices and groups.
    We use fragments to partition the graph into regions for security
    control and ease of work.
    """

    uid = UniqueIdProperty()
    name = StringProperty(max_length=255, required=True)

    vertices = Relationship(Vertex, RELATION_TYPES.contains)
    groups = Relationship(Group, RELATION_TYPES.contains)

    def delete(self, cascade=True):
        """Delete this fragment.

        If cascade is enabled, delete all related vertices and groups in
        a cascading fashion.
        """

        if cascade:
            self.clear()

        return super().delete()

    def clear(self):
        """Delete all related vertices and groups in a cascading fashion."""

        for vertex in self.vertices.all():
            vertex.delete(cascade=True)

        for group in self.groups.all():
            group.delete()

    @property
    def edges(self) -> List[Tuple[Port, EdgeRel, Port]]:
        """Return a list of tuples (start, edge, end) inside this fragment."""

        q = (
            f"MATCH (f) WHERE id(f)={self.id} "
            "MATCH (f) -- (:Vertex) "
            f"  -- (src:Port) -[e:{RELATION_TYPES.edge}]-> (dst:Port) "
            "MATCH (dst)  -- (:Vertex) -- (f) "
            "RETURN src, e, dst"
        )
        results, _ = db.cypher_query(q, resolve_objects=True)

        return [(r[0], r[1], r[2]) for r in results]
