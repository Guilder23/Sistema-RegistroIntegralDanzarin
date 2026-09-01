from django.urls import path
from .views import listar_bloques, crear_bloque, editar_bloque, eliminar_bloque

app_name = 'bloques'
urlpatterns = [
    path('', listar_bloques, name='listar_bloques'),
    path('crear/', crear_bloque, name='crear_bloque'),
    path('<int:pk>/editar/', editar_bloque, name='editar_bloque'),
    path('<int:pk>/eliminar/', eliminar_bloque, name='eliminar_bloque'),
]
