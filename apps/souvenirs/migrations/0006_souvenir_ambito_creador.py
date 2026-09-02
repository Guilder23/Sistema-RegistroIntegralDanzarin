from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('eventos', '0004_evento_creado_por'),
        ('souvenirs', '0005_souvenir_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='souvenir', name='asociacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='souvenirs', to='core.asociacion'),
        ),
        migrations.AddField(
            model_name='souvenir', name='conjunto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='souvenirs', to='core.conjunto'),
        ),
        migrations.AddField(
            model_name='souvenir', name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='souvenirs_creados', to=settings.AUTH_USER_MODEL),
        ),
    ]