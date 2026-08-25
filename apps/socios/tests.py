from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Grupo, Subgrupo
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
        self.grupo = Grupo.objects.create(nombre='Grupo A')
        self.subgrupo = Subgrupo.objects.create(grupo=self.grupo, nombre='Subgrupo A')

    def test_deuda_suspendes_y_pago_al_dia_reactiva(self):
        membresia = Membresia.objects.create(
            socio=self.socio,
            grupo=self.grupo,
            subgrupo=self.subgrupo,
            estado_pago='con_deuda',
        )
        self.assertEqual(membresia.estado, 'suspendido')

        membresia.estado_pago = 'al_dia'
        membresia.save()
        self.assertEqual(membresia.estado, 'activo')

    def test_no_permite_dos_membresias_vigentes_en_un_grupo(self):
        Membresia.objects.create(socio=self.socio, grupo=self.grupo, subgrupo=self.subgrupo)
        otro_subgrupo = Subgrupo.objects.create(grupo=self.grupo, nombre='Subgrupo B')
        with self.assertRaises((ValueError, IntegrityError)):
            Membresia.inscribir(self.socio, self.grupo, otro_subgrupo)


class RolesSociosTests(TestCase):
    def setUp(self):
        self.grupo = Grupo.objects.create(nombre='Grupo Roles')
        self.subgrupo = Subgrupo.objects.create(grupo=self.grupo, nombre='Subgrupo Roles')

    def crear_usuario(self, username, rol):
        user = User.objects.create_user(username=username, password='secret123', is_staff=True)
        user.userprofile.rol = rol
        user.userprofile.grupo = self.grupo
        user.userprofile.subgrupo = self.subgrupo if rol == 'administrador_subgrupo' else None
        user.userprofile.save()
        return user

    def test_administrador_grupo_no_puede_registrar_socios(self):
        self.client.force_login(self.crear_usuario('admin-grupo', 'administrador_grupo'))
        response = self.client.post(reverse('socios:crear_socio'), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Socio.objects.count(), 0)

    def test_administrador_subgrupo_puede_registrar_socio_con_membresia(self):
        self.client.force_login(self.crear_usuario('admin-subgrupo', 'administrador_subgrupo'))
        response = self.client.post(reverse('socios:crear_socio'), {
            'username': 'nuevo-socio', 'password': 'secret123', 'nombre': 'Luis',
            'apellido_paterno': 'Gomez', 'email': 'luis@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membresia.objects.filter(grupo=self.grupo, subgrupo=self.subgrupo).exists())