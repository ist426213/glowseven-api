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


""" class ProductSerializer(serializers.ModelSerializer):
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
            "category",
            "summary",
            "tag",
            "is_new",
            "is_featured",
        ]

    #def get_in_promo(self, obj):
    #    return bool(obj.original_price and obj.original_price > obj.price) """


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "order"]


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
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

            # media
            "image",
            "images",

            # category
            "category",

            # content
            "summary",
            "description",
            "details",

            # commerce / UI
            "sku",
            "shipping_info",
            "tag",

            # variants
            "variants",
        ]

    def get_in_promo(self, obj):
        return bool(obj.original_price and obj.original_price > obj.price)

    

class ProductSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
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
            "category",
            "summary",
            "tag",
            "is_new",
            "is_featured",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url)