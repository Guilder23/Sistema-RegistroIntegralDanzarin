from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Grupo, Subgrupo


class GestionRolesTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_superuser('root', 'root@example.com', 'secret123')
		self.grupo = Grupo.objects.create(nombre='Grupo Usuarios')
		self.subgrupo = Subgrupo.objects.create(grupo=self.grupo, nombre='Subgrupo Usuarios')
		self.client.force_login(self.admin)

	def test_crea_administrador_de_subgrupo_con_ambito(self):
		response = self.client.post(reverse('core:registro'), {
			'username': 'admin-sub', 'email': 'sub@example.com',
			'password': 'secret123', 'password2': 'secret123',
			'rol': 'administrador_subgrupo', 'grupo_id': self.grupo.pk,
			'subgrupo_id': self.subgrupo.pk,
		})
		self.assertEqual(response.status_code, 302)
		usuario = User.objects.get(username='admin-sub')
		self.assertEqual(usuario.userprofile.rol, 'administrador_subgrupo')
		self.assertEqual(usuario.userprofile.grupo_id, self.grupo.pk)
		self.assertEqual(usuario.userprofile.subgrupo_id, self.subgrupo.pk)

	def test_no_crea_administrador_de_grupo_sin_grupo(self):
		self.client.post(reverse('core:registro'), {
			'username': 'sin-grupo', 'email': 'sin@example.com',
			'password': 'secret123', 'password2': 'secret123',
			'rol': 'administrador_grupo',
		})
		self.assertFalse(User.objects.filter(username='sin-grupo').exists())

	def test_miembro_crea_socio_y_membresia(self):
		self.client.post(reverse('core:registro'), {
			'username': 'miembro', 'first_name': 'María', 'last_name': 'López',
			'email': 'maria@example.com', 'password': 'secret123', 'password2': 'secret123',
			'rol': 'miembro', 'grupo_id': self.grupo.pk, 'subgrupo_id': self.subgrupo.pk,
		})
		usuario = User.objects.get(username='miembro')
		self.assertTrue(hasattr(usuario, 'socio_profile'))
		self.assertTrue(usuario.socio_profile.membresias.filter(grupo=self.grupo, subgrupo=self.subgrupo).exists())

# Create your tests here.
