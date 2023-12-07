from django.urls import re_path

from .views import GraphView

app_name = "supergraph"

urlpatterns = [
    re_path(r'^complex_rest_dtcd_supergraph/v1/graph/?$', GraphView.as_view()),
]