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


# marketing/models.py

from django.db import models


class VipMarketingSection(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()

    # Media
    background_desktop = models.ImageField(upload_to="marketing/vip/desktop/")
    background_mobile = models.ImageField(upload_to="marketing/vip/mobile/")

    # Control
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# marketing/models.py

from django.contrib.auth.models import User


class VipSubscriber(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vip_profile",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)

    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional WhatsApp number",
    )

    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Testimonial(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)

    avatar = models.ImageField(
        upload_to="marketing/testimonials/",
        blank=True,
        null=True,
        help_text="Optional author photo",
    )

    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Rating from 1 to 5",
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.author} ({self.location})"