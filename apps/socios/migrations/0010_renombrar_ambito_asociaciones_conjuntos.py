from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_renombrar_esquema_asociaciones_conjuntos'),
        ('socios', '0009_socio_modalidad_socio_sexo'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'socios_userprofile' AND column_name = 'grupo_id') THEN
                        ALTER TABLE socios_userprofile RENAME COLUMN grupo_id TO asociacion_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'socios_userprofile' AND column_name = 'subgrupo_id') THEN
                        ALTER TABLE socios_userprofile RENAME COLUMN subgrupo_id TO conjunto_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'socios_membresia' AND column_name = 'grupo_id') THEN
                        ALTER TABLE socios_membresia RENAME COLUMN grupo_id TO asociacion_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'socios_membresia' AND column_name = 'subgrupo_id') THEN
                        ALTER TABLE socios_membresia RENAME COLUMN subgrupo_id TO conjunto_id;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]