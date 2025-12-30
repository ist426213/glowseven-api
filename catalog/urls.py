from django.urls import path
from .views import CollectionListAPIView

urlpatterns = [
    path("collections", CollectionListAPIView.as_view()),
]
