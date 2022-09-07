"""
Management operations for containers and their content.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.

WARNING: be careful with cyclic imports.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, List, Mapping, Sequence

import neomodel

from rest_auth.authorization import check_authorization

from . import nodes
from .. import structures
from ..settings import ROLE_MODEL_ACTION_NAMES as ACTION_NAMES
from ..utils import connect_if_not_connected, free_properties
from .relations import RELATION_TYPES


def reconnect_to_container(
    container: "nodes.Container",
    vertices: Iterable["nodes.Vertex"],
    groups: Iterable["nodes.Group"],
):
    """Connect vertices and groups to a given container."""

    for vertex in vertices:
        connect_if_not_connected(container.vertices, vertex)

    for group in groups:
        connect_if_not_connected(container.groups, group)


class Reader:
    """Read operations on a container."""

    @staticmethod
    def _query_ports(vertices: Iterable["nodes.Vertex"]):
        ports: List["nodes.Port"] = []
        vertex2ports = defaultdict(set)  # parent:children uid pairs

        for vertex in vertices:
            for port in vertex.ports.all():
                ports.append(port)
                vertex2ports[vertex.uid].add(port.uid)

        return ports, vertex2ports

    @staticmethod
    def _to_primitive(node: "nodes.AbstractPrimitive", subclass):
        uid = node.uid
        properties = free_properties(node)
        meta = node.meta_

        return subclass(uid=uid, properties=properties, meta=meta)

    @classmethod
    def _to_vertex(cls, node: "nodes.Vertex", vertex2ports):
        vertex = cls._to_primitive(node, subclass=structures.Vertex)

        # populate ports mappings
        for port_id in vertex2ports.get(vertex.uid, []):
            vertex.ports.add(port_id)

        return vertex

    @classmethod
    def read(cls, container: "nodes.Container") -> structures.Content:
        """Query and return the content of a given container."""

        # step 1 - get the insides
        vertices = container.vertices.all()
        # TODO role model permission check here is very bad
        for vertex in vertices:
            check_authorization(vertex, ACTION_NAMES.read)
        ports, vertex2ports = cls._query_ports(vertices)
        edges = container.edges
        groups = container.groups.all()

        # step 2 - map to content
        # TODO move conversion to structures, leave populate_ports here?
        vertices = [cls._to_vertex(node, vertex2ports) for node in vertices]
        ports = [cls._to_primitive(node, structures.Port) for node in ports]
        edges = [
            structures.Edge(start=start.uid, end=end.uid, meta=edge.meta_)
            for (start, edge, end) in edges
        ]
        groups = [cls._to_primitive(node, structures.Group) for node in groups]

        return structures.Content(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )


class Deprecator:
    """Deletes deprecated content of a container."""

    @staticmethod
    def _delete_deprecated_vertices_groups_ports(
        container: "nodes.Container", content: structures.Content
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
        container: "nodes.Container", content: structures.Content
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

    @classmethod
    def delete_difference(
        cls, container: "nodes.Container", content: structures.Content
    ):
        """Delete entities from the container that are not in the content."""

        cls._delete_deprecated_vertices_groups_ports(container, content)
        cls._delete_deprecated_edges(container, content)


class Merger:
    """Merges content entities."""

    @dataclass(frozen=True)
    class MergedResult:
        """Lightweight container for merged entities."""

        __slots__ = ["vertices", "ports", "edges", "groups"]
        vertices: Sequence["nodes.Vertex"]
        ports: Sequence["nodes.Port"]
        edges: Sequence["nodes.EdgeRel"]
        groups: Sequence["nodes.Group"]

    @staticmethod
    def _merge_ports(ports: Iterable[structures.Port]):
        # FIXME possible clash between user-defined property name and uid/meta_ key
        data = [
            dict(uid=port.uid, meta_=port.meta, **port.properties) for port in ports
        ]

        return nodes.Port.create_or_update(*data)

    @staticmethod
    def _merge_edges(
        edges: Iterable[structures.Edge],
        uid2port: Mapping[structures.ID, "nodes.Port"],
    ) -> List["nodes.EdgeRel"]:
        result = []

        for edge in edges:
            output_port = uid2port[edge.start]
            input_port = uid2port[edge.end]
            rel = connect_if_not_connected(output_port.neighbor, input_port)
            rel.meta_ = edge.meta  # over-write metadata
            rel.save()
            result.append(rel)

        return result

    @staticmethod
    def _merge_vertices(
        vertices: Iterable[structures.Vertex],
        uid2port: Mapping[structures.ID, "nodes.Port"],
    ) -> List["nodes.Vertex"]:
        result = []

        # NOTE we may try to set the owner here, but this is tricky
        for vertex in vertices:
            # FIXME possible clash between user-defined property name and uid/meta_ key
            node = nodes.Vertex.create_or_update(
                dict(uid=vertex.uid, meta_=vertex.meta, **vertex.properties),
                lazy=True,
            )[0]
            result.append(node)

            # connect this vertex to ports
            for uid in vertex.ports:
                port = uid2port[uid]
                connect_if_not_connected(node.ports, port)

        return result

    @staticmethod
    def _merge_groups(groups: Iterable[structures.Group]):
        data = [dict(uid=group.uid, meta_=group.meta) for group in groups]

        return nodes.Group.create_or_update(*data, lazy=True)

    @classmethod
    def merge(cls, content: structures.Content):
        """Merge content entities."""

        ports = cls._merge_ports(content.ports)
        uid2port = {port.uid: port for port in ports}
        edges = cls._merge_edges(content.edges, uid2port)
        vertices = cls._merge_vertices(content.vertices, uid2port)
        groups = cls._merge_groups(content.groups)

        return cls.MergedResult(
            vertices=vertices,
            ports=ports,
            edges=edges,
            groups=groups,
        )
