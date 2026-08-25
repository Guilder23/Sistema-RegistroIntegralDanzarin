from django.urls import path

from .views import (
    cerrar_sesion,
    editar_usuario,
    eliminar_usuario,
    faq,
    inicio,
    iniciar_sesion,
    robots_txt,
    registrar_usuario,
    sitemap_xml,
    toggle_bloqueo_usuario,
)

app_name = 'core'

urlpatterns = [
    path('', inicio, name='inicio'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('registro/', registrar_usuario, name='registro'),
    path('faq/', faq, name='faq'),
    path('robots.txt', robots_txt, name='robots'),
    path('sitemap.xml', sitemap_xml, name='sitemap'),
    path('usuarios/<int:user_id>/editar/', editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/bloqueo/', toggle_bloqueo_usuario, name='toggle_bloqueo_usuario'),
    path('usuarios/<int:user_id>/eliminar/', eliminar_usuario, name='eliminar_usuario'),
]
