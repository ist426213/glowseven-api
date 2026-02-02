from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView, 
    CreateAPIView
)
from .models import (
    HeroBanner, 
    VipMarketingSection, 
    VipSubscriber,
    Testimonial
)
from .serializers import (
    HeroBannerSerializer, 
    VipMarketingSectionSerializer,
    VipSubscriberSerializer,
    TestimonialSerializer
)
from rest_framework.response import Response
from rest_framework import status


class HeroBannerListAPIView(ListAPIView):
    serializer_class = HeroBannerSerializer

    def get_queryset(self):
        return HeroBanner.objects.filter(is_active=True)



class VipMarketingSectionAPIView(RetrieveAPIView):
    serializer_class = VipMarketingSectionSerializer

    def get_object(self):
        return VipMarketingSection.objects.filter(is_active=True).first()
    


class VipSubscribeAPIView(CreateAPIView):

    serializer_class = VipSubscriberSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")

        if VipSubscriber.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email already subscribed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)
    

class TestimonialListAPIView(ListAPIView):
    serializer_class = TestimonialSerializer

    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True)