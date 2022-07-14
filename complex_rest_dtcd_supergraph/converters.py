"""
This module contains converter classes.

They help to translate parts of our domain model between Python objects
and Neo4j-comptabile structures.
"""

from itertools import chain
from typing import List, Tuple

from neotools.serializers import RecursiveSerializer
from neotools.structures import Tree
from py2neo import Node, Relationship, Subgraph

from .settings import SCHEMA


class Loader:
    """A class that supports loading of data structures as subgraphs.

    Uses `RecursiveSerializer` to load nested Python containers.
    """

    def __init__(self, config):
        # TODO better config management: split into keys / labels / types?
        self._c = config
        self._serializer = RecursiveSerializer(config=config)
        # keep track of loaded nodes & rels
        self._nodes = []
        self._relationships = []
        self._id2root = {}

    def _clear(self):
        self._nodes.clear()
        self._relationships.clear()
        self._id2root.clear()

    def _save_tree(self, tree: Tree):
        """Save tree nodes & rels."""

        self._nodes.extend(tree.subgraph.nodes)
        self._relationships.extend(tree.subgraph.relationships)

    def _map(self, root: Node):
        """Remember id:root pair."""

        id_ = root[self._c["keys"]["yfiles_id"]]
        self._id2root[id_] = root

    def _load_data(self, data: dict) -> Tree:
        """Recursively construct a tree from data."""

        tree = self._serializer.load(data)
        tree.root.add_label(self._c["labels"]["data"])
        return tree

    def _entity(self, data: dict) -> Tree:
        """Recursively construct entity tree."""

        # create root Entity node
        root = Node(self._c["labels"]["entity"])
        # load data for this entity
        data_tree = self._load_data(data)
        # link data to root node
        type_ = self._c["types"]["has_data"]
        r = Relationship(root, type_, data_tree.root)
        return Tree(root, data_tree.subgraph | r)

    def _vertex(self, data: dict) -> Tree:
        """Recursively construct vertex tree."""

        tree = self._entity(data)
        # remember vertex id on root Entity node
        id_key = self._c["keys"]["yfiles_id"]
        tree.root[id_key] = data[id_key]
        tree.root.add_label(self._c["labels"]["node"])
        return tree

    def _edge(self, data: dict) -> Tree:
        """Recursively construct edge tree."""

        tree = self._entity(data)
        root = tree.root
        root.add_label(self._c["labels"]["edge"])

        src_node = self._c["keys"]["source_node"]
        root[src_node] = data[src_node]

        src_port = self._c["keys"]["source_port"]
        root[src_port] = data[src_port]

        tgt_node = self._c["keys"]["target_node"]
        root[tgt_node] = data[tgt_node]

        tgt_port = self._c["keys"]["target_port"]
        root[tgt_port] = data[tgt_port]

        return tree

    def _link_edge_root(self, root: Node):
        # links src --> edge root --> tgt
        src_id = root[self._c["keys"]["source_node"]]
        src = self._id2root[src_id]
        r1 = Relationship(src, self._c["types"]["out"], root)

        tgt_id = root[self._c["keys"]["target_node"]]
        tgt = self._id2root[tgt_id]
        r2 = Relationship(root, self._c["types"]["in"], tgt)

        self._relationships.extend((r1, r2))

    def _group(self, data: dict) -> Tree:
        # group is a vertex, for now; the only difference = root label
        tree = self._vertex(data)
        tree.root.remove_label(self._c["labels"]["node"])
        tree.root.add_label(self._c["labels"]["group"])
        return tree

    def _link_parent(self, obj: dict):
        id_ = obj[self._c["keys"]["yfiles_id"]]
        parent_id = obj.get(self._c["keys"]["parent_id"])

        if parent_id is not None:
            this = self._id2root[id_]
            parent = self._id2root[parent_id]
            self._relationships.append(
                Relationship(parent, self._c["types"]["contains_entity"], this)
            )

    def load(self, data: dict) -> Subgraph:
        # assume data is valid
        # order matters here!

        self._clear()

        vertices = data[self._c["keys"]["nodes"]]
        for vertex_dict in vertices:
            # (recursively) construct root node and its (nested) properties
            tree = self._vertex(vertex_dict)
            # save nodes & rels created, remember the root to link with edges later
            self._save_tree(tree)
            self._map(tree.root)

        edges = data[self._c["keys"]["edges"]]
        for edge_dict in edges:
            tree = self._edge(edge_dict)
            self._save_tree(tree)
            self._link_edge_root(tree.root)

        # optionally add groups
        groups = data.get(self._c["keys"]["groups"], [])  # TODO hardcoded, cheeky
        for group_dict in groups:
            tree = self._group(group_dict)
            self._save_tree(tree)
            self._map(tree.root)

        # link groups and its content entities, if necessary
        for obj in chain(vertices, groups):
            self._link_parent(obj)

        return Subgraph(self._nodes, self._relationships)


class Dumper:
    """A class that supports conversion of subgraphs into data structures.

    Uses `RecursiveSerializer` to translate subgraphs into nested Python
    containers.
    """

    def __init__(self, config):
        self._c = config

    def _extract_roots(
        self, subgraph: Subgraph
    ) -> Tuple[List[Node], List[Node], List[Node]]:
        vertices, edges, groups = [], [], []

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

            # put data tree root into corresp. list
            if start.has_label(self._c["labels"]["node"]):
                vertices.append(end)
            elif start.has_label(self._c["labels"]["edge"]):
                edges.append(end)
            elif start.has_label(self._c["labels"]["group"]):
                groups.append(end)

        return vertices, edges, groups

    def dump(self, subgraph: Subgraph) -> dict:
        """Convert subgraph in a specified format to Python data structure."""

        # TODO subgraphs of incorrect format (missing VERTEX nodes / EDGE rels)
        vertices, edges, groups = self._extract_roots(subgraph)

        # O(n) + O(r), where n is node count and r is rel count
        serializer = RecursiveSerializer(subgraph=subgraph, config=self._c)

        # around O(n)
        result = {
            self._c["keys"]["nodes"]: [serializer.dump(v) for v in vertices],
            self._c["keys"]["edges"]: [serializer.dump(e) for e in edges],
        }

        # optionally add groups to the dict  TODO this is bad, but does not break tests
        if groups:
            result[self._c["keys"]["groups"]] = [serializer.dump(g) for g in groups]

        return result


class Converter:
    """Supports conversion between Python containers and Neo4j structures."""

    def __init__(self, config=SCHEMA) -> None:
        self._loader = Loader(config)
        self._dumper = Dumper(config)

    def load(self, data: dict):
        """Create a subgraph from data.

        See `docs/Format.md` for exchange format specification.

        The nodes in the created subgraph are unbound.
        See https://py2neo.org/2021.1/data/index.html#py2neo.data.Node.
        """

        return self._loader.load(data)

    def dump(self, subgraph: Subgraph):
        """Dump the subgraph to a dictionary.

        See See `docs/Format.md` for exchange format specification.
        """

        return self._dumper.dump(subgraph)
