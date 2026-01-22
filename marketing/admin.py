from django.contrib import admin
from .models import HeroBanner


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "collection", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("order",)

    fieldsets = (
        (
            "Content",
            {
                "fields": ("title", "subtitle"),
            },
        ),
        (
            "Images",
            {
                "fields": ("image_desktop", "image_mobile"),
            },
        ),
        (
            "CTA (Optional)",
            {
                "fields": ("collection", "cta_text"),
            },
        ),
        (
            "Control",
            {
                "fields": ("order", "is_active"),
            },
        ),
    )
