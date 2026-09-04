from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from io import BytesIO


class Evento(models.Model):
    ESTADO_CHOICES = [('programado', 'Programado'), ('finalizado', 'Finalizado')]
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    fecha_evento = models.DateField(verbose_name='Fecha del evento')
    lugar = models.CharField(max_length=250, blank=True, default='')
    activo = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    asociacion = models.ForeignKey('core.Asociacion', on_delete=models.PROTECT, related_name='eventos', null=True, blank=True)
    conjunto = models.ForeignKey('core.Conjunto', on_delete=models.PROTECT, related_name='eventos', null=True, blank=True)
    participantes = models.ManyToManyField('danzarines.Danzarin', through='EventoParticipante', related_name='eventos')
    creado = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='eventos_creados', null=True, blank=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_evento', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        was_programado = False
        if self.pk:
            was_programado = Evento.objects.filter(pk=self.pk, estado='programado').exists()
        super().save(*args, **kwargs)
        if was_programado and self.estado == 'finalizado':
            self.generar_certificados()

    def generar_certificados(self):
        for danzarin in self.participantes.all():
            if Certificado.objects.filter(evento=self, danzarin=danzarin).exists():
                continue
            buffer = BytesIO()
            documento = canvas.Canvas(buffer)
            documento.drawCentredString(300, 700, 'CERTIFICADO DE PARTICIPACION')
            documento.drawCentredString(300, 650, f'Se certifica que {danzarin} participo en {self.nombre}.')
            documento.drawCentredString(300, 600, f'Fecha: {self.fecha_evento:%d/%m/%Y}')
            documento.save()
            certificado = Certificado(evento=self, danzarin=danzarin)
            certificado.archivo.save(
                f'certificado_{self.pk}_{danzarin.pk}.pdf',
                ContentFile(buffer.getvalue()),
                save=True,
            )


class EventoParticipante(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscripciones')
    danzarin = models.ForeignKey('danzarines.Danzarin', on_delete=models.CASCADE, related_name='participaciones')
    registrado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evento', 'danzarin'], name='unique_participante_evento'),
        ]


class Certificado(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='certificados')
    danzarin = models.ForeignKey('danzarines.Danzarin', on_delete=models.CASCADE, related_name='certificados')
    archivo = models.FileField(upload_to='certificados/')
    generado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evento', 'danzarin'], name='unique_certificado_evento_danzarin'),
        ]
