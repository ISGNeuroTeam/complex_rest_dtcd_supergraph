"""
This module contains classes from domain/business layer.

For now, classes here represent intermediary step between presentation
layer and database-related activities.
"""

from dataclasses import dataclass, field
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
    meta: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass
class Port(Primitive):
    """A vertex port.

    Vertices connect to one another through the ports.
    """


@dataclass
class Vertex(Primitive):
    """A vertex coming from Y-files.

    Vertices contain user-defined properties and additional metadata
    for front-end.
    Vertices may have multiple ports, through which they connect
    to other vertices.
    """

    ports: MutableSet[ID] = field(default_factory=set)


@dataclass
class Group(Primitive):
    """A group is a container for vertices or other groups.

    Front-end needs it to group objects. Currently it has no backend use.
    """


@dataclass
class Edge:
    """An edge between an output and an input ports of two vertices."""

    start: ID  # output port ID
    end: ID  # input port ID
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

    @property
    def info(self):
        """Print basic statistics about the content."""

        return ", ".join(
            (
                f"{len(self.vertices)} vertices",
                f"{len(self.ports)} ports",
                f"{len(self.edges)} edges",
                f"{len(self.groups)} groups",
            )
        )
