"""
CAJA BLANCA — Pruebas de helpers/funciones privadas de views.py.

Clases:
  CalcularResumenCarritoTests  → _calcular_resumen_carrito() con los tres tipos de envío
  FusionarCarritoSesionTests   → _fusionar_carrito_sesion() al hacer login
"""

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from online.models import (
    Carrito,
    Categoria,
    Impuestos,
    ItemCarrito,
    Producto,
)
from online.views import _calcular_resumen_carrito, _fusionar_carrito_sesion


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
# _calcular_resumen_carrito()
# ---------------------------------------------------------------------------

class CalcularResumenCarritoTests(TestCase):
    """
    CAJA BLANCA — Verifica la lógica interna de _calcular_resumen_carrito().

    Se llama directamente a la función privada con distintos tipos de envío
    y se comprueba que el subtotal, costo de despacho y total sean correctos.
    Se usa RequestFactory para construir un request mínimo (usuario anónimo).
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.limpieza = Categoria.objects.create(nombre='Limpieza')
        self.producto = crear_producto(self.limpieza, precio=10000, stock=5)
        Impuestos.objects.create(iva=0.19, despacho=3990, region='Región Metropolitana')

    def _request_anonimo(self):
        """Request GET mínimo con usuario anónimo."""
        from django.contrib.auth.models import AnonymousUser
        req = self.factory.get('/')
        req.user = AnonymousUser()
        return req

    def _carrito_con_items(self, tipo_envio='retiro', cantidad=2):
        carrito = Carrito.objects.create(tipo_envio=tipo_envio)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=cantidad)
        return carrito

    def test_retiro_sin_costo_de_despacho(self):
        """tipo_envio='retiro' → costoDespacho=0 y total=subtotal."""
        carrito = self._carrito_con_items(tipo_envio='retiro', cantidad=1)
        resumen = _calcular_resumen_carrito(self._request_anonimo(), carrito)
        self.assertEqual(resumen['subtotal'], 10000)
        self.assertEqual(resumen['costoDespacho'], 0)
        self.assertEqual(resumen['total'], 10000)

    def test_despacho_normal_suma_costo_fijo(self):
        """tipo_envio='despacho' → costoDespacho=3990 tomado de Impuestos."""
        carrito = self._carrito_con_items(tipo_envio='despacho', cantidad=2)
        resumen = _calcular_resumen_carrito(self._request_anonimo(), carrito)
        self.assertEqual(resumen['subtotal'], 20000)
        self.assertEqual(resumen['costoDespacho'], 3990)
        self.assertEqual(resumen['total'], 23990)

    def test_envio_express_cobra_1_5_del_despacho(self):
        """tipo_envio='envio_express' → costoDespacho = despacho * 1.5."""
        carrito = self._carrito_con_items(tipo_envio='envio_express', cantidad=1)
        resumen = _calcular_resumen_carrito(self._request_anonimo(), carrito)
        self.assertEqual(resumen['subtotal'], 10000)
        self.assertEqual(resumen['costoDespacho'], round(3990 * 1.5))
        self.assertEqual(resumen['total'], 10000 + round(3990 * 1.5))

    def test_cantidad_total_items_en_resumen(self):
        """La lista 'items' en el resumen refleja todos los ítems del carrito."""
        carrito = self._carrito_con_items(tipo_envio='retiro', cantidad=3)
        resumen = _calcular_resumen_carrito(self._request_anonimo(), carrito)
        self.assertEqual(len(resumen['items']), 1)
        self.assertEqual(resumen['items'][0].cantidad, 3)


# ---------------------------------------------------------------------------
# _fusionar_carrito_sesion()
# ---------------------------------------------------------------------------

class FusionarCarritoSesionTests(TestCase):
    """
    CAJA BLANCA — Verifica la lógica interna de _fusionar_carrito_sesion().

    Simula que un usuario anónimo tiene ítems en su carrito de sesión y luego
    hace login; los ítems deben fusionarse en el carrito del usuario autenticado.
    Se usa el cliente de test para que la sesión esté disponible.
    """

    CLAVE = 'Bio2026!Seguro'

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')
        self.p1 = crear_producto(self.limpieza, 'P1', precio=5000, stock=10)
        self.p2 = crear_producto(self.limpieza, 'P2', precio=3000, stock=4)
        self.usuario = User.objects.create_user('comprador', password=self.CLAVE)

    def _request_con_sesion(self, carrito_sesion):
        """Crea un request con sesión que apunta al carrito anónimo dado."""
        from django.contrib.auth.models import AnonymousUser
        from django.test import RequestFactory
        req = RequestFactory().get('/')
        # Simulamos la sesión usando el middleware de sesión de Django
        from django.test import Client
        client = Client()
        # Accedemos a la sesión vía client para que sea una sesión real
        session = client.session
        session['carrito_id'] = carrito_sesion.id
        session.save()
        req.session = session
        req.user = AnonymousUser()
        return req

    def test_fusion_crea_carrito_de_usuario_si_no_existe(self):
        """Si el usuario no tiene carrito, se crea uno con los ítems de sesión."""
        carrito_sesion = Carrito.objects.create()
        ItemCarrito.objects.create(carrito=carrito_sesion, producto=self.p1, cantidad=2)
        req = self._request_con_sesion(carrito_sesion)

        _fusionar_carrito_sesion(req, self.usuario)

        carrito_usuario = Carrito.objects.get(usuario=self.usuario)
        self.assertEqual(carrito_usuario.items.count(), 1)
        self.assertEqual(carrito_usuario.items.first().cantidad, 2)

    def test_fusion_suma_cantidades_de_producto_existente(self):
        """Si el usuario ya tiene el producto en su carrito, las cantidades se suman."""
        carrito_usuario = Carrito.objects.create(usuario=self.usuario)
        ItemCarrito.objects.create(carrito=carrito_usuario, producto=self.p1, cantidad=1)

        carrito_sesion = Carrito.objects.create()
        ItemCarrito.objects.create(carrito=carrito_sesion, producto=self.p1, cantidad=2)
        req = self._request_con_sesion(carrito_sesion)

        _fusionar_carrito_sesion(req, self.usuario)

        item = ItemCarrito.objects.get(carrito=carrito_usuario, producto=self.p1)
        self.assertEqual(item.cantidad, 3)

    def test_fusion_respeta_limite_de_stock(self):
        """La cantidad fusionada no puede superar el stock disponible del producto."""
        carrito_usuario = Carrito.objects.create(usuario=self.usuario)
        # p2 tiene stock=4; ya tiene 3 en el carrito del usuario
        ItemCarrito.objects.create(carrito=carrito_usuario, producto=self.p2, cantidad=3)

        carrito_sesion = Carrito.objects.create()
        # intenta agregar 2 más → solo cabe 1 (stock máximo = 4)
        ItemCarrito.objects.create(carrito=carrito_sesion, producto=self.p2, cantidad=2)
        req = self._request_con_sesion(carrito_sesion)

        _fusionar_carrito_sesion(req, self.usuario)

        item = ItemCarrito.objects.get(carrito=carrito_usuario, producto=self.p2)
        self.assertEqual(item.cantidad, self.p2.stock)  # máximo = 4
