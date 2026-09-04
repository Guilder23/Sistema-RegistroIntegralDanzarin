from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.bloques.models import Bloque
from apps.core.models import Asociacion, Conjunto


class BloquesAdministradorConjuntoTests(TestCase):
    def test_modal_creacion_muestra_bloques_del_conjunto_asignado(self):
        asociacion = Asociacion.objects.create(nombre='Asociacion Bloques')
        conjunto = Conjunto.objects.create(asociacion=asociacion, nombre='Conjunto Bloques')
        bloque = Bloque.objects.create(conjunto=conjunto, nombre='Bloque Principal')
        administrador = User.objects.create_user(username='admin-conjunto', password='secret123')
        perfil = administrador.userprofile
        perfil.rol = 'administrador_conjunto'
        perfil.asociacion = asociacion
        perfil.conjunto = conjunto
        perfil.save()

        self.client.force_login(administrador)
        response = self.client.get(reverse('danzarines:listar_danzarines'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="crearDanzarinAsociacion"')
        self.assertContains(response, f'id="crearDanzarinConjunto"')
        self.assertContains(response, f'value="{conjunto.pk}" selected')
        self.assertContains(response, f'value="{bloque.pk}"')
        self.assertContains(response, bloque.nombre)