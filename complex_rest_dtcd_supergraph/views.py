import logging
import uuid

import neomodel
from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from .models import Fragment
from .serializers import FragmentSerializer
from .utils import get_node_or_404


logger = logging.getLogger("supergraph")


class FragmentListView(APIView):
    """List existing fragments or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    def get(self, request: Request):
        """Read a list of existing fragment names."""

        fragments = list(Fragment.nodes)
        serializer = self.serializer_class(fragments, many=True)

        return SuccessResponse({"fragments": serializer.data})

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

    def get(self, request: Request, pk: uuid.UUID):
        """Return a fragment."""

        # Neo4j generates and stored uuid in hex format
        fragment = get_node_or_404(Fragment, uid=pk.hex)
        serializer = self.serializer_class(fragment)

        return SuccessResponse({"fragment": serializer.data})

    def put(self, request: Request, pk: uuid.UUID):
        """Update a fragment."""

        old = get_node_or_404(Fragment, uid=pk.hex)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse({"fragment": serializer.data})

    def delete(self, request: Request, pk: uuid.UUID):
        """Delete a fragment and its content."""

        fragment = get_node_or_404(Fragment, uid=pk.hex)
        fragment.delete(cascade=True)

        return SuccessResponse()


class FragmentGraphView(APIView):
    """Retrieve, replace or delete graph content of a fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)

    def get(self, request: Request, pk):
        """Read graph content of a fragment with the given id."""

        raise NotImplementedError

    def put(self, request: Request, pk):
        """Replace graph content of a fragment with given id."""

        raise NotImplementedError

    def delete(self, request: Request, pk):
        """Delete graph content of a fragment with the given id."""

        raise NotImplementedError


class RootGraphView(APIView):
    """Retrieve, replace or delete full graph content."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        """Read all content."""

        raise NotImplementedError

    def put(self, request: Request):
        """Replace graph content."""

        raise NotImplementedError

    def delete(self, request: Request):
        """Delete whole graph content."""

        raise NotImplementedError


class ResetNeo4j(APIView):
    """A view to reset Neo4j database."""

    http_method_names = ["post"]
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        neomodel.clear_neo4j_database(neomodel.db)  # TODO constraints? indexes?
        return SuccessResponse()
