from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ReportesExcelTests(TestCase):
    def test_descarga_reporte_socios_entrega_excel(self):
        User = get_user_model()
        user = User.objects.create_user(username='stafftest', password='secret123', is_staff=True)

        self.client.force_login(user)
        response = self.client.get(reverse('reportes:descargar_reporte_socios'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response['Content-Type'])
        self.assertIn('reporte_socios.xlsx', response['Content-Disposition'])
