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

    def test_superadministrador_puede_crear_evento_para_asociacion(self):
        self.client.force_login(self.usuario('superadmin', 'superadministrador'))
        datos = self.datos_evento() | {
            'tipo_ambito': 'asociacion',
            'asociacion_id': self.asociacion.pk,
        }

        response = self.client.post(reverse('eventos:crear_evento'), datos)

        self.assertEqual(response.status_code, 302)
        evento = Evento.objects.get()
        self.assertEqual(evento.asociacion, self.asociacion)
        self.assertIsNone(evento.conjunto)
        self.assertEqual(evento.creado_por.username, 'superadmin')

    def test_superadministrador_puede_crear_evento_para_conjunto(self):
        self.client.force_login(self.usuario('superadmin-conjunto', 'superadministrador'))
        datos = self.datos_evento() | {
            'tipo_ambito': 'conjunto',
            'asociacion_id': self.asociacion.pk,
            'conjunto_id': self.conjunto.pk,
        }

        response = self.client.post(reverse('eventos:crear_evento'), datos)

        self.assertEqual(response.status_code, 302)
        evento = Evento.objects.get()
        self.assertEqual(evento.asociacion, self.asociacion)
        self.assertEqual(evento.conjunto, self.conjunto)

    def test_no_permite_conjunto_de_otra_asociacion(self):
        otra_asociacion = Asociacion.objects.create(nombre='Otra Asociacion')
        otro_conjunto = Conjunto.objects.create(asociacion=otra_asociacion, nombre='Otro Conjunto')
        self.client.force_login(self.usuario('superadmin-invalido', 'superadministrador'))
        datos = self.datos_evento() | {
            'tipo_ambito': 'conjunto',
            'asociacion_id': self.asociacion.pk,
            'conjunto_id': otro_conjunto.pk,
        }

        response = self.client.post(reverse('eventos:crear_evento'), datos)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Evento.objects.exists())
