from django.db import models
from catalog.models import Collection


class HeroBanner(models.Model):

    MEDIA_TYPES = (
        ("image", "Imagem"),
        ("video", "Vídeo"),
    )

    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)

    show_text = models.BooleanField(
        default=True,
        help_text="Se ativado, exibe título, subtítulo e CTA sobre o banner.",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        default="image",
        help_text="Selecione imagem ou vídeo para este banner.",
    )
    image_desktop = models.ImageField(
        upload_to="banners/desktop/",
        blank=True,
        null=True,
        help_text="Usado se media_type for 'image' ou como fallback.",
    )
    image_mobile = models.ImageField(
        upload_to="banners/mobile/",
        blank=True,
        null=True,
        help_text="Usado se media_type for 'image' ou como fallback.",
    )

    video_desktop = models.FileField(
        upload_to="banners/video/desktop/",
        blank=True,
        null=True,
        help_text="Vídeo para desktop (se media_type for 'video').",
    )
    video_mobile = models.FileField(
        upload_to="banners/video/mobile/",
        blank=True,
        null=True,
        help_text="Vídeo para mobile (se media_type for 'video').",
    )
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

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    POSITION_X_CHOICES = [
        ("left", "Esquerda"),
        ("center", "Centro"),
        ("right", "Direita"),
    ]
    POSITION_Y_CHOICES = [
        ("top", "Topo"),
        ("center", "Centro"),
        ("bottom", "Fundo"),
    ]

    # ---- Desktop ----
    object_position_x_desktop = models.CharField(
        max_length=10,
        choices=POSITION_X_CHOICES,
        default="center",
        help_text="Posição horizontal (desktop)."
    )
    object_position_y_desktop = models.CharField(
        max_length=10,
        choices=POSITION_Y_CHOICES,
        default="center",
        help_text="Posição vertical (desktop)."
    )

    # ---- Mobile ----
    object_position_x_mobile = models.CharField(
        max_length=10,
        choices=POSITION_X_CHOICES,
        default="center",
        help_text="Posição horizontal (mobile)."
    )
    object_position_y_mobile = models.CharField(
        max_length=10,
        choices=POSITION_Y_CHOICES,
        default="center",
        help_text="Posição vertical (mobile)."
    )


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title




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


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ArtisanProcess(models.Model):

    title = models.CharField(
        max_length=200,
        default="O luxo começa muito antes do primeiro passo."
    )
    description = models.TextField(
        default="Cada par Glow Seven nasce de um processo artesanal, onde a experiência, a precisão e a atenção aos detalhes se unem para criar sapatos elegantes, confortáveis e feitos para durar."
    )

    # Vídeos (separados por dispositivo)
    video_desktop = models.FileField(
        upload_to="marketing/artisan/videos/desktop/",
        blank=True,
        null=True,
        help_text="Vídeo para desktop (MP4, WebM)."
    )
    video_mobile = models.FileField(
        upload_to="marketing/artisan/videos/mobile/",
        blank=True,
        null=True,
        help_text="Vídeo para mobile (MP4, WebM)."
    )

    # Póster (thumbnail) – opcional
    poster = models.ImageField(
        upload_to="marketing/artisan/posters/",
        blank=True,
        null=True,
        help_text="Imagem de pré-visualização (exibida antes do vídeo carregar)."
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title



class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'Sem assunto'}"