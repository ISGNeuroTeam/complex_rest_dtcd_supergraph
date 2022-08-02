from django.urls import path

from .views import (
    GraphView,
    FragmentDetailView,
    FragmentListView,
    ResetNeo4j,
    RootDetailView,
    RootFragmentGraphView,
    RootFragmentDetailView,
    RootFragmentListView,
    RootListView,
)


app_name = "supergraph"
urlpatterns = [
    path("roots", RootListView.as_view(), name="roots"),
    path("roots/<uuid:pk>", RootDetailView.as_view(), name="root-detail"),
    path(
        "roots/<uuid:pk>/fragments",
        RootFragmentListView.as_view(),
        name="root-fragments",
    ),
    path(
        "roots/<uuid:root_pk>/fragments/<uuid:fragment_pk>",
        RootFragmentDetailView.as_view(),
        name="root-fragment-detail",
    ),
    path(
        "roots/<uuid:root_pk>/fragments/<uuid:fragment_pk>/graph",
        RootFragmentGraphView.as_view(),
        name="root-fragment-graph",
    ),
    path("roots/<uuid:pk>/graph", GraphView.as_view(), name="root-graph"),
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path("fragments/<uuid:pk>", FragmentDetailView.as_view(), name="fragment-detail"),
    path("fragments/<uuid:pk>/graph", GraphView.as_view(), name="fragment-graph"),
    path("reset", ResetNeo4j.as_view(), name="reset"),
]
