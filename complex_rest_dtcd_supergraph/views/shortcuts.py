import logging
from typing import Union

import neomodel
from rest_framework.exceptions import NotFound

from ..exceptions import LoadingError, ManagerError


logger = logging.getLogger("complex_rest_dtcd_supergraph")


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
        logger.error("Error: \n" + str(e))
        raise exception


def to_content_or_400(converter, data):
    """Try to use the converter to convert the data to content.

    Calls `converter.to_content(data)` and returns the result. Raises
    `LoadingError` on exception and logs it.
    """

    # FIXME too broad of an exception
    try:
        return converter.to_content(data)
    except Exception as e:
        logger.error("Loading error: \n" + str(e))
        raise LoadingError


def replace_or_400(manager, container, new_content):
    """Try to use the manager to replace the content of a container with new one.

    Calls `manager.replace(container, content)` and returns the result.
    Raises `Manager` on exception and logs it.
    """

    # FIXME too broad of an exception
    try:
        return manager.replace(container, new_content)
    except Exception as e:
        logger.error("Manager error: \n" + str(e))
        raise ManagerError
