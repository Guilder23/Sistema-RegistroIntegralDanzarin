from django.conf import settings
from django.db import models


class Grupo(models.Model):
	nombre = models.CharField(max_length=150, unique=True)
	activo = models.BooleanField(default=True)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['nombre']

	def __str__(self):
		return self.nombre


class Subgrupo(models.Model):
	grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='subgrupos')
	nombre = models.CharField(max_length=150)
	activo = models.BooleanField(default=True)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['grupo', 'nombre'], name='unique_subgrupo_por_grupo'),
		]
		ordering = ['grupo__nombre', 'nombre']

	def __str__(self):
		return f'{self.grupo} / {self.nombre}'


class Auditoria(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='acciones_auditadas')
	fecha_hora = models.DateTimeField(auto_now_add=True)
	accion = models.CharField(max_length=100)
	registro_afectado = models.CharField(max_length=255)
	valor_anterior = models.JSONField(null=True, blank=True)
	valor_nuevo = models.JSONField(null=True, blank=True)
	grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
	subgrupo = models.ForeignKey(Subgrupo, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')

	class Meta:
		ordering = ['-fecha_hora']

	def __str__(self):
		return f'{self.accion} - {self.registro_afectado}'

