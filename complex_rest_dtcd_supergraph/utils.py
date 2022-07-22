"""
This module provides custom utility functions for working with Cypher.
"""

from typing import Generator

from py2neo import Node, Relationship, Subgraph, Transaction
from py2neo.cypher import Cursor, cypher_join

from . import clauses


def filter_nodes(subgraph: Subgraph, label: str) -> Generator[Node, None, None]:
    """Construct an iterator over subgraph nodes with the given label."""
    return (x for x in subgraph.nodes if x.has_label(label))


def match_nodes(tx: Transaction, match_clause: str, **params) -> Cursor:
    """Run Cypher query and return a cursor over node records.

    Uses provided match clause to construct a query. The clause itself
    must have a `p` pattern variable representing a path with nodes &
    relationships we are interested in.
    """

    # match clause must have 'p' pattern variable representing a path with
    # nodes & relationships we are interested in
    q, params = cypher_join(match_clause, clauses.RETURN_NODES, **params)
    return tx.run(q, params)


def match_relationships(tx: Transaction, match_clause: str, **params) -> Cursor:
    """Run Cypher query and return a cursor over relationship records.

    Uses provided match clause to construct a query. The clause itself
    must have a `p` pattern variable representing a path with nodes &
    relationships we are interested in.

    The records have the following keys:
    - `start_id`
    - `end_id`
    - `type`
    - `properties`
    """

    q, params = cypher_join(match_clause, clauses.RETURN_RELATIONSHIPS, **params)
    return tx.run(q, params)


def subgraph(nodes_cursor: Cursor, relationships_cursor: Cursor) -> Subgraph:
    """Return bound subgraph from cursors.

    Relationship records must reference nodes from node cursor.
    """

    # nodes
    nodes = set(record[0] for record in nodes_cursor)
    id2node = {node.identity: node for node in nodes}

    # relationships
    # workaround: py2neo sucks at efficient conversion of rels to Subgraph
    # manually construct Relationships
    relationships = []

    for record in relationships_cursor:
        start_node = id2node[record["start_id"]]
        end_node = id2node[record["end_id"]]
        type_ = record["type"]
        properties = record.get("properties", {})
        relationships.append(Relationship(start_node, type_, end_node, **properties))

    return Subgraph(id2node.values(), relationships)


def subgraph_from_match_clause(
    tx: Transaction, match_clause: str, **params
) -> Subgraph:
    """Run Cypher query using the provided clause and return a subgraph.

    Uses provided match clause to construct a query for nodes &
    relationships. The clause itself must have a `p` pattern variable
    representing a path with nodes & relationships we are interested in.
    """

    nodes_cursor = match_nodes(tx, match_clause, **params)
    rels_cursor = match_relationships(tx, match_clause, **params)
    return subgraph(nodes_cursor, rels_cursor)
