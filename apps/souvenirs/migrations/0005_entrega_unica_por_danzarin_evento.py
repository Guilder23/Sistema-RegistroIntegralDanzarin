from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('souvenirs', '0004_unico_souvenir_por_evento'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='souvenirentrega',
            constraint=models.UniqueConstraint(
                fields=['danzarin', 'evento'],
                name='unique_entrega_danzarin_evento',
            ),
        ),
    ]
