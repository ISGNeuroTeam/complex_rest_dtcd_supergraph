from django.urls import path

from .views import (
    FragmentDetailView,
    FragmentGraphView,
    FragmentListView,
    ResetNeo4j,
    RootGraphView,
)

app_name = "complex_rest_dtcd_supergraph"
urlpatterns = [
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path("fragments/<int:pk>", FragmentDetailView.as_view(), name="fragment-detail"),
    path(
        "fragments/<int:pk>/graph", FragmentGraphView.as_view(), name="fragment-graph"
    ),
    path("fragments/root/graph", RootGraphView.as_view(), name="root-graph"),
    path("reset", ResetNeo4j.as_view(), name="reset"),
]
