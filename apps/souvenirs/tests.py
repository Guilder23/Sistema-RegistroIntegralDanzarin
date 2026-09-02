from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Asociacion, Conjunto
from apps.eventos.models import Evento
from apps.socios.models import Membresia, Socio
from .models import Souvenir, SouvenirEntrega


class EntregaSouvenirScopeTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Entregas')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto A')
        self.otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto B')
        self.evento = Evento.objects.create(
            nombre='Evento A', fecha_evento=date(2026, 9, 1),
            asociacion=self.asociacion, conjunto=self.conjunto,
        )
        self.otro_evento = Evento.objects.create(
            nombre='Evento B', fecha_evento=date(2026, 9, 2),
            asociacion=self.asociacion, conjunto=self.otro_conjunto,
        )
        self.souvenir = Souvenir.objects.create(
            nombre='Souvenir A', asociacion=self.asociacion,
            conjunto=self.conjunto, evento=self.evento, stock=2,
        )
        self.otro_souvenir = Souvenir.objects.create(
            nombre='Souvenir B', asociacion=self.asociacion,
            conjunto=self.otro_conjunto, evento=self.otro_evento, stock=2,
        )
        socio_user = User.objects.create_user('socio-entrega', password='secret123')
        self.socio = Socio.objects.create(
            user=socio_user, nombre='Socio', apellido='Entrega',
            email='socio@example.com',
        )
        Membresia.objects.create(
            socio=self.socio, asociacion=self.asociacion,
            conjunto=self.conjunto,
        )
        self.admin = User.objects.create_user('admin-conjunto-entrega', password='secret123', is_staff=True)
        self.admin.userprofile.rol = 'administrador_conjunto'
        self.admin.userprofile.asociacion = self.asociacion
        self.admin.userprofile.conjunto = self.conjunto
        self.admin.userprofile.save()

    def datos_entrega(self, evento, souvenir):
        return {
            'asociacion_id': self.asociacion.pk,
            'conjunto_id': self.conjunto.pk,
            'socio_id': self.socio.pk,
            'evento_id': evento.pk,
            'souvenir_id': souvenir.pk,
        }

    def test_admin_conjunto_puede_entregar_souvenir_de_su_evento(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:registrar_entrega'),
            self.datos_entrega(self.evento, self.souvenir),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SouvenirEntrega.objects.filter(socio=self.socio, evento=self.evento).exists())

    def test_admin_conjunto_no_puede_usar_evento_de_otro_conjunto(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:registrar_entrega'),
            self.datos_entrega(self.otro_evento, self.otro_souvenir),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SouvenirEntrega.objects.exists())
