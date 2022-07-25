"""
This module provides custom utility functions.
"""

import uuid

import neomodel
from rest_framework.exceptions import NotFound


# custom Django path converters
# https://docs.djangoproject.com/en/4.0/topics/http/urls/#registering-custom-path-converters
class HexUUIDConverter:
    """Matches/converts a UUID from/to a string of 32 hexadecimal digits."""

    regex = "[0-9a-f]{32}"

    def to_python(self, value: str):
        return uuid.UUID(value)

    def to_url(self, value: str):
        return str(value)


# shortcuts for working with Neomodel
# a la https://docs.djangoproject.com/en/4.0/topics/http/shortcuts/
def get_node_or_404(
    model: neomodel.StructuredNode, lazy=False, **kwargs
) -> neomodel.StructuredNode:
    """Call `.nodes.get()` on a given node.

    Raises `rest_framework.exceptions.NotFound` if a node is missing.
    """

    try:
        return model.nodes.get(lazy=lazy, **kwargs)
    except neomodel.DoesNotExist:
        raise NotFound
