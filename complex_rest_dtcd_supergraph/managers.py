"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Tuple

import neomodel

from . import models
from . import structures
from .utils import connect_if_not_connected, free_properties


class Reader:
    """Read operations on a fragment."""

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

            # skip missing neighbors or neighbors from outside this fragment
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
        # TODO mention somehow that order matters here!
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
            structures.Edge(start=op_uid, end=ip_uid, meta=edge.meta_)
            for (op_uid, ip_uid), edge in edges.items()
        ]
        groups = [self._to_primitive(node, structures.Group) for node in groups]

        return structures.Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )


class Writer:
    """Write operations on a fragment."""

    def __init__(self):
        self._fragment = None
        self._content = None
        self._uid2port = None  # mapping of ID to merged input/output ports
        # merged nodes
        self._vertices = None
        self._groups = None

    def _delete_deprecated_vertices_groups_ports(self):

        # get uids of primitive nodes (vertices, groups, ports) in the fragment
        uid2node = {}

        for vertex in self._fragment.vertices.all():
            uid2node[vertex.uid] = vertex

            for port in vertex.ports.all():
                uid2node[port.uid] = port

        for group in vertex.groups.all():
            uid2node[group.uid] = group

        new_uids = set(
            item.uid
            for item in chain(
                self._content.vertices,
                self._content.ports,
                self._content.groups,
            )
        )
        deprecated_uids = set(uid2node) - new_uids

        for uid in deprecated_uids:
            uid2node[uid].delete()

    def _delete_deprecated_edges(self):
        results, _ = self._fragment.cypher(
            "MATCH (f) WHERE id(f)={self} "
            "MATCH (f) -- (:Vertex) "
            "  -- (src:OutputPort) -[:EDGE]-> (dst:InputPort) "
            "  -- (:Vertex) -- (f) "
            "RETURN src.uid, dst.uid"
        )
        current_uids = set((row[0], row[1]) for row in results)  # opID, ipID pairs
        new_uids = set(edge.uid for edge in self._content.edges)
        deprecated_uids = current_uids - new_uids

        neomodel.db.cypher_query(
            query=(
                "UNWIND $list AS pair"
                "MATCH (:OutputPort {uid: pair[0]}) -[r:EDGE]-> (:InputPort {uid: pair[1]}) "
                "DELETE r"
            ),
            params={"list": list(deprecated_uids)},
        )

    def _delete_difference(self):
        """Delete entities in the fragment that are not in the new content."""

        self._delete_deprecated_vertices_groups_ports()
        self._delete_deprecated_edges()

    def _merge_input_ports(self):
        data = [
            dict(uid=port.uid, meta_=port.meta, **port.properties)
            for port in self._content.input_ports
        ]

        return models.InputPort.create_or_update(*data)

    def _merge_output_ports(self):
        data = [
            dict(uid=port.uid, meta_=port.meta, **port.properties)
            for port in self._content.output_ports
        ]

        return models.OutputPort.create_or_update(*data)

    def _merge_edges(self) -> List[models.EdgeRel]:
        relations = []

        for edge in self._content.edges:
            output_port = self._uid2port[edge.start]
            input_port = self._uid2port[edge.end]
            rel = output_port.neighbor.replace(
                input_port, properties={"meta_": edge.meta}
            )
            relations.append(rel)

        return relations

    def _merge_vertices(self) -> List[models.Vertex]:
        nodes = []

        for vertex in self._content.vertices:
            node = models.Vertex.create_or_update(
                dict(uid=vertex.uid, meta_=vertex.meta, **vertex.properties),
                lazy=True,
            )[0]
            nodes.append(node)

            # connect this vertex to ports
            for uid in vertex.ports.incoming:
                input_port = self._uid2port[uid]
                connect_if_not_connected(node.input_ports, input_port)

            for uid in vertex.ports.outgoing:
                output_port = self._uid2port[uid]
                connect_if_not_connected(node.output_ports, output_port)

        return nodes

    def _merge_groups(self):
        data = [dict(uid=group.uid, meta_=group.meta) for group in self._content.groups]

        return models.Group.create_or_update(*data, lazy=True)

    def _merge(self):
        """Merge content entities."""

        input_ports = self._merge_input_ports()
        output_ports = self._merge_output_ports()

        self._uid2port = {port.uid: port for port in chain(input_ports, output_ports)}

        self._merge_edges()
        self._vertices = self._merge_vertices()
        self._groups = self._merge_groups()

    def _reconnect_to_fragment(self):
        """Reconnect merged entities to parent fragment."""

        for vertex in self._vertices:
            connect_if_not_connected(self._fragment.vertices, vertex)

        for group in self._groups:
            connect_if_not_connected(self._fragment.groups, group)

    def replace(self, fragment: models.Fragment, content: structures.Content):
        """Replace the content of a given fragment."""

        # content pre-conditions (referential integrity within the content):
        # - for each edge, start (output) & end (input) ports exist in content
        # - for each vertex, all ports exist in content

        # initialize working variables
        self._fragment = fragment
        self._content = content

        self._delete_difference()
        self._merge()
        self._reconnect_to_fragment()


class Manager:
    def __init__(self) -> None:
        self._reader = Reader()
        self._writer = Writer()

    def read(self, fragment: models.Fragment):
        """Return the content of a given fragment."""

        return self._reader.read(fragment)

    def replace(self, fragment: models.Fragment, content: structures.Content):
        """Replace the content of a given fragment."""

        return self._writer.replace(fragment, content)
