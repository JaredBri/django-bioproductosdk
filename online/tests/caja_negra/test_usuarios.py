"""
CAJA NEGRA — Pruebas de gestión de usuario: registro, login, perfil,
edición de perfil y logout.

Clases:
  UsuarioTests       → flujos de autenticación y acceso
  PerfilEdicionTests → edición del perfil de usuario autenticado
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from online.models import Perfil


# ---------------------------------------------------------------------------
# Flujos de autenticación
# ---------------------------------------------------------------------------

class UsuarioTests(TestCase):
    """
    CAJA NEGRA — Comportamiento observable de los flujos de autenticación.

    Se prueban rutas de registro, login, perfil y logout desde el punto de
    vista del cliente HTTP, sin acceder directamente a la lógica interna.
    """

    CLAVE = 'Bio2026!Seguro'

    def test_registro_crea_usuario_con_clave_cifrada_y_perfil(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'nuevo_cliente',
            'first_name': 'Nuevo Cliente',
            'email': 'nuevo@correo.cl',
            'password1': self.CLAVE,
            'password2': self.CLAVE,
        })
        self.assertRedirects(respuesta, reverse('inicio'))
        usuario = User.objects.get(username='nuevo_cliente')
        self.assertNotEqual(usuario.password, self.CLAVE)
        self.assertTrue(usuario.check_password(self.CLAVE))
        self.assertEqual(usuario.email, 'nuevo@correo.cl')
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_registro_rechaza_claves_distintas(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'cliente2',
            'first_name': 'Cliente Dos',
            'email': 'cliente2@correo.cl',
            'password1': self.CLAVE,
            'password2': 'OtraClave!2026',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username='cliente2').exists())

    def test_registro_rechaza_usuario_repetido(self):
        User.objects.create_user('repetido', password=self.CLAVE, email='rep1@correo.cl')
        self.client.post(reverse('registro'), {
            'username': 'repetido',
            'first_name': 'Repetido',
            'email': 'rep2@correo.cl',
            'password1': self.CLAVE,
            'password2': self.CLAVE,
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


# ---------------------------------------------------------------------------
# Edición de perfil
# ---------------------------------------------------------------------------

class PerfilEdicionTests(TestCase):
    """
    CAJA NEGRA — Edición del perfil de usuario autenticado vía HTTP.
    """

    CLAVE = 'Bio2026!Seguro'

    def setUp(self):
        self.usuario = User.objects.create_user(
            'cliente_edit',
            first_name='Nombre Inicial',
            email='inicial@correo.cl',
            password=self.CLAVE,
        )
        self.perfil = Perfil.objects.create(usuario=self.usuario)

    def test_editar_perfil_sin_sesion_redirige_a_login(self):
        respuesta = self.client.get(reverse('editarPerfil'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('login'), respuesta.url)

    def test_editar_perfil_post_actualiza_usuario_y_perfil(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(
            reverse('editarPerfil'),
            {
                'first_name': 'Camila Actualizada',
                'email': 'camila.nueva@correo.cl',
                'telefono': '+56 9 5555 4444',
                'direccion': 'Los Leones 450',
                'comuna': 'Providencia',
                'region': 'Región Metropolitana',
            },
            follow=True,
        )
        self.assertRedirects(respuesta, reverse('perfil'))
        self.usuario.refresh_from_db()
        self.perfil.refresh_from_db()
        self.assertEqual(self.usuario.first_name, 'Camila Actualizada')
        self.assertEqual(self.usuario.email, 'camila.nueva@correo.cl')
        self.assertEqual(self.perfil.telefono, '+56 9 5555 4444')
        self.assertEqual(self.perfil.direccion, 'Los Leones 450')
        self.assertEqual(self.perfil.comuna, 'Providencia')
        self.assertEqual(self.perfil.region, 'Región Metropolitana')
