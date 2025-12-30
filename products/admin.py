from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "original_price",
        "is_active",
        "created_at",
    )

    list_filter = ("category", "is_active")
    search_fields = ("name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

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
            "Pricing",
            {
                "fields": (
                    "price",
                    "original_price",
                )
            },
        ),
        (
            "Display",
            {
                "fields": (
                    "image",
                    "colors",
                    "is_active",
                )
            },
        ),
    )
