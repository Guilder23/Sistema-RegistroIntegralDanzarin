from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.core.models import Asociacion
from apps.core.permissions import get_role, registrar_auditoria


def is_superadmin(user):
    return get_role(user) == 'superadministrador'


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def listar_asociaciones(request):
    q = request.GET.get('q', '').strip()
    asociaciones = Asociacion.objects.all()
    if q:
        asociaciones = asociaciones.filter(nombre__icontains=q)
    return render(request, 'asociaciones/asociaciones.html', {'asociaciones': asociaciones, 'q': q})


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def crear_asociacion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        if nombre and not Asociacion.objects.filter(nombre__iexact=nombre).exists():
            asociacion = Asociacion.objects.create(nombre=nombre, activo=activo)
            registrar_auditoria(
                request.user,
                'creacion_asociacion',
                f'Asociacion {asociacion.nombre}',
                nuevo={'nombre': asociacion.nombre, 'activo': asociacion.activo},
                asociacion=asociacion,
            )
            messages.success(request, 'Asociacion creada correctamente.')
        else:
            messages.error(request, 'El nombre es obligatorio y debe ser único.')
    return redirect('asociaciones:listar_asociaciones')


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def editar_asociacion(request, pk):
    asociacion = get_object_or_404(Asociacion, pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': asociacion.nombre, 'activo': asociacion.activo}
        asociacion.nombre = request.POST.get('nombre', asociacion.nombre).strip()
        asociacion.activo = request.POST.get('activo') == 'on'
        asociacion.save()
        registrar_auditoria(
            request.user,
            'modificacion_asociacion',
            f'Asociacion {asociacion.nombre}',
            anterior=anterior,
            nuevo={'nombre': asociacion.nombre, 'activo': asociacion.activo},
            asociacion=asociacion,
        )
        messages.success(request, 'Asociacion actualizada correctamente.')
    return redirect('asociaciones:listar_asociaciones')


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def eliminar_asociacion(request, pk):
    asociacion = get_object_or_404(Asociacion, pk=pk)
    if request.method == 'POST':
        asociacion.activo = False
        asociacion.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'desactivacion_asociacion',
            f'Asociacion {asociacion.nombre}',
            nuevo={'activo': False},
            asociacion=asociacion,
        )
        messages.success(request, 'Asociacion desactivada correctamente.')
    return redirect('asociaciones:listar_asociaciones')

