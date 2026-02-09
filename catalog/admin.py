""" from django.contrib import admin
from .models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (
            "Collection Info",
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "image",
                    "is_active",
                )
            },
        ),
    )
 """

from django.contrib import admin
from .models import Collection
from products.models import Product

class ProductInline(admin.TabularInline):
    model = Product.collections.through
    extra = 1

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "is_visible")
    list_filter = ("is_active", "is_visible")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

    inlines = [ProductInline]

    exclude = ("products",)
