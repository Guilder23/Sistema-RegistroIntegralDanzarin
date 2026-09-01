from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Asociacion, Conjunto


class GestionRolesTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_superuser('root', 'root@example.com', 'secret123')
		self.asociacion = Asociacion.objects.create(nombre='Asociacion Usuarios')
		self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Usuarios')
		self.client.force_login(self.admin)

	def test_crea_administrador_de_conjunto_con_ambito(self):
		response = self.client.post(reverse('core:registro'), {
			'username': 'admin-con', 'email': 'con@example.com',
			'password': 'secret123', 'password2': 'secret123',
			'rol': 'administrador_conjunto', 'asociacion_id': self.asociacion.pk,
			'conjunto_id': self.conjunto.pk,
		})
		self.assertEqual(response.status_code, 302)
		usuario = User.objects.get(username='admin-con')
		self.assertEqual(usuario.userprofile.rol, 'administrador_conjunto')
		self.assertEqual(usuario.userprofile.asociacion_id, self.asociacion.pk)
		self.assertEqual(usuario.userprofile.conjunto_id, self.conjunto.pk)

	def test_no_crea_administrador_de_asociacion_sin_asociacion(self):
		self.client.post(reverse('core:registro'), {
			'username': 'sin-asociacion', 'email': 'sin@example.com',
			'password': 'secret123', 'password2': 'secret123',
			'rol': 'administrador_asociacion',
		})
		self.assertFalse(User.objects.filter(username='sin-asociacion').exists())

	def test_miembro_crea_socio_y_membresia(self):
		self.client.post(reverse('core:registro'), {
			'username': 'miembro', 'first_name': 'María', 'last_name': 'López',
			'email': 'maria@example.com', 'password': 'secret123', 'password2': 'secret123',
			'rol': 'miembro', 'asociacion_id': self.asociacion.pk, 'conjunto_id': self.conjunto.pk,
		})
		usuario = User.objects.get(username='miembro')
		self.assertTrue(hasattr(usuario, 'socio_profile'))
		self.assertTrue(usuario.socio_profile.membresias.filter(asociacion=self.asociacion, conjunto=self.conjunto).exists())

# Create your tests here.
