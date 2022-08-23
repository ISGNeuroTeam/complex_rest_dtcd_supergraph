from django.urls import path

from .views import (
    DefaultRootFragmentDetailView,
    DefaultRootFragmentGraphView,
    DefaultRootFragmentListView,
    DefaultRootGraphView,
    ResetNeo4jView,
    RootDetailView,
    RootFragmentDetailView,
    RootFragmentGraphView,
    RootFragmentListView,
    RootGraphView,
    RootListView,
)


app_name = "supergraph"

urlpatterns = [
    # root management
    path("roots", RootListView.as_view(), name="roots"),
    path("roots/<uuid:pk>", RootDetailView.as_view(), name="root-detail"),
    path("roots/<uuid:pk>/graph", RootGraphView.as_view(), name="root-graph"),
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
    # services
    path("reset", ResetNeo4jView.as_view(), name="reset"),
]

# backward API compatibility: fragment management for default root
# TODO deprecate when front-end moves to explicit root management
urlpatterns += [
    path(
        "fragments",
        DefaultRootFragmentListView.as_view(),
        name="default-root-fragments",
    ),
    path(
        "fragments/<uuid:pk>",
        DefaultRootFragmentDetailView.as_view(),
        name="default-root-fragment-detail",
    ),
    path(
        "fragments/<uuid:pk>/graph",
        DefaultRootFragmentGraphView.as_view(),
        name="default-root-fragment-graph",
    ),
    path(
        "fragments/root/graph",
        DefaultRootGraphView.as_view(),
        name="default-root-graph",
    ),
]
