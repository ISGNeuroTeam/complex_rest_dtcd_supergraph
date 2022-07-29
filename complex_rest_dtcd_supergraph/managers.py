"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Mapping, Tuple

import neomodel

from . import models
from . import structures
from .utils import connect_if_not_connected, free_properties


class Reader:
    """Read operations on a fragment."""

    def __init__(self) -> None:
        self._foreign_key_mapping = defaultdict(set)  # parent:children uid pairs

    def _query_ports(self, vertices: Iterable[models.Vertex]):
        ports: List[models.Port] = []

        for vertex in vertices:
            for port in vertex.ports.all():
                ports.append(port)
                self._foreign_key_mapping[vertex.uid].add(port.uid)

        return ports

    def _query_edges(
        self,
        fragment: models.Fragment,
    ) -> Dict[Tuple[structures.ID, structures.ID], models.EdgeRel]:

        return {
            (output_port.uid, input_port.uid): edge
            for output_port, edge, input_port in fragment.edges
        }

    @staticmethod
    def _to_primitive(node, subclass):
        uid = node.uid
        properties = free_properties(node)
        meta = node.meta_

        return subclass(uid=uid, properties=properties, meta=meta)

    def _to_vertex(self, node: models.Vertex):
        vertex = self._to_primitive(node, subclass=structures.Vertex)

        # populate ports mappings
        for child_id in self._foreign_key_mapping.get(vertex.uid, []):
            vertex.ports.add(child_id)

        return vertex

    def read(self, fragment: models.Fragment) -> structures.Content:
        self._foreign_key_mapping.clear()

        # step 1 - get the insides
        vertices = fragment.vertices.all()
        ports = self._query_ports(vertices)
        edges = self._query_edges(fragment)
        groups = fragment.groups.all()

        # step 2 - map to content
        vertices = [self._to_vertex(node) for node in vertices]
        ports = [self._to_primitive(node, structures.Port) for node in ports]
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


class Deprecator:
    """Deletes deprecated content of a fragment."""

    @staticmethod
    def _delete_deprecated_vertices_groups_ports(
        fragment: models.Fragment, content: structures.Content
    ):
        """Delete vertices, groups and ports in the fragment not in the content."""

        # query uids of primitive nodes (vertices, groups, ports) in the fragment
        uid2node = {}

        for vertex in fragment.vertices.all():
            uid2node[vertex.uid] = vertex

            for port in vertex.ports.all():
                uid2node[port.uid] = port

        for group in fragment.groups.all():
            uid2node[group.uid] = group

        new_uids = set(
            item.uid
            for item in chain(
                content.vertices,
                content.ports,
                content.groups,
            )
        )
        deprecated_uids = set(uid2node) - new_uids

        for uid in deprecated_uids:
            uid2node[uid].delete()

        return deprecated_uids

    @staticmethod
    def _delete_deprecated_edges(
        fragment: models.Fragment, content: structures.Content
    ):
        """Delete edges in the fragment not in the content."""

        current_uids = set((op.uid, ip.uid) for op, _, ip in fragment.edges)
        new_uids = set(edge.uid for edge in content.edges)
        deprecated_uids = current_uids - new_uids

        neomodel.db.cypher_query(
            query=(
                "UNWIND $list AS pair "
                "MATCH ({uid: pair[0]}) -[r:EDGE]-> ({uid: pair[1]}) "
                "DELETE r"
            ),
            params={"list": list(deprecated_uids)},
        )

    def delete_difference(self, fragment: models.Fragment, content: structures.Content):
        """Delete entities in the fragment that are not in the content."""

        self._delete_deprecated_vertices_groups_ports(fragment, content)
        self._delete_deprecated_edges(fragment, content)


class Merger:
    """Merges content entities into the fragment."""

    def __init__(self):
        self._fragment = None
        self._content = None
        self._uid2port = None  # mapping of ID to merged ports
        # merged nodes
        self._vertices = None
        self._groups = None

    @staticmethod
    def _merge_ports(ports: Iterable[structures.Port]):
        data = [
            dict(uid=port.uid, meta_=port.meta, **port.properties) for port in ports
        ]

        return models.Port.create_or_update(*data)

    @staticmethod
    def _merge_edges(
        edges: Iterable[structures.Edge],
        uid2port: Mapping[structures.ID, models.Port],
    ) -> List[models.EdgeRel]:
        relations = []

        for edge in edges:
            output_port = uid2port[edge.start]
            input_port = uid2port[edge.end]
            rel = connect_if_not_connected(
                output_port.neighbor, input_port, {"meta_": edge.meta}
            )
            relations.append(rel)

        return relations

    @staticmethod
    def _merge_vertices(
        vertices: Iterable[structures.Vertex],
        uid2port: Mapping[structures.ID, models.Port],
    ) -> List[models.Vertex]:
        nodes = []

        for vertex in vertices:
            node = models.Vertex.create_or_update(
                dict(uid=vertex.uid, meta_=vertex.meta, **vertex.properties),
                lazy=True,
            )[0]
            nodes.append(node)

            # connect this vertex to ports
            for uid in vertex.ports:
                port = uid2port[uid]
                connect_if_not_connected(node.ports, port)

        return nodes

    @staticmethod
    def _merge_groups(groups: Iterable[structures.Group]):
        data = [dict(uid=group.uid, meta_=group.meta) for group in groups]

        return models.Group.create_or_update(*data, lazy=True)

    @staticmethod
    def _reconnect_to_fragment(
        fragment: models.Fragment,
        vertices: Iterable[models.Vertex],
        groups: Iterable[models.Group],
    ):
        """Reconnect merged entities to parent fragment."""

        for vertex in vertices:
            connect_if_not_connected(fragment.vertices, vertex)

        for group in groups:
            connect_if_not_connected(fragment.groups, group)

    def merge(self, fragment: models.Fragment, content: structures.Content):
        """Merge content entities."""

        ports = self._merge_ports(content.ports)
        uid2port = {port.uid: port for port in ports}
        self._merge_edges(content.edges, uid2port)
        vertices = self._merge_vertices(content.vertices, uid2port)
        groups = self._merge_groups(content.groups)

        self._reconnect_to_fragment(fragment, vertices, groups)


class Writer:
    """Write operations on a fragment."""

    def __init__(self):
        self._deprecator = Deprecator()
        self._merger = Merger()

    def replace(self, fragment: models.Fragment, content: structures.Content):
        """Replace the content of a given fragment."""

        # content pre-conditions (referential integrity within the content):
        # - for each edge, start (output) & end (input) ports exist in content
        # - for each vertex, all ports exist in content
        self._deprecator.delete_difference(fragment, content)
        self._merger.merge(fragment, content)


class Manager:
    """Handles read and write operations on fragment's content."""

    def __init__(self) -> None:
        self._reader = Reader()
        self._writer = Writer()

    def read(self, fragment: models.Fragment):
        """Return the content of a given fragment."""

        return self._reader.read(fragment)

    def replace(self, fragment: models.Fragment, content: structures.Content):
        """Replace the content of a given fragment."""

        return self._writer.replace(fragment, content)
