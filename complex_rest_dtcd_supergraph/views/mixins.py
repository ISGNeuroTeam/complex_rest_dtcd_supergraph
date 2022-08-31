import logging

from .. import models
from ..settings import PLUGIN_NAME
from .shortcuts import to_content_or_400, replace_or_400

logger = logging.getLogger(PLUGIN_NAME)


class ContainerManagementMixin:
    """Provides `read` and `replace` methods for working with container
    and converting back and forth between domain classes and Python primitives.
    """

    manager = None

    def read(self, container: models.Container) -> dict:
        """Read container's content as Python primitives in correct format.

        1. Uses `manager` to query Neo4j database and get `Content` back.
        2. Uses `converter` to convert the `Content` into Python primitives.
        """

        # content = self.manager.read(container)
        content = container.read_content()
        logger.info("Queried content: %s", content.info)
        data = content.to_dict()

        return data

    def replace(self, container: models.Container, data: dict):
        """Replace container's content with new one.

        1. Uses `converter` to convert incoming data to `Content`.
        2. Uses `manager` that maps from `Content` to Neo4j database entities.
        """

        new_content = to_content_or_400(data)
        logger.info("Converted to content: %s", new_content.info)
        replace_or_400(self.manager, container, new_content)
