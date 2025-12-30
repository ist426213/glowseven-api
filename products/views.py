from rest_framework.generics import ListAPIView
from .models import Product
from .serializers import ProductSerializer

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
