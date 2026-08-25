from django.urls import path
from .views import reportes_socios, descargar_reporte_socios

app_name = 'reportes'

urlpatterns = [
    path('', reportes_socios, name='reportes_socios'),
    path('socios/pdf/', descargar_reporte_socios, name='descargar_reporte_socios'),
]
