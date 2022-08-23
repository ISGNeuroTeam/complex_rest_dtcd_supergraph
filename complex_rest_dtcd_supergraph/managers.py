"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, List, Mapping, Sequence

import neomodel

from . import models
from . import structures
from .models.relations import RELATION_TYPES
from .utils import connect_if_not_connected, free_properties


def reconnect_to_container(
    container: models.Container,
    vertices: Iterable[models.Vertex],
    groups: Iterable[models.Group],
):
    """Connect vertices and groups to given container."""

    for vertex in vertices:
        connect_if_not_connected(container.vertices, vertex)

    for group in groups:
        connect_if_not_connected(container.groups, group)


class _Reader:
    """Read operations on a container."""

    def __init__(self) -> None:
        self._foreign_key_mapping = defaultdict(set)  # parent:children uid pairs

    def _query_ports(self, vertices: Iterable[models.Vertex]):
        ports: List[models.Port] = []

        for vertex in vertices:
            for port in vertex.ports.all():
                ports.append(port)
                self._foreign_key_mapping[vertex.uid].add(port.uid)

        return ports

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

    def read(self, container: models.Container) -> structures.Content:
        self._foreign_key_mapping.clear()

        # step 1 - get the insides
        vertices = container.vertices.all()
        ports = self._query_ports(vertices)
        edges = container.edges
        groups = container.groups.all()

        # step 2 - map to content
        vertices = [self._to_vertex(node) for node in vertices]
        ports = [self._to_primitive(node, structures.Port) for node in ports]
        edges = [
            structures.Edge(start=start.uid, end=end.uid, meta=edge.meta_)
            for (start, edge, end) in edges
        ]
        groups = [self._to_primitive(node, structures.Group) for node in groups]

        return structures.Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )


class _Deprecator:
    """Deletes deprecated content of a container."""

    @staticmethod
    def _delete_deprecated_vertices_groups_ports(
        container: models.Container, content: structures.Content
    ):
        """Delete vertices, groups and ports from the container not in the content."""

        # query uids of primitive nodes (vertices, groups, ports) in the container
        uid2node = {}

        for vertex in container.vertices.all():
            uid2node[vertex.uid] = vertex

            for port in vertex.ports.all():
                uid2node[port.uid] = port

        for group in container.groups.all():
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
        container: models.Container, content: structures.Content
    ):
        """Delete edges from the container not in the content."""

        current_uids = set((op.uid, ip.uid) for op, _, ip in container.edges)
        new_uids = set(edge.uid for edge in content.edges)
        deprecated_uids = current_uids - new_uids

        neomodel.db.cypher_query(
            query=(
                "UNWIND $list AS pair "
                "MATCH ({uid: pair[0]}) "
                f" -[r:{RELATION_TYPES.edge}]-> "
                "({uid: pair[1]}) "
                "DELETE r"
            ),
            params={"list": list(map(list, deprecated_uids))},
        )

        return deprecated_uids

    def delete_difference(
        self, container: models.Container, content: structures.Content
    ):
        """Delete entities from the container that are not in the content."""

        self._delete_deprecated_vertices_groups_ports(container, content)
        self._delete_deprecated_edges(container, content)


class _Merger:
    """Merges content entities."""

    @dataclass(frozen=True)
    class MergedResult:
        """Lightweight container for merged entities."""

        __slots__ = ["vertices", "ports", "edges", "groups"]
        vertices: Sequence[models.Vertex]
        ports: Sequence[models.Port]
        edges: Sequence[models.EdgeRel]
        groups: Sequence[models.Group]

    @staticmethod
    def _merge_ports(ports: Iterable[structures.Port]):
        # FIXME possible clash between user-defined property name and uid/meta_ key
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
            rel = connect_if_not_connected(output_port.neighbor, input_port)
            rel.meta_ = edge.meta  # over-write metadata
            rel.save()
            relations.append(rel)

        return relations

    @staticmethod
    def _merge_vertices(
        vertices: Iterable[structures.Vertex],
        uid2port: Mapping[structures.ID, models.Port],
    ) -> List[models.Vertex]:
        nodes = []

        for vertex in vertices:
            # FIXME possible clash between user-defined property name and uid/meta_ key
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

    def merge(self, content: structures.Content):
        """Merge content entities."""

        ports = self._merge_ports(content.ports)
        uid2port = {port.uid: port for port in ports}
        edges = self._merge_edges(content.edges, uid2port)
        vertices = self._merge_vertices(content.vertices, uid2port)
        groups = self._merge_groups(content.groups)

        return self.MergedResult(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )


class Manager:
    """Handles read and write operations on the container's content."""

    def __init__(self) -> None:
        self._reader = _Reader()
        self._deprecator = _Deprecator()
        self._merger = _Merger()

    def read(self, container: models.Container):
        """Return the content of a given container."""

        return self._reader.read(container)

    def replace(self, container: models.Container, content: structures.Content):
        """Replace the content of a given container."""

        # content pre-conditions (referential integrity within the content):
        # - for each edge, start (output) & end (input) ports exist in content
        # - for each vertex, all ports exist in content
        self._deprecator.delete_difference(container, content)
        # TODO does not replace old properties
        # TODO possible clashes between structured and user-defined properties
        result = self._merger.merge(content)
        # TODO leaves existing connections to different containers
        reconnect_to_container(container, result.vertices, result.groups)

    def reconnect(self, parent: models.Container, child: models.Container):
        """Reconnect the content of a child container to parent."""

        reconnect_to_container(parent, child.vertices, child.groups)
