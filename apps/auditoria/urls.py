from django.urls import path
from .views import listar_auditoria

app_name = 'auditoria'
urlpatterns = [path('', listar_auditoria, name='listar_auditoria')]
