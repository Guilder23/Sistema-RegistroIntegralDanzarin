from django.db import models
from django.contrib.auth.models import User


class SouvenirEntrega(models.Model):
    socio = models.ForeignKey('socios.Socio', on_delete=models.CASCADE, related_name='entregas_souvenir')
    evento = models.ForeignKey('eventos.Evento', on_delete=models.CASCADE, null=True, blank=True, related_name='entregas_souvenir')
    souvenir = models.ForeignKey('Souvenir', on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas')
    fecha_entrega = models.DateField(auto_now_add=True, verbose_name='Fecha de entrega')
    entregado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas_souvenir')
    observacion = models.TextField(blank=True, default='', verbose_name='Observación')

    class Meta:
        verbose_name = 'Entrega de souvenir'
        verbose_name_plural = 'Entregas de souvenirs'
        ordering = ['-fecha_entrega']

    def __str__(self):
        evento_text = self.evento.nombre if self.evento else 'Sin evento'
        return f'{self.socio} - {evento_text} - {self.fecha_entrega}'


class Souvenir(models.Model):
    nombre = models.CharField(max_length=200)
    evento = models.ForeignKey('eventos.Evento', on_delete=models.SET_NULL, null=True, blank=True, related_name='souvenirs')
    descripcion = models.TextField(blank=True, default='')
    imagen = models.ImageField(upload_to='souvenirs/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Souvenir'
        verbose_name_plural = 'Souvenirs'

    def __str__(self):
        return self.nombre
