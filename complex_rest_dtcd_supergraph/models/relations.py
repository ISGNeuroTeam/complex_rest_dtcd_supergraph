"""
Relationship classes from neomodel.
"""

from types import SimpleNamespace

from neomodel import JSONProperty, StructuredRel


# settings
RELATION_TYPES = SimpleNamespace()
RELATION_TYPES.contains = "CONTAINS"
RELATION_TYPES.default = "CONN"  # TODO better name?
RELATION_TYPES.edge = "EDGE"


class EdgeRel(StructuredRel):
    """An edge between the ports of vertices."""

    # TODO this must be semi-structured too
    meta_ = JSONProperty()
