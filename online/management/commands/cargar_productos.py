from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from online.models import Categoria, Producto


PRODUCTOS_INICIALES = [
    {
        "nombre": "Detergente líquido biodegradable Cítrico",
        "categoria": "Limpieza del hogar",
        "marca": "Bioclar",
        "medida": 1.0,
        "unidad": "L",
        "precio": 6990,
        "stock": 25,
        "aroma": "Cítrico",
        "destacado": True,
        "imagen": "detergentes_citrico_eucalipto.jpg",
        "descripcion": (
            "Detergente líquido concentrado formulado con nanoemulsiones verdes y extractos "
            "cítricos obtenidos a partir de residuos agroindustriales. Limpia en profundidad "
            "cuidando las fibras y el agua."
        ),
    },
    {
        "nombre": "Detergente líquido concentrado Eucalipto",
        "categoria": "Limpieza del hogar",
        "marca": "Bioclar",
        "medida": 1.0,
        "unidad": "L",
        "precio": 6990,
        "stock": 20,
        "aroma": "Eucalipto",
        "destacado": False,
        "imagen": "detergente_concentrado.jpg",
        "descripcion": (
            "Fórmula biodegradable de alto rendimiento con aceite esencial de eucalipto "
            "y activos antimicrobianos de origen vegetal. Ideal para ropa blanca y de color."
        ),
    },
    {
        "nombre": "Dúo Detergente Bioclar (Cítrico + Eucalipto)",
        "categoria": "Packs",
        "marca": "Bioclar",
        "medida": 2.0,
        "unidad": "L",
        "precio": 12990,
        "stock": 14,
        "aroma": "Cítrico y Eucalipto",
        "destacado": True,
        "imagen": "detergentes_par.jpg",
        "descripcion": (
            "Pack de dos botellas de 1 L de detergente líquido biodegradable Bioclar en sus "
            "dos variedades: cítrico y eucalipto."
        ),
    },
    {
        "nombre": "Pack Familiar Limpieza Sustentable",
        "categoria": "Packs",
        "marca": "Bioclar",
        "medida": 4.0,
        "unidad": "L",
        "precio": 23990,
        "stock": 8,
        "aroma": "Natural",
        "destacado": False,
        "imagen": "pack_detergentes.jpg",
        "descripcion": (
            "Pack ahorro pensado para el hogar o comercios: cuatro formatos de detergente "
            "concentrado biodegradable con activos vegetales."
        ),
    },
    {
        "nombre": "Champú sólido Bio-Renua Romero y Menta",
        "categoria": "Cuidado personal",
        "marca": "Biorenua",
        "medida": 90,
        "unidad": "g",
        "precio": 8990,
        "stock": 18,
        "aroma": "Romero y Menta",
        "destacado": True,
        "imagen": "shampoo_solido_biorenua.jpg",
        "descripcion": (
            "Champú sólido vegano y libre de sulfatos agresivos, enriquecido con extractos "
            "botánicos de origen circular para fortalecer el cabello sin generar envases plásticos."
        ),
    },
    {
        "nombre": "Champú sólido Bio-Renua Hierbas Verdes",
        "categoria": "Cuidado personal",
        "marca": "Biorenua",
        "medida": 90,
        "unidad": "g",
        "precio": 8990,
        "stock": 15,
        "aroma": "Herbal",
        "destacado": False,
        "imagen": "shampoo_solido_verde.jpg",
        "descripcion": (
            "Barra capilar biodegradable con extractos vegetales y aceites esenciales que "
            "equilibran el cuero cabelludo con espuma suave y cremosa."
        ),
    },
    {
        "nombre": "Sales de baño minerales Bio-Renua",
        "categoria": "Cuidado personal",
        "marca": "Biorenua",
        "medida": 300,
        "unidad": "g",
        "precio": 7490,
        "stock": 12,
        "aroma": "Lavanda",
        "destacado": True,
        "imagen": "sales_de_bano.jpg",
        "descripcion": (
            "Sales de baño relajantes elaboradas con minerales naturales y aceites esenciales "
            "extraídos mediante procesos de bajo impacto ambiental."
        ),
    },
    {
        "nombre": "Trío Sales de baño aromáticas",
        "categoria": "Packs",
        "marca": "Biorenua",
        "medida": 750,
        "unidad": "g",
        "precio": 18990,
        "stock": 6,
        "aroma": "Surtido",
        "destacado": False,
        "imagen": "sales_de_bano_trio.jpg",
        "descripcion": (
            "Set de tres frascos de sales de baño Bio-Renua con distintos aromas botánicos "
            "para una experiencia de cuidado personal consciente."
        ),
    },
]


class Command(BaseCommand):
    help = "Carga categorías y productos iniciales usando las imágenes de recursos/imagenes_productos/."

    def handle(self, *args, **options):
        carpeta_imagenes = Path(settings.BASE_DIR) / "recursos" / "imagenes_productos"
        creados = 0
        actualizados = 0

        for item in PRODUCTOS_INICIALES:
            categoria, _ = Categoria.objects.get_or_create(nombre=item["categoria"])
            producto, creado = Producto.objects.get_or_create(
                nombre=item["nombre"],
                defaults={
                    "categoria": categoria,
                    "marca": item["marca"],
                    "medida": item["medida"],
                    "unidad": item["unidad"],
                    "precio": item["precio"],
                    "stock": item["stock"],
                    "aroma": item["aroma"],
                    "destacado": item["destacado"],
                    "descripcion": item["descripcion"],
                },
            )

            ruta_imagen = carpeta_imagenes / item["imagen"]
            if ruta_imagen.exists() and not producto.imagen:
                with ruta_imagen.open("rb") as archivo:
                    producto.imagen.save(item["imagen"], File(archivo), save=True)

            if creado:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga completada: {creados} productos creados, {actualizados} ya existían. "
                f"Total en BD: {Producto.objects.count()}."
            )
        )
