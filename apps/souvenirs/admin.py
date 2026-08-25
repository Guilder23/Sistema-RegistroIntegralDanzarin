from django.contrib import admin
from .models import SouvenirEntrega, Souvenir


@admin.register(Souvenir)
class SouvenirAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'evento', 'stock', 'activo')
    list_filter = ('activo', 'evento')
    search_fields = ('nombre', 'descripcion', 'evento__nombre')


@admin.register(SouvenirEntrega)
class SouvenirEntregaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'evento', 'fecha_entrega', 'entregado_por')
    search_fields = ('socio__nombre', 'socio__apellido', 'evento__nombre')
