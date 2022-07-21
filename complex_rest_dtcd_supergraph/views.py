import logging
import uuid

import neomodel
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from . import settings
from .models import Fragment
from .serializers import GraphSerializer, FragmentSerializer
from .exceptions import LoadingError
from .managers import Neo4jGraphManager
from .converters import Converter


logger = logging.getLogger("supergraph")

GRAPH_MANAGER = Neo4jGraphManager(
    settings.NEO4J["uri"],
    settings.NEO4J["name"],
    auth=(settings.NEO4J["user"], settings.NEO4J["password"]),
)


def get_node_or_404(model: neomodel.StructuredNode, lazy=False, **kwargs):
    """Call `.nodes.get()` on a given node.

    Raises `rest_framework.exceptions.NotFound` if a node is missing.
    """

    try:
        return model.nodes.get(lazy=lazy, **kwargs)
    except neomodel.DoesNotExist:
        raise NotFound


def get_fragment_or_404(manager: Neo4jGraphManager, id_: int) -> Fragment:
    """Return a fragment with the given id from the provided manager.

    Raises `NotFound` if the fragment does not exist.
    """

    fragment = manager.fragments.get(id_)

    if fragment is not None:
        return fragment
    else:
        raise NotFound


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
        fragment.delete()  # TODO recursively delete this fragment's content

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
        subgraph = self.graph_manager.fragments.content.read(fragment)
        logger.info(
            f"Read {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        # convert to representation format
        converter = self.converter_class()
        payload = converter.dump(subgraph)
        v, e, g = describe(payload)
        logger.info(f"Converted to payload with {v} vertices, {e} edges, {g} groups.")

        # TODO validation checks?
        # TODO move hard-coded key to config

        return SuccessResponse({"graph": payload})

    def put(self, request: Request, pk: int):
        """Replace graph content of a fragment with given id."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["graph"]
        v, e, g = describe(payload)
        logger.info(f"Got payload with {v} vertices, {e} edges, {g} groups.")

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
        subgraph = self.graph_manager.fragments.content.read()
        logger.info(
            f"Read {len(subgraph.nodes)} nodes, "
            f"{len(subgraph.relationships)} relationships."
        )

        converter = self.converter_class()
        payload = converter.dump(subgraph)
        v, e, g = describe(payload)
        logger.info(f"Converted to payload with {v} vertices, {e} edges, {g} groups.")

        return SuccessResponse({"graph": payload})

    def put(self, request: Request):
        """Replace graph content."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["graph"]
        v, e, g = describe(payload)
        logger.info(f"Got payload with {v} vertices, {e} edges, {g} groups.")

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

    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        neomodel.clear_neo4j_database(neomodel.db)  # TODO constraints? indexes?
        return SuccessResponse()


def describe(data):
    """Return (num_nodes, num_edges, num_groups) tuple from data."""
    # TODO get from settings
    return len(data["nodes"]), len(data["edges"]), len(data.get("groups", []))
