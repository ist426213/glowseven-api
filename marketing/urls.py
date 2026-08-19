from django.urls import path
from .views import (
    HeroBannerListAPIView,
    VipMarketingSectionAPIView,
    VipSubscribeAPIView,
    TestimonialListAPIView,
    NewsletterSubscribeAPIView,
    ArtisanProcessAPIView,
    ContactMessageCreateAPIView
)


urlpatterns = [
    path("hero-banners", HeroBannerListAPIView.as_view()),
    path("vip-section", VipMarketingSectionAPIView.as_view()),
    path("vip-subscribe", VipSubscribeAPIView.as_view()),
    path("testimonials", TestimonialListAPIView.as_view()),
    path("newsletter-subscribe", NewsletterSubscribeAPIView.as_view()),
    path("artisan-process", ArtisanProcessAPIView.as_view()),
    path("contact", ContactMessageCreateAPIView.as_view()),
]
