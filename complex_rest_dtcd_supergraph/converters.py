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

    def _extract_savable_properties(self, properties: Dict[str, dict]):
        result = {}

        for name in properties:
            data = properties[name]

            if savable_as_property(data.get("value")):
                result[name] = data.pop("value")

        return result

    def _get_ports(self, nodes: Iterable[dict]):
        # TODO hardcoded
        return chain.from_iterable(map(itemgetter("initPorts"), nodes))

    def _to_vertex(self, node: dict):
        meta = deepcopy(node)
        # TODO hardcoded
        uid = meta.pop("primitiveID")
        properties = self._extract_savable_properties(meta["properties"])
        # ports - save only ids
        # TODO hub with incoming / outgoing ports
        ports = meta.pop("initPorts")
        port_ids = set(map(itemgetter("primitiveID"), ports))
        # TODO Hub? ports?

        return Vertex(uid=uid, properties=properties, meta=meta)

    def _to_port(self, port: dict):
        meta = deepcopy(port)
        uid = meta.pop("primitiveID")
        # TODO
        properties = self._extract_savable_properties(meta["properties"])

        return Port(uid=uid, properties=properties, meta=meta)

    def _to_edge(self, edge: dict):
        meta = deepcopy(edge)
        start = meta.pop("sourcePort")
        end = meta.pop("targetPort")

        return Edge(start=start, end=end, meta=meta)

    def _to_group(self, group: dict):
        meta = deepcopy(group)
        uid = meta.pop("primitiveID")

        return Group(uid=uid, meta=meta)

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
        raise NotImplementedError
