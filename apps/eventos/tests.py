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
        return {
            'nombre': 'Ensayo general',
            'fecha_inicio': '2026-09-01',
            'fecha_fin': '2026-09-01',
            'activo': 'on',
            'tipo_ambito': 'conjunto',
            'asociacion_id': self.asociacion.pk,
            'conjunto_id': self.conjunto.pk,
        }

    def test_administrador_asociacion_puede_crear_eventos_de_su_asociacion(self):
        self.client.force_login(self.usuario('asociacion', 'administrador_asociacion'))
        response = self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(asociacion=self.asociacion).exists())

    def test_conjunto_puede_crear_eventos_y_miembro_no(self):
        self.client.force_login(self.usuario('conjunto', 'administrador_conjunto'))
        response = self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evento.objects.count(), 1)
        self.client.force_login(self.usuario('miembro', 'miembro'))
        self.client.post(reverse('eventos:crear_evento'), self.datos_evento())
        self.assertEqual(Evento.objects.count(), 1)

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

    def test_evento_guarda_fecha_de_inicio_y_fecha_fin(self):
        self.client.force_login(self.usuario('asociacion-rango', 'administrador_asociacion'))
        datos = self.datos_evento() | {
            'fecha_inicio': '2026-09-01',
            'fecha_fin': '2026-09-05',
            'tipo_ambito': 'asociacion',
            'asociacion_id': self.asociacion.pk,
        }

        response = self.client.post(reverse('eventos:crear_evento'), datos)

        self.assertEqual(response.status_code, 302)
        evento = Evento.objects.get()
        self.assertEqual(str(evento.fecha_inicio), '2026-09-01')
        self.assertEqual(str(evento.fecha_fin), '2026-09-05')

    def test_no_permite_fecha_fin_anterior_al_inicio(self):
        self.client.force_login(self.usuario('asociacion-fecha-invalida', 'administrador_asociacion'))
        datos = self.datos_evento() | {
            'fecha_inicio': '2026-09-05',
            'fecha_fin': '2026-09-01',
            'tipo_ambito': 'asociacion',
            'asociacion_id': self.asociacion.pk,
        }

        response = self.client.post(reverse('eventos:crear_evento'), datos)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Evento.objects.exists())

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
