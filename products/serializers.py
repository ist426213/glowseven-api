# serializers.py
from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage


class ProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source="size.value")
    material = serializers.CharField(source="material.name")
    color = serializers.CharField(source="color.name")
    color_hex = serializers.CharField(source="color.hex_code")

    class Meta:
        model = ProductVariant
        fields = ["size", "material", "color", "color_hex", "stock"]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image", "order"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    in_promo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "original_price",
            "in_promo",
            "image",
            "images",
            "video_url",
            "category",
            "summary",
            "description",
            "details",
            "sku",
            "shipping_info",
            "tag",
            "variants",
            "materials",
            "heel_height",
            "lining",
            "insole",
            "care_instructions",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        return None

    def get_in_promo(self, obj):
        return bool(obj.original_price and obj.original_price > obj.price)


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    in_promo = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "original_price",
            "in_promo",
            "image",
            "video_url",
            "category",
            "summary",
            "tag",
            "is_new",
            "is_featured",
            "is_best_seller",  
            "best_seller_position",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_video_url(self, obj):
            request = self.context.get("request")
            if obj.video and request:
                return request.build_absolute_uri(obj.video.url)
            return None