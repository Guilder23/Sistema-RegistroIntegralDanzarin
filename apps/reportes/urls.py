from django.urls import path
from .views import reportes_danzarines, descargar_reporte_danzarines, descargar_reporte_danzarines_pdf

app_name = 'reportes'

urlpatterns = [
    path('', reportes_danzarines, name='reportes_danzarines'),
    path('danzarines/pdf/', descargar_reporte_danzarines, name='descargar_reporte_danzarines'),
    path('danzarines/reporte-pdf/', descargar_reporte_danzarines_pdf, name='descargar_reporte_danzarines_pdf'),
]
