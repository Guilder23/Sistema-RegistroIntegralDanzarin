from datetime import date
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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

    def test_danzarin_solo_recibe_un_souvenir_por_evento(self):
        self.client.force_login(self.admin)
        datos = self.datos_entrega(self.evento, self.souvenir)

        primera = self.client.post(reverse('souvenirs:registrar_entrega'), datos)
        segunda = self.client.post(reverse('souvenirs:registrar_entrega'), datos)

        self.assertEqual(primera.status_code, 302)
        self.assertEqual(segunda.status_code, 302)
        self.assertEqual(
            SouvenirEntrega.objects.filter(danzarin=self.danzarin, evento=self.evento).count(),
            1,
        )

    def test_admin_conjunto_puede_entregar_souvenir_de_evento_de_asociacion(self):
        evento_asociacion = Evento.objects.create(
            nombre='Evento Asociación', fecha_inicio=date(2026, 9, 3),
            fecha_fin=date(2026, 9, 3), asociacion=self.asociacion,
        )
        souvenir_asociacion = Souvenir.objects.create(
            nombre='Souvenir Asociación', asociacion=self.asociacion,
            evento=evento_asociacion, stock=2,
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:registrar_entrega'),
            self.datos_entrega(evento_asociacion, souvenir_asociacion),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SouvenirEntrega.objects.filter(evento=evento_asociacion).exists())

    def test_admin_conjunto_no_puede_usar_evento_de_otro_conjunto(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:registrar_entrega'),
            self.datos_entrega(self.otro_evento, self.otro_souvenir),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SouvenirEntrega.objects.exists())

    def test_admin_conjunto_ve_su_conjunto_y_solo_sus_eventos(self):
        evento_asociacion = Evento.objects.create(
            nombre='Evento Asociación', fecha_inicio=date(2026, 9, 3),
            fecha_fin=date(2026, 9, 3), asociacion=self.asociacion,
        )

        self.client.force_login(self.admin)
        response = self.client.get(reverse('souvenirs:listar_souvenirs'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conjunto.nombre)
        self.assertContains(response, self.evento.nombre)
        self.assertNotContains(response, self.otro_evento.nombre)
        self.assertContains(response, evento_asociacion.nombre)

    def test_admin_conjunto_solo_puede_ver_souvenir_de_asociacion(self):
        evento_asociacion = Evento.objects.create(
            nombre='Evento Asociación Souvenir Solo Ver',
            fecha_inicio=date(2026, 9, 5),
            fecha_fin=date(2026, 9, 6),
            asociacion=self.asociacion,
        )
        souvenir_asociacion = Souvenir.objects.create(
            nombre='Souvenir Asociación Solo Ver',
            asociacion=self.asociacion,
            evento=evento_asociacion,
        )

        self.client.force_login(self.admin)
        response = self.client.get(reverse('souvenirs:listar_souvenirs'))

        self.assertContains(response, souvenir_asociacion.nombre)
        self.assertNotContains(response, f'data-id="{souvenir_asociacion.pk}"')
        self.assertEqual(
            self.client.post(reverse('souvenirs:editar_souvenir', args=[souvenir_asociacion.pk])).status_code,
            404,
        )

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


class GestionSouvenirAmbitoTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Souvenirs')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Souvenirs')
        self.otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Otro Conjunto')
        self.evento_asociacion = Evento.objects.create(
            nombre='Evento Asociación', fecha_inicio=date(2026, 10, 1),
            fecha_fin=date(2026, 10, 2), asociacion=self.asociacion,
        )
        self.evento_conjunto = Evento.objects.create(
            nombre='Evento Conjunto', fecha_inicio=date(2026, 10, 3),
            fecha_fin=date(2026, 10, 4), asociacion=self.asociacion,
            conjunto=self.conjunto,
        )
        self.admin = User.objects.create_user('admin-asociacion-souvenir', password='secret123', is_staff=True)
        self.admin.userprofile.rol = 'administrador_asociacion'
        self.admin.userprofile.asociacion = self.asociacion
        self.admin.userprofile.save()

    def datos_souvenir(self, evento, tipo_ambito, conjunto_id=''):
        return {
            'nombre': f'Souvenir {evento.nombre}',
            'tipo_ambito': tipo_ambito,
            'asociacion_id': self.asociacion.pk,
            'conjunto_id': conjunto_id,
            'evento_id': evento.pk,
            'stock': '2',
        }

    def test_admin_asociacion_puede_crear_souvenir_para_asociacion(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:crear_souvenir'),
            self.datos_souvenir(self.evento_asociacion, 'asociacion'),
        )

        self.assertEqual(response.status_code, 302)
        souvenir = Souvenir.objects.get()
        self.assertIsNone(souvenir.conjunto)
        self.assertEqual(souvenir.evento, self.evento_asociacion)

    def test_admin_asociacion_puede_crear_souvenir_para_su_conjunto(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:crear_souvenir'),
            self.datos_souvenir(self.evento_conjunto, 'conjunto', self.conjunto.pk),
        )

        self.assertEqual(response.status_code, 302)
        souvenir = Souvenir.objects.get()
        self.assertEqual(souvenir.conjunto, self.conjunto)
        self.assertEqual(souvenir.evento, self.evento_conjunto)

    def test_souvenir_de_conjunto_no_puede_usar_evento_de_asociacion(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:crear_souvenir'),
            self.datos_souvenir(self.evento_asociacion, 'conjunto', self.conjunto.pk),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Souvenir.objects.exists())

    def test_no_se_puede_crear_dos_souvenirs_para_un_evento(self):
        Souvenir.objects.create(
            nombre='Souvenir existente',
            asociacion=self.asociacion,
            evento=self.evento_asociacion,
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('souvenirs:crear_souvenir'),
            self.datos_souvenir(self.evento_asociacion, 'asociacion'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Souvenir.objects.filter(evento=self.evento_asociacion).count(), 1)

    def test_certificado_se_habilita_despues_de_fecha_fin(self):
        evento_futuro = Evento.objects.create(
            nombre='Evento Futuro',
            fecha_inicio=timezone.localdate(),
            fecha_fin=timezone.localdate(),
            asociacion=self.asociacion,
        )
        souvenir = Souvenir.objects.create(
            nombre='Souvenir Futuro', asociacion=self.asociacion, evento=evento_futuro,
        )
        danzarin_user = User.objects.create_user('danzarin-certificado', password='secret123')
        danzarin = Danzarin.objects.create(
            user=danzarin_user, nombre='Danzarin Certificado', email='certificado@example.com',
        )
        entrega = SouvenirEntrega.objects.create(
            danzarin=danzarin, evento=evento_futuro, souvenir=souvenir, entregado_por=self.admin,
        )

        self.client.force_login(danzarin_user)
        response = self.client.get(
            reverse('souvenirs:descargar_certificado_entrega', args=[entrega.pk])
        )

        self.assertEqual(response.status_code, 404)

        evento_futuro.fecha_fin = timezone.localdate() - timedelta(days=1)
        evento_futuro.save(update_fields=['fecha_fin'])
        response = self.client.get(
            reverse('souvenirs:descargar_certificado_entrega', args=[entrega.pk])
        )
        self.assertEqual(response.status_code, 200)
