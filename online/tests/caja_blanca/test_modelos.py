"""
CAJA BLANCA — Pruebas de lógica interna de modelos y formularios.

Clases:
  ModelosTests  → invariantes ORM, cálculos, relaciones en cascada/protect
  FormsTests    → validación interna de formularios Django
"""

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase

from online.forms import ContactoForm, PerfilForm, RegistroForm, UsuarioUpdateForm
from online.models import (
    Carrito,
    Categoria,
    ItemCarrito,
    Perfil,
    Producto,
)


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
# Pruebas de modelos
# ---------------------------------------------------------------------------

class ModelosTests(TestCase):
    """
    CAJA BLANCA — Lógica interna de los modelos ORM.

    Verifica invariantes de negocio que se implementan dentro de los modelos
    (save(), relaciones, valores por defecto y cálculos).
    """

    def setUp(self):
        self.limpieza = Categoria.objects.create(nombre='Limpieza')

    # --- Producto ---

    def test_marca_se_normaliza_al_guardar(self):
        """save() quita espacios y deja solo la primera letra en mayúscula."""
        producto = crear_producto(self.limpieza, marca='  bioPRODUCTOS dk  ')
        self.assertEqual(producto.marca, 'Bioproductos dk')

    def test_str_de_los_modelos(self):
        """__str__ de Categoria y Producto devuelven el nombre correcto."""
        producto = crear_producto(self.limpieza)
        self.assertEqual(str(self.limpieza), 'Limpieza')
        self.assertEqual(str(producto), 'Detergente Cítrico')

    def test_destacado_es_falso_por_defecto(self):
        """El campo `destacado` debe ser False al crear un producto sin especificarlo."""
        producto = crear_producto(self.limpieza)
        self.assertFalse(producto.destacado)

    # --- Carrito e ItemCarrito ---

    def test_subtotal_del_item_de_carrito(self):
        """subtotal() = precio del producto × cantidad."""
        producto = crear_producto(self.limpieza, precio=8990)
        carrito = Carrito.objects.create()
        item = ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=3)
        self.assertEqual(item.subtotal(), 26970)

    def test_carrito_usa_retiro_en_tienda_por_defecto(self):
        """El tipo de envío por defecto es 'retiro' y el carrito no está completado."""
        carrito = Carrito.objects.create()
        self.assertEqual(carrito.tipo_envio, 'retiro')
        self.assertFalse(carrito.completado)

    # --- Integridad referencial ---

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


# ---------------------------------------------------------------------------
# Pruebas de formularios
# ---------------------------------------------------------------------------

class FormsTests(TestCase):
    """
    CAJA BLANCA — Validación interna de los formularios Django.

    Se instancian directamente los formularios y se inspeccionan sus errores
    sin pasar por el ciclo HTTP (sin self.client).
    """

    CLAVE = 'Bio2026!Seguro'

    def test_registro_form_valido_y_crea_perfil(self):
        """RegistroForm normaliza el email a minúsculas y crea el Perfil asociado."""
        form = RegistroForm(data={
            'username': 'ana_dk',
            'first_name': 'Ana Pérez',
            'email': 'ANA@CORREO.CL',
            'password1': self.CLAVE,
            'password2': self.CLAVE,
        })
        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertEqual(usuario.email, 'ana@correo.cl')
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())

    def test_registro_form_rechaza_correo_duplicado_y_campos_vacios(self):
        """RegistroForm rechaza email ya registrado y nombre vacío."""
        User.objects.create_user('existente', email='duplicado@correo.cl', password=self.CLAVE)
        form = RegistroForm(data={
            'username': 'otro',
            'first_name': '',
            'email': 'DUPLICADO@correo.cl',
            'password1': self.CLAVE,
            'password2': self.CLAVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)

    def test_perfil_form_y_usuario_update_form_validos(self):
        """PerfilForm y UsuarioUpdateForm aceptan datos correctos."""
        usuario = User.objects.create_user(
            'pedro', first_name='Pedro', email='pedro@correo.cl', password=self.CLAVE,
        )
        perfil = Perfil.objects.create(usuario=usuario)

        u_form = UsuarioUpdateForm(
            data={'first_name': 'Pedro Rojas', 'email': 'pedro.rojas@correo.cl'},
            instance=usuario,
        )
        p_form = PerfilForm(
            data={
                'telefono': '+56 9 8888 7777',
                'direccion': 'Av. Providencia 1234',
                'comuna': 'Providencia',
                'region': 'Metropolitana',
            },
            instance=perfil,
        )
        self.assertTrue(u_form.is_valid(), u_form.errors)
        self.assertTrue(p_form.is_valid(), p_form.errors)

    def test_contacto_form_valido_y_campos_vacios(self):
        """ContactoForm acepta un formulario válido y rechaza campos requeridos vacíos."""
        form_valido = ContactoForm(data={
            'nombre': 'Lucía',
            'correo': 'lucia@ejemplo.cl',
            'telefono': '',
            'tipo_consulta': 'Maquila ISP',
            'mensaje': 'Consulta sobre maquila.',
        })
        self.assertTrue(form_valido.is_valid())

        form_invalido = ContactoForm(data={
            'nombre': '   ',
            'correo': 'correo-invalido',
            'tipo_consulta': 'B2C / Cliente',
            'mensaje': '',
        })
        self.assertFalse(form_invalido.is_valid())
        self.assertIn('nombre', form_invalido.errors)
        self.assertIn('correo', form_invalido.errors)
        self.assertIn('mensaje', form_invalido.errors)
