# Quita ANID y CORFO de la tabla de colaboradores (si se crearon con la versión anterior de la 0002).
# Sus logos ahora se muestran en el pie de página como "Proyecto apoyado por:".

from django.db import migrations


def quitar(apps, schema_editor):
    Colaboradores = apps.get_model('online', 'Colaboradores')
    Colaboradores.objects.filter(nombre_colaborador__in=['ANID', 'CORFO']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('online', '0002_colaboradores_iniciales'),
    ]

    operations = [
        migrations.RunPython(quitar, migrations.RunPython.noop),
    ]
