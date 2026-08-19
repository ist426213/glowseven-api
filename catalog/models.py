from django.db import models

class Collection(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to="collections/", help_text="Imagem para a homepage")
    cover_image = models.ImageField(upload_to="collections/covers/", blank=True, null=True, help_text="Imagem de capa para a página da coleção")
    label = models.CharField(max_length=50, default="COLEÇÃO", help_text="Ex: COLEÇÃO OUTONO")
    tagline = models.CharField(max_length=120, blank=True, help_text="Ex: Elegância intemporal")
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Ordem de exibição (menor primeiro)")

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
