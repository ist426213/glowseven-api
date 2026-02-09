from rest_framework.generics import ListAPIView
from .models import Category
from .serializers import CategorySerializer

class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.filter(is_visible=True)
    serializer_class = CategorySerializer
