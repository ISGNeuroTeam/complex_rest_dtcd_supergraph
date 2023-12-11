from django.urls import path

from .views import GraphView, GraphDetailView

app_name = "supergraph"

urlpatterns = [
    path('graphs/', GraphView.as_view(), name='graphs'),
    path('graphs/<str:graph_id>/', GraphDetailView.as_view(), name='graphs_detail')
]
