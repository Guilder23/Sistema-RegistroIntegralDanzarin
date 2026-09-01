from django.urls import path
from .views import listar_asociaciones, crear_asociacion, editar_asociacion, eliminar_asociacion

app_name = 'asociaciones'
urlpatterns = [
    path('', listar_asociaciones, name='listar_asociaciones'),
    path('crear/', crear_asociacion, name='crear_asociacion'),
    path('<int:pk>/editar/', editar_asociacion, name='editar_asociacion'),
    path('<int:pk>/eliminar/', eliminar_asociacion, name='eliminar_asociacion'),
]
