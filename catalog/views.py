from rest_framework.generics import ListAPIView
from .models import Collection
from .serializers import CollectionSerializer

class CollectionListAPIView(ListAPIView):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.filter(is_active=True)

    def get_serializer_context(self):
        return {"request": self.request}
