from django.contrib import admin
from .models import Order, OrderItem, Coupon, MBwayPayment, MultibancoPayment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code", "discount_type", "discount_value",
        "min_order_value", "max_discount", "valid_from",
        "valid_to", "is_active", "used_count"
    ]
    list_filter = ["is_active", "discount_type"]
    search_fields = ["code"]
    ordering = ["-created_at"]


@admin.register(MBwayPayment)
class MBwayPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "phone", "authorized", "authorized_at",
        "request_id", "status", "amount", "created_at"
    ]
    list_filter = ["authorized"]
    search_fields = ["phone", "request_id"]
    readonly_fields = ["created_at"]


@admin.register(MultibancoPayment)
class MultibancoPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "entity", "reference", "amount", "paid",
        "paid_at", "request_id", "status", "created_at"
    ]
    list_filter = ["paid"]
    search_fields = ["entity", "reference", "request_id"]
    readonly_fields = ["created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_ref", "id", "user", "full_name", "email",
        "total", "status", "payment_method", "created_at"
    ]
    list_filter = ["status", "shipping_method", "payment_method", "user"]
    search_fields = ["order_ref", "full_name", "email", "id", "user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [OrderItemInline]

    fieldsets = (
        ("Cliente", {"fields": ("user", "full_name", "email")}),
        ("Morada", {"fields": ("street", "number", "floor", "postal_code", "city", "country")}),
        ("Envio e Pagamento", {
            "fields": ("shipping_method", "payment_method", "mbway_payment", "multibanco_payment")
        }),
        ("Cupão", {"fields": ("coupon", "coupon_discount")}),
        ("Valores", {"fields": ("subtotal", "shipping_cost", "total")}),
        ("Estado", {"fields": ("status",)}),
    )