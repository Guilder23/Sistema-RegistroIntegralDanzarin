from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('souvenirs', '0003_unico_souvenir_por_evento'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='souvenir',
            constraint=models.UniqueConstraint(
                fields=['evento'],
                name='unique_souvenir_por_evento',
            ),
        ),
    ]
