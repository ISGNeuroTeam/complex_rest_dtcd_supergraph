from django.urls import path

from .views import (
    FragmentDetailView,
    FragmentGraphView,
    FragmentListView,
    ResetNeo4j,
    RootGraphView,
)


app_name = "supergraph"
urlpatterns = [
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path("fragments/<uuid:pk>", FragmentDetailView.as_view(), name="fragment-detail"),
    path(
        "fragments/<uuid:pk>/graph", FragmentGraphView.as_view(), name="fragment-graph"
    ),
    path("fragments/root/graph", RootGraphView.as_view(), name="root-graph"),
    path("reset", ResetNeo4j.as_view(), name="reset"),
]
