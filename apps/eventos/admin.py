from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_evento', 'lugar', 'activo')
    list_filter = ('activo', 'fecha_evento')
    search_fields = ('nombre', 'descripcion', 'lugar')
