"""
CAJA NEGRA — Pruebas de páginas informativas y formulario de contacto.

Clase:
  PaginasInformativasTests → respuestas HTTP, templates, pie de página y POST de contacto.
"""

from django.test import TestCase
from django.urls import reverse


class PaginasInformativasTests(TestCase):
    """
    CAJA NEGRA — Comportamiento observable de las páginas informativas.

    Se verifican únicamente el código de respuesta, el template renderizado
    y el contenido HTML devuelto al navegador.
    """

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
        """El pie de página debe contener los logos de ANID y CORFO (prueba cubierta por contrato)."""
        respuesta = self.client.get(reverse('inicio'))
        self.assertContains(respuesta, 'Proyecto apoyado por:')
        self.assertContains(respuesta, 'logoANID.jpg')
        self.assertContains(respuesta, 'logoCORFO.jpg')

    def test_contacto_post_valido_muestra_mensaje_confirmacion(self):
        respuesta = self.client.post(
            reverse('contacto'),
            {
                'nombre': 'Camila Soto',
                'correo': 'camila@empresa.cl',
                'telefono': '+56 9 1234 5678',
                'tipo_consulta': 'Biodistribuidor DK',
                'mensaje': 'Me interesa distribuir sus bio-detergentes.',
            },
            follow=True,
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Camila Soto')
