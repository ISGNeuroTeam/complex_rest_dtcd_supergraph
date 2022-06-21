"""
Helper module with custom Cypher clauses.

Object-based functionality of py2neo is limited, so we need to use raw
queries to do stuff on custom structures. Queries can get big and
complicated quickly; we also re-use some of them in different places.
This module is a collection of such queries.
"""

from py2neo.cypher import cypher_join

from ..settings import SCHEMA


LABELS = SCHEMA["labels"]
TYPES = SCHEMA["types"]
data_tree_relationship_types = "|".join(
    [
        TYPES["has_attribute"],
        TYPES["contains_item"],
    ]
)

# TODO table-driven methods?
# TODO explain what each clause is used for
# TODO documentation? what variables you get? templates?
MATCH_FRAGMENT, _ = cypher_join(
    "MATCH (fragment:{})".format(LABELS["fragment"]),
    "WHERE id(fragment) = $id",
)

MATCH_ENTITIES, _ = cypher_join(
    f"MATCH (fragment) -[:{TYPES['contains_entity']}]-> (entity:{LABELS['entity']})",
)

MATCH_DATA, _ = cypher_join(
    f"OPTIONAL MATCH p = (entity) -[:{TYPES['has_data']}]-> (:{LABELS['data']})",
    f"-[:{data_tree_relationship_types}*0..]-> (descendant)",
)

RETURN_NODES, _ = cypher_join(
    "UNWIND nodes(p) AS n",
    "RETURN DISTINCT n",
)

_FINAL = ", ".join(
    [
        "id(startNode(r)) AS start_id",
        "id(endNode(r)) AS end_id",
        "type(r) AS `type`",
        "properties(r) AS `properties`",
    ]
)

RETURN_RELATIONSHIPS, _ = cypher_join(
    "UNWIND relationships(p) AS r",
    "WITH DISTINCT r AS r",
    "RETURN",
    _FINAL,
)

DELETE_DESCENDANTS, _ = cypher_join(
    "MATCH (fragment) -[*1..]-> (descendant)",
    "WITH DISTINCT descendant AS d",
    "DETACH DELETE d",
)

DELETE_NODES, _ = cypher_join(
    "UNWIND nodes(p) AS n",
    "WITH DISTINCT n AS n",
    "DETACH DELETE n",
)
