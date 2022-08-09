"""
Views for root management operations.
"""

import uuid

import neomodel
from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from ..models import Root
from ..serializers import RootSerializer
from .shortcuts import get_node_or_404


class RootListView(APIView):
    """List existing roots or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = RootSerializer

    @neomodel.db.transaction
    def get(self, request: Request):
        """Read a list of existing roots."""

        roots = list(Root.nodes)
        serializer = self.serializer_class(roots, many=True)

        return SuccessResponse({"roots": serializer.data})

    @neomodel.db.transaction
    def post(self, request: Request):
        """Create a new root."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse(
            data={"root": serializer.data},
            http_status=status.HTTP_201_CREATED,
        )


class RootDetailView(APIView):
    """Retrieve, update or delete a root."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    serializer_class = RootSerializer

    @neomodel.db.transaction
    def get(self, request: Request, pk: uuid.UUID):
        """Return a root."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        serializer = self.serializer_class(root)

        return SuccessResponse({"root": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, pk: uuid.UUID):
        """Update a fragment."""

        old = get_node_or_404(Root.nodes, uid=pk.hex)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse({"root": serializer.data})

    @neomodel.db.transaction
    def delete(self, request: Request, pk: uuid.UUID):
        """Delete a fragment and its content."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        root.delete()

        return SuccessResponse()
