from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Order, OrderItem
from .serializers import CheckoutSerializer
from products.models import Product


class CheckoutAPIView(APIView):
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        items_data = data.pop("items")

        subtotal = Decimal("0.00")
        order_items = []

        for item in items_data:
            product = get_object_or_404(Product, id=item["product_id"])
            quantity = item["quantity"]

            subtotal += product.price * quantity
            order_items.append((product, quantity, product.price))

        with transaction.atomic():
            order = Order.objects.create(
                subtotal=subtotal,
                total=subtotal,
                **data,
            )

            for product, quantity, price in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                )

        return Response(
            {
                "order_id": order.id,
                "status": order.status,
                "total": order.total,
            },
            status=status.HTTP_201_CREATED,
        )
