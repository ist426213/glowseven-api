from django.urls import path
from .views import HeroBannerListAPIView

urlpatterns = [
    path("hero-banners", HeroBannerListAPIView.as_view()),
]
