from rest.urls import path
from cache import cache_page
from .views.example import ExampleView
from .views.hello import HelloView


# Use cache_page decorator for caching view

# urlpatterns = [
#     path('example/', cache_page(60 * 15)(ExampleView.as_view())),
# ]

urlpatterns = [
    path('example/', ExampleView.as_view()),
    path('hello/', HelloView.as_view())
]