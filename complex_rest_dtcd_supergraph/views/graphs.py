from rest.views import APIView
from rest.response import Response, status
from rest.permissions import AllowAny
from rest_framework.request import Request
from ..utils.filesystem_graphmanager import FilesystemGraphManager
from ..settings import GRAPH_BASE_PATH, GRAPH_TMP_PATH, GRAPH_ID_NAME_MAP_PATH
import logging

logger = logging.getLogger('supergraph')


class Graph(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'put', 'delete']
    graph_manager = FilesystemGraphManager(GRAPH_BASE_PATH, GRAPH_TMP_PATH, GRAPH_ID_NAME_MAP_PATH)

    def post(self, request) -> Response:
        graphs = request.data
        for graph in graphs:
            try:
                self.graph_manager.write(graph)
            except Exception as e:
                return Response(
                    {"status": "ERROR", "msg": str(e)},
                    status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {"status": "SUCCESS"},
            status.HTTP_200_OK
        )

    def put(self, request: Request) -> Response:
        graphs = request.data
        for graph in graphs:
            try:
                self.graph_manager.update(graph)
            except Exception as e:
                return Response(
                    {"status": "ERROR", "msg": str(e)},
                    status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {"status": "SUCCESS"},
            status.HTTP_200_OK
        )

    def delete(self, request) -> Response:
        ids = request.data
        for id in ids:
            try:
                self.graph_manager.remove(id)
            except Exception as e:
                return Response(
                    {"status": "ERROR", "msg": str(e)},
                    status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {"status": "SUCCESS"},
            status.HTTP_200_OK
        )

    def get(self, request: Request) -> Response:
        qs = dict(request.query_params)
        if 'id' not in qs:
            return Response(self.graph_manager.read_all(), status.HTTP_200_OK)
        try:
            graph_content = self.graph_manager.read(qs['id'][0])
        except Exception as e:
            return Response({"status": "ERROR", "msg": str(e)}, status.HTTP_400_BAD_REQUEST)
        return Response(graph_content, status.HTTP_200_OK)
