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
    

""" class CategoryFiltersAPIView(APIView):
    def get(self, request, slug):
        variants = ProductVariant.objects.filter(
            product__category__slug=slug,
            product__is_active=True,
            stock__gt=0
        ).select_related("size", "material", "color")

        sizes = sorted({v.size.value for v in variants})
        materials = sorted({v.material.name for v in variants})
        colors = {
            v.color.name: v.color.hex_code
            for v in variants
        }

        return Response({
            "sizes": sizes,
            "materials": materials,
            "colors": [
                {"name": name, "hex": hex}
                for name, hex in colors.items()
            ],
        })
     """

class CategoryFiltersAPIView(APIView):
    def get(self, request, slug):

        variants = ProductVariant.objects.filter(
            product__is_active=True,
            stock__gt=0
        )

        # ✅ ONLY filter by category if slug != "all"
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
            .order_by("-created_at")[:8]  # limit homepage load
        )