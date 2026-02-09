from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "is_visible")
    list_filter = ("is_active", "is_visible")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
