from typing import Mapping

from neotools.serializers import RecursiveSerializer
from neotools.structures import Tree
from py2neo import Node, Relationship, Subgraph

from ..settings import SCHEMA


class Converter:
    """ADT for data serialization to/from specified exchange formats."""

    def __init__(self, config: Mapping[str, Mapping[str, str]] = SCHEMA) -> None:
        self._c = config
        self._loader = RecursiveSerializer(config=config)

    def _load_data(self, data: dict) -> Tree:
        """Recursively construct a tree from data."""

        tree = self._loader.load(data)
        tree.root.add_label(self._c["labels"]["data"])

        return tree

    def _load_entity(self, data: dict) -> Tree:
        """Recursively construct entity tree."""

        # create root Entity node
        root = Node(self._c["labels"]["entity"])

        # load data for this entity
        data_tree = self._load_data(data)

        # link data to root node
        type_ = self._c["types"]["has_data"]
        r = Relationship(root, type_, data_tree.root)

        return Tree(root, data_tree.subgraph | r)

    def _load_vertex(self, vertex_dict: dict) -> Tree:
        """Recursively construct vertex tree."""

        tree = self._load_entity(vertex_dict)
        # remember vertex id on root Entity node
        id_key = self._c["keys"]["yfiles_id"]
        tree.root[id_key] = vertex_dict[id_key]
        tree.root.add_label(self._c["labels"]["node"])

        return tree

    def _load_edge(self, edge_dict: dict) -> Tree:
        """Recursively construct edge tree."""

        tree = self._load_entity(edge_dict)
        root = tree.root
        root.add_label(self._c["labels"]["edge"])

        src_node = self._c["keys"]["source_node"]
        root[src_node] = edge_dict[src_node]

        src_port = self._c["keys"]["source_port"]
        root[src_port] = edge_dict[src_port]

        tgt_node = self._c["keys"]["target_node"]
        root[tgt_node] = edge_dict[tgt_node]

        tgt_port = self._c["keys"]["target_port"]
        root[tgt_port] = edge_dict[tgt_port]

        return tree

    def load(self, data: dict) -> Subgraph:
        """Create a subgraph from data.

        See `docs/Format.md` for exchange format specification.

        The nodes in the created subgraph are unbound.
        See https://py2neo.org/2021.1/data/index.html#py2neo.data.Node.
        """

        nodes, rels = [], []
        id2root = {}

        # yfiles nodes
        for vertex_dict in data[self._c["keys"]["nodes"]]:
            # (recursively) construct root node and its (nested) properties
            vertex_tree = self._load_vertex(vertex_dict)
            # save nodes & rels created
            nodes.extend(vertex_tree.subgraph.nodes)
            rels.extend(vertex_tree.subgraph.relationships)
            # remember the root to link with edges later
            id_ = vertex_dict[self._c["keys"]["yfiles_id"]]
            id2root[id_] = vertex_tree.root

        # yfiles edges
        for edge_dict in data[self._c["keys"]["edges"]]:
            edge_tree = self._load_edge(edge_dict)
            nodes.extend(edge_tree.subgraph.nodes)
            rels.extend(edge_tree.subgraph.relationships)
            # link the edge with src and tgt nodes
            # TODO what happens if src / tgt node ids are not in nodes?
            e = edge_tree.root
            src = id2root[e[self._c["keys"]["source_node"]]]
            tgt = id2root[e[self._c["keys"]["target_node"]]]
            r1 = Relationship(src, self._c["types"]["out"], e)
            r2 = Relationship(e, self._c["types"]["in"], tgt)
            rels.extend((r1, r2))

        return Subgraph(nodes, rels)

    def dump(self, subgraph: Subgraph) -> dict:
        """Dump the subgraph to a dictionary.

        See See `docs/Format.md` for exchange format specification.
        """

        # TODO subgraphs of incorrect format (missing VERTEX nodes / EDGE rels)
        vertices, edges = [], []

        # TODO better way to recursively re-construct initial dict from data?

        # look for rels between entity roots and data nodes
        # O(r), where r is rel count
        for r in subgraph.relationships:
            start = r.start_node  # entity tree root
            end = r.end_node  # data tree root

            # make sure this is a rel between entity root and its data tree
            if not (
                start.has_label(self._c["labels"]["entity"])
                and end.has_label(self._c["labels"]["data"])
            ):
                continue

            # put data tree root into corresp. (vertex / edge) list
            if start.has_label(self._c["labels"]["node"]):
                vertices.append(end)
            elif start.has_label(self._c["labels"]["edge"]):
                edges.append(end)

        # O(n) + O(r), where n is node count and r is rel count
        serializer = RecursiveSerializer(subgraph=subgraph, config=self._c)

        # around O(n)
        result = {
            self._c["keys"]["nodes"]: [serializer.dump(v) for v in vertices],
            self._c["keys"]["edges"]: [serializer.dump(e) for e in edges],
        }

        return result
