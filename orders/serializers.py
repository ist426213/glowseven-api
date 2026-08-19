from rest_framework import serializers
from .models import Order, OrderItem, Coupon, MBwayPayment, MultibancoPayment
from products.models import Product


class OrderItemInputSerializer(serializers.Serializer):
    """Serializer para entrada de itens no checkout."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    size = serializers.CharField(required=False, allow_blank=True)
    color = serializers.CharField(required=False, allow_blank=True)


class CouponValidateSerializer(serializers.Serializer):
    """Serializer para validação de cupão."""
    code = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        code = data.get("code")
        subtotal = data.get("subtotal")
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Cupão inválido.")
        valid, msg = coupon.is_valid(subtotal)
        if not valid:
            raise serializers.ValidationError(msg)
        data["coupon"] = coupon
        data["discount"] = coupon.apply_discount(subtotal)
        return data


class CheckoutSerializer(serializers.Serializer):
    """Serializer para o checkout completo."""
    email = serializers.EmailField()
    full_name = serializers.CharField()
    street = serializers.CharField()
    number = serializers.CharField()
    floor = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField(default="Portugal")

    shipping_method = serializers.ChoiceField(choices=Order.SHIPPING_METHODS)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHODS)
    mbway_phone = serializers.CharField(required=False, allow_blank=True)

    coupon_code = serializers.CharField(required=False, allow_blank=True)

    items = OrderItemInputSerializer(many=True)

    def validate(self, data):
        if data["payment_method"] == "mbway" and not data.get("mbway_phone"):
            raise serializers.ValidationError("Número de telemóvel obrigatório para MBWAY.")

        if not data["items"]:
            raise serializers.ValidationError("Carrinho vazio.")

        subtotal = 0
        for item in data["items"]:
            try:
                product = Product.objects.get(id=item["product_id"], is_active=True)
                if not product.is_active:
                    raise serializers.ValidationError(f"Produto {product.name} indisponível.")
                item["_product"] = product
                item["_price"] = product.price
                subtotal += product.price * item["quantity"]
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Produto {item['product_id']} não encontrado.")

        data["subtotal"] = subtotal

        shipping_cost = 10 if data["shipping_method"] == "express" else 0
        data["shipping_cost"] = shipping_cost

        coupon_code = data.get("coupon_code", "").strip()
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                valid, msg = coupon.is_valid(subtotal)
                if valid:
                    discount = coupon.apply_discount(subtotal)
                    data["coupon"] = coupon
                    data["coupon_discount"] = discount
                    subtotal -= discount
                else:
                    raise serializers.ValidationError(msg)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Cupão inválido.")
        else:
            data["coupon"] = None
            data["coupon_discount"] = 0

        data["total"] = subtotal + shipping_cost
        return data


class MBwayPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBwayPayment
        fields = [
            "id", "phone", "authorized", "authorized_at",
            "request_id", "amount", "message", "status", "raw_data", "created_at"
        ]


class MultibancoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultibancoPayment
        fields = [
            "id", "entity", "reference", "amount", "paid", "paid_at",
            "request_id", "order_id", "expiry_date", "message", "status", "raw_data", "created_at"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "product_price", "quantity", "size", "color"]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer principal para encomendas."""
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    mbway_payment = MBwayPaymentSerializer(read_only=True)
    multibanco_payment = MultibancoPaymentSerializer(read_only=True)

    payment_details = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id", "email", "full_name", "street", "number", "floor",
            "postal_code", "city", "country", "shipping_method",
            "payment_method", "coupon_discount", "subtotal",
            "shipping_cost", "total", "status", "created_at",
            "items", "items_count",
            "mbway_payment", "multibanco_payment", "payment_details"
        ]

    def get_order_id(self, obj):
        return obj.order_ref

    def get_payment_details(self, obj):
        if obj.payment_method == "mbway" and obj.mbway_payment:
            return {
                "phone": obj.mbway_payment.phone,
                "authorized": obj.mbway_payment.authorized,
                "status": obj.mbway_payment.status,
            }
        elif obj.payment_method == "multibanco" and obj.multibanco_payment:
            return {
                "entity": obj.multibanco_payment.entity,
                "reference": obj.multibanco_payment.reference,
                "amount": str(obj.multibanco_payment.amount),
                "paid": obj.multibanco_payment.paid,
                "status": obj.multibanco_payment.status,
            }
        return None