from django.urls import path

from .views import (
    FragmentDetailView,
    FragmentListView,
    GraphView,
    ResetNeo4jView,
    RootDetailView,
    RootFragmentDetailView,
    RootFragmentGraphView,
    RootFragmentListView,
    RootListView,
)


app_name = "supergraph"
urlpatterns = [
    # root management
    path("roots", RootListView.as_view(), name="roots"),
    path("roots/<uuid:pk>", RootDetailView.as_view(), name="root-detail"),
    path("roots/<uuid:pk>/graph", GraphView.as_view(), name="root-graph"),
    # root fragments
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
    # fragment management
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path("fragments/<uuid:pk>", FragmentDetailView.as_view(), name="fragment-detail"),
    path("fragments/<uuid:pk>/graph", GraphView.as_view(), name="fragment-graph"),
    # services
    path("reset", ResetNeo4jView.as_view(), name="reset"),
]
