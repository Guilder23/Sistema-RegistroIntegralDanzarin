from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_renombrar_esquema_asociaciones_conjuntos'),
        ('eventos', '0002_evento_estado_evento_grupo_evento_subgrupo_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'eventos_evento' AND column_name = 'grupo_id') THEN
                        ALTER TABLE eventos_evento RENAME COLUMN grupo_id TO asociacion_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'eventos_evento' AND column_name = 'subgrupo_id') THEN
                        ALTER TABLE eventos_evento RENAME COLUMN subgrupo_id TO conjunto_id;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]