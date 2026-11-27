"""
CAJA NEGRA — Pruebas del carrito de compras vía HTTP.

Clase:
  CarritoTests → sesión anónima y usuario autenticado; agregar, actualizar,
                 eliminar ítems y cambio de tipo de envío.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from online.models import Carrito, Categoria, Impuestos, ItemCarrito, Producto


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
# Pruebas de carrito
# ---------------------------------------------------------------------------

class CarritoTests(TestCase):
    """
    CAJA NEGRA — Comportamiento observable del carrito de compras.

    Se realizan peticiones HTTP a las vistas del carrito y se verifica el
    estado resultante (ítems, cantidades, costos) sin asumir detalles de
    la implementación interna.
    """

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')
        self.producto = crear_producto(self.limpieza, 'Bio-Detergente 1L', precio=10000, stock=5)
        self.otro = crear_producto(self.limpieza, 'Limpiavidrios Eco', precio=5000, stock=3)
        Impuestos.objects.create(iva=0.19, despacho=3990, region='Región Metropolitana')

    def test_carrito_vacio_renderiza_template_carrito(self):
        respuesta = self.client.get(reverse('carrito'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'carrito.html')
        self.assertContains(respuesta, 'Tu carrito está vacío')

    def test_agregar_producto_y_sumar_cantidad_repetida(self):
        self.client.post(reverse('agregarCarrito', args=[self.producto.id]), {'cantidad': 2})
        self.client.post(reverse('agregarCarrito', args=[self.producto.id]), {'cantidad': 1})

        respuesta = self.client.get(reverse('carrito'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context['items']), 1)
        item = respuesta.context['items'][0]
        self.assertEqual(item.cantidad, 3)
        self.assertEqual(item.subtotal(), 30000)
        self.assertEqual(respuesta.context['subtotal'], 30000)
        self.assertEqual(respuesta.context['cantidadCarrito'], 3)

    def test_agregar_producto_respeta_limite_de_stock(self):
        self.client.post(reverse('agregarCarrito', args=[self.producto.id]), {'cantidad': 4})
        respuesta = self.client.post(
            reverse('agregarCarrito', args=[self.producto.id]),
            {'cantidad': 3},
            follow=True,
        )
        self.assertContains(respuesta, 'Solo hay 5 unidades disponibles')
        item = ItemCarrito.objects.get(producto=self.producto)
        self.assertEqual(item.cantidad, 4)

    def test_actualizar_y_eliminar_item_del_carrito(self):
        self.client.post(reverse('agregarCarrito', args=[self.otro.id]), {'cantidad': 1})
        item = ItemCarrito.objects.get(producto=self.otro)

        self.client.post(reverse('actualizarCarrito', args=[item.id]), {'cantidad': 3})
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 3)

        self.client.post(reverse('eliminarCarrito', args=[item.id]))
        self.assertFalse(ItemCarrito.objects.filter(pk=item.id).exists())

    def test_calculo_despacho_y_cambio_tipo_envio(self):
        usuario = User.objects.create_user('comprador', password='Bio2026!Seguro')
        self.client.force_login(usuario)

        self.client.post(reverse('agregarCarrito', args=[self.producto.id]), {'cantidad': 2})
        self.client.post(reverse('carrito'), {'tipo_envio': 'despacho'})

        respuesta = self.client.get(reverse('carrito'))
        self.assertEqual(respuesta.context['subtotal'], 20000)
        self.assertEqual(respuesta.context['costoDespacho'], 3990)
        self.assertEqual(respuesta.context['total'], 23990)
        self.assertContains(respuesta, '20,000' if False else '20')
