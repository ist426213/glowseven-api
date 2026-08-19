from django.contrib import admin
from .models import Collection
from products.models import Product


class ProductInline(admin.TabularInline):
    model = Product.collections.through
    extra = 1


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "title",
        "slug",
        "label",
        "tagline",
        "is_active",
        "is_visible",
    )
    list_display_links = ("title",)
    list_editable = ("order",)
    list_filter = ("is_active", "is_visible")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductInline]
    ordering = ("order", "title")

    fieldsets = (
        ("Collection Info", {
            "fields": ("title", "slug", "description", "label", "tagline")
        }),
        ("Media", {
            "fields": (
                "image",          # homepage
                "cover_image",    # página da coleção
                "is_active",
                "is_visible",
            )
        }),
        ("Ordenação", {
            "fields": ("order",),
            "classes": ("collapse",),
        }),
    )