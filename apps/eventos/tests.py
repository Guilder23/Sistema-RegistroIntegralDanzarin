from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Asociacion, Conjunto
from .models import Evento


class RolesEventosTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Eventos')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Eventos')

    def usuario(self, username, rol):
        user = User.objects.create_user(username=username, password='secret123', is_staff=rol != 'miembro')
        user.userprofile.rol = rol
        user.userprofile.asociacion = self.asociacion
        user.userprofile.conjunto = self.conjunto if rol == 'administrador_conjunto' else None
        user.userprofile.save()
        return user

    def datos_evento(self):
        return {'nombre': 'Ensayo general', 'fecha_evento': '2026-09-01', 'activo': 'on'}

    def test_administrador_asociacion_puede_crear_eventos_de_su_asociacion(self):
        self.client.force_login(self.usuario('asociacion', 'administrador_asociacion'))
        response = self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(asociacion=self.asociacion).exists())

    def test_conjunto_y_miembro_no_pueden_crear_eventos(self):
        self.client.force_login(self.usuario('conjunto', 'administrador_conjunto'))
        self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.client.force_login(self.usuario('miembro', 'miembro'))
        self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(Evento.objects.count(), 0)
