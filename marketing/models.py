from django.db import models
from catalog.models import Collection


class HeroBanner(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)

    # Media
    image_desktop = models.ImageField(upload_to="banners/desktop/")
    image_mobile = models.ImageField(upload_to="banners/mobile/")

    # Optional CTA
    collection = models.ForeignKey(
        Collection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="banners",
        help_text="Optional: if set, banner button links to this collection",
    )

    cta_text = models.CharField(
        max_length=50,
        blank=True,
        default="Explorar Coleção",
    )

    # Control
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
