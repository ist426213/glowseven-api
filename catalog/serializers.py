from rest_framework import serializers
from .models import Collection

class CollectionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "is_active",
            "is_visible",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url)
