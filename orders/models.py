from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import secrets
import string


def generate_order_ref():
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))


class Coupon(models.Model):
    
    """Modelo para cupões de desconto."""
    DISCOUNT_TYPES = [
        ("percent", "Percentagem"),
        ("fixed", "Valor Fixo"),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default="percent")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self, cart_total):
        from django.utils.timezone import now
        if not self.is_active:
            return False, "Cupão inativo"
        if now() < self.valid_from or now() > self.valid_to:
            return False, "Cupão expirado"
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Limite de utilizações esgotado"
        if self.min_order_value and cart_total < self.min_order_value:
            return False, f"Valor mínimo de compra: €{self.min_order_value}"
        return True, ""

    def apply_discount(self, subtotal):
        if self.discount_type == "percent":
            discount = (self.discount_value / 100) * subtotal
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        return min(self.discount_value, subtotal)


class MBwayPayment(models.Model):
    """Dados do pagamento MBWAY."""
    phone = models.CharField(max_length=20)
    authorized = models.BooleanField(default=False)
    authorized_at = models.DateTimeField(null=True, blank=True)
    request_id = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    message = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MBWAY {self.phone} - {self.status}"


class MultibancoPayment(models.Model):
    """Dados do pagamento Multibanco."""
    entity = models.CharField(max_length=50, blank=True)
    reference = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    request_id = models.CharField(max_length=50, blank=True)
    order_id = models.CharField(max_length=25, blank=True)
    expiry_date = models.CharField(max_length=20, blank=True)
    message = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Multibanco {self.reference}"


class Order(models.Model):
    """Modelo principal de encomenda."""
    PAYMENT_METHODS = [
        ("mbway", "MBWAY"),
        ("multibanco", "Multibanco"),
        ("credit_card", "Cartão de Crédito"),
    ]
    SHIPPING_METHODS = [
        ("normal", "CTT Normal"),
        ("express", "CTT Express"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("shipped", "Enviado"),
        ("delivered", "Entregue"),
        ("cancelled", "Cancelado"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Cliente
    email = models.EmailField()
    full_name = models.CharField(max_length=120)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=50)
    floor = models.CharField(max_length=50, blank=True, default='')
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=150)
    country = models.CharField(max_length=100, default="Portugal")

    # Envio
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default="normal")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Pagamento
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="mbway")
    mbway_phone = models.CharField(max_length=50, blank=True, default='')
    multibanco_ref = models.CharField(max_length=50, blank=True, default='')
    multibanco_entity = models.CharField(max_length=50, blank=True, default='')

    # Cupão
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Valores
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Referência pública
    order_ref = models.CharField(
        max_length=8,
        unique=True,
        db_index=True,
        editable=False,
        default=generate_order_ref,
        help_text="Identificador único alfanumérico (8 caracteres)."
    )

    # Relações com pagamentos
    mbway_payment = models.OneToOneField(
        MBwayPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order"
    )
    multibanco_payment = models.OneToOneField(
        MultibancoPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_ref} - {self.full_name}"

    @property
    def items_count(self):
        return self.items.count()

    def save(self, *args, **kwargs):
        if not self.order_ref:
            self.order_ref = generate_order_ref()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Item individual de uma encomenda."""
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=50, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"