"""
Views for fragment management operations.

Fragments belong to roots.
"""

import uuid

from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse

from .. import settings
from ..apidoc import ApiDoc
from ..models import Fragment, Root
from ..serializers import FragmentSerializer
from .generics import Neo4jAPIView
from .shortcuts import get_node_or_404


def get_fragment_from_root_or_404(
    root_pk: uuid.UUID, fragment_pk: uuid.UUID
) -> Fragment:
    root = get_node_or_404(Root.nodes, uid=root_pk.hex)
    fragment = get_node_or_404(root.fragments, uid=fragment_pk.hex)

    return fragment


class RootFragmentListView(Neo4jAPIView):
    """List existing fragments of a root or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @ApiDoc.RootFragmentList.get
    def get(self, request: Request, pk: uuid.UUID):
        """Read a list of root's fragments."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        fragments = root.fragments.all()
        serializer = self.serializer_class(fragments, many=True)

        return SuccessResponse({"fragments": serializer.data})

    @ApiDoc.RootFragmentList.post
    def post(self, request: Request, pk: uuid.UUID):
        """Create a new fragment for this root."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        # create a fragment
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        fragment = serializer.save()
        # connect root to this fragment
        root.fragments.connect(fragment)

        return SuccessResponse(
            data={"fragment": serializer.data},
            http_status=status.HTTP_201_CREATED,
        )


class DefaultRootFragmentListView(RootFragmentListView):
    """List existing fragments of the default root or create a new one."""

    # TODO deprecate when front-end moves to explicit root management
    pk = settings.DEFAULT_ROOT_UUID

    def get(self, request: Request):
        """Read a list of default root's fragments."""

        return super().get(request, self.pk)

    def post(self, request: Request):
        """Create a new fragment for the default root."""

        return super().post(request, self.pk)


class RootFragmentDetailView(Neo4jAPIView):
    """Retrieve, update or delete this root's fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @ApiDoc.RootFragmentDetail.get
    def get(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Return root's fragment."""

        fragment = get_fragment_from_root_or_404(root_pk, fragment_pk)
        serializer = self.serializer_class(fragment)

        return SuccessResponse({"fragment": serializer.data})

    @ApiDoc.RootFragmentDetail.put
    def put(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Update this root's fragment."""

        old = get_fragment_from_root_or_404(root_pk, fragment_pk)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse({"fragment": serializer.data})

    @ApiDoc.RootFragmentDetail.delete
    def delete(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Delete this root's fragment and its content."""

        fragment = get_fragment_from_root_or_404(root_pk, fragment_pk)
        fragment.delete()

        return SuccessResponse()


class DefaultRootFragmentDetailView(RootFragmentDetailView):
    """Retrieve, update or delete default root's fragment."""

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
