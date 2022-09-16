"""
Views for graph management operations for roots and fragments.
"""

import uuid

from rest_framework.request import Request

from rest.permissions import IsAuthenticated
from rest.response import SuccessResponse

from .. import settings
from ..models import Root
from ..serializers import ContentSerializer, GraphSerializer
from .fragments import get_fragment_from_root_or_404
from .generics import Neo4jAPIView
from .mixins import ContainerManagementMixin
from .shortcuts import get_node_or_404


class RootGraphView(ContainerManagementMixin, Neo4jAPIView):
    """Retrieve, replace or delete graph content of a root."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, pk: uuid.UUID):
        """Read graph content of a root."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        payload = self.read_content_as_dict(root)
        serializer = ContentSerializer(instance=payload)

        return SuccessResponse(data={"graph": serializer.data})

    def put(self, request: Request, pk: uuid.UUID):
        """Replace graph content of a root."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.replace_content_from_dict(root, serializer.data["graph"])

        return SuccessResponse()

    def delete(self, request: Request, pk: uuid.UUID):
        """Delete graph content of a root."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        root.clear(content_only=True)

        return SuccessResponse()


class DefaultRootGraphView(RootGraphView):
    """Retrieve, replace or delete graph content of the default root."""

    # TODO deprecate when front-end moves to explicit root management
    pk = settings.DEFAULT_ROOT_UUID

    def get(self, request: Request):
        return super().get(request, self.pk)

    def put(self, request: Request):
        return super().put(request, self.pk)

    def delete(self, request: Request):
        return super().delete(request, self.pk)


class RootFragmentGraphView(ContainerManagementMixin, Neo4jAPIView):
    """Retrieve, replace or delete graph content of this root's fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Read graph content of the given root's fragment."""

        fragment = get_fragment_from_root_or_404(root_pk, fragment_pk)
        payload = self.read_content_as_dict(fragment)
        serializer = ContentSerializer(instance=payload)

        return SuccessResponse(data={"graph": serializer.data})

    def put(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Replace graph content of this root's fragment."""

        # validate incoming graph content
        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # query root and fragment
        root = get_node_or_404(Root.nodes, uid=root_pk.hex)
        fragment = get_node_or_404(root.fragments, uid=fragment_pk.hex)
        # convert to domain classes, update fragment's content
        self.replace_content_from_dict(fragment, serializer.data["graph"])
        # re-connect root to fragment's new content
        root.reconnect_to_content(fragment)

        return SuccessResponse()

    def delete(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Delete graph content this root's fragment."""

        fragment = get_fragment_from_root_or_404(root_pk, fragment_pk)
        fragment.clear()

        return SuccessResponse()


class DefaultRootFragmentGraphView(RootFragmentGraphView):
    """Retrieve, replace or delete graph content of default root's fragment."""

    # TODO deprecate when front-end moves to explicit root management
    root_pk = settings.DEFAULT_ROOT_UUID

    def get(self, request: Request, pk: uuid.UUID):
        fragment_pk = pk
        return super().get(request, self.root_pk, fragment_pk)

    def put(self, request: Request, pk: uuid.UUID):
        fragment_pk = pk
        return super().put(request, self.root_pk, fragment_pk)

    def delete(self, request: Request, pk: uuid.UUID):
        fragment_pk = pk
        return super().delete(request, self.root_pk, fragment_pk)
