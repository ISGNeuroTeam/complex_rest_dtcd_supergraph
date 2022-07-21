from dataclasses import dataclass, field
from typing import Any, MutableMapping, MutableSet, MutableSequence

from .settings import DEFAULT_ID_TYPE


# custom types / aliases
ID = DEFAULT_ID_TYPE


@dataclass
class Primitive:
    uid: ID
    data: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass
class Port(Primitive):
    pass


@dataclass
class InputPort(Port):
    pass


@dataclass
class OutputPort(Port):
    pass


@dataclass
class Hub:
    incoming: MutableSet[ID] = field(default_factory=set)
    outgoing: MutableSet[ID] = field(default_factory=set)


@dataclass
class Vertex(Primitive):
    ports: Hub = Hub()


@dataclass
class Group(Primitive):
    objects: MutableSet[ID] = field(default_factory=set)


@dataclass
class Edge:
    start: ID
    end: ID
    data: MutableMapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.uid = (self.start, self.end)


@dataclass
class Content:
    """
    Represents graph content.

    We assume that incoming data is valid: referential integrity is ok,
    all ids are unique, etc.
    """

    vertices: MutableSequence[Vertex]  # TODO different structure? dict[ID, Vertex]
    edges: MutableSequence[Edge]
    ports: MutableSequence[Port]
    groups: MutableSequence[Group]

    # TODO empty content?
