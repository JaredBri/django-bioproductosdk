"""
Pruebas automatizadas de BioProductos DK (app "online").

Cubren lo que existe hoy en el proyecto: modelos, catálogo (tienda y detalle),
páginas informativas y gestión de usuario (registro, login, perfil y logout).

Ejecutar con:
    python manage.py test online

Django crea una base de datos de prueba temporal (test_bioproductos) y la borra
al terminar, así que no se tocan los datos reales. El usuario de la base de datos
necesita permiso para crear bases de datos.
"""

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .models import Carrito, Categoria, ItemCarrito, Perfil, Producto


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


# =====================================================================
# 1. MODELOS
# =====================================================================

class ModelosTests(TestCase):

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')

    def test_marca_se_normaliza_al_guardar(self):
        """save() quita espacios y deja solo la primera letra en mayúscula."""
        producto = crear_producto(self.limpieza, marca='  bioPRODUCTOS dk  ')
        self.assertEqual(producto.marca, 'Bioproductos dk')

    def test_str_de_los_modelos(self):
        producto = crear_producto(self.limpieza)
        self.assertEqual(str(self.limpieza), 'Limpieza')
        self.assertEqual(str(producto), 'Detergente Cítrico')

    def test_destacado_es_falso_por_defecto(self):
        producto = crear_producto(self.limpieza)
        self.assertFalse(producto.destacado)

    def test_subtotal_del_item_de_carrito(self):
        """subtotal() = precio del producto x cantidad."""
        producto = crear_producto(self.limpieza, precio=8990)
        carrito = Carrito.objects.create()
        item = ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=3)
        self.assertEqual(item.subtotal(), 26970)

    def test_carrito_usa_retiro_en_tienda_por_defecto(self):
        carrito = Carrito.objects.create()
        self.assertEqual(carrito.tipo_envio, 'retiro')
        self.assertFalse(carrito.completado)

    def test_no_se_puede_borrar_categoria_con_productos(self):
        """on_delete=PROTECT: una categoría con productos no se puede eliminar."""
        crear_producto(self.limpieza)
        with self.assertRaises(ProtectedError):
            self.limpieza.delete()

    def test_perfil_se_borra_junto_con_el_usuario(self):
        """on_delete=CASCADE: al borrar el usuario se borra su perfil."""
        usuario = User.objects.create_user('cliente', password='Bio2026!Seguro')
        Perfil.objects.create(usuario=usuario, comuna='Maipú')
        usuario.delete()
        self.assertEqual(Perfil.objects.count(), 0)


# =====================================================================
# 2. CATÁLOGO: INICIO, TIENDA Y DETALLE DE PRODUCTO
# =====================================================================

class CatalogoTests(TestCase):

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


# =====================================================================
# 3. PÁGINAS INFORMATIVAS
# =====================================================================

class PaginasInformativasTests(TestCase):

    def test_paginas_responden_200_con_su_template(self):
        paginas = {
            'nosotros': 'nosotros.html',
            'ciencia': 'ciencia.html',
            'colaboradores': 'colaboradores.html',
            'contacto': 'contacto.html',
        }
        for nombre, template in paginas.items():
            with self.subTest(pagina=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)
                self.assertTemplateUsed(respuesta, template)

    def test_pie_de_pagina_muestra_proyecto_apoyado_por(self):
        respuesta = self.client.get(reverse('inicio'))
        self.assertContains(respuesta, 'Proyecto apoyado por:')
        self.assertContains(respuesta, 'logoANID.jpg')
        self.assertContains(respuesta, 'logoCORFO.jpg')


# =====================================================================
# 4. GESTIÓN DE USUARIO: REGISTRO, LOGIN, PERFIL Y LOGOUT
# =====================================================================

class UsuarioTests(TestCase):

    CLAVE = 'Bio2026!Seguro'

    def test_registro_crea_usuario_con_clave_cifrada_y_lo_loguea(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'nuevo_cliente',
            'password1': self.CLAVE,
            'password2': self.CLAVE,
        })
        self.assertRedirects(respuesta, reverse('inicio'))
        usuario = User.objects.get(username='nuevo_cliente')
        self.assertNotEqual(usuario.password, self.CLAVE)    # no se guarda en texto plano
        self.assertTrue(usuario.check_password(self.CLAVE))  # pero el hash la valida
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_registro_rechaza_claves_distintas(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'cliente2',
            'password1': self.CLAVE,
            'password2': 'OtraClave!2026',
        })
        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el formulario
        self.assertFalse(User.objects.filter(username='cliente2').exists())

    def test_registro_rechaza_usuario_repetido(self):
        User.objects.create_user('repetido', password=self.CLAVE)
        self.client.post(reverse('registro'), {
            'username': 'repetido', 'password1': self.CLAVE, 'password2': self.CLAVE,
        })
        self.assertEqual(User.objects.filter(username='repetido').count(), 1)

    def test_login_correcto_redirige_al_inicio(self):
        User.objects.create_user('cliente', password=self.CLAVE)
        respuesta = self.client.post(reverse('login'), {'username': 'cliente', 'password': self.CLAVE})
        self.assertRedirects(respuesta, reverse('inicio'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_con_clave_incorrecta_no_inicia_sesion(self):
        User.objects.create_user('cliente', password=self.CLAVE)
        respuesta = self.client.post(reverse('login'), {'username': 'cliente', 'password': 'mala'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(respuesta.context['form'].errors)

    def test_usuario_logueado_no_ve_login_ni_registro(self):
        usuario = User.objects.create_user('cliente', password=self.CLAVE)
        self.client.force_login(usuario)
        self.assertRedirects(self.client.get(reverse('login')), reverse('inicio'))
        self.assertRedirects(self.client.get(reverse('registro')), reverse('inicio'))

    def test_perfil_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse('perfil'))
        self.assertRedirects(respuesta, reverse('login'))

    def test_perfil_con_sesion_muestra_los_datos(self):
        usuario = User.objects.create_user('cliente', password=self.CLAVE, email='cliente@correo.cl')
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse('perfil'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'cliente@correo.cl')

    def test_logout_por_post_cierra_la_sesion(self):
        usuario = User.objects.create_user('cliente', password=self.CLAVE)
        self.client.force_login(usuario)
        respuesta = self.client.post(reverse('logout'))
        self.assertTemplateUsed(respuesta, 'logout.html')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_por_get_no_cierra_la_sesion(self):
        """Por seguridad, solo se cierra sesión con POST (formulario con token CSRF)."""
        usuario = User.objects.create_user('cliente', password=self.CLAVE)
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse('logout'))
        self.assertRedirects(respuesta, reverse('inicio'))
        self.assertIn('_auth_user_id', self.client.session)