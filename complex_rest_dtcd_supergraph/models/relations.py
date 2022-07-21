"""
Relationship classes for neomodel.
"""

from types import SimpleNamespace

from neomodel import JSONProperty, StructuredRel


# settings
RELATION_TYPES = SimpleNamespace()
RELATION_TYPES.contains = "CONTAINS"
RELATION_TYPES.default = "CONN"
RELATION_TYPES.edge = "EDGE"


class EdgeRel(StructuredRel):
    """An edge between the ports of vertices."""

    # TODO this is semi-structured too
    data = JSONProperty()
