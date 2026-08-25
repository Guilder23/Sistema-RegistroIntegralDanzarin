from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

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