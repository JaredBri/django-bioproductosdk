"""
Paquete de pruebas de BioProductos DK (app "online").

Estructura:
    caja_blanca/   → pruebas de lógica interna (modelos, formularios, helpers privados)
    caja_negra/    → pruebas de comportamiento externo (HTTP, templates, API REST)

Ejecutar todas:
    python manage.py test online

Ejecutar solo caja blanca:
    python manage.py test online.tests.caja_blanca

Ejecutar solo caja negra:
    python manage.py test online.tests.caja_negra
"""
