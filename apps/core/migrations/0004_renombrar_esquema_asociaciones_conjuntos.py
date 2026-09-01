from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_auditoria_grupo_auditoria_subgrupo'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF to_regclass('public.core_grupo') IS NOT NULL THEN
                        ALTER TABLE core_grupo RENAME TO core_asociacion;
                    END IF;
                    IF to_regclass('public.core_subgrupo') IS NOT NULL THEN
                        ALTER TABLE core_subgrupo RENAME TO core_conjunto;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_conjunto' AND column_name = 'grupo_id') THEN
                        ALTER TABLE core_conjunto RENAME COLUMN grupo_id TO asociacion_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_auditoria' AND column_name = 'grupo_id') THEN
                        ALTER TABLE core_auditoria RENAME COLUMN grupo_id TO asociacion_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_auditoria' AND column_name = 'subgrupo_id') THEN
                        ALTER TABLE core_auditoria RENAME COLUMN subgrupo_id TO conjunto_id;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_auditoria' AND column_name = 'asociacion_id') THEN
                        ALTER TABLE core_auditoria RENAME COLUMN asociacion_id TO grupo_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_auditoria' AND column_name = 'conjunto_id') THEN
                        ALTER TABLE core_auditoria RENAME COLUMN conjunto_id TO subgrupo_id;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'core_conjunto' AND column_name = 'asociacion_id') THEN
                        ALTER TABLE core_conjunto RENAME COLUMN asociacion_id TO grupo_id;
                    END IF;
                    IF to_regclass('public.core_conjunto') IS NOT NULL THEN
                        ALTER TABLE core_conjunto RENAME TO core_subgrupo;
                    END IF;
                    IF to_regclass('public.core_asociacion') IS NOT NULL THEN
                        ALTER TABLE core_asociacion RENAME TO core_grupo;
                    END IF;
                END $$;
            """,
        ),
    ]