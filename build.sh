#!/usr/bin/env bash
set -o errexit

echo "==== Actualizando pip ===="
pip install --upgrade pip

echo "==== Instalando dependencias ===="
pip install -r requirements.txt

echo "==== Recolectando archivos estáticos ===="
python manage.py collectstatic --no-input

echo "==== Ejecutando migraciones ===="
python manage.py migrate --noinput

echo "==== Configurando usuario administrador ===="
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'}); user.email = 'admin@example.com'; user.is_staff = True; user.is_superuser = True; user.set_password('admin12345'); user.save()"

echo "==== Build completado exitosamente ===="