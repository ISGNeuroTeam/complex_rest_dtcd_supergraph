from django.urls import re_path

from .views import GraphView

app_name = "supergraph"

urlpatterns = [
    re_path(r'^graphContent/object/?$', GraphView.as_view()),
]