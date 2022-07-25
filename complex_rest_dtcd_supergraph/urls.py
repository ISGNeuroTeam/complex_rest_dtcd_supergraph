from django.urls import path, register_converter

from .views import (
    FragmentDetailView,
    FragmentGraphView,
    FragmentListView,
    ResetNeo4j,
    RootGraphView,
)
from .utils import HexUUIDConverter


register_converter(HexUUIDConverter, "hexuuid")


app_name = "supergraph"
urlpatterns = [
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path(
        "fragments/<hexuuid:pk>", FragmentDetailView.as_view(), name="fragment-detail"
    ),
    path(
        "fragments/<hexuuid:pk>/graph",
        FragmentGraphView.as_view(),
        name="fragment-graph",
    ),
    path("fragments/root/graph", RootGraphView.as_view(), name="root-graph"),
    path("reset", ResetNeo4j.as_view(), name="reset"),
]
