from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import (
    Product,
    ProductVariant,
    ProductImage,
    Size,
    Material,
    Color,
)

# --------------------------------------------------
# Product Variant Inline
# --------------------------------------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    autocomplete_fields = ("size", "material", "color")
    fields = ("size", "material", "color", "stock")
    show_change_link = True


# --------------------------------------------------
# Product Image Inline (GALLERY)
# --------------------------------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    ordering = ("order",)


# --------------------------------------------------
# Product Admin
# --------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_featured",   # ✅
        "is_new",        # ✅
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "is_featured",   # ✅
        "is_new",        # ✅
        "collections",
    )

    search_fields = ("name", "category__name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

    filter_horizontal = ("collections",)

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "tag",
                )
            },
        ),
        (
            "Pricing & Promotion",
            {
                "fields": (
                    "price",
                    "original_price",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "summary",
                    "description",
                    "details",
                ),
            },
        ),
        (
            "Collections",
            {
                "fields": ("collections",),
                "description": "Marketing collections (homepage & campaigns).",
            },
        ),
        (
            "Homepage Visibility",   # ✅ VERY IMPORTANT
            {
                "fields": (
                    "is_featured",
                    "is_new",
                ),
                "description": "Controls homepage sections like Featured & New arrivals.",
            },
        ),
        (
            "Commerce Details",
            {
                "fields": (
                    "sku",
                    "shipping_info",
                )
            },
        ),
        (
            "Display & Status",
            {
                "fields": (
                    "image",
                    "is_active",
                )
            },
        ),
    )

    # Better JSON editor for details
    formfield_overrides = {
        models.JSONField: {
            "widget": Textarea(attrs={"rows": 6, "cols": 80})
        }
    }

    # ✅ Bulk actions (PRO UX)
    actions = [
        "mark_as_featured",
        "unmark_as_featured",
        "mark_as_new",
        "unmark_as_new",
    ]

    @admin.action(description="Mark selected products as Featured")
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove Featured flag from selected products")
    def unmark_as_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description="Mark selected products as New")
    def mark_as_new(self, request, queryset):
        queryset.update(is_new=True)

    @admin.action(description="Remove New flag from selected products")
    def unmark_as_new(self, request, queryset):
        queryset.update(is_new=False)


# --------------------------------------------------
# Color Admin
# --------------------------------------------------
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")
    search_fields = ("name",)


# --------------------------------------------------
# Size Admin
# --------------------------------------------------
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("value",)
    search_fields = ("value",)
    ordering = ("value",)


# --------------------------------------------------
# Material Admin
# --------------------------------------------------
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


# --------------------------------------------------
# Product Variant Admin
# --------------------------------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "material",
        "color",
        "stock",
    )

    list_filter = ("size", "material", "color")
    search_fields = ("product__name",)
    autocomplete_fields = ("product", "size", "material", "color")
