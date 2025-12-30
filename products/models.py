from django.db import models
from categories.models import Category

class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    image = models.ImageField(upload_to="products/")
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )

    tag = models.CharField(max_length=50, blank=True)
    colors = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
