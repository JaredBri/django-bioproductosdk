"""
CAJA NEGRA — Pruebas de la API REST v1 (DRF).

Clase:
  ApiRestTests → endpoints de productos, categorías, colaboradores,
                 registro de usuario, perfil autenticado y carrito API.
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from online.models import Carrito, Categoria, Colaboradores, ItemCarrito, Perfil, Producto


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
# Pruebas de API REST
# ---------------------------------------------------------------------------

class ApiRestTests(APITestCase):
    """
    CAJA NEGRA — Comportamiento observable de la API REST v1.

    Se prueban los endpoints públicos y protegidos desde el exterior,
    verificando códigos de estado, estructura y contenido de las respuestas JSON.
    """

    CLAVE = 'Bio2026!Seguro'

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')
        self.cuidado = Categoria.objects.create(nombre='Cuidado personal')
        self.p1 = crear_producto(self.limpieza, 'Bio-Detergente Cítrico', precio=8990)
        self.p2 = crear_producto(self.cuidado, 'Champú Sólido Romero', precio=6990)
        self.colab = Colaboradores.objects.create(nombre_colaborador='USACH')
        self.usuario = User.objects.create_user(
            'apiuser', first_name='API User', email='api@correo.cl', password=self.CLAVE,
        )
        self.perfil = Perfil.objects.create(usuario=self.usuario, comuna='Santiago')

    def test_listar_productos_y_filtrar_por_categoria_y_search(self):
        resp = self.client.get('/api/v1/productos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['categoria_nombre'], 'Limpieza')

        resp_cat = self.client.get('/api/v1/productos/?categoria=Cuidado personal')
        self.assertEqual(resp_cat.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_cat.data), 1)
        self.assertEqual(resp_cat.data[0]['nombre'], 'Champú Sólido Romero')

        resp_search = self.client.get('/api/v1/productos/?search=cítrico')
        self.assertEqual(resp_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_search.data), 1)
        self.assertEqual(resp_search.data[0]['id'], self.p1.id)

    def test_detalle_producto_api_y_404(self):
        resp = self.client.get(f'/api/v1/productos/{self.p1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['nombre'], 'Bio-Detergente Cítrico')

        resp_404 = self.client.get('/api/v1/productos/99999/')
        self.assertEqual(resp_404.status_code, status.HTTP_404_NOT_FOUND)

    def test_listar_categorias_y_colaboradores(self):
        resp_cat = self.client.get('/api/v1/categorias/')
        self.assertEqual(resp_cat.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_cat.data), 2)

        resp_col = self.client.get('/api/v1/colaboradores/')
        self.assertEqual(resp_col.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_col.data), 1)
        self.assertEqual(resp_col.data[0]['nombre_colaborador'], 'USACH')

    def test_registro_usuario_api_crea_usuario_y_rechaza_invalido(self):
        resp = self.client.post('/api/v1/auth/registro/', {
            'username': 'nuevo_api',
            'first_name': 'Nuevo API',
            'email': 'nuevo_api@correo.cl',
            'password': self.CLAVE,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='nuevo_api').exists())

        resp_bad = self.client.post('/api/v1/auth/registro/', {
            'username': 'nuevo_api_2',
            'first_name': 'Otro',
            'email': 'nuevo_api@correo.cl',
            'password': '123',
        })
        self.assertEqual(resp_bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_perfil_y_carrito_protegidos_sin_autenticacion(self):
        resp_perfil = self.client.get('/api/v1/perfil/')
        self.assertIn(resp_perfil.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        resp_carrito = self.client.get('/api/v1/carrito/')
        self.assertIn(resp_carrito.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_perfil_autenticado_get_y_put(self):
        self.client.force_authenticate(user=self.usuario)

        resp_get = self.client.get('/api/v1/perfil/')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_get.data['email'], 'api@correo.cl')

        resp_put = self.client.put('/api/v1/perfil/', {
            'first_name': 'API Actualizado',
            'comuna': 'Ñuñoa',
        })
        self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.perfil.refresh_from_db()
        self.assertEqual(self.usuario.first_name, 'API Actualizado')
        self.assertEqual(self.perfil.comuna, 'Ñuñoa')

    def test_carrito_autenticado_api(self):
        carrito = Carrito.objects.create(usuario=self.usuario)
        ItemCarrito.objects.create(carrito=carrito, producto=self.p1, cantidad=2)

        self.client.force_authenticate(user=self.usuario)
        resp = self.client.get('/api/v1/carrito/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total'], 17980)
        self.assertEqual(len(resp.data['items']), 1)
