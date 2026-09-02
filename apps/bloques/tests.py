from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

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


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class BloqueRolesTest(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Bloques')
        self.otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Otro Conjunto')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Principal')
        self.otra_asociacion = Asociacion.objects.create(nombre='Otra Asociacion')
        self.privado = Conjunto.objects.create(asociacion=self.otra_asociacion, nombre='Conjunto Privado')

    def crear_usuario(self, username, rol, conjunto=None):
        usuario = User.objects.create_user(username=username, password='secret123', is_staff=True)
        usuario.userprofile.rol = rol
        usuario.userprofile.asociacion = self.asociacion
        usuario.userprofile.conjunto = conjunto
        usuario.userprofile.save()
        return usuario

    def datos_bloque(self, conjunto_id):
        return {'asociacion_id': self.asociacion.pk, 'conjunto_id': conjunto_id, 'nombre': 'Bloque Nuevo'}

    def test_superadministrador_puede_asignar_bloque_a_un_conjunto(self):
        usuario = User.objects.create_superuser('super', 'super@example.com', 'secret123')
        self.client.force_login(usuario)

        response = self.client.post(reverse('bloques:crear_bloque'), self.datos_bloque(self.conjunto.pk))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bloque.objects.filter(conjunto=self.conjunto).exists())
        self.assertEqual(Bloque.objects.get().creado_por, usuario)

    def test_administrador_asociacion_ve_y_crea_en_todos_sus_conjuntos(self):
        self.client.force_login(self.crear_usuario('asociacion', 'administrador_asociacion'))

        response = self.client.get(reverse('bloques:listar_bloques'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conjunto.nombre)
        self.assertContains(response, self.otro_conjunto.nombre)

        response = self.client.post(reverse('bloques:crear_bloque'), self.datos_bloque(self.otro_conjunto.pk))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bloque.objects.filter(conjunto=self.otro_conjunto).exists())

    def test_administrador_conjunto_solo_ve_y_crea_en_su_conjunto(self):
        Bloque.objects.create(conjunto=self.privado, nombre='Bloque Privado')
        self.client.force_login(self.crear_usuario('conjunto', 'administrador_conjunto', self.conjunto))

        response = self.client.get(reverse('bloques:listar_bloques'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Bloque Privado')

        response = self.client.post(reverse('bloques:crear_bloque'), self.datos_bloque(self.privado.pk))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bloque.objects.filter(conjunto=self.conjunto, nombre='Bloque Nuevo').exists())
        self.assertFalse(Bloque.objects.filter(conjunto=self.privado, nombre='Bloque Nuevo').exists())
