import logging
import uuid

import neomodel
from rest_framework import status
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from ..converters import GraphDataConverter
from ..managers import Manager
from ..models import Container, Fragment, Root
from ..serializers import (
    ContentSerializer,
    FragmentSerializer,
    GraphSerializer,
    RootSerializer,
)
from .shortcuts import (
    get_node_or_404,
    get_root_then_fragment_or_404,
    replace_or_400,
    to_content_or_400,
)

logger = logging.getLogger("supergraph")


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


class RootFragmentListView(APIView):
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
        new_content = to_content_or_400(self.converter, serializer.data["graph"])
        logger.info("Converted to content: " + new_content.info)
        # query root and fragment
        root = get_node_or_404(Root.nodes, uid=root_pk.hex)
        fragment = get_node_or_404(root.fragments, uid=fragment_pk.hex)
        # update fragment's content
        replace_or_400(self.manager, fragment, new_content)
        # re-connect root to content
        self.manager.reconnect(root, fragment)

        return SuccessResponse()

    @neomodel.db.transaction
    def delete(self, request: Request, root_pk: uuid.UUID, fragment_pk: uuid.UUID):
        """Delete graph content this root's fragment."""

        fragment = get_root_then_fragment_or_404(root_pk, fragment_pk)
        fragment.clear()

        return SuccessResponse()


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
        new_content = to_content_or_400(self.converter, serializer.data["graph"])
        logger.info("Converted to content: " + new_content.info)
        container = get_node_or_404(Container.nodes, uid=pk.hex)
        replace_or_400(self.manager, container, new_content)

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

    @neomodel.db.transaction
    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        neomodel.clear_neo4j_database(neomodel.db)

        return SuccessResponse()
