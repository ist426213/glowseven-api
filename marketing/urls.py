from django.urls import path
from .views import (
    HeroBannerListAPIView,
    VipMarketingSectionAPIView,
    VipSubscribeAPIView,
    TestimonialListAPIView
)


urlpatterns = [
    path("hero-banners", HeroBannerListAPIView.as_view()),
    path("vip-section", VipMarketingSectionAPIView.as_view()),
    path("vip-subscribe", VipSubscribeAPIView.as_view()),
    path("testimonials", TestimonialListAPIView.as_view()),
]
