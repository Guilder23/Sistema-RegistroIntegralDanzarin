from django.urls import path
from .views import listar_conjuntos, crear_conjunto, editar_conjunto, eliminar_conjunto

app_name = 'conjuntos'
urlpatterns = [
    path('', listar_conjuntos, name='listar_conjuntos'),
    path('crear/', crear_conjunto, name='crear_conjunto'),
    path('<int:pk>/editar/', editar_conjunto, name='editar_conjunto'),
    path('<int:pk>/eliminar/', eliminar_conjunto, name='eliminar_conjunto'),
]
