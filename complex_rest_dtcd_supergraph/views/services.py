import neomodel

from rest.permissions import AllowAny
from rest.response import SuccessResponse
from rest.views import APIView


class ResetNeo4jView(APIView):
    """A view to reset Neo4j database."""

    http_method_names = ["post"]
    permission_classes = (AllowAny,)

    @neomodel.db.transaction
    def post(self, request, *args, **kwargs):
        """Delete all nodes and relationships from Neo4j database."""

        # TODO deprecated
        # TODO this also deletes teh default root
        neomodel.clear_neo4j_database(neomodel.db)

        return SuccessResponse()
