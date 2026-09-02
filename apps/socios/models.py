from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


class Socio(models.Model):
    SEXO_CHOICES = [('m', 'Varón'), ('f', 'Mujer'), ('otro', 'Otro')]
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='socio_profile')
    codigo_socio = models.CharField(max_length=6, unique=True, blank=True, null=True, verbose_name='Código de socio')
    nombre = models.CharField(max_length=150, verbose_name='Nombres')
    apellido_paterno = models.CharField(max_length=150, blank=True, default='', verbose_name='Apellido paterno')
    apellido_materno = models.CharField(max_length=150, blank=True, default='', verbose_name='Apellido materno')
    # Mantener campo legado para compatibilidad
    apellido = models.CharField(max_length=150, blank=True, default='', verbose_name='Apellidos')
    email = models.EmailField(verbose_name='Correo electrónico')
    carnet_ci = models.CharField(max_length=30, blank=True, default='', verbose_name='CI / Carnet')
    carnet_complemento = models.CharField(max_length=20, blank=True, default='', verbose_name='Complemento CI')
    telefono = models.CharField(max_length=20, blank=True, default='', verbose_name='Teléfono')
    ciudad = models.CharField(max_length=150, blank=True, default='', verbose_name='Ciudad')
    direccion = models.CharField(max_length=250, blank=True, default='', verbose_name='Dirección')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, blank=True, default='')
    modalidad = models.CharField(max_length=100, blank=True, default='', verbose_name='Categoría o modalidad')
    razon = models.TextField(blank=True, default='', verbose_name='Razón de ingreso')
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name='Fecha de ingreso')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    recibio_souvenir = models.BooleanField(default=False, verbose_name='Recibió souvenir')
    observacion = models.TextField(blank=True, default='', verbose_name='Observación')
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, related_name='socios_creados', null=True, blank=True)

    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['-fecha_ingreso', 'apellido', 'nombre']

    def __str__(self):
        if self.apellido_paterno or self.apellido_materno:
            return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()
        return f'{self.nombre} {self.apellido}'


class Membresia(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('castigado', 'Castigado'),
        ('baja', 'Dado de baja'),
    ]
    PAGO_CHOICES = [
        ('al_dia', 'Al día'),
        ('con_deuda', 'Con deuda'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='membresias')
    asociacion = models.ForeignKey('core.Asociacion', on_delete=models.PROTECT, related_name='membresias')
    conjunto = models.ForeignKey('core.Conjunto', on_delete=models.PROTECT, related_name='membresias')
    bloque = models.ForeignKey('bloques.Bloque', on_delete=models.PROTECT, related_name='membresias', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    estado_pago = models.CharField(max_length=20, choices=PAGO_CHOICES, default='al_dia')
    fecha_ingreso = models.DateField(auto_now_add=True)
    antiguedad = models.PositiveIntegerField(default=0, verbose_name='Antigüedad (años)')
    observacion = models.TextField(blank=True, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['socio', 'asociacion', 'conjunto'], name='unique_membresia_socio_conjunto'),
            models.UniqueConstraint(
                fields=['socio', 'asociacion'],
                condition=~Q(estado='baja'),
                name='unique_membresia_vigente_por_asociacion',
            ),
        ]
        ordering = ['-fecha_ingreso']

    @classmethod
    def inscribir(cls, socio, asociacion, conjunto, bloque=None, **kwargs):
        if conjunto.asociacion_id != asociacion.pk:
            raise ValueError('El conjunto debe pertenecer a la asociación indicada.')
        if bloque and bloque.conjunto_id != conjunto.pk:
            raise ValueError('El bloque debe pertenecer al conjunto indicado.')
        if cls.objects.filter(socio=socio, asociacion=asociacion).exclude(estado='baja').exists():
            raise ValueError('El socio debe estar dado de baja antes de cambiar de conjunto.')
        return cls.objects.create(socio=socio, asociacion=asociacion, conjunto=conjunto, bloque=bloque, **kwargs)

    def save(self, *args, **kwargs):
        if self.estado_pago == 'con_deuda':
            self.estado = 'suspendido'
        elif self.estado == 'suspendido' and self.estado_pago == 'al_dia':
            self.estado = 'activo'
        if self.conjunto.asociacion_id != self.asociacion_id:
            raise ValueError('El conjunto debe pertenecer a la asociación de la membresía.')
        if self.bloque_id and self.bloque.conjunto_id != self.conjunto_id:
            raise ValueError('El bloque debe pertenecer al conjunto de la membresía.')
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    foto = models.ImageField(upload_to='profiles/', null=True, blank=True)
    ROL_CHOICES = [
        ('superadministrador', 'Superadministrador'),
        ('administrador_asociacion', 'Administrador de Asociacion'),
        ('administrador_conjunto', 'Administrador de Conjunto'),
        ('miembro', 'Miembro'),
    ]
    rol = models.CharField(max_length=30, choices=ROL_CHOICES, default='miembro')
    asociacion = models.ForeignKey('core.Asociacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='administradores')
    conjunto = models.ForeignKey('core.Conjunto', on_delete=models.SET_NULL, null=True, blank=True, related_name='administradores')

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil {self.user.username}'


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        rol = 'superadministrador' if instance.is_superuser else ('administrador_asociacion' if instance.is_staff else 'miembro')
        UserProfile.objects.create(user=instance, rol=rol)


def generar_codigo_socio():
    """
    Genera el siguiente código de socio incremental.
    El formato es 260001, 260002, 260003, etc.
    """
    with transaction.atomic():
        # Obtener el último código asignado
        ultimo_socio = Socio.objects.filter(codigo_socio__isnull=False).order_by('-codigo_socio').first()
        
        if ultimo_socio and ultimo_socio.codigo_socio:
            # Extraer el número del código y sumar 1
            ultimo_numero = int(ultimo_socio.codigo_socio)
            nuevo_numero = ultimo_numero + 1
        else:
            # Si no hay códigos, empezar desde 260001
            nuevo_numero = 260001
        
        return str(nuevo_numero)
