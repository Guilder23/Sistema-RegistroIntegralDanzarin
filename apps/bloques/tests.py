from django.test import TestCase

from apps.core.models import Asociacion, Conjunto
from .models import Bloque


class BloqueModelTest(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociación Test')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Test')

    def test_bloque_pertenece_a_un_conjunto(self):
        bloque = Bloque.objects.create(conjunto=self.conjunto, nombre='Bloque A', activo=True)
        self.assertEqual(bloque.conjunto, self.conjunto)
        self.assertEqual(str(bloque), 'Asociación Test / Conjunto Test / Bloque A')

    def test_no_permite_dos_bloques_iguales_en_un_conjunto(self):
        Bloque.objects.create(conjunto=self.conjunto, nombre='Bloque A', activo=True)
        with self.assertRaises(Exception):
            Bloque.objects.create(conjunto=self.conjunto, nombre='Bloque A', activo=True)
