from rest_framework import serializers
from .models import (
    HeroBanner,
    VipMarketingSection, 
    VipSubscriber,
    Testimonial
)


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


class VipMarketingSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VipMarketingSection
        fields = [
            "id",
            "title",
            "description",
            "background_desktop",
            "background_mobile",
        ]


class VipSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = VipSubscriber
        fields = ["name", "email", "whatsapp"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "quote",
            "author",
            "location",
            "avatar",
            "rating",
        ]