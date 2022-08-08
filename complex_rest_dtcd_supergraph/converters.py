"""
This module contains converter classes.
"""

from copy import deepcopy
from operator import itemgetter
from typing import Iterable, Dict

from .settings import KEYS
from .structures import Content, Edge, Group, Port, Vertex
from .utils import savable_as_property


class GraphDataConverter:
    """Supports conversion between front-end data and internal classes."""

    @staticmethod
    def _extract_savable_properties(properties: Dict[str, dict]):
        result = {}

        for name in properties:
            data = properties[name]
            value = data.get(KEYS.value)

            if value is not None and savable_as_property(value):
                result[name] = data.pop(KEYS.value)

        return result

    @staticmethod
    def _restore_properties(original: dict, properties: dict):
        for name, value in properties.items():
            if name in original:  # FIXME handle this elsewhere
                original[name][KEYS.value] = value

    @staticmethod
    def _get_ports(nodes: Iterable[dict]):
        for node in nodes:
            for port in node.get(KEYS.init_ports, []):
                yield port

    def _to_vertex(self, data: dict):
        meta = deepcopy(data)
        uid = meta.pop(KEYS.yfiles_id)
        properties = self._extract_savable_properties(meta.get(KEYS.properties, {}))
        ports = meta.pop(KEYS.init_ports, [])  #  save only ids
        port_ids = set(map(itemgetter(KEYS.yfiles_id), ports))

        return Vertex(uid=uid, properties=properties, meta=meta, ports=port_ids)

    def _from_vertex(self, vertex: Vertex, id2port: dict):
        data = deepcopy(vertex.meta)
        data[KEYS.yfiles_id] = vertex.uid

        # FIXME workaround to handle stale properties on nodes; find better way
        if KEYS.properties in data:
            self._restore_properties(data[KEYS.properties], vertex.properties)

        ports = [id2port[port_id] for port_id in vertex.ports]
        if ports:
            data[KEYS.init_ports] = ports

        return data

    def _to_port(self, data: dict):
        meta = deepcopy(data)
        uid = meta.pop(KEYS.yfiles_id)
        properties = self._extract_savable_properties(meta.get(KEYS.properties, {}))

        return Port(uid=uid, properties=properties, meta=meta)

    def _from_port(self, port: Port):
        data = deepcopy(port.meta)
        data[KEYS.yfiles_id] = port.uid

        # FIXME workaround to handle stale properties on nodes; find better way
        if KEYS.properties in data:
            self._restore_properties(data[KEYS.properties], port.properties)

        return data

    @staticmethod
    def _to_edge(data: dict):
        meta = deepcopy(data)
        start = meta.pop(KEYS.source_port)
        end = meta.pop(KEYS.target_port)

        return Edge(start=start, end=end, meta=meta)

    @staticmethod
    def _from_edge(edge: Edge):
        data = deepcopy(edge.meta)
        data[KEYS.source_port] = edge.start
        data[KEYS.target_port] = edge.end

        return data

    @staticmethod
    def _to_group(data: dict):
        meta = deepcopy(data)
        uid = meta.pop(KEYS.yfiles_id)

        return Group(uid=uid, meta=meta)

    @staticmethod
    def _from_group(group: Group):
        data = deepcopy(group.meta)
        data[KEYS.yfiles_id] = group.uid

        return data

    def _from_vertices_and_ports(self, content: Content):
        ports = list(map(self._from_port, content.ports))
        id2port = {p[KEYS.yfiles_id]: p for p in ports}
        nodes = [self._from_vertex(v, id2port) for v in content.vertices]

        return nodes

    def to_content(self, data: dict) -> Content:
        """Convert graph data in specified format to content."""

        # pre-condition: data is valid
        nodes = data[KEYS.nodes]
        vertices = list(map(self._to_vertex, nodes))
        ports = list(map(self._to_port, self._get_ports(nodes)))
        edges = list(map(self._to_edge, data.get(KEYS.edges, [])))
        groups = list(map(self._to_group, data.get(KEYS.groups, [])))

        return Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )

    def to_data(self, content: Content) -> dict:
        """Convert content to graph data in specified exchange format."""

        nodes = self._from_vertices_and_ports(content)
        edges = list(map(self._from_edge, content.edges))
        groups = list(map(self._from_group, content.groups))

        result = {
            KEYS.nodes: nodes,
            KEYS.edges: edges,
            KEYS.groups: groups,
        }

        return result
