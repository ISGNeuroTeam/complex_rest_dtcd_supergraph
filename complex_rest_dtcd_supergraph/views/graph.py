import uuid

import neomodel
from rest_framework.request import Request

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from ..converters import GraphDataConverter
from ..managers import Manager
from ..models import Container
from ..serializers import (
    ContentSerializer,
    GraphSerializer,
)
from .mixins import ContainerManagementMixin
from .shortcuts import get_node_or_404


class GraphView(ContainerManagementMixin, APIView):
    """Retrieve, replace or delete graph content of a container."""

    http_method_names = ["get", "put", "delete"]
    permission_classes = (AllowAny,)
    converter = GraphDataConverter()
    manager = Manager()

    @neomodel.db.transaction
    def get(self, request: Request, pk: uuid.UUID):
        """Read graph content of a container with the given id."""

        container = get_node_or_404(Container.nodes, uid=pk.hex)
        payload = self.read(container)
        serializer = ContentSerializer(instance=payload)

        return SuccessResponse(data={"graph": serializer.data})

    @neomodel.db.transaction
    def put(self, request: Request, pk: uuid.UUID):
        """Replace graph content of a container with the given id."""

        serializer = GraphSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = get_node_or_404(Container.nodes, uid=pk.hex)
        self.replace(container, serializer.data["graph"])

        return SuccessResponse()

    @neomodel.db.transaction
    def delete(self, request: Request, pk: uuid.UUID):
        """Delete graph content of a container with the given id."""

        container = get_node_or_404(Container.nodes, uid=pk.hex)
        container.clear()

        return SuccessResponse()
