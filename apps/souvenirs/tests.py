from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Asociacion, Conjunto
from apps.eventos.models import Evento
from apps.danzarines.models import Membresia, Danzarin
from .models import Souvenir, SouvenirEntrega


class EntregaSouvenirScopeTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Entregas')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto A')
        self.otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto B')
        self.evento = Evento.objects.create(
            nombre='Evento A', fecha_inicio=date(2026, 9, 1), fecha_fin=date(2026, 9, 1),
            asociacion=self.asociacion, conjunto=self.conjunto,
        )
        self.otro_evento = Evento.objects.create(
            nombre='Evento B', fecha_inicio=date(2026, 9, 2), fecha_fin=date(2026, 9, 2),
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
        danzarin_user = User.objects.create_user('danzarin-entrega', password='secret123')
        self.danzarin = Danzarin.objects.create(
            user=danzarin_user, nombre='Danzarin', apellido_paterno='Entrega',
            email='danzarin@example.com',
        )
        Membresia.objects.create(
            danzarin=self.danzarin, asociacion=self.asociacion,
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
            'danzarin_id': self.danzarin.pk,
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
        self.assertTrue(SouvenirEntrega.objects.filter(danzarin=self.danzarin, evento=self.evento).exists())

    def test_admin_conjunto_no_puede_usar_evento_de_otro_conjunto(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:registrar_entrega'),
            self.datos_entrega(self.otro_evento, self.otro_souvenir),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SouvenirEntrega.objects.exists())

    def test_miembro_descarga_certificado_de_su_entrega(self):
        entrega = SouvenirEntrega.objects.create(
            danzarin=self.danzarin,
            evento=self.evento,
            souvenir=self.souvenir,
            entregado_por=self.admin,
        )
        self.client.force_login(self.danzarin.user)

        response = self.client.get(reverse('souvenirs:descargar_certificado_entrega', args=[entrega.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_miembro_no_descarga_certificado_de_otro_danzarin(self):
        otro_usuario = User.objects.create_user('otro-danzarin', password='secret123')
        otro_danzarin = Danzarin.objects.create(
            user=otro_usuario, nombre='Otro', apellido_paterno='Danzarin',
            email='otro@example.com',
        )
        entrega = SouvenirEntrega.objects.create(
            danzarin=otro_danzarin,
            evento=self.evento,
            souvenir=self.souvenir,
            entregado_por=self.admin,
        )
        self.client.force_login(self.danzarin.user)

        response = self.client.get(reverse('souvenirs:descargar_certificado_entrega', args=[entrega.pk]))

        self.assertEqual(response.status_code, 404)
