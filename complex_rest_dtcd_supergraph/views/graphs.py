import json

from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from rest_framework.request import Request
from ..utils.filesystem_graphmanager import FilesystemGraphManager
from ..settings import GRAPH_BASE_PATH, GRAPH_TMP_PATH, GRAPH_ID_NAME_MAP_PATH
import logging

logger = logging.getLogger('supergraph')


class GraphView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']
    graph_manager = FilesystemGraphManager(GRAPH_BASE_PATH, GRAPH_TMP_PATH, GRAPH_ID_NAME_MAP_PATH)

    def post(self, request: Request) -> Response:
        graph = request.data

        id_and_title = (self.graph_manager.write(graph))
        # try:
        #     id_and_title = (self.graph_manager.write(graph))
        # except Exception as e:
        #     return Response(
        #         {"status": "ERROR", "msg": str(e)},
        #         status.HTTP_400_BAD_REQUEST
        #     )
        return Response(
            {"status": "SUCCESS", "result": id_and_title},
            status.HTTP_200_OK
        )

    def get(self, request: Request) -> Response:
        return Response(self.graph_manager.read_all(), status.HTTP_200_OK)


class GraphDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'put', 'delete']
    graph_manager = FilesystemGraphManager(GRAPH_BASE_PATH, GRAPH_TMP_PATH, GRAPH_ID_NAME_MAP_PATH)

    def put(self, request: Request, graph_id: str) -> Response:
        try:
            self.graph_manager.update(request.data, graph_id)
        except Exception as e:
            return Response(
                {"status": "ERROR", "msg": str(e)},
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"status": "SUCCESS"},
            status.HTTP_200_OK
        )

    def get(self, request: Request, graph_id: str) -> Response:
        try:
            graph_content = self.graph_manager.read(graph_id)
        except Exception as e:
            return Response({"status": "ERROR", "msg": str(e)}, status.HTTP_400_BAD_REQUEST)
        return Response(graph_content, status.HTTP_200_OK)

    def delete(self, request: Request, graph_id: str) -> Response:
        try:
            self.graph_manager.remove(graph_id)
        except Exception as e:
            return Response(
                {"status": "ERROR", "msg": str(e)},
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"status": "SUCCESS"},
            status.HTTP_200_OK
        )
