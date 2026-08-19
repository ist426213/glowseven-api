from django.contrib import admin
from .models import (
    HeroBanner,
    VipMarketingSection,
    VipSubscriber,
    Testimonial,
    NewsletterSubscriber,
    ArtisanProcess
)

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "show_text",
        "media_type",
        "collection",
        "is_active",
        "order",
        "object_position_x_desktop",
        "object_position_y_desktop",
        "object_position_x_mobile",
        "object_position_y_mobile",
    )
    list_filter = ("is_active", "media_type", "show_text")
    search_fields = ("title",)

    fieldsets = (
        ("Conteúdo", {
            "fields": ("title", "subtitle", "media_type")
        }),
        ("Imagens", {
            "fields": ("image_desktop", "image_mobile"),
            "classes": ("collapse",),
        }),
        ("Vídeos", {
            "fields": ("video_desktop", "video_mobile"),
            "classes": ("collapse",),
        }),
        ("Enquadramento Desktop", {
            "fields": ("object_position_x_desktop", "object_position_y_desktop"),
            "description": "Posição do foco para desktop.",
        }),
        ("Enquadramento Mobile", {
            "fields": ("object_position_x_mobile", "object_position_y_mobile"),
            "description": "Posição do foco para mobile.",
        }),
        ("Call-to-Action", {
            "fields": ("cta_text", "collection")
        }),
        ("Exibição", {
            "fields": ("show_text", "is_active", "order")
        }),
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


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)


@admin.register(ArtisanProcess)
class ArtisanProcessAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("order",)

    fieldsets = (
        ("Conteúdo", {
            "fields": ("title", "description")
        }),
        ("Vídeos", {
            "fields": ("video_desktop", "video_mobile")
        }),
        ("Póster", {
            "fields": ("poster",),
            "description": "Imagem exibida antes do vídeo carregar (thumbnail)."
        }),
        ("Controlo", {
            "fields": ("is_active", "order")
        }),
    )


from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description="Marcar como lidas")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Marcar como não lidas")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)