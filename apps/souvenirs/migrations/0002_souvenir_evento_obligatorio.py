from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eventos', '0003_alter_evento_options_remove_evento_fecha_evento_and_more'),
        ('souvenirs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='souvenir',
            name='evento',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='souvenirs',
                to='eventos.evento',
            ),
        ),
    ]
