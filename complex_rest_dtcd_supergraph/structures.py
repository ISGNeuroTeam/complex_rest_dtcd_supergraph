"""
This module contains classes from domain/business layer.

For now, classes here represent intermediary step between presentation
layer and database-related activities.
"""

from dataclasses import dataclass, field
from itertools import chain
from operator import attrgetter
from typing import Any, MutableMapping, MutableSet, MutableSequence


# custom types / aliases
ID = str


@dataclass
class Primitive:
    """A primitive entity.

    Primitive entities have unique IDs and may contain user-defined
    properties and metadata.
    """

    # TODO ABC?
    uid: ID
    properties: MutableMapping[str, Any] = field(default_factory=dict)
    meta: MutableMapping[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class Port(Primitive):
    """A vertex port.

    Vertices connect to one another using input and output ports.
    """


@dataclass
class InputPort(Port):
    """A vertex port for incoming connections."""


@dataclass
class OutputPort(Port):
    """A vertex port for outgoing connections."""


@dataclass
class Hub:
    """Abstraction for collections of input and output ports."""

    incoming: MutableSet[ID] = field(default_factory=set)
    outgoing: MutableSet[ID] = field(default_factory=set)


@dataclass
class Vertex(Primitive):
    """A vertex coming from Y-files.

    Vertices contain user-defined properties and additional metadata
    for front-end.
    Vertices may have input and output ports, through which they connect
    to other vertices.
    """

    ports: Hub = Hub()


@dataclass
class Group(Primitive):
    """A group is a container for vertices or other groups.

    Front-end needs it to group objects. Currently it has no backend use.
    """

    objects: MutableSet[ID] = field(default_factory=set)


@dataclass
class Edge:
    """An edge between an input and an output ports of two vertices."""

    start: ID
    end: ID
    meta: MutableMapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.uid = (self.start, self.end)


@dataclass
class Content:
    """
    Represents graph content.

    We assume that incoming data is valid: referential integrity is ok,
    all ids are unique, etc.
    """

    vertices: MutableSequence[Vertex]
    ports: MutableSequence[Port]
    edges: MutableSequence[Edge]
    groups: MutableSequence[Group]
    # TODO how about keeping explicit input/output ports here and using
    #   just .ports attribute with IDs on vertices?

    @property
    def input_ports(self):
        """A list of input ports."""

        uids = set(
            uid
            for uid in chain.from_iterable(
                map(attrgetter("ports.incoming"), self.vertices)
            )
        )

        return [port for port in self.ports if port.uid in uids]

    @property
    def output_ports(self):
        """A list of output ports."""

        uids = set(
            uid
            for uid in chain.from_iterable(
                map(attrgetter("ports.outgoing"), self.vertices)
            )
        )

        return [port for port in self.ports if port.uid in uids]
