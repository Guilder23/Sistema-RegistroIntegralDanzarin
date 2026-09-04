from django.contrib.auth.models import User
from io import BytesIO
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from apps.core.models import Asociacion, Conjunto
from apps.bloques.models import Bloque
from .models import Membresia, Danzarin


class MembresiaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='miembro', password='secret')
        self.danzarin = Danzarin.objects.create(
            user=self.usuario,
            nombre='Ana',
            apellido_paterno='Perez',
            email='ana@example.com',
        )
        self.asociacion = Asociacion.objects.create(nombre='Asociacion A')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto A')

    def test_deuda_suspendes_y_pago_al_dia_reactiva(self):
        membresia = Membresia.objects.create(
            danzarin=self.danzarin,
            asociacion=self.asociacion,
            conjunto=self.conjunto,
            estado_pago='con_deuda',
        )
        self.assertEqual(membresia.estado, 'suspendido')

        membresia.estado_pago = 'al_dia'
        membresia.save()
        self.assertEqual(membresia.estado, 'activo')

    def test_no_permite_dos_membresias_vigentes_en_un_asociacion(self):
        Membresia.objects.create(danzarin=self.danzarin, asociacion=self.asociacion, conjunto=self.conjunto)
        otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto B')
        with self.assertRaises((ValueError, IntegrityError)):
            Membresia.inscribir(self.danzarin, self.asociacion, otro_conjunto)


