from django.core.management.base import BaseCommand
from categories.models import Category
from products.models import Product
from catalog.models import Collection


class Command(BaseCommand):
    help = "Seed development data (small & realistic)"

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Seeding DEV data...")

        self.categories = self.create_categories()
        self.create_collections()
        self.create_products()

        self.stdout.write(self.style.SUCCESS("✅ DEV data seeded"))

    # -----------------
    # Categories (6)
    # -----------------
    def create_categories(self):
        data = [
            ("Saltos", "saltos", "categories/heels.jpg"),
            ("Tênis", "tenis", "categories/sneakers.webp"),
            ("Botas", "botas", "categories/boots.avif"),
            ("Sandálias", "sandalias", "categories/sandals.avif"),
            ("Sapatilhas", "sapatilhas", "categories/flats.webp"),
            ("Promoções", "promocoes", "categories/sale.jpg"),
        ]

        categories = []

        for name, slug, image in data:
            obj, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "image": image,
                    "is_active": True,
                },
            )
            categories.append(obj)

        return categories

    # -----------------
    # Collections (3)
    # -----------------
    def create_collections(self):
        data = [
            ("Performance", "performance", "Projetados para estilos de vida ativos"),
            ("Dia a Dia", "dia-a-dia", "Conforto diário com estilo"),
            ("Aventura", "aventura", "Feitos para explorar"),
        ]

        for title, slug, desc in data:
            Collection.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "description": desc,
                    "image": "collections/collection_01.webp",
                    "is_active": True,
                },
            )

    # -----------------
    # Products (24 max)
    # -----------------
    def create_products(self):
        base_products = [
            ("Stride Pro", 129, 149, "Novo", 7),
            ("Urban Flow", 99, None, "Vegano", 4),
            ("Trail Hawk", 149, None, "Impermeável", 5),
            ("Everyday Cloud", 89, 109, "Leve", 6),
        ]

        count = 0

        for category in self.categories:
            for name, price, original, tag, colors in base_products:
                if count >= 24:
                    return

                slug = f"{name.lower().replace(' ', '-')}-{category.slug}"

                Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": f"{name} {category.name}",
                        "price": price,
                        "original_price": original,
                        "tag": tag,
                        "colors": colors,
                        "category": category,
                        "image": "products/prod_01.jpg",
                        "is_active": True,
                    },
                )

                count += 1
