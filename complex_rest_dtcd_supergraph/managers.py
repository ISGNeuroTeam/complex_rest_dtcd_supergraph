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
from .utils import free_properties


def save_properties(properties, node):
    """Save dictionary with properties on a given node."""

    for key, val in properties.items():
        setattr(node, key, val)

    return node


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


class Writer:
    """Write operations on a fragment."""

    # TODO maybe instantiate with fragment & content? avoids passing args around

    def _delete_nodes(self, uids: Iterable[structures.ID]):
        pass

    def _delete_difference(
        self, fragment: models.Fragment, content: structures.Content
    ):
        # get uids of nodes (vertices, groups, ports) in the fragment
        results, _ = fragment.cypher(
            "MATCH (f) --> (v:Vertex) WHERE id(f)={self} "
            "OPTIONAL MATCH path = (v) --> (:Port) "
            "UNWIND nodes(path) AS n "
            "RETURN DISTINCT n.uid"
        )  # TODO delete old nodes right here
        old_uids = set(row[0] for row in results)
        for group in fragment.groups.all():
            old_uids.add(group.uid)

        new_uids = set(
            item.uid
            for item in chain(
                content.vertices,
                content.ports,
                content.groups,
            )
        )
        deprecated_uids = old_uids - new_uids
        neomodel.db.cypher_query(
            query=(
                "MATCH (n) "
                "WHERE "
                "  n.uid IS NOT NULL"
                "  AND n.uid IN $deprecated"
                "DETACH DELETE n"
            ),
            params={"deprecated": list(deprecated_uids)},
        )

        # edges
        results, _ = fragment.cypher(
            "MATCH (f) WHERE id(f)={self} "
            "MATCH (f) -- (:Vertex) "
            "  -- (start:Port) -[:EDGE]-> (end:Port) "
            "  -- (:Vertex) -- (f) "
            "RETURN start, end"
        )
        old_uids = set((row[0], row[1]) for row in results)
        new_uids = set(edge.uid for edge in content.edges)
        deprecated = old_uids - new_uids
        # FIXME remove edges with start-end ports in deprecated iterable

    def _merge_group(self, fragment: models.Fragment, group: structures.Group):
        node = models.Group(uid=group.uid, meta_=group.meta).save()
        fragment.groups.connect(node)

    def _merge(self, fragment: models.Fragment, content: structures.Content):
        # merge ports
        # FIXME here we need incoming and outgoing ports from content
        input_ports = {}
        output_ports = {}

        # link ports with edges
        for edge in content.edges:
            output_port_node = output_ports[edge.start]
            input_port_node = input_ports[edge.end]
            # TODO what if we already have this edge?
            output_port_node.neighbor.connect(
                input_port_node, properties={"meta_": edge.meta}
            )

        # merge vertices
        for vertex in content.vertices:
            vertex_node = models.Vertex(uid=vertex.uid, meta_=vertex.meta)
            save_properties(vertex.properties, vertex_node)  # save user-defined props
            vertex_node.save()  # TODO merge of existing stuff?

            # connect this vertex to ports
            for port_id in vertex.ports.incoming:
                inpu_port_node = input_ports[port_id]
                vertex_node.input_ports.connect(inpu_port_node)

            for port_id in vertex.ports.outgoing:
                output_port_node = output_ports[port_id]
                vertex_node.output_ports.connect(output_port_node)

            # link to fragment
            fragment.vertices.connect(vertex_node)

        # merge groups
        for group in content.groups:
            self._merge_group(fragment, group)

    def replace(self, fragment: models.Fragment, content: structures.Content):
        self._delete_difference(fragment, content)
        self._merge(fragment, content)


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
