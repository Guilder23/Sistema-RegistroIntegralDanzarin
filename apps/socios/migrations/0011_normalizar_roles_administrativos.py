from django.db import migrations


def normalizar_roles(apps, schema_editor):
    UserProfile = apps.get_model('socios', 'UserProfile')
    UserProfile.objects.filter(rol='administrador_grupo').update(rol='administrador_asociacion')
    UserProfile.objects.filter(rol='administrador_subgrupo').update(rol='administrador_conjunto')


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0010_renombrar_ambito_asociaciones_conjuntos'),
    ]

    operations = [
        migrations.RunPython(normalizar_roles, migrations.RunPython.noop),
    ]