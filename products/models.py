from django.db import models
from categories.models import Category
from catalog.models import Collection

class Size(models.Model):
    value = models.CharField(max_length=5)  # 36, 37, 38...

    class Meta:
        ordering = ["value"]

    def __str__(self):
        return self.value


class Material(models.Model):
    name = models.CharField(max_length=50)  # Couro, Sintético

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)      
    hex_code = models.CharField(max_length=7)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    # Media
    image = models.ImageField(upload_to="products/")

    # Content
    summary = models.CharField(
        max_length=255,
        blank=True,
        help_text="Resumo curto exibido no topo do produto",
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição longa do produto",
    )
    details = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de detalhes (bullet points)",
    )

    # Marketing / UI
    tag = models.CharField(
        max_length=50,
        blank=True,
        help_text="Etiqueta visual: Novo, Promoção, Mais Vendido, etc",
    )

    # Commerce
    sku = models.CharField(max_length=50, blank=True)
    shipping_info = models.CharField(
        max_length=255,
        blank=True,
        default="Envio em 1–2 dias úteis. Devolução grátis em 30 dias.",
    )

    # Flags (logic, not labels)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )

    collections = models.ManyToManyField(
        Collection,
        related_name="products",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def in_promo(self):
        return bool(self.original_price and self.original_price > self.price)



class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "size", "material")

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.material}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/gallery/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} image"