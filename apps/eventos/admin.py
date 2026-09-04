from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'lugar', 'activo')
    list_filter = ('activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion', 'lugar')
