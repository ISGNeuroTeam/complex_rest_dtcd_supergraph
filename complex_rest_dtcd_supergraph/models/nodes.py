"""
Node classes for neomodel.
"""

from neomodel import (
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
CustomUniqueIdProperty = StringProperty


class AbstractPrimitive(SemiStructuredNode):
    """Abstract entity.

    May contain nested data in its `data` property, as well as ad-hoc
    properties not specified here.
    """

    __abstract_node__ = True

    uid = CustomUniqueIdProperty(unique_index=True, required=True)
    data_ = JSONProperty()


class Port(AbstractPrimitive):
    """Abstract node for a vertex port.

    An output ports connect to an input ports via an edge relationship.
    """

    # TODO rel back to parent vertex?
    neighbor = Relationship(
        "Port", RELATION_TYPES.edge, cardinality=ZeroOrOne, model=EdgeRel
    )


class InputPort(Port):
    pass


class OutputPort(Port):
    pass


class Vertex(AbstractPrimitive):
    """A vertex coming from Y-files.

    Vertices have ports, through which they connect to other vertices.
    """

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
