import neomodel

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView

from ..apidoc import ApiDoc
from .generics import Neo4jAPIView


class ResetNeo4jView(Neo4jAPIView):
    """A view to reset Neo4j database."""

    http_method_names = ["post"]
    permission_classes = (AllowAny,)

    @ApiDoc.ResetNeo4j.post
    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        # TODO deprecated
        # TODO this also deletes the default root
        neomodel.clear_neo4j_database(neomodel.db)

        return SuccessResponse()
