from django.urls import path
from .views import listar_danzarines, crear_danzarin, editar_danzarin, activar_danzarin, desactivar_danzarin, eliminar_danzarin, perfil_danzarin, historial_souvenirs
from .views import subir_foto
from .views import crear_admin, importar_danzarines, importar_danzarines_masivo, importar_danzarines_xlsx_preview, importar_danzarines_xlsx_confirm
from .views import descargar_plantilla_excel, importar_danzarines_xlsx, descargar_danzarin_pdf
from .views import listar_admins, ver_admin, editar_admin, eliminar_admin, mis_souvenirs
from .views import editar_perfil, cambiar_contrasena, certificado_publico, certificado_qr

app_name = 'danzarines'

urlpatterns = [
    path('', listar_danzarines, name='listar_danzarines'),
    path('nuevo/', crear_danzarin, name='crear_danzarin'),
    path('<int:danzarin_id>/editar/', editar_danzarin, name='editar_danzarin'),
    path('<int:danzarin_id>/historial_souvenirs/', historial_souvenirs, name='historial_souvenirs'),
    path('<int:danzarin_id>/pdf/', descargar_danzarin_pdf, name='descargar_danzarin_pdf'),
    path('<int:danzarin_id>/activar/', activar_danzarin, name='activar_danzarin'),
    path('<int:danzarin_id>/desactivar/', desactivar_danzarin, name='desactivar_danzarin'),
    path('<int:danzarin_id>/eliminar/', eliminar_danzarin, name='eliminar_danzarin'),
    path('perfil/', perfil_danzarin, name='perfil_danzarin'),
    path('certificado/<str:token>/', certificado_publico, name='certificado_publico'),
    path('certificado/<str:token>', certificado_publico, name='certificado_publico_sin_barra'),
    path('certificado/<str:token>/qr/', certificado_qr, name='certificado_qr'),
    path('certificado/<str:token>/qr', certificado_qr, name='certificado_qr_sin_barra'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/cambiar_contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
    path('subir_foto/', subir_foto, name='subir_foto'),
    path('crear_admin/', crear_admin, name='crear_admin'),
    path('importar/', importar_danzarines, name='importar_danzarines'),
    path('importar/masivo/', importar_danzarines_masivo, name='importar_danzarines_masivo'),
    path('importar/masivo/preview/', importar_danzarines_xlsx_preview, name='importar_danzarines_xlsx_preview'),
    path('importar/masivo/confirmar/', importar_danzarines_xlsx_confirm, name='importar_danzarines_xlsx_confirm'),
    path('importar/xlsx/', importar_danzarines_xlsx, name='importar_danzarines_xlsx'),
    path('importar/plantilla/', descargar_plantilla_excel, name='descargar_plantilla_excel'),
    path('admins/', listar_admins, name='listar_admins'),
    path('admins/<int:user_id>/', ver_admin, name='ver_admin'),
    path('admins/<int:user_id>/editar/', editar_admin, name='editar_admin'),
    path('admins/<int:user_id>/eliminar/', eliminar_admin, name='eliminar_admin'),
    path('mis_souvenirs/', mis_souvenirs, name='mis_souvenirs'),
]
