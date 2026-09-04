from django.db import migrations, models


def eliminar_souvenirs_duplicados(apps, schema_editor):
    Souvenir = apps.get_model('souvenirs', 'Souvenir')
    evento_ids = (
        Souvenir.objects.values('evento_id')
        .annotate(total=models.Count('id'))
        .filter(total__gt=1)
        .values_list('evento_id', flat=True)
    )
    for evento_id in evento_ids:
        duplicados = Souvenir.objects.filter(evento_id=evento_id).order_by('-creado', '-pk')
        ids_a_eliminar = list(duplicados.values_list('pk', flat=True)[1:])
        Souvenir.objects.filter(pk__in=ids_a_eliminar).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('souvenirs', '0002_souvenir_evento_obligatorio'),
    ]

    operations = [
        migrations.RunPython(eliminar_souvenirs_duplicados, migrations.RunPython.noop),
    ]
