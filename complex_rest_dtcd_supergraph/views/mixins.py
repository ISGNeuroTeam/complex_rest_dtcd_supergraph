import logging

from .shortcuts import to_content_or_400, replace_or_400

logger = logging.getLogger("supergraph")


class ManagerMixin:
    converter = None
    manager = None

    def read(self, container) -> dict:
        content = self.manager.read(container)
        logger.info("Queried content: " + content.info)
        data = self.converter.to_data(content)

        return data

    def replace(self, container, data: dict):
        new_content = to_content_or_400(self.converter, data)
        logger.info("Converted to content: " + new_content.info)
        replace_or_400(self.manager, container, new_content)
