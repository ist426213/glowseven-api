from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
from products.models import Product  # assumindo que o modelo Product existe


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    activation_token = models.CharField(max_length=64, blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_activation_token(self):
        self.activation_token = secrets.token_urlsafe(32)
        self.save()
        return self.activation_token

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Address(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, blank=True, help_text="Apelido da morada (ex: Casa, Trabalho)")
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    floor = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=150)
    country = models.CharField(max_length=100, default='Portugal')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = "Addresses"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user_profile=self.user_profile, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or 'Morada'} - {self.street}, {self.city}"


class Wishlist(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.product.name}"


# Sinais para criação automática do perfil
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.generate_activation_token()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()