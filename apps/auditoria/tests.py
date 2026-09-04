from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Asociacion, Auditoria, Conjunto


class HistorialAuditoriaTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion A')
        self.otra_asociacion = Asociacion.objects.create(nombre='Asociacion B')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto A')
        self.otro_conjunto = Conjunto.objects.create(asociacion=self.otra_asociacion, nombre='Conjunto B')

        self.superadmin = User.objects.create_superuser(
            username='superadmin', email='super@example.com', password='secret123'
        )
        self.admin_asociacion = User.objects.create_user(
            username='admin-asociacion', password='secret123'
        )
        self.admin_asociacion.userprofile.rol = 'administrador_asociacion'
        self.admin_asociacion.userprofile.asociacion = self.asociacion
        self.admin_asociacion.userprofile.save()

        self.admin_conjunto = User.objects.create_user(
            username='admin-conjunto', password='secret123'
        )
        self.admin_conjunto.userprofile.rol = 'administrador_conjunto'
        self.admin_conjunto.userprofile.asociacion = self.asociacion
        self.admin_conjunto.userprofile.conjunto = self.conjunto
        self.admin_conjunto.userprofile.save()

        self.registro_superadmin = Auditoria.objects.create(
            usuario=self.superadmin,
            accion='superadmin',
            registro_afectado='Asociacion A',
            asociacion=self.asociacion,
        )
        self.registro_asociacion = Auditoria.objects.create(
            usuario=self.admin_asociacion,
            accion='asociacion',
            registro_afectado='Asociacion A',
            asociacion=self.asociacion,
        )
        self.registro_conjunto = Auditoria.objects.create(
            usuario=self.admin_conjunto,
            accion='conjunto',
            registro_afectado='Conjunto A',
            conjunto=self.conjunto,
        )
        self.registro_fuera = Auditoria.objects.create(
            usuario=self.superadmin,
            accion='fuera',
            registro_afectado='Asociacion B',
            asociacion=self.otra_asociacion,
            conjunto=self.otro_conjunto,
        )

    def acciones_visibles(self, usuario):
        self.client.force_login(usuario)
        response = self.client.get(reverse('auditoria:listar_auditoria'))
        return [registro.accion for registro in response.context['registros']]

    def test_alcance_por_rol_y_orden_ascendente(self):
        self.assertEqual(self.acciones_visibles(self.admin_conjunto), ['conjunto'])
        self.assertEqual(
            self.acciones_visibles(self.admin_asociacion),
            ['asociacion', 'conjunto'],
        )
        self.assertEqual(
            self.acciones_visibles(self.superadmin),
            ['superadmin', 'asociacion', 'conjunto', 'fuera'],
        )