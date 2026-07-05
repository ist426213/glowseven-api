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
        "is_best_seller",      # ✅ NOVO
        "best_seller_position", # ✅ NOVO
        "is_featured",
        "is_new",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "is_best_seller",      # ✅ NOVO
        "is_featured",
        "is_new",
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
            "Homepage Visibility",
            {
                "fields": (
                    "is_featured",
                    "is_new",
                ),
                "description": "Controls homepage sections like Featured & New arrivals.",
            },
        ),
        (
            "Best Sellers",  # ✅ NOVO: Secção dedicada para Best Sellers
            {
                "fields": (
                    "is_best_seller",
                    "best_seller_position",
                ),
                "description": "Configuração para a seção Best Sellers. A posição define a ordem de exibição (1 = primeiro lugar).",
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
        "mark_as_best_seller",       # ✅ NOVO
        "unmark_as_best_seller",     # ✅ NOVO
        "set_best_seller_position",  # ✅ NOVO
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

    # ✅ NOVAS AÇÕES PARA BEST SELLERS

    @admin.action(description="Mark selected products as Best Sellers")
    def mark_as_best_seller(self, request, queryset):
        queryset.update(is_best_seller=True)

    @admin.action(description="Remove Best Seller flag from selected products")
    def unmark_as_best_seller(self, request, queryset):
        queryset.update(is_best_seller=False)

    @admin.action(description="Set Best Seller position (1-based)")
    def set_best_seller_position(self, request, queryset):
        # Esta ação abre um formulário para definir a posição
        # Mas como o Django admin não suporta facilmente isso, 
        # vamos apenas numerar sequencialmente os selecionados
        position = 1
        for product in queryset.order_by('id'):
            product.best_seller_position = position
            product.is_best_seller = True
            product.save()
            position += 1
        self.message_user(
            request, 
            f"Best Seller positions set from 1 to {position - 1} for {queryset.count()} products."
        )


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