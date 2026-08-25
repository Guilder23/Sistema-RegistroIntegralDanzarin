from django.urls import path
from .views import listar_eventos, crear_evento, editar_evento, eliminar_evento, ver_evento, cambiar_estado_evento, descargar_certificado

app_name = 'eventos'

urlpatterns = [
    path('', listar_eventos, name='listar_eventos'),
    path('crear/', crear_evento, name='crear_evento'),
    path('<int:pk>/', ver_evento, name='ver_evento'),
    path('<int:pk>/editar/', editar_evento, name='editar_evento'),
    path('<int:pk>/eliminar/', eliminar_evento, name='eliminar_evento'),
    path('<int:pk>/estado/', cambiar_estado_evento, name='cambiar_estado_evento'),
    path('certificados/<int:pk>/descargar/', descargar_certificado, name='descargar_certificado'),
]
