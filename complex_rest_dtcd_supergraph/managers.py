"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Tuple

from . import models
from . import structures
from .utils import free_properties


class Manager:
    def __init__(self) -> None:
        self._foreign_key_mapping = defaultdict(set)  # parent:children uid pairs
        self._input_port_ids = set()

    def _clear(self):
        self._foreign_key_mapping.clear()
        self._input_port_ids.clear()

    def _query_input_ports(self, vertices: Iterable[models.Vertex]):
        # saves: foreign keys from vertex to ports, input port ids
        ports: List[models.InputPort] = []

        for vertex in vertices:
            for port in vertex.input_ports.all():
                ports.append(port)
                self._foreign_key_mapping[vertex.uid].add(port.uid)
                self._input_port_ids.add(port.uid)

        return ports

    def _query_output_ports(self, vertices: Iterable[models.Vertex]):
        # saves foreign keys from vertex to ports
        ports: List[models.OutputPort] = []

        for vertex in vertices:
            for port in vertex.output_ports.all():
                ports.append(port)
                self._foreign_key_mapping[vertex.uid].add(port.uid)

        return ports

    def _query_edges(
        self, output_ports: Iterable[models.OutputPort]
    ) -> Dict[Tuple[structures.ID, structures.ID], models.EdgeRel]:
        edges = {}

        for op in output_ports:
            neighbor = op.neighbor.single()  # can be None

            # skip missing ports or ports from outside this fragment
            if neighbor is None or neighbor.uid not in self._input_port_ids:
                continue

            edge = op.neighbor.relationship(neighbor)
            edge_id = (op.uid, neighbor.uid)
            edges[edge_id] = edge

        return edges

    @staticmethod
    def _to_primitive(node, subclass):
        # TODO move it somewhere else?
        uid = node.uid
        properties = free_properties(node)
        meta = node.meta_

        return subclass(uid=uid, properties=properties, meta=meta)

    def _to_vertex(self, node: models.Vertex):
        vertex = self._to_primitive(node, subclass=structures.Vertex)

        # populate ports mappings
        for child_id in self._foreign_key_mapping.get(vertex.uid, []):
            if child_id in self._input_port_ids:
                vertex.ports.incoming.add(child_id)
            else:
                vertex.ports.outgoing.add(child_id)

        return vertex

    def read(self, fragment: models.Fragment) -> structures.Content:
        self._clear()

        # step 1 - get the insides
        # TODO a lot of queries
        vertices = fragment.vertices.all()
        input_ports = self._query_input_ports(vertices)
        output_ports = self._query_output_ports(vertices)
        edges = self._query_edges(output_ports)
        groups = fragment.groups.all()

        # step 2 - map to content
        vertices = [self._to_vertex(node) for node in vertices]
        ports = [
            self._to_primitive(node, structures.Port)
            for node in chain(input_ports, output_ports)
        ]
        edges = [
            structures.Edge(start=opID, end=ipID, meta=edge.meta_)
            for (opID, ipID), edge in edges.items()
        ]
        groups = [self._to_primitive(node, structures.Group) for node in groups]

        return structures.Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )

    def replace(self, fragment: models.Fragment, content: structures.Content):
        raise NotImplementedError
