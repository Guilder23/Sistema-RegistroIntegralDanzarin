from django.urls import path
from .views import listar_entregas, registrar_entrega, listar_souvenirs, crear_souvenir, editar_souvenir, eliminar_souvenir, ver_souvenir, cambiar_estado_souvenir

app_name = 'souvenirs'

urlpatterns = [
    path('', listar_entregas, name='listar_entregas'),
    path('registrar/', registrar_entrega, name='registrar_entrega'),
    path('gestion/', listar_souvenirs, name='listar_souvenirs'),
    path('gestion/crear/', crear_souvenir, name='crear_souvenir'),
    path('gestion/<int:pk>/', ver_souvenir, name='ver_souvenir'),
    path('gestion/<int:pk>/editar/', editar_souvenir, name='editar_souvenir'),
    path('gestion/<int:pk>/eliminar/', eliminar_souvenir, name='eliminar_souvenir'),
    path('gestion/<int:pk>/estado/', cambiar_estado_souvenir, name='cambiar_estado_souvenir'),
]
