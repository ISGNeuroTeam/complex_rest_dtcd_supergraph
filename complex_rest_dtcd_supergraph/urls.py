from django.urls import path

from .views import (
    ContainerView,
    FragmentDetailView,
    FragmentListView,
    ResetNeo4j,
    RootDetailView,
    RootListView,
)


app_name = "supergraph"
urlpatterns = [
    path("roots", RootListView.as_view(), name="roots"),
    path("roots/<uuid:pk>", RootDetailView.as_view(), name="root-detail"),
    path("fragments", FragmentListView.as_view(), name="fragments"),
    path("fragments/<uuid:pk>", FragmentDetailView.as_view(), name="fragment-detail"),
    path("fragments/<uuid:pk>/graph", ContainerView.as_view(), name="fragment-graph"),
    path("reset", ResetNeo4j.as_view(), name="reset"),
]
