from django.urls import path
from .views import FAQListAPIView, SupportTicketListCreateAPIView, SupportTicketRetrieveAPIView

urlpatterns = [
    path('faqs/', FAQListAPIView.as_view(), name='faq-list'),
    path('tickets/', SupportTicketListCreateAPIView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', SupportTicketRetrieveAPIView.as_view(), name='ticket-detail'),
]