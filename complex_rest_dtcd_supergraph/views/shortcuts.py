import logging
from typing import Union

import neomodel
from rest_framework.exceptions import NotFound

from ..exceptions import LoadingError, ManagerError
from ..settings import PLUGIN_NAME
from ..structures import Content


logger = logging.getLogger(PLUGIN_NAME)


# shortcuts for working with Neomodel
# a la https://docs.djangoproject.com/en/4.0/topics/http/shortcuts/
def get_node_or_404(
    queryset: Union[neomodel.NodeSet, neomodel.RelationshipManager], **kwargs
) -> neomodel.StructuredNode:
    """Call `.get()` on a given node set or relationship manager.

    Raises `rest_framework.exceptions.NotFound` if a node is missing.
    """

    try:
        return queryset.get(**kwargs)
    except neomodel.DoesNotExist:
        raise NotFound


def func_or_400(func, *args, exception=None, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
        raise exception


def to_content_or_400(data: dict):
    """Try to load content from data.

    Calls `Content.from_dict(data)` and returns the result. Raises
    `LoadingError` on exception and logs it.
    """

    # FIXME too broad of an exception
    try:
        return Content.from_dict(data)
    except Exception as e:
        logger.error("Loading error: %s", e, exc_info=True)
        raise LoadingError


def replace_or_400(manager, container, new_content):
    """Try to use the manager to replace the content of a container with new one.

    Calls `manager.replace(container, content)` and returns the result.
    Raises `ManagerError` on exception and logs it.
    """

    # FIXME too broad of an exception
    try:
        return manager.replace(container, new_content)
    except Exception as e:
        logger.error("Manager error: %s", e, exc_info=True)
        raise ManagerError
