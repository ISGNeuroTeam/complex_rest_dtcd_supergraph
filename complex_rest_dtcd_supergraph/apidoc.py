"""
Utilities for drf-spectacular OpenAPI scheme generation.
"""

from types import SimpleNamespace

from drf_spectacular.utils import extend_schema
from rest_framework import status

from rest.serializers import ResponseSerializer

from .serializers import (
    FragmentSerializer,
    RootSerializer,
    ContentSerializer,
)

# ----------------------------------------------------------------------
# Serializers for custom responses
# ----------------------------------------------------------------------

# TODO why do you need all this stuff?
class SingleFragmentResponseSerializer(ResponseSerializer):
    fragment = FragmentSerializer()


class MultipleFragmentResponseSerializer(ResponseSerializer):
    fragments = FragmentSerializer(many=True)


class SingleRootResponseSerializer(ResponseSerializer):
    root = RootSerializer()


class MultipleRootResponseSerializer(ResponseSerializer):
    roots = RootSerializer(many=True)


class GraphResponseSerializer(ResponseSerializer):
    graph = ContentSerializer()


# ----------------------------------------------------------------------
# Decorators for views
# ----------------------------------------------------------------------
ApiDoc = SimpleNamespace()

ApiDoc.RootList = SimpleNamespace()
ApiDoc.RootList.get = extend_schema(
    request=None,
    responses=MultipleRootResponseSerializer,
    summary="Retrieve a list of roots",
    description="Retrieve a list of existing roots.",
    examples=None,
)
ApiDoc.RootList.post = extend_schema(
    request=RootSerializer,
    responses={
        201: SingleRootResponseSerializer,
        400: None,
    },
    summary="Create a new root",
    description="Create a new root.",
    examples=None,
)