class RolesDanzarinesTests(TestCase):
    def setUp(self):
        self.asociacion = Asociacion.objects.create(nombre='Asociacion Roles')
        self.conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Roles')
        self.bloque = Bloque.objects.create(conjunto=self.conjunto, nombre='Bloque Roles')

    def crear_usuario(self, username, rol):
        user = User.objects.create_user(username=username, password='secret123', is_staff=True)
        user.userprofile.rol = rol
        user.userprofile.asociacion = self.asociacion
        user.userprofile.conjunto = self.conjunto if rol == 'administrador_conjunto' else None
        user.userprofile.save()
        return user

    def test_administrador_asociacion_puede_registrar_danzarines(self):
        self.client.force_login(self.crear_usuario('admin-asociacion', 'administrador_asociacion'))
        response = self.client.post(reverse('danzarines:crear_danzarin'), {
            'username': 'danzarin-asociacion', 'password': 'secret123', 'nombre': 'Ana',
            'apellido_paterno': 'Lopez', 'email': 'ana@example.com',
            'conjunto_id': self.conjunto.pk, 'bloque_id': self.bloque.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Danzarin.objects.filter(nombre='Ana').exists())

    def test_administrador_conjunto_puede_registrar_danzarin_con_membresia(self):
        self.client.force_login(self.crear_usuario('admin-conjunto', 'administrador_conjunto'))
        response = self.client.post(reverse('danzarines:crear_danzarin'), {
            'username': 'nuevo-danzarin', 'password': 'secret123', 'nombre': 'Luis',
            'apellido_paterno': 'Gomez', 'email': 'luis@example.com',
            'bloque_id': self.bloque.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membresia.objects.filter(asociacion=self.asociacion, conjunto=self.conjunto).exists())
        self.assertEqual(Membresia.objects.get(danzarin__nombre='Luis').bloque, self.bloque)

    def test_mismo_danzarin_puede_pertenecer_a_otra_asociacion_por_carnet(self):
        usuario = self.crear_usuario('admin-asociacion-2', 'administrador_asociacion')
        otra_asociacion = Asociacion.objects.create(nombre='Asociacion B')
        otro_conjunto = Conjunto.objects.create(asociacion=otra_asociacion, nombre='Conjunto B')
        otro_bloque = Bloque.objects.create(conjunto=otro_conjunto, nombre='Bloque B')
        self.client.force_login(usuario)
        primera = self.client.post(reverse('danzarines:crear_danzarin'), {
            'username': 'persona-a', 'password': 'secret123', 'nombre': 'Persona',
            'apellido_paterno': 'Prueba', 'email': 'persona@example.com',
            'conjunto_id': self.conjunto.pk, 'bloque_id': self.bloque.pk,
            'carnet_ci': '12345', 'carnet_complemento': 'A',
        })
        self.assertEqual(primera.status_code, 302)

        administrador_super = User.objects.create_superuser('super-inscripcion', 'super@example.com', 'secret123')
        self.client.force_login(administrador_super)
        segunda = self.client.post(reverse('danzarines:crear_danzarin'), {
            'nombre': 'Persona', 'carnet_ci': '12345', 'carnet_complemento': 'A',
            'asociacion_id': otra_asociacion.pk, 'conjunto_id': otro_conjunto.pk,
            'bloque_id': otro_bloque.pk,
        })

        self.assertEqual(segunda.status_code, 302)
        danzarin = Danzarin.objects.get(carnet_ci='12345', carnet_complemento='A')
        self.assertEqual(Membresia.objects.filter(danzarin=danzarin).count(), 2)

    def test_no_permite_dos_conjuntos_activos_en_la_misma_asociacion(self):
        danzarin_user = User.objects.create_user('persona-activa', password='secret123')
        danzarin = Danzarin.objects.create(user=danzarin_user, nombre='Persona', apellido_paterno='Activa', email='activa@example.com', carnet_ci='54321', carnet_complemento='B')
        Membresia.objects.create(danzarin=danzarin, asociacion=self.asociacion, conjunto=self.conjunto, bloque=self.bloque)
        otro_conjunto = Conjunto.objects.create(asociacion=self.asociacion, nombre='Conjunto Dos')
        otro_bloque = Bloque.objects.create(conjunto=otro_conjunto, nombre='Bloque Dos')
        self.client.force_login(User.objects.create_superuser('super-activa', 'activa@example.com', 'secret123'))

        response = self.client.post(reverse('danzarines:crear_danzarin'), {
            'nombre': 'Persona', 'carnet_ci': '54321', 'carnet_complemento': 'B',
            'asociacion_id': self.asociacion.pk, 'conjunto_id': otro_conjunto.pk,
            'bloque_id': otro_bloque.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Membresia.objects.filter(danzarin=danzarin, asociacion=self.asociacion).count(), 1)

    def test_deuda_suspendida_y_pago_al_dia_activa_con_update_fields(self):
        danzarin_user = User.objects.create_user('persona-pago', password='secret123')
        danzarin = Danzarin.objects.create(user=danzarin_user, nombre='Persona', apellido_paterno='Pago', email='pago@example.com')
        membresia = Membresia.objects.create(danzarin=danzarin, asociacion=self.asociacion, conjunto=self.conjunto, bloque=self.bloque)

        membresia.estado_pago = 'con_deuda'
        membresia.save(update_fields=['estado_pago'])
        self.assertEqual(membresia.estado, 'suspendido')

        membresia.estado_pago = 'al_dia'
        membresia.save(update_fields=['estado_pago'])
        self.assertEqual(membresia.estado, 'activo')


class PlantillaDanzarinesExcelTests(TestCase):
    def test_plantilla_tiene_encabezados_y_ejemplo_alineados(self):
        administrador = User.objects.create_superuser(
            username='admin-plantilla', email='admin@example.com', password='secret123'
        )
        self.client.force_login(administrador)

        response = self.client.get(reverse('danzarines:descargar_plantilla_excel'))

        self.assertEqual(response.status_code, 200)
        workbook = load_workbook(BytesIO(response.content))
        worksheet = workbook.active
        headers = [cell.value for cell in worksheet[1]]
        example = [cell.value for cell in worksheet[2]]
        self.assertEqual(len(headers), 16)
        self.assertEqual(len(example), 16)
        self.assertEqual(headers[4:7], ['sexo', 'email', 'password'])
        self.assertEqual(example[4:7], ['M', 'jdoe@example.com', 'Passw0rd!'])
        self.assertEqual(example[13:], [
            'Nombre exacto de asociación',
            'Nombre exacto de conjunto',
            'Nombre exacto de bloque',
        ])
        self.assertEqual(worksheet.column_dimensions['P'].width, 28)