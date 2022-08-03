import logging
import uuid

import neomodel
from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from .converters import GraphDataConverter
from .extensions import (
    ListCreateNeomodelAPIView,
    RetrieveUpdateDestroyNeomodelAPIView,
)
from .managers import Manager
from .models import Container, Fragment, Root
from .serializers import (
    ContentSerializer,
    FragmentSerializer,
    GraphSerializer,
    RootSerializer,
)
from .utils import get_node_or_404


logger = logging.getLogger("supergraph")


def get_root_then_fragment_or_404(
    root_pk: uuid.UUID, fragment_pk: uuid.UUID
) -> Fragment:
    root = get_node_or_404(Root.nodes, uid=root_pk.hex)
    fragment = get_node_or_404(root.fragments, uid=fragment_pk.hex)

    return fragment


class RootListView(ListCreateNeomodelAPIView):
    """List existing roots or create a new one."""

    http_method_names = ["get", "post"]
    model = Root
    permission_classes = (AllowAny,)
    serializer_class = RootSerializer


class RootDetailView(RetrieveUpdateDestroyNeomodelAPIView):
    """Retrieve, update or delete a root."""

    http_method_names = ["get", "put", "delete"]
    lookup_field = "uid"
    lookup_url_kwarg = "pk"
    model = Root
    permission_classes = (AllowAny,)
    serializer_class = RootSerializer


class RootFragmentListView(ListCreateNeomodelAPIView):
    """List existing fragments of a root or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @neomodel.db.transaction
    def get(self, request: Request, pk: uuid.UUID):
        """Read a list of root's fragments."""

        root = get_node_or_404(Root.nodes, uid=pk.hex)
        fragments = list(root.fragments.all())
        serializer = self.serializer_class(fragments, many=True)

        return SuccessResponse({"fragments": serializer.data})

    @neomodel.db.transaction
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


class RootFragmentDetailView(APIView):
    """Retrieve, update or delete this root's fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer

    @neomodel.db.transaction
    def get(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Return root's fragment."""

        fragment = get_root_then_fragment_or_404(root_pk, fragment_pk)
        serializer = self.serializer_class(fragment)

        return SuccessResponse({"fragment": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Update this root's fragment."""

        old = get_root_then_fragment_or_404(root_pk, fragment_pk)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return SuccessResponse({"fragment": serializer.data})

    @neomodel.db.transaction
    def delete(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Delete this root's fragment and its content."""

        fragment = get_root_then_fragment_or_404(root_pk, fragment_pk)
        fragment.delete()

        return SuccessResponse()


class RootFragmentGraphView(APIView):
    """Retrieve, replace or delete graph content of this root's fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    converter = GraphDataConverter()
    manager = Manager()

    @neomodel.db.transaction
    def get(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Read graph content of the given root's fragment."""

        fragment = get_root_then_fragment_or_404(root_pk, fragment_pk)
        content = self.manager.read(fragment)
        logger.info("Queried content: " + content.info)
        payload = self.converter.to_data(content)
        serializer = ContentSerializer(instance=payload)

        return SuccessResponse(data={"graph": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Replace graph content of this root's fragment."""

        # validate incoming graph content
        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # convert to domain classes
        new_content = self.converter.to_content(serializer.data["graph"])
        logger.info("Converted to content: " + new_content.info)
        # query root and fragment
        root = get_node_or_404(Root.nodes, uid=root_pk.hex)
        fragment = get_node_or_404(root.fragments, uid=fragment_pk.hex)
        # update fragment's content
        self.manager.replace(fragment, new_content)
        # re-connect root to content
        self.manager.reconnect(root, fragment)

        return SuccessResponse()

    @neomodel.db.transaction
    def delete(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Delete graph content this root's fragment."""

        fragment = get_root_then_fragment_or_404(root_pk, fragment_pk)
        fragment.clear()

        return SuccessResponse()


class FragmentListView(ListCreateNeomodelAPIView):
    """List existing fragments or create a new one."""

    http_method_names = ["get", "post"]
    lookup_field = "uid"
    lookup_url_kwarg = "pk"
    model = Fragment
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer


class FragmentDetailView(RetrieveUpdateDestroyNeomodelAPIView):
    """Retrieve, update or delete a fragment."""

    http_method_names = ["get", "put", "delete"]
    lookup_field = "uid"
    lookup_url_kwarg = "pk"
    model = Fragment
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer


class GraphView(APIView):
    """Retrieve, replace or delete graph content of a container."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    converter = GraphDataConverter()
    manager = Manager()

    @neomodel.db.transaction
    def get(self, request: Request, pk: uuid.UUID):
        """Read graph content of a container with the given id."""

        container = get_node_or_404(Container.nodes, uid=pk.hex)
        content = self.manager.read(container)
        logger.info("Queried content: " + content.info)
        payload = self.converter.to_data(content)
        serializer = ContentSerializer(instance=payload)

        return SuccessResponse(data={"graph": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, pk: uuid.UUID):
        """Replace graph content of a container with the given id."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_content = self.converter.to_content(serializer.data["graph"])
        logger.info("Converted to content: " + new_content.info)
        container = get_node_or_404(Container.nodes, uid=pk.hex)
        self.manager.replace(container, new_content)

        return SuccessResponse()

    @neomodel.db.transaction
    def delete(self, request: Request, pk: uuid.UUID):
        """Delete graph content of a container with the given id."""

        container = get_node_or_404(Container.nodes, uid=pk.hex)
        container.clear()

        return SuccessResponse()


class ResetNeo4jView(APIView):
    """A view to reset Neo4j database."""

    http_method_names = ["post"]
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        neomodel.clear_neo4j_database(neomodel.db)

        return SuccessResponse()
