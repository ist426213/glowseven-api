from django.urls import path
from .views import CollectionListAPIView, ProductsByCollectionAPIView

urlpatterns = [
    path("collections", CollectionListAPIView.as_view()),
    path("collections/<slug:slug>/products", ProductsByCollectionAPIView.as_view()),
]
