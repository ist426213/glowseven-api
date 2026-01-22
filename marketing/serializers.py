from rest_framework import serializers
from .models import HeroBanner


class HeroBannerSerializer(serializers.ModelSerializer):
    collection_slug = serializers.SerializerMethodField()

    class Meta:
        model = HeroBanner
        fields = [
            "id",
            "title",
            "subtitle",
            "image_desktop",
            "image_mobile",
            "cta_text",
            "collection_slug",
        ]

    def get_collection_slug(self, obj):
        return obj.collection.slug if obj.collection else None
