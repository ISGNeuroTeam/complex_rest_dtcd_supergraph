"""
This module contains classes from domain/business layer.

For now, classes here represent intermediary step between presentation
layer and database-related activities.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from operator import itemgetter
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    MutableMapping,
    MutableSequence,
    MutableSet,
)

from .settings import KEYS
from .utils import savable_as_property


# custom types / aliases
ID = str


# helper functions
def extract_savable_properties(properties: Dict[str, dict]):
    result = {}

    for name in properties:
        data = properties[name]
        value = data.get(KEYS.value)

        if value is not None and savable_as_property(value):
            result[name] = data.pop(KEYS.value)

    return result


def restore_properties(original: dict, properties: dict):
    for name, value in properties.items():
        if name in original:  # FIXME handle this elsewhere?
            original[name][KEYS.value] = value


def get_ports(nodes: Iterable[dict]) -> Generator[dict, None, None]:
    for node in nodes:
        for port in node.get(KEYS.init_ports, []):
            yield port


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

    @staticmethod
    def _extract_fields(data: dict):
        meta = deepcopy(data)
        uid = meta.pop(KEYS.yfiles_id)
        properties = extract_savable_properties(meta.get(KEYS.properties, {}))

        return meta, uid, properties

    @classmethod
    def from_dict(cls, data: dict) -> "Primitive":
        """Load primitive from dictionary."""

        meta, uid, properties = cls._extract_fields(data)

        return cls(uid=uid, properties=properties, meta=meta)

    def to_dict(self) -> dict:
        """Dump this primitive's data to dictionary."""

        data = deepcopy(self.meta)
        data[KEYS.yfiles_id] = self.uid

        # FIXME workaround to handle stale properties on nodes; find better way
        if KEYS.properties in data:
            restore_properties(data[KEYS.properties], self.properties)

        return data


@dataclass
class Port(Primitive):
    """A vertex port.

    Vertices connect to one another through the ports.
    """

    @classmethod
    def from_dict(cls, data: dict) -> "Port":
        """Load port from dictionary."""

        return super().from_dict(data)


@dataclass
class Vertex(Primitive):
    """A vertex coming from Y-files.

    Vertices contain user-defined properties and additional metadata
    for front-end.
    Vertices may have multiple ports, through which they connect
    to other vertices.
    """

    ports: MutableSet[ID] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict) -> "Vertex":
        """Load vertex from dictionary."""

        meta, uid, properties = cls._extract_fields(data)
        ports = meta.pop(KEYS.init_ports, [])  #  save only ids
        port_ids = set(map(itemgetter(KEYS.yfiles_id), ports))

        return cls(uid=uid, properties=properties, meta=meta, ports=port_ids)

    def to_dict(self, id2port: dict) -> dict:
        """Dump this vertex data to dictionary.

        Args:
            id2port: mapping between IDs and ports, connected to this vertex.
        """

        data = super().to_dict()

        ports = [id2port[port_id] for port_id in self.ports]
        if ports:
            data[KEYS.init_ports] = ports

        return data


@dataclass
class Group(Primitive):
    """A group is a container for vertices or other groups.

    Front-end needs it to group objects. Currently it has no backend use.
    """

    @classmethod
    def from_dict(cls, data: dict) -> "Group":
        """Load group from dictionary."""

        return super().from_dict(data)


@dataclass
class Edge:
    """An edge between an output and an input ports of two vertices."""

    start: ID  # output port ID
    end: ID  # input port ID
    meta: MutableMapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.uid = (self.start, self.end)

    @classmethod
    def from_dict(cls, data: dict) -> "Edge":
        """Load edge from dictionary."""

        meta = deepcopy(data)
        start = meta.pop(KEYS.source_port)
        end = meta.pop(KEYS.target_port)

        return cls(start=start, end=end, meta=meta)

    def to_dict(self) -> dict:
        """Dump this edge data to dictionary."""

        data = deepcopy(self.meta)
        data[KEYS.source_port] = self.start
        data[KEYS.target_port] = self.end

        return data


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

    @classmethod
    def from_dict(cls, data: dict) -> "Content":
        """Load graph data from dictionary in specified format."""

        # pre-condition: data is valid
        # TODO more validation / error handling?
        nodes = data[KEYS.nodes]
        vertices = list(map(Vertex.from_dict, nodes))
        ports = list(map(Port.from_dict, get_ports(nodes)))
        edges = list(map(Edge.from_dict, data.get(KEYS.edges, [])))
        groups = list(map(Group.from_dict, data.get(KEYS.groups, [])))

        return cls(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )

    def _to_nodes(self):
        ports = list(map(Port.to_dict, self.ports))
        id2port = {p[KEYS.yfiles_id]: p for p in ports}
        nodes = [vertex.to_dict(id2port) for vertex in self.vertices]

        return nodes

    def to_dict(self) -> dict:
        """Dump this content data to dictionary."""

        nodes = self._to_nodes()
        edges = list(map(Edge.to_dict, self.edges))
        groups = list(map(Group.to_dict, self.groups))

        result = {
            KEYS.nodes: nodes,
            KEYS.edges: edges,
            KEYS.groups: groups,
        }

        return result

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
