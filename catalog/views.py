from rest_framework.generics import ListAPIView
from .models import Collection
from .serializers import CollectionSerializer
from products.serializers import ProductSerializer
from products.models import Product


class CollectionListAPIView(ListAPIView):

    serializer_class = CollectionSerializer
    queryset = Collection.objects.filter(is_visible=True)

    def get_serializer_context(self):
        return {"request": self.request}


class ProductsByCollectionAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        return Product.objects.filter(
            collections__slug=slug,
            is_active=True
        ).distinct()