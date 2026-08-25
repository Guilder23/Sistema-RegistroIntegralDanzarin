from django.urls import path
from .views import listar_grupos, crear_grupo, editar_grupo, eliminar_grupo

app_name = 'grupos'
urlpatterns = [
    path('', listar_grupos, name='listar_grupos'),
    path('crear/', crear_grupo, name='crear_grupo'),
    path('<int:pk>/editar/', editar_grupo, name='editar_grupo'),
    path('<int:pk>/eliminar/', eliminar_grupo, name='eliminar_grupo'),
]
