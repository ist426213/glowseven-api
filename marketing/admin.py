from django.contrib import admin
from .models import (
    HeroBanner, 
    VipMarketingSection, 
    VipSubscriber, 
    Testimonial
)


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


@admin.register(VipMarketingSection)
class VipMarketingSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Content",
            {
                "fields": ("title", "description"),
            },
        ),
        (
            "Images",
            {
                "fields": ("background_desktop", "background_mobile"),
            },
        ),
        (
            "Control",
            {
                "fields": ("is_active",),
            },
        ),
    )


@admin.register(VipSubscriber)
class VipSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "whatsapp",
        "is_active",
        "subscribed_at",
    )

    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email", "name", "whatsapp")
    ordering = ("-subscribed_at",)

    readonly_fields = ("subscribed_at",)

    fieldsets = (
        (
            "Subscriber Info",
            {
                "fields": ("name", "email", "whatsapp"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("subscribed_at",),
            },
        ),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "location",
        "rating",
        "is_active",
        "order",
    )

    list_filter = ("is_active", "rating")
    search_fields = ("author", "quote", "location")
    ordering = ("order",)

    fieldsets = (
        (
            "Testimonial",
            {
                "fields": ("quote",),
            },
        ),
        (
            "Author",
            {
                "fields": ("author", "location", "avatar"),
            },
        ),
        (
            "Rating & Control",
            {
                "fields": ("rating", "order", "is_active"),
            },
        ),
    )