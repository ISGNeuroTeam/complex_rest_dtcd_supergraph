"""
Utilities for drf-spectacular OpenAPI scheme generation.
"""

from types import SimpleNamespace

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from rest.serializers import ResponseSerializer

from .serializers import (
    FragmentSerializer,
    RootSerializer,
    ContentSerializer,
)


RESPONSES = SimpleNamespace()
RESPONSES.HTTP_400_BAD_REQUEST = OpenApiResponse(description="Bad request.")
RESPONSES.HTTP_404_NOT_FOUND = OpenApiResponse(description="Resource is missing.")


# ----------------------------------------------------------------------
# Serializers for custom responses
# ----------------------------------------------------------------------
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
        400: RESPONSES.HTTP_400_BAD_REQUEST,
    },
    summary="Create a new root",
    description="Create a new root.",
    examples=None,
)

ApiDoc.RootDetail = SimpleNamespace()
ApiDoc.RootDetail.get = extend_schema(
    request=None,
    responses={
        200: SingleRootResponseSerializer,
        404: RESPONSES.HTTP_404_NOT_FOUND,
    },
    summary="Get root detail",
    description="",
    examples=None,
)
ApiDoc.RootDetail.put = extend_schema(
    request=RootSerializer,
    responses={
        200: SingleRootResponseSerializer,
        400: RESPONSES.HTTP_400_BAD_REQUEST,
        404: RESPONSES.HTTP_404_NOT_FOUND,
    },
    summary="Update the root",
    description="",
    examples=None,
)
ApiDoc.RootDetail.delete = extend_schema(
    request=None,
    responses={
        200: None,
        404: RESPONSES.HTTP_404_NOT_FOUND,
    },
    summary="Delete the root and its content",
    description="",
    examples=None,
)

# TODO ApiDoc.RootGraph = SimpleNamespace()
# TODO same for root fragments
# TODO default root fragments
