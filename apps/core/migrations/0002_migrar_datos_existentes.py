from django.db import migrations


def migrar_datos_existentes(apps, schema_editor):
    Grupo = apps.get_model('core', 'Grupo')
    Subgrupo = apps.get_model('core', 'Subgrupo')
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('socios', 'UserProfile')
    Socio = apps.get_model('socios', 'Socio')
    Membresia = apps.get_model('socios', 'Membresia')
    Evento = apps.get_model('eventos', 'Evento')

    grupo, _ = Grupo.objects.get_or_create(nombre='General')
    subgrupo, _ = Subgrupo.objects.get_or_create(grupo=grupo, nombre='General')

    for user in User.objects.all().iterator():
        perfil, _ = UserProfile.objects.get_or_create(user_id=user.pk)
        if user.is_superuser:
            perfil.rol = 'superadministrador'
            perfil.grupo_id = None
            perfil.subgrupo_id = None
        elif user.is_staff:
            perfil.rol = 'administrador_grupo'
            perfil.grupo_id = grupo.pk
            perfil.subgrupo_id = None
        else:
            perfil.rol = 'miembro'
        perfil.save(update_fields=['rol', 'grupo', 'subgrupo'])

    for socio in Socio.objects.all().iterator():
        Membresia.objects.get_or_create(
            socio_id=socio.pk,
            grupo_id=grupo.pk,
            subgrupo_id=subgrupo.pk,
            defaults={
                'estado': 'activo' if socio.estado == 'activo' else 'baja',
                'estado_pago': 'al_dia',
            },
        )

    Evento.objects.filter(grupo__isnull=True).update(grupo_id=grupo.pk)
    Evento.objects.filter(estado='programado', activo=False).update(estado='finalizado')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        ('socios', '0008_membresia_unique_membresia_vigente_por_grupo'),
        ('eventos', '0002_evento_estado_evento_grupo_evento_subgrupo_and_more'),
    ]

    operations = [migrations.RunPython(migrar_datos_existentes, migrations.RunPython.noop)]