"""
CAJA NEGRA — Pruebas de catálogo: inicio, tienda y detalle de producto.

Clase:
  CatalogoTests → respuestas HTTP, contenido de templates y contexto de vistas
                  sin conocer los detalles internos de las vistas.
"""

from django.test import TestCase
from django.urls import reverse

from online.models import Categoria, Producto


# ---------------------------------------------------------------------------
# Helper compartido
# ---------------------------------------------------------------------------

def crear_producto(categoria, nombre='Detergente Cítrico', precio=8990, **extra):
    """Crea un producto con valores mínimos válidos."""
    datos = {
        'nombre': nombre,
        'precio': precio,
        'stock': 10,
        'descripcion': 'Detergente biodegradable de origen vegetal.',
        'categoria': categoria,
        'marca': 'bioproductos dk',
    }
    datos.update(extra)
    return Producto.objects.create(**datos)


# ---------------------------------------------------------------------------
# Pruebas de catálogo
# ---------------------------------------------------------------------------

class CatalogoTests(TestCase):
    """
    CAJA NEGRA — Comportamiento observable del catálogo desde el exterior.

    Se realizan peticiones HTTP reales al cliente de test y se verifica el
    código de estado, el template usado y el contexto devuelto, sin asumir
    nada sobre la implementación interna de las vistas.
    """

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')
        self.cuidado = Categoria.objects.create(nombre='Cuidado personal')
        self.citrico = crear_producto(self.limpieza, 'Detergente Cítrico', destacado=True)
        self.eucalipto = crear_producto(self.limpieza, 'Detergente Eucalipto')
        self.champu = crear_producto(self.cuidado, 'Champú sólido', precio=6990)

    def test_inicio_muestra_solo_productos_destacados(self):
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'index.html')
        self.assertEqual(list(respuesta.context['productosDestacados']), [self.citrico])

    def test_tienda_lista_todos_los_productos(self):
        respuesta = self.client.get(reverse('tienda'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context['productos']), 3)

    def test_tienda_filtra_por_categoria(self):
        respuesta = self.client.get(reverse('tiendaCategoria', args=['Cuidado personal']))
        self.assertEqual(list(respuesta.context['productos']), [self.champu])
        self.assertEqual(respuesta.context['categoriaActual'], 'Cuidado personal')

    def test_busqueda_no_distingue_mayusculas(self):
        respuesta = self.client.get(reverse('tienda'), {'busqueda': 'DETERGENTE'})
        nombres = {p.nombre for p in respuesta.context['productos']}
        self.assertEqual(nombres, {'Detergente Cítrico', 'Detergente Eucalipto'})

    def test_busqueda_sin_resultados(self):
        respuesta = self.client.get(reverse('tienda'), {'busqueda': 'xyz'})
        self.assertEqual(len(respuesta.context['productos']), 0)

    def test_detalle_de_producto(self):
        respuesta = self.client.get(reverse('detalleProducto', args=[self.citrico.id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Detergente Cítrico')

    def test_relacionados_son_de_la_misma_categoria_y_excluyen_el_actual(self):
        respuesta = self.client.get(reverse('detalleProducto', args=[self.citrico.id]))
        self.assertEqual(list(respuesta.context['productosRelacionados']), [self.eucalipto])

    def test_relacionados_son_maximo_cuatro(self):
        for i in range(6):
            crear_producto(self.limpieza, f'Detergente {i}')
        respuesta = self.client.get(reverse('detalleProducto', args=[self.citrico.id]))
        self.assertEqual(len(respuesta.context['productosRelacionados']), 4)

    def test_producto_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse('detalleProducto', args=[9999]))
        self.assertEqual(respuesta.status_code, 404)
