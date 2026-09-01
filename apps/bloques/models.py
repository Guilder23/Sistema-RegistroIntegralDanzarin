from django.db import models


class Bloque(models.Model):
    conjunto = models.ForeignKey('core.Conjunto', on_delete=models.CASCADE, related_name='bloques')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['conjunto__asociacion__nombre', 'conjunto__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(fields=['conjunto', 'nombre'], name='unique_bloque_por_conjunto'),
        ]

    def __str__(self):
        return f'{self.conjunto.asociacion} / {self.conjunto.nombre} / {self.nombre}'
