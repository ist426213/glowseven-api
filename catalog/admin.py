from django.contrib import admin
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
