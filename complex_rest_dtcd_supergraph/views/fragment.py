import uuid

import neomodel
from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from ..models import Fragment
from ..serializers import (
    FragmentSerializer,
)
from .shortcuts import get_node_or_404


class FragmentListView(APIView):
    """List existing fragments or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @neomodel.db.transaction
    def get(self, request: Request):
        """Read a list of existing fragment names."""

        fragments = list(Fragment.nodes)
        serializer = self.serializer_class(fragments, many=True)

        return SuccessResponse({"fragments": serializer.data})

    @neomodel.db.transaction
    def post(self, request: Request):
        """Create a new fragment."""

        # validation
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # create a fragment
        serializer.save()

        return SuccessResponse(
            data={"fragment": serializer.data},
            http_status=status.HTTP_201_CREATED,
        )


class FragmentDetailView(APIView):
    """Retrieve, update or delete a fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @neomodel.db.transaction
    def get(self, request: Request, pk: uuid.UUID):
        """Return a fragment."""

        # Neo4j generates and stored uuid in hex format
        fragment = get_node_or_404(Fragment.nodes, uid=pk.hex)
        serializer = self.serializer_class(fragment)

        return SuccessResponse({"fragment": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, pk: uuid.UUID):
        """Update a fragment."""

        old = get_node_or_404(Fragment.nodes, uid=pk.hex)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse({"fragment": serializer.data})

    @neomodel.db.transaction
    def delete(self, request: Request, pk: uuid.UUID):
        """Delete a fragment and its content."""

        fragment = get_node_or_404(Fragment.nodes, uid=pk.hex)
        fragment.delete()

        return SuccessResponse()
