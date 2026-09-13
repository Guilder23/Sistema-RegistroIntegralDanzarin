from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.core.models import Asociacion, Conjunto
from apps.core.permissions import get_role, registrar_auditoria


def can_manage_conjuntos(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion'}


def scoped_conjuntos(user):
    if get_role(user) == 'superadministrador':
        return Conjunto.objects.select_related('asociacion').all()
    return Conjunto.objects.filter(asociacion_id=user.userprofile.asociacion_id).select_related('asociacion')


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def listar_conjuntos(request):
    q = request.GET.get('q', '').strip()
    asociacion_id = request.GET.get('asociacion_id', '').strip()
    activo = request.GET.get('activo', '').strip()
    conjuntos = scoped_conjuntos(request.user)
    if q:
        conjuntos = conjuntos.filter(nombre__icontains=q)
    if asociacion_id and get_role(request.user) == 'superadministrador':
        conjuntos = conjuntos.filter(asociacion_id=asociacion_id)
    if activo == 'si':
        conjuntos = conjuntos.filter(activo=True)
    elif activo == 'no':
        conjuntos = conjuntos.filter(activo=False)
    asociaciones = Asociacion.objects.all() if get_role(request.user) == 'superadministrador' else Asociacion.objects.filter(pk=request.user.userprofile.asociacion_id)
    return render(request, 'conjuntos/conjuntos.html', {
        'conjuntos': conjuntos,
        'asociaciones': asociaciones,
        'q': q,
        'asociacion_id': asociacion_id,
        'activo': activo,
    })


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def crear_conjunto(request):
    if request.method == 'POST':
        asociacion_id = request.POST.get('asociacion_id')
        if get_role(request.user) != 'superadministrador':
            asociacion_id = request.user.userprofile.asociacion_id
        asociacion = Asociacion.objects.filter(pk=asociacion_id, activo=True).first()
        nombre = request.POST.get('nombre', '').strip()
        if asociacion and nombre:
            conjunto, created = Conjunto.objects.get_or_create(asociacion=asociacion, nombre=nombre, defaults={'activo': True})
            if created:
                registrar_auditoria(
                    request.user,
                    'creacion_conjunto',
                    f'Conjunto {conjunto.nombre} ({asociacion.nombre})',
                    nuevo={'nombre': conjunto.nombre, 'asociacion': asociacion.nombre},
                    asociacion=asociacion,
                    conjunto=conjunto,
                )
                messages.success(request, 'Conjunto creado correctamente.')
            else:
                messages.info(request, 'El conjunto ya existe.')
        else:
            messages.error(request, 'Asociacion y nombre son obligatorios.')
    return redirect('conjuntos:listar_conjuntos')


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def editar_conjunto(request, pk):
    conjunto = get_object_or_404(scoped_conjuntos(request.user), pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': conjunto.nombre, 'activo': conjunto.activo}
        conjunto.nombre = request.POST.get('nombre', conjunto.nombre).strip()
        conjunto.activo = request.POST.get('activo') == 'on'
        conjunto.save()
        registrar_auditoria(
            request.user,
            'modificacion_conjunto',
            f'Conjunto {conjunto.nombre}',
            anterior=anterior,
            nuevo={'nombre': conjunto.nombre, 'activo': conjunto.activo},
            asociacion=conjunto.asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Conjunto actualizado correctamente.')
    return redirect('conjuntos:listar_conjuntos')


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def activar_conjunto(request, pk):
    conjunto = get_object_or_404(scoped_conjuntos(request.user), pk=pk)
    if request.method == 'POST':
        conjunto.activo = True
        conjunto.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'activacion_conjunto',
            f'Conjunto {conjunto.nombre}',
            nuevo={'activo': True},
            asociacion=conjunto.asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Conjunto activado correctamente.')
    return redirect('conjuntos:listar_conjuntos')


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def desactivar_conjunto(request, pk):
    conjunto = get_object_or_404(scoped_conjuntos(request.user), pk=pk)
    if request.method == 'POST':
        conjunto.activo = False
        conjunto.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'desactivacion_conjunto',
            f'Conjunto {conjunto.nombre}',
            nuevo={'activo': False},
            asociacion=conjunto.asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Conjunto desactivado correctamente.')
    return redirect('conjuntos:listar_conjuntos')


@login_required
@user_passes_test(can_manage_conjuntos, login_url='/login/')
def eliminar_conjunto(request, pk):
    conjunto = get_object_or_404(scoped_conjuntos(request.user), pk=pk)
    if request.method == 'POST':
        if conjunto.bloques.exists():
            messages.error(request, 'No puedes eliminar el conjunto porque tiene bloques asignados.')
            return redirect('conjuntos:listar_conjuntos')
        nombre = conjunto.nombre
        asociacion = conjunto.asociacion
        conjunto.delete()
        registrar_auditoria(request.user, 'eliminacion_conjunto', f'Conjunto {nombre}', asociacion=asociacion)
        messages.success(request, 'Conjunto eliminado correctamente.')
    return redirect('conjuntos:listar_conjuntos')

