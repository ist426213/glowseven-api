from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Address, Wishlist


# ✅ UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "phone")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


# ✅ Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user_profile",
        "name",
        "street",
        "number",
        "postal_code",
        "city",
        "country",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default", "country", "created_at")
    search_fields = (
        "user_profile__user__username",
        "user_profile__user__email",
        "name",
        "street",
        "city",
        "postal_code",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-is_default", "-created_at")
    list_select_related = ("user_profile",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user_profile__user")


# ✅ Wishlist Admin (corrigido)
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "product", "created_at")        # ← campos corretos
    list_filter = ("created_at",)
    search_fields = ("user_profile__user__username", "user_profile__user__email", "product__name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


# ✅ Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )


# Re-registar o User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)