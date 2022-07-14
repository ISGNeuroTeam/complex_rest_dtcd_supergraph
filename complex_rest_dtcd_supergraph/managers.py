"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from itertools import chain
from typing import List, Set, Tuple, Union

from py2neo import Graph, Node, Relationship, Subgraph, Transaction
from py2neo import ogm
from py2neo.cypher import cypher_join

from . import clauses
from .exceptions import (
    FragmentDoesNotBelongToGraph,
    FragmentIsNotBound,
)
from .models import Fragment
from .settings import SCHEMA
from .utils import filter_nodes, match_nodes, subgraph_from_match_clause


# TODO custom type aliases
FragmentID = int

KEYS = SCHEMA["keys"]
LABELS = SCHEMA["labels"]
TYPES = SCHEMA["types"]


class Neo4jGraphManager:
    """Interface to Neo4j operations."""

    def __init__(self, profile: str, name: str = None, **settings):
        self._graph = Graph(profile, name, **settings)
        # TODO make sure graph is available
        self._fragment_manager = FragmentManager(self._graph)

    def clear(self):
        """Remove all nodes and relationships from managed graph."""

        self._graph.delete_all()

    @property
    def fragments(self):
        """Fragment manager for this graph."""

        return self._fragment_manager


class FragmentManager:
    """ADT for fragment and content management."""

    def __init__(self, graph: Graph):
        self._graph = graph
        self._repo = ogm.Repository.wrap(self._graph)  # ogm management
        # content manager works on the same graph
        self._content_manager = ContentManager(self._graph)

    def all(self) -> List[Fragment]:
        """Return a list of all fragments."""
        return Fragment.match(self._repo).all()

    def get(self, fragment_id: int) -> Union[Fragment, None]:
        """Return a fragment with given id if it exists, None otherwise."""
        return self._repo.get(Fragment, fragment_id)

    def save(self, *fragments: Fragment):
        """Save local fragments into the repository.

        Creates or updates fragments depending on if they exist in the
        database.
        """
        self._repo.save(*fragments)

    def remove(self, fragment: Fragment):
        """Remove fragment and its content."""

        # TODO separate txs
        self.content.remove(fragment)
        self._repo.delete(fragment)

    # TODO clear method

    @property
    def content(self):
        """Content manager for this graph."""
        return self._content_manager


