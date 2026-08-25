from django.urls import path
from .views import listar_subgrupos, crear_subgrupo, editar_subgrupo, eliminar_subgrupo

app_name = 'subgrupos'
urlpatterns = [
    path('', listar_subgrupos, name='listar_subgrupos'),
    path('crear/', crear_subgrupo, name='crear_subgrupo'),
    path('<int:pk>/editar/', editar_subgrupo, name='editar_subgrupo'),
    path('<int:pk>/eliminar/', eliminar_subgrupo, name='eliminar_subgrupo'),
]
