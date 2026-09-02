from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bloques', '0002_bloque_creado_por'),
        ('socios', '0011_normalizar_roles_administrativos'),
    ]

    operations = [
        migrations.AddField(
            model_name='socio', name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='socios_creados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membresia', name='bloque',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='membresias', to='bloques.bloque'),
        ),
    ]