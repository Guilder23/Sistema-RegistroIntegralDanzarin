from django.contrib import admin
from .models import Socio


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'email', 'estado', 'fecha_ingreso')
    list_filter = ('estado',)
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'email')