class ContentManager:
    """ADT for management of fragment's content."""

    def __init__(self, graph: Graph):
        self._graph = graph

    def _validate(self, fragment: Fragment):
        """Validate the given fragment.

        - Raise `FragmentIsNotBound` exception if a fragment is not bound.
        - Raise `FragmentDoesNotBelongToGraph` if fragment's graph is
            different from this one.
        """

        if fragment.__primaryvalue__ is None:
            raise FragmentIsNotBound
        if fragment.__node__.graph != self._graph:
            raise FragmentDoesNotBelongToGraph

    @staticmethod
    def _match_entity_trees_clause(fragment_id: int = None) -> Tuple[str, dict]:
        """Prepare Cypher clause and params to match graph's content.

        If `fragment_id` is provided, then match entities, their trees
        and relationships between them from a given fragment. Otherwise,
        match all content.
        """

        # TODO does not match (entity) --> (entity) relationships
        # case 1: match all entities
        if fragment_id is None:
            label = LABELS["entity"]
            return cypher_join(
                f"MATCH (entity:{label})",
                clauses.MATCH_DATA,
            )
        # case 2: match entities of a given fragment
        else:
            return cypher_join(
                clauses.MATCH_FRAGMENT,
                clauses.MATCH_ENTITIES,
                clauses.MATCH_DATA,
                id=fragment_id,
            )

    def _nodes(self, tx: Transaction, fragment_id: int = None) -> Set[Node]:
        """
        Return a set of content nodes.

        If `fragment_id` is provided, then match nodes from a given
        fragment. Otherwise, match all content nodes.
        """

        match_clause, params = self._match_entity_trees_clause(fragment_id)
        cursor = match_nodes(tx, match_clause, **params)
        return set(record[0] for record in cursor)

    def _all(self, tx: Transaction) -> Subgraph:
        """Return bound subgraph with content."""

        match_clause, params = self._match_entity_trees_clause()
        return subgraph_from_match_clause(tx, match_clause, **params)

    def _get(self, tx: Transaction, fragment: Fragment) -> Subgraph:
        """Return bound subgraph with content of a given fragment."""

        self._validate(fragment)
        fragment_id = fragment.__primaryvalue__
        match_clause, params = self._match_entity_trees_clause(fragment_id)
        return subgraph_from_match_clause(tx, match_clause, **params)

    def read(self, fragment: Fragment = None) -> Subgraph:
        """Return a bound subgraph with content.

        If a fragment is given, then content belongs to the given fragment.
        Otherwise, returns full content.
        """

        tx = self._graph.begin(readonly=True)

        if fragment is None:
            subgraph = self._all(tx)
        else:
            subgraph = self._get(tx, fragment)

        self._graph.commit(tx)

        return subgraph

    @staticmethod
    def _merge_vertices(tx: Transaction, subgraph: Subgraph) -> Set[Node]:
        """Merge Vertex nodes from subgraph, return a set of merged nodes."""

        # merge vertex roots on (label, yfiles_id)
        label = LABELS["node"]
        vertices = filter_nodes(subgraph, label)  # O(n)
        key = KEYS["yfiles_id"]
        subgraph = Subgraph(vertices)  # TODO better way to return merged nodes?
        tx.merge(subgraph, label, key)

        return set(subgraph.nodes)

    @staticmethod
    def _merge_edges(tx: Transaction, subgraph: Subgraph) -> Set[Node]:
        """Merge Edge nodes from subgraph, return a set of merged nodes."""
        label = LABELS["edge"]
        edges = filter_nodes(subgraph, label)  # O(n)
        keys = tuple(
            KEYS[key]
            for key in ("source_node", "source_port", "target_node", "target_port")
        )
        subgraph = Subgraph(edges)  # TODO better way to return merged nodes?
        tx.merge(subgraph, label, keys)

        return set(subgraph.nodes)

    @staticmethod
    def _merge_groups(tx: Transaction, subgraph: Subgraph) -> Set[Node]:
        """Merge Group nodes from subgraph, return a set of merged nodes."""

        label = LABELS["group"]
        groups = filter_nodes(subgraph, label)  # O(n)
        key = KEYS["yfiles_id"]
        subgraph = Subgraph(groups)
        tx.merge(subgraph, label, key)

        return set(subgraph.nodes)

    def _merge(self, tx: Transaction, subgraph: Subgraph, fragment: Fragment = None):
        """Merge given subgraph into the fragment.

        We want to preserve connections (edges and frontier vertices)
        between fragments. The merge is made as follows:

        1. Merge roots of the following entity trees:
            1. vertices
            2. edges
            3. groups
        2. Remove old nodes & relationships.
        3. Re-link fragment with new entities to be created.
        4. Merge the rest and fragment-entity links.
        """

        # FIXME this procedure fails when adding existing entities
        # outside current fragment
        # merge tree roots = preserve relationships
        vertices = self._merge_vertices(tx, subgraph)
        edges = self._merge_edges(tx, subgraph)
        groups = self._merge_groups(tx, subgraph)

        # delete outdated nodes
        if fragment is not None:
            current = self._nodes(tx, fragment.__primaryvalue__)
        else:
            current = self._nodes(tx)
        old = current - vertices - edges - groups
        tx.delete(Subgraph(old))

        # re-link fragment to subgraph entities (roots of their trees)
        if fragment is not None:
            root = fragment.__node__
            type_ = TYPES["contains_entity"]
            links = set(
                Relationship(root, type_, entity)
                for entity in chain(vertices, edges, groups)
            )
        else:
            links = []

        # create the rest of the subgraph & fragment-entity links
        # skips existing nodes & relationships
        tx.create(subgraph | Subgraph(relationships=links))

    def replace(self, subgraph: Subgraph, fragment: Fragment = None):
        """Replace old content of a fragment with a new one.

        Merges existing and deletes old nodes, binds subgraph nodes on
        success.
        If `fragment` is provided, then replace content from a given
        fragment. Otherwise, replace the whole content.
        """

        # TODO error handling? (non-bound fragment, empty, bad format / input)
        if fragment is not None:
            self._validate(fragment)

        tx = self._graph.begin()
        self._merge(tx, subgraph, fragment)
        self._graph.commit(tx)

    def remove(self, fragment: Fragment):
        """Remove content of a given fragment.

        Does not remove fragment root node.
        """

        self._validate(fragment)
        fragment_id = fragment.__primaryvalue__
        match_clause, params = self._match_entity_trees_clause(fragment_id)
        q, params = cypher_join(
            match_clause,
            clauses.DELETE_NODES,
            **params,
        )
        self._graph.update(q, params)

    def clear(self):
        """Remove all content from this graph."""

        match_content, _ = self._match_entity_trees_clause()
        q, _ = cypher_join(
            match_content,
            clauses.DELETE_NODES,
        )
        self._graph.update(q)

    def empty(self, fragment: Fragment) -> bool:
        """Return True if fragment's content is empty, False otherwise."""

        self._validate(fragment)
        # empty if there are no links to entities
        n = fragment.__node__
        link = self._graph.match_one((n,), r_type=TYPES["contains_entity"])

        return link is None
