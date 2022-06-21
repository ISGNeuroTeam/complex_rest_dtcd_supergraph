from itertools import chain
from typing import Generator, List, Set, Tuple, Union

from py2neo import Graph, Node, Relationship, Subgraph, Transaction
from py2neo import ogm
from py2neo.cypher import Cursor, cypher_join

from . import clauses
from .exceptions import (
    FragmentDoesNotBelongToGraph,
    FragmentDoesNotExist,
    FragmentIsNotBound,
)
from ..models import Fragment
from ..settings import SCHEMA

# TODO custom type aliases
FragmentID = int

KEYS = SCHEMA["keys"]
LABELS = SCHEMA["labels"]
TYPES = SCHEMA["types"]


def filter_nodes(subgraph: Subgraph, label: str) -> Generator[Node, None, None]:
    """Construct an iterator over subgraph nodes with the given label."""
    return (x for x in subgraph.nodes if x.has_label(label))


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

    def get_or_exception(self, fragment_id: int) -> Fragment:
        """Return a fragment with given id.

        Raises `FragmentDoesNotExist` if the fragment is missing.
        """

        fragment = self.get(fragment_id)

        if fragment is not None:
            return fragment
        else:
            raise FragmentDoesNotExist(f"fragment [{fragment_id}] does not exist")

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
        """Validate given fragment.

        - Raises `FragmentIsNotBound` exception if a fragment is not bound.
        - Raises `FragmentDoesNotBelongToGraph` if fragment's graph is
            different from this one.
        """

        if fragment.__primaryvalue__ is None:
            raise FragmentIsNotBound
        if fragment.__node__.graph != self._graph:
            raise FragmentDoesNotBelongToGraph

    @staticmethod
    def _match_query(fragment_id: int = None) -> Tuple[str, dict]:
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

    def _cursor(
        self, tx: Transaction, return_clause: str, fragment_id: int = None
    ) -> Cursor:
        match_clause, kwargs = self._match_query(fragment_id)
        q, params = cypher_join(match_clause, return_clause, **kwargs)
        cursor = tx.run(q, params)
        return cursor

    def _match_nodes(self, tx: Transaction, fragment_id: int = None) -> Cursor:
        return self._cursor(tx, clauses.RETURN_NODES, fragment_id)

    def _nodes(self, tx: Transaction, fragment_id: int = None) -> Set[Node]:
        """
        Return a set of content nodes.

        If `fragment_id` is provided, then match nodes from a given
        fragment. Otherwise, match all content nodes.
        """

        cursor = self._match_nodes(tx, fragment_id)
        return set(record[0] for record in cursor)

    def _match_relationships(self, tx: Transaction, fragment_id: int = None) -> Cursor:
        """
        Match content relationships.

        If `fragment_id` is provided, then match relationships from a given
        fragment. Otherwise, match all content relationships.
        """

        return self._cursor(tx, clauses.RETURN_RELATIONSHIPS, fragment_id)

    def _content(self, tx: Transaction, fragment_id: int = None) -> Subgraph:
        """Return bound subgraph with content.

        If `fragment_id` is provided, then return content subgraph from
        a given fragment. Otherwise, return the whole content.
        """

        # nodes
        nodes = self._nodes(tx, fragment_id)
        id2node = {node.identity: node for node in nodes}

        # relationships
        rels_cursor = self._match_relationships(tx, fragment_id)

        # workaround: py2neo sucks at efficient conversion of rels to Subgraph
        # manually construct Relationships
        relationships = []
        for record in rels_cursor:
            start_node = id2node[record["start_id"]]
            end_node = id2node[record["end_id"]]
            t = record["type"]
            properties = record.get("properties", {})
            relationships.append(Relationship(start_node, t, end_node, **properties))

        return Subgraph(id2node.values(), relationships)

    def get(self, fragment: Fragment = None) -> Subgraph:
        """Return bound subgraph with content.

        If `fragment` is provided, then return content subgraph from
        a given fragment. Otherwise, return the whole content.
        """

        # TODO error handling + docs
        if fragment is not None:
            self._validate(fragment)
            fragment_id = fragment.__primaryvalue__
        else:
            fragment_id = None

        tx = self._graph.begin(readonly=True)
        subgraph = self._content(tx, fragment_id)
        self._graph.commit(tx)

        return subgraph

    @staticmethod
    def _merge_vertices(tx: Transaction, subgraph: Subgraph) -> Set[Node]:
        """Merge Vertex nodes from subgraph, return a set of merged nodes."""

        # merge vertex roots on (label, yfiles_id)
        label = LABELS["node"]
        vertices = set(filter_nodes(subgraph, label))  # O(n)
        key = KEYS["yfiles_id"]
        subgraph = Subgraph(vertices)  # TODO better way to return merged nodes?
        tx.merge(subgraph, label, key)

        return set(subgraph.nodes)

    @staticmethod
    def _merge_edges(tx: Transaction, subgraph: Subgraph) -> Set[Node]:
        """Merge Edge nodes from subgraph, return a set of merged nodes."""
        label = LABELS["edge"]
        edges = set(filter_nodes(subgraph, label))  # O(n)
        keys = tuple(
            KEYS[key]
            for key in ("source_node", "source_port", "target_node", "target_port")
        )
        subgraph = Subgraph(edges)  # TODO better way to return merged nodes?
        tx.merge(subgraph, label, keys)

        return set(subgraph.nodes)

    def _merge(self, tx: Transaction, subgraph: Subgraph, fragment: Fragment = None):
        """Merge given subgraph into the fragment.

        We want to preserve connections (edges and frontier vertices)
        between fragments. The merge is made as follows:

        1. Merge entity roots:
            1. Merge root nodes of *vertex* trees.
            2. Merge root nodes of *edge* trees.
        2. Remove old content (entity roots and their trees).
        3. Re-link fragment with new entities to be created.
        4. Merge newly created entities and links.
        """

        vertices = self._merge_vertices(tx, subgraph)
        edges = self._merge_edges(tx, subgraph)

        # delete difference
        # TODO think about this more
        if fragment is not None:
            # TODO validation + docs
            self._validate(fragment)
            current = self._nodes(tx, fragment.__primaryvalue__)
        else:
            current = self._nodes(tx)
        old = current - vertices - edges
        tx.delete(Subgraph(old))

        # re-link fragment to subgraph entities (roots of vertex and edge trees)
        # entities with existing relationship are skipped
        if fragment is not None:
            root = fragment.__node__
            type_ = TYPES["contains_entity"]
            links = set(
                Relationship(root, type_, entity) for entity in chain(vertices, edges)
            )
        else:
            links = []

        # create the rest of the subgraph & fragment-entity links
        # skips already bound nodes & relationships
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
        q, params = cypher_join(
            clauses.MATCH_FRAGMENT,
            clauses.DELETE_DESCENDANTS,
            id=fragment_id,
        )
        self._graph.update(q, params)

    def clear(self):
        """Remove all content from this graph."""

        match_content = self._match_query()
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
