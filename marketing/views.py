from rest_framework.generics import ListAPIView
from .models import HeroBanner
from .serializers import HeroBannerSerializer


class HeroBannerListAPIView(ListAPIView):
    serializer_class = HeroBannerSerializer

    def get_queryset(self):
        return HeroBanner.objects.filter(is_active=True)
