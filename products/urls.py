# urls.py
from django.urls import path
from .views import (
    ProductListAPIView, 
    ProductByCategoryAPIView, 
    ProductDetailAPIView, 
    CategoryFiltersAPIView, 
    FeaturedProductListAPIView,
    BestSellersListAPIView,  # Importar nova view
)

urlpatterns = [
    path("", ProductListAPIView.as_view()),
    path("products/featured/", FeaturedProductListAPIView.as_view()),
    path("products/best-sellers/", BestSellersListAPIView.as_view()),  # Nova rota
    path("products/category/<slug:slug>/", ProductByCategoryAPIView.as_view()),
    path("products/<slug:slug>/", ProductDetailAPIView.as_view()),
    path("categories/<slug:slug>/filters/", CategoryFiltersAPIView.as_view()),
]