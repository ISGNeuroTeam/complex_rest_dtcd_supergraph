"""
This module contains converter classes.
"""

from copy import deepcopy
from itertools import chain
from operator import itemgetter
from typing import Iterable, Dict

from .structures import Content, Edge, Group, Port, Vertex
from .utils import savable_as_property


class GraphDataConverter:
    """Supports conversion between front-end data and internal classes."""

    def __init__(self, config):
        self._config = config

    @staticmethod
    def _extract_savable_properties(properties: Dict[str, dict]):
        result = {}

        for name in properties:
            data = properties[name]

            if savable_as_property(data.get("value")):
                result[name] = data.pop("value")

        return result

    @staticmethod
    def _restore_properties(original: dict, properties: dict):
        for key, value in properties.items():
            original[key]["value"] = value

    @staticmethod
    def _get_ports(nodes: Iterable[dict]):
        # TODO hardcoded
        return chain.from_iterable(map(itemgetter("initPorts"), nodes))

    def _to_vertex(self, data: dict):
        meta = deepcopy(data)
        # TODO hardcoded
        uid = meta.pop("primitiveID")
        properties = self._extract_savable_properties(meta["properties"])
        # ports - save only ids
        # TODO hub with incoming / outgoing ports
        ports = meta.pop("initPorts")
        port_ids = set(map(itemgetter("primitiveID"), ports))
        # TODO Hub? ports?

        return Vertex(uid=uid, properties=properties, meta=meta)

    def _from_vertex(self, vertex: Vertex, id2port: dict):
        data = deepcopy(vertex.meta)
        data["primitiveID"] = vertex.uid
        self._restore_properties(data["properties"], vertex.properties)
        ports = [
            id2port[port_id]
            for port_id in chain(vertex.ports.incoming, vertex.ports.outgoing)
        ]
        data["initPorts"] = ports

        return data

    def _to_port(self, data: dict):
        meta = deepcopy(data)
        uid = meta.pop("primitiveID")
        properties = self._extract_savable_properties(meta["properties"])

        return Port(uid=uid, properties=properties, meta=meta)

    def _from_port(self, port: Port):
        data = deepcopy(port.meta)
        data["primitiveID"] = port.uid
        self._restore_properties(data["properties"], port.properties)

        return data

    @staticmethod
    def _to_edge(data: dict):
        meta = deepcopy(data)
        start = meta.pop("sourcePort")
        end = meta.pop("targetPort")

        return Edge(start=start, end=end, meta=meta)

    @staticmethod
    def _from_edge(edge: Edge):
        data = deepcopy(edge.meta)
        data["sourcePort"] = edge.start
        data["targetPort"] = edge.end

        return data

    @staticmethod
    def _to_group( data: dict):
        meta = deepcopy(data)
        uid = meta.pop("primitiveID")

        return Group(uid=uid, meta=meta)

    @staticmethod
    def _from_group(group: Group):
        data = deepcopy(group.meta)
        data["primitiveID"] = group.uid

        return data

    def _from_vertices_and_ports(self, content: Content):
        ports = list(map(self._from_port, content.ports))
        id2port = {p["primitiveID"]: p for p in ports}
        nodes = [self._from_vertex(v, id2port) for v in content.vertices]

        return nodes

    def to_content(self, data: dict) -> Content:
        # pre-condition: data is valid
        nodes = data["nodes"]
        vertices = list(map(self._to_vertex, nodes))
        ports = list(map(self._to_port, self._get_ports(nodes)))
        edges = list(map(self._to_edge, data["edges"]))
        groups = list(map(self._to_group, data["groups"]))

        return Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )

    def to_data(self, content: Content) -> dict:
        nodes = self._from_vertices_and_ports(content)
        edges = list(map(self._from_edge, content.edges))
        groups = list(map(self._from_group, content.groups))

        result = {
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        }

        return result
