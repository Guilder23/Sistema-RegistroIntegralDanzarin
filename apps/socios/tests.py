from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Asociacion, Conjunto
from .models import Membresia, Socio


class MembresiaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='miembro', password='secret')
        self.socio = Socio.objects.create(
            user=self.usuario,
            nombre='Ana',
            apellido='Perez',
            email='ana@example.com',
        )
        self.asociacion = Asociacion.objects.create(nombre='Asociacion A')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto A')

    def test_deuda_suspendes_y_pago_al_dia_reactiva(self):
        membresia = Membresia.objects.create(
            socio=self.socio,
            asociacion=self.asociacion,
            conjunto=self.conjunto,
            estado_pago='con_deuda',
        )
        self.assertEqual(membresia.estado, 'suspendido')

        membresia.estado_pago = 'al_dia'
        membresia.save()
        self.assertEqual(membresia.estado, 'activo')

    def test_no_permite_dos_membresias_vigentes_en_un_asociacion(self):
        Membresia.objects.create(socio=self.socio, asociacion=self.asociacion, conjunto=self.conjunto)
        otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto B')
        with self.assertRaises((ValueError, IntegrityError)):
            Membresia.inscribir(self.socio, self.asociacion, otro_conjunto)


class RolesSociosTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Roles')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Roles')

    def crear_usuario(self, username, rol):
        user = User.objects.create_user(username=username, password='secret123', is_staff=True)
        user.userprofile.rol = rol
        user.userprofile.asociacion = self.asociacion
        user.userprofile.conjunto = self.conjunto if rol == 'administrador_conjunto' else None
        user.userprofile.save()
        return user

    def test_administrador_asociacion_no_puede_registrar_socios(self):
        self.client.force_login(self.crear_usuario('admin-asociacion', 'administrador_asociacion'))
        response = self.client.post(reverse('socios:crear_socio'), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Socio.objects.count(), 0)

    def test_administrador_conjunto_puede_registrar_socio_con_membresia(self):
        self.client.force_login(self.crear_usuario('admin-conjunto', 'administrador_conjunto'))
        response = self.client.post(reverse('socios:crear_socio'), {
            'username': 'nuevo-socio', 'password': 'secret123', 'nombre': 'Luis',
            'apellido_paterno': 'Gomez', 'email': 'luis@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membresia.objects.filter(asociacion=self.asociacion, conjunto=self.conjunto).exists())