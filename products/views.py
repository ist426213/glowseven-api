# views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Product
from .serializers import ProductSerializer, ProductDetailSerializer
from .models import ProductVariant
from rest_framework.views import APIView
from rest_framework.response import Response


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class ProductByCategoryAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        qs = Product.objects.filter(
            category__slug=slug,
            is_active=True
        )

        # --- Filters ---
        size = self.request.query_params.getlist("size")
        color = self.request.query_params.getlist("color")
        material = self.request.query_params.getlist("material")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if size:
            qs = qs.filter(variants__size__value__in=size)
        
        if color:
            qs = qs.filter(variants__color__name__in=color)

        if material:
            qs = qs.filter(variants__material__name__in=material)

        if min_price:
            qs = qs.filter(price__gte=min_price)

        if max_price:
            qs = qs.filter(price__lte=max_price)

        return qs.distinct()
    

class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                "variants",
                "variants__size",
                "variants__material",
                "variants__color",
            )
        )


class CategoryFiltersAPIView(APIView):
    def get(self, request, slug):
        variants = ProductVariant.objects.filter(
            product__is_active=True,
            stock__gt=0
        )

        if slug != "all":
            variants = variants.filter(product__category__slug=slug)

        variants = variants.select_related("size", "material", "color")

        sizes = sorted({v.size.value for v in variants if v.size})
        materials = sorted({v.material.name for v in variants if v.material})

        colors = {}
        for v in variants:
            if v.color:
                colors[v.color.name] = v.color.hex_code

        return Response({
            "sizes": sizes,
            "materials": materials,
            "colors": [
                {"name": name, "hex": hex}
                for name, hex in colors.items()
            ],
        })


class FeaturedProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True, is_featured=True)
            .select_related("category")
            .order_by("-created_at")[:8]
        )


# NOVO: Best Sellers API View
class BestSellersListAPIView(ListAPIView):
    """
    Retorna os produtos marcados como Best Sellers, ordenados por posição.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True, is_best_seller=True)
            .select_related("category")
            .order_by("best_seller_position")[:10]  # Limite de 10 best sellers
        )




from rest_framework import status
from .models import ProductVariant, StockNotification
from .serializers import StockNotificationSerializer
from rest_framework.permissions import AllowAny

class StockNotificationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StockNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        size = serializer.validated_data["size"].strip()
        email = serializer.validated_data["email"].lower().strip()
        intent = serializer.validated_data["intent"]

        variants = ProductVariant.objects.filter(product=product, size__value=size)

        if variants.filter(stock__gt=0).exists():
            return Response(
                {"detail": f"O tamanho {size} encontra-se disponível para compra.", "available": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification, created = StockNotification.objects.get_or_create(
            product=product,
            size=size,
            email=email,
            defaults={"intent": intent},
        )

        if not created and notification.intent != intent:
            notification.intent = intent
            notification.save(update_fields=["intent"])

        return Response(
            {
                "detail": (
                    "O teu pedido de encomenda foi registado. Entraremos em contacto contigo assim que possível."
                    if intent == "ORDER"
                    else "Registámos o teu pedido. Avisaremos por email assim que este tamanho estiver disponível."
                ),
                "already_registered": not created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )