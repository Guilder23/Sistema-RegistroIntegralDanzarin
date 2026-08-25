from django.urls import path
from .views import listar_membresias, cambiar_membresia

app_name = 'membresias'
urlpatterns = [
    path('', listar_membresias, name='listar_membresias'),
    path('<int:pk>/editar/', cambiar_membresia, name='cambiar_membresia'),
]
