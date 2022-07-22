"""
This module contains converter classes.
"""


class Loader:
    pass


class Dumper:
    pass


class Converter:
    """Supports conversion between Python containers and Neo4j structures."""

    def __init__(self):
        self._loader = Loader()
        self._dumper = Dumper()

    def load(self):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError
