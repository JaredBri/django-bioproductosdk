# Esta migración creaba ANID y CORFO como colaboradores.
# Se dejó vacía porque ANID y CORFO no son colaboradores: ahora aparecen en el pie de página
# como "Proyecto apoyado por:". Se mantiene el archivo para no romper bases de datos
# donde ya se aplicó; la 0003 elimina esos registros si existen.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online', '0001_initial'),
    ]

    operations = []
