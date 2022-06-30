import logging

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from rest.response import SuccessResponse

from . import settings
from .models import Fragment
from .serializers import GraphSerializer, FragmentSerializer
from .exceptions import FragmentDoesNotExist, LoadingError
from .managers import Neo4jGraphManager
from .converters import Converter


logger = logging.getLogger("dtcd_supergraph")

GRAPH_MANAGER = Neo4jGraphManager(
    settings.NEO4J["uri"],
    settings.NEO4J["name"],
    auth=(settings.NEO4J["user"], settings.NEO4J["password"]),
)


def get_fragment_or_404(manager: Neo4jGraphManager, id_: int) -> Fragment:
    """Return a fragment with a given id from the provided manager.

    Calls `.fragments.get()` on a given manager, but raises `NotFound`
    instead of `FragmentDoesNotExist`.
    """

    try:
        return manager.fragments.get_or_exception(id_)
    except FragmentDoesNotExist as e:
        raise NotFound(detail=str(e))


def load_or_400(loader: Converter, data: dict):
    """Convert data to subgraph.

    Calls `.load()` on a given loader and raises `LoadingError` if it
    cannot convert the data.
    """

    try:
        return loader.load(data)
    except Exception:
        raise LoadingError


class FragmentListView(APIView):
    """List existing fragments or create a new one."""

    http_method_names = ["get", "post"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer
    graph_manager = GRAPH_MANAGER

    def get(self, request: Request):
        """Read a list of existing fragment names."""

        fragments = self.graph_manager.fragments.all()
        serializer = self.serializer_class(fragments, many=True)

        return SuccessResponse({"fragments": serializer.data})

    def post(self, request: Request):
        """Create a new fragment."""

        # validation
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create a fragment
        fragment = serializer.save()
        self.graph_manager.fragments.save(fragment)

        return SuccessResponse(
            # TODO how to get rid of additional serializer here?
            data={"fragment": self.serializer_class(fragment).data},
            http_status=status.HTTP_201_CREATED,
        )


class FragmentDetailView(APIView):
    """Retrieve, update or delete a fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    serializer_class = FragmentSerializer
    graph_manager = GRAPH_MANAGER

    def get(self, request: Request, pk: int):
        """Return a fragment."""

        fragment = get_fragment_or_404(self.graph_manager, pk)
        serializer = self.serializer_class(fragment)

        return SuccessResponse({"fragment": serializer.data})

    def put(self, request: Request, pk: int):
        """Update a fragment."""

        old = get_fragment_or_404(self.graph_manager, pk)
        serializer = self.serializer_class(old, data=request.data)
        serializer.is_valid(raise_exception=True)
        new = serializer.save()
        self.graph_manager.fragments.save(new)

        return SuccessResponse({"fragment": serializer.data})

    def delete(self, request: Request, pk: int):
        """Delete a fragment and its content."""

        fragment = get_fragment_or_404(self.graph_manager, pk)
        self.graph_manager.fragments.remove(fragment)

        return SuccessResponse()


class FragmentGraphView(APIView):
    """Retrieve, replace or delete graph content of a fragment."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    converter_class = Converter
    graph_manager = GRAPH_MANAGER

    def get(self, request: Request, pk: int):
        """Read graph content of a fragment with the given id."""

        # read fragment's graph
        fragment = get_fragment_or_404(self.graph_manager, pk)
        subgraph = self.graph_manager.fragments.content.get(fragment)
        logger.info(
            f"Read {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        # convert to representation format
        converter = self.converter_class()
        payload = converter.dump(subgraph)
        n, m = describe(payload)
        logger.info(f"Converted to payload with {n} vertices, {m} edges.")

        # TODO validation checks?
        # TODO move hard-coded key to config

        return SuccessResponse({"graph": payload})

    def put(self, request: Request, pk: int):
        """Replace graph content of a fragment with given id."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["graph"]
        n, m = describe(payload)
        logger.info(f"Got payload with {n} vertices, {m} edges.")

        # convert dict to subgraph
        converter = self.converter_class()
        subgraph = load_or_400(converter, payload)
        logger.info(
            f"Writing {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        # replace fragment content with new subgraph
        fragment = get_fragment_or_404(self.graph_manager, pk)
        self.graph_manager.fragments.content.replace(subgraph, fragment)

        return SuccessResponse()

    def delete(self, request: Request, pk: int):
        """Delete graph content of a fragment with the given id."""

        fragment = get_fragment_or_404(self.graph_manager, pk)
        self.graph_manager.fragments.content.remove(fragment)

        return SuccessResponse()


class RootGraphView(APIView):
    """Retrieve, replace or delete full graph content."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    converter_class = Converter
    graph_manager = GRAPH_MANAGER

    def get(self, request: Request):
        """Read all content."""

        # TODO copy-paste from FragmentGraphView
        subgraph = self.graph_manager.fragments.content.get()
        logger.info(
            f"Read {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        converter = self.converter_class()
        payload = converter.dump(subgraph)
        n, m = describe(payload)
        logger.info(f"Converted to payload with {n} vertices, {m} edges.")

        return SuccessResponse({"graph": payload})

    def put(self, request: Request):
        """Replace graph content."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["graph"]
        n, m = describe(payload)
        logger.info(f"Got payload with {n} vertices, {m} edges.")

        converter = self.converter_class()
        subgraph = load_or_400(converter, payload)
        logger.info(
            f"Writing {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        self.graph_manager.fragments.content.replace(subgraph)

        return SuccessResponse()

    def delete(self, request: Request):
        """Delete whole graph content."""
        self.graph_manager.fragments.content.clear()
        return SuccessResponse()


class ResetNeo4j(APIView):
    """A view to reset Neo4j database."""

    http_method_names = ["post"]
    permission_classes = (AllowAny,)
    graph_manager = GRAPH_MANAGER

    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""
        self.graph_manager.clear()
        return SuccessResponse()


def describe(data):
    """Return (num_nodes, num_edges) tuple from data."""
    return len(data["nodes"]), len(data["edges"])
