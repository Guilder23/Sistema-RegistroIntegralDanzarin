from django.urls import path
from .views import listar_socios, crear_socio, editar_socio, activar_socio, desactivar_socio, eliminar_socio, perfil_socio, historial_souvenirs
from .views import subir_foto
from .views import crear_admin, importar_socios, importar_socios_masivo, importar_socios_xlsx_preview, importar_socios_xlsx_confirm
from .views import descargar_plantilla_excel, importar_socios_xlsx
from .views import listar_admins, ver_admin, editar_admin, eliminar_admin, mis_souvenirs
from .views import editar_perfil, cambiar_contrasena

app_name = 'socios'

urlpatterns = [
    path('', listar_socios, name='listar_socios'),
    path('nuevo/', crear_socio, name='crear_socio'),
    path('<int:socio_id>/editar/', editar_socio, name='editar_socio'),
    path('<int:socio_id>/historial_souvenirs/', historial_souvenirs, name='historial_souvenirs'),
    path('<int:socio_id>/activar/', activar_socio, name='activar_socio'),
    path('<int:socio_id>/desactivar/', desactivar_socio, name='desactivar_socio'),
    path('<int:socio_id>/eliminar/', eliminar_socio, name='eliminar_socio'),
    path('perfil/', perfil_socio, name='perfil_socio'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/cambiar_contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
    path('subir_foto/', subir_foto, name='subir_foto'),
    path('crear_admin/', crear_admin, name='crear_admin'),
    path('importar/', importar_socios, name='importar_socios'),
    path('importar/masivo/', importar_socios_masivo, name='importar_socios_masivo'),
    path('importar/masivo/preview/', importar_socios_xlsx_preview, name='importar_socios_xlsx_preview'),
    path('importar/masivo/confirmar/', importar_socios_xlsx_confirm, name='importar_socios_xlsx_confirm'),
    path('importar/xlsx/', importar_socios_xlsx, name='importar_socios_xlsx'),
    path('importar/plantilla/', descargar_plantilla_excel, name='descargar_plantilla_excel'),
    path('admins/', listar_admins, name='listar_admins'),
    path('admins/<int:user_id>/', ver_admin, name='ver_admin'),
    path('admins/<int:user_id>/editar/', editar_admin, name='editar_admin'),
    path('admins/<int:user_id>/eliminar/', eliminar_admin, name='eliminar_admin'),
    path('mis_souvenirs/', mis_souvenirs, name='mis_souvenirs'),
]
