from rest_framework import serializers
from .models import (
    HeroBanner,
    VipMarketingSection, 
    VipSubscriber,
    Testimonial,
    NewsletterSubscriber,
    ArtisanProcess,
    ContactMessage
)

class HeroBannerSerializer(serializers.ModelSerializer):
    collection_slug = serializers.SerializerMethodField()

    class Meta:
        model = HeroBanner
        fields = [
            "id",
            "title",
            "subtitle",
            "media_type",
            "image_desktop",
            "image_mobile",
            "video_desktop",
            "video_mobile",
            "cta_text",
            "collection_slug",
            "show_text",
            "object_position_x_desktop",
            "object_position_y_desktop",
            "object_position_x_mobile",
            "object_position_y_mobile",
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


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]


class ArtisanProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanProcess
        fields = [
            "id",
            "title",
            "description",
            "video_desktop",
            "video_mobile",
            "poster",
            "is_active",
            "order",
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "subject", "message", "created_at", "is_read"]
        read_only_fields = ["id", "created_at", "is_read"]