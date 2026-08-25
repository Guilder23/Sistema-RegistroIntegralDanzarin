from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Grupo, Subgrupo
from .models import Evento


class RolesEventosTests(TestCase):
    def setUp(self):
        self.grupo = Grupo.objects.create(nombre='Grupo Eventos')
        self.subgrupo = Subgrupo.objects.create(grupo=self.grupo, nombre='Subgrupo Eventos')

    def usuario(self, username, rol):
        user = User.objects.create_user(username=username, password='secret123', is_staff=rol != 'miembro')
        user.userprofile.rol = rol
        user.userprofile.grupo = self.grupo
        user.userprofile.subgrupo = self.subgrupo if rol == 'administrador_subgrupo' else None
        user.userprofile.save()
        return user

    def datos_evento(self):
        return {'nombre': 'Ensayo general', 'fecha_evento': '2026-09-01', 'activo': 'on'}

    def test_administrador_grupo_puede_crear_eventos_de_su_grupo(self):
        self.client.force_login(self.usuario('grupo', 'administrador_grupo'))
        response = self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(grupo=self.grupo).exists())

    def test_subgrupo_y_miembro_no_pueden_crear_eventos(self):
        self.client.force_login(self.usuario('subgrupo', 'administrador_subgrupo'))
        self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.client.force_login(self.usuario('miembro', 'miembro'))
        self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(Evento.objects.count(), 0)
