from django.urls import path
from .views import reportes_socios, descargar_reporte_socios, descargar_reporte_socios_pdf

app_name = 'reportes'

urlpatterns = [
    path('', reportes_socios, name='reportes_socios'),
    path('socios/pdf/', descargar_reporte_socios, name='descargar_reporte_socios'),
    path('socios/reporte-pdf/', descargar_reporte_socios_pdf, name='descargar_reporte_socios_pdf'),
]
