from django.conf import settings
from django.db import models


class Asociacion(models.Model):
	nombre = models.CharField(max_length=150, unique=True)
	activo = models.BooleanField(default=True)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['nombre']

	def __str__(self):
		return self.nombre


class Conjunto(models.Model):
	asociacion = models.ForeignKey(Asociacion, on_delete=models.CASCADE, related_name='conjuntos')
	nombre = models.CharField(max_length=150)
	activo = models.BooleanField(default=True)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['asociacion', 'nombre'], name='unique_conjunto_por_asociacion'),
		]
		ordering = ['asociacion__nombre', 'nombre']

	def __str__(self):
		return f'{self.asociacion} / {self.nombre}'


class Auditoria(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='acciones_auditadas')
	fecha_hora = models.DateTimeField(auto_now_add=True)
	accion = models.CharField(max_length=100)
	registro_afectado = models.CharField(max_length=255)
	valor_anterior = models.JSONField(null=True, blank=True)
	valor_nuevo = models.JSONField(null=True, blank=True)
	asociacion = models.ForeignKey(Asociacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
	conjunto = models.ForeignKey(Conjunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')

	class Meta:
		ordering = ['-fecha_hora']

	def __str__(self):
		return f'{self.accion} - {self.registro_afectado}'

