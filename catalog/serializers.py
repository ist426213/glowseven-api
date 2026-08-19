from rest_framework import serializers
from .models import Collection

class CollectionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "cover_image",
            "label",
            "tagline",
            "is_active",
            "is_visible",
            "order",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        # fallback: se cover_image não existir, usar image
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None