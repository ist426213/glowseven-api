from django.urls import path
from .views import (
    CheckoutAPIView,
    ValidateCouponAPIView,
    PaymentMBWayAPIView,
    PaymentMultibancoAPIView,
    PaymentMBWayWebhookAPIView,
    PaymentMultibancoWebhookAPIView,
)

urlpatterns = [
    path("checkout", CheckoutAPIView.as_view()),
    path("validate-coupon", ValidateCouponAPIView.as_view()),

    path("payment/mbway", PaymentMBWayAPIView.as_view()),
    path("payment/multibanco", PaymentMultibancoAPIView.as_view()),

    path("callback_mbway/", PaymentMBWayWebhookAPIView.as_view()),
    path("callback_multibanco/", PaymentMultibancoWebhookAPIView.as_view()),
]