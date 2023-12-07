from django.urls import path

from .views import GraphView

app_name = "supergraph"

urlpatterns = [
    path('graph/', GraphView.as_view()),
]
