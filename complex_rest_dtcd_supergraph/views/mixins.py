import logging

from .. import models
from ..settings import PLUGIN_NAME
from .shortcuts import to_content_or_400, replace_or_400

logger = logging.getLogger(PLUGIN_NAME)


class ContainerManagementMixin:
    """Provides methods for working with containers and converting back
    and forth between domain classes and Python primitives.
    """

    def read_content_as_dict(self, container: models.Container) -> dict:
        """Read container's content as Python primitives."""

        content = container.read_content()
        logger.info("Queried content: %s", content.info)
        data = content.to_dict()

        return data

    def replace_content_from_dict(self, container: models.Container, data: dict):
        """Replace container's content with new one from data."""

        new_content = to_content_or_400(data)
        logger.info("Converted to content: %s", new_content.info)
        replace_or_400(container, new_content)
