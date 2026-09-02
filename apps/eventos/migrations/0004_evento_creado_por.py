from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventos', '0003_renombrar_ambito_asociaciones_conjuntos'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='creado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='eventos_creados',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]