"""
This module provides custom utility functions.
"""

import uuid
from typing import (
    Dict,
    Generator,
    Iterable,
    Sequence,
)

import neomodel
from neomodel import contrib

from .settings import KEYS


# allowed property types in neo4j
# see https://neo4j.com/docs/cypher-manual/current/syntax/values/#property-types
# TODO date, time, datetime, point, etc.
PROPERTY_TYPES = (int, float, str, bool)


# custom Django path converters
# https://docs.djangoproject.com/en/4.0/topics/http/urls/#registering-custom-path-converters
class HexUUIDConverter:
    """Matches/converts a UUID from/to a string of 32 hexadecimal digits."""

    regex = "[0-9a-f]{32}"

    def to_python(self, value: str):
        return uuid.UUID(value)

    def to_url(self, value: str):
        return str(value)


def free_properties(node: contrib.SemiStructuredNode):
    """Return a dictionary with ad-hoc properties for a given node.

    Ad-hoc properties are those not specified at node's definition.
    """

    # see SemiStructuredNode.inflate, NodeMeta and PropertyManager
    defined: dict = node.defined_properties(aliases=False, rels=False)
    existing: dict = node.__properties__
    free = set(existing) - set(defined) - {"id"}

    return {key: existing[key] for key in free}


def save_properties(properties: dict, node: contrib.SemiStructuredNode):
    """Save properties dictionary on a given node."""

    for key, val in properties.items():
        setattr(node, key, val)

    return node


def connect_if_not_connected(
    manager: neomodel.RelationshipManager,
    node: neomodel.StructuredNode,
    properties: dict = None,
) -> neomodel.StructuredRel:
    """Use the relationship manager to connect a node.

    If the connection exists, return it. Otherwise, create new relation
    with the given properties and return it.
    """

    if not manager.is_connected(node):
        return manager.connect(node, properties)
    else:
        return manager.relationship(node)


def valid_property(value) -> bool:
    """
    Return `True` if the value is a valid Neo4j property, `False` otherwise.
    """

    return isinstance(value, PROPERTY_TYPES)


def homogeneous(seq: Sequence) -> bool:
    """Return `True` if all items in a sequence have the same type,
    `False` otherwise."""

    if len(seq) == 0:
        return True

    t = type(seq[0])

    return all(type(item) is t for item in seq)


def savable_as_property(value) -> bool:
    """Return `True` if the value can be stored as Neo4j property,
    `False` otherwise.

    See https://neo4j.com/docs/cypher-manual/current/syntax/values/ for
    more information on property types.
    """

    # valid property
    if valid_property(value):
        return True

    # homogeneous lists of valid properties
    if (
        isinstance(value, list)
        and all(map(valid_property, value))
        and homogeneous(value)
    ):
        return True

    # anything else is invalid
    return False


def extract_savable_properties(properties: Dict[str, dict]):
    # TODO docs
    result = {}

    for name in properties:
        data = properties[name]
        value = data.get(KEYS.value)

        if value is not None and savable_as_property(value):
            result[name] = data.pop(KEYS.value)

    return result


def restore_properties(original: dict, properties: dict):
    # TODO docs
    for name, value in properties.items():
        if name in original:  # FIXME handle this elsewhere?
            original[name][KEYS.value] = value


def get_ports(nodes: Iterable[dict]) -> Generator[dict, None, None]:
    # TODO docs
    for node in nodes:
        for port in node.get(KEYS.init_ports, []):
            yield port
