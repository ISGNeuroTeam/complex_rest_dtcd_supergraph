"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from .models import Fragment
from .structures import Content


class Manager:
    def read(self, fragment: Fragment) -> Content:
        # get the insides
        # map to content
        raise NotImplementedError

    def replace(self, fragment: Fragment, content: Content):
        raise NotImplementedError
