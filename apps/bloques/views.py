from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.models import Asociacion, Conjunto
from apps.core.permissions import get_role, registrar_auditoria
from .models import Bloque


def can_manage_bloques(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion'}


def scoped_bloques(user):
    if get_role(user) == 'superadministrador':
        return Bloque.objects.select_related('conjunto__asociacion').all()
    return Bloque.objects.filter(conjunto__asociacion_id=user.userprofile.asociacion_id).select_related('conjunto__asociacion')


@login_required
@user_passes_test(can_manage_bloques, login_url='/login/')
def listar_bloques(request):
    q = request.GET.get('q', '').strip()
    bloques = scoped_bloques(request.user)
    if q:
        bloques = bloques.filter(nombre__icontains=q)

    asociaciones = (
        Asociacion.objects.filter(activo=True)
        if get_role(request.user) == 'superadministrador'
        else Asociacion.objects.filter(pk=request.user.userprofile.asociacion_id)
    )
    conjuntos = Conjunto.objects.filter(activo=True).select_related('asociacion')
    if get_role(request.user) != 'superadministrador':
        conjuntos = conjuntos.filter(asociacion_id=request.user.userprofile.asociacion_id)

    return render(request, 'bloques/bloques.html', {
        'bloques': bloques,
        'asociaciones': asociaciones,
        'conjuntos': conjuntos,
        'q': q,
    })


@login_required
@user_passes_test(can_manage_bloques, login_url='/login/')
def crear_bloque(request):
    if request.method == 'POST':
        asociacion_id = request.POST.get('asociacion_id')
        conjunto_id = request.POST.get('conjunto_id')
        if get_role(request.user) != 'superadministrador':
            asociacion_id = request.user.userprofile.asociacion_id

        asociacion = Asociacion.objects.filter(pk=asociacion_id, activo=True).first()
        conjunto = None
        if asociacion:
            conjunto = Conjunto.objects.filter(pk=conjunto_id, asociacion=asociacion, activo=True).first()

        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if asociacion and conjunto and nombre:
            bloque, created = Bloque.objects.get_or_create(
                conjunto=conjunto,
                nombre=nombre,
                defaults={'descripcion': descripcion, 'activo': True},
            )
            if created:
                registrar_auditoria(
                    request.user,
                    'creacion_bloque',
                    f'Bloque {bloque.nombre} ({conjunto.nombre})',
                    nuevo={'nombre': bloque.nombre, 'descripcion': bloque.descripcion, 'conjunto': conjunto.nombre},
                    asociacion=asociacion,
                    conjunto=conjunto,
                )
                messages.success(request, 'Bloque creado correctamente.')
            else:
                messages.info(request, 'El bloque ya existe en este conjunto.')
        else:
            messages.error(request, 'Debes seleccionar una asociación y conjunto válidos y completar el nombre.')
    return redirect('bloques:listar_bloques')


@login_required
@user_passes_test(can_manage_bloques, login_url='/login/')
def editar_bloque(request, pk):
    bloque = get_object_or_404(scoped_bloques(request.user), pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': bloque.nombre, 'descripcion': bloque.descripcion, 'activo': bloque.activo, 'conjunto': bloque.conjunto_id}
        bloque.nombre = request.POST.get('nombre', bloque.nombre).strip()
        bloque.descripcion = request.POST.get('descripcion', bloque.descripcion).strip()
        bloque.activo = request.POST.get('activo') == 'on'

        conjunto_id = request.POST.get('conjunto_id')
        if conjunto_id:
            conjunto = Conjunto.objects.filter(pk=conjunto_id, asociacion=bloque.conjunto.asociacion, activo=True).first()
            if conjunto:
                bloque.conjunto = conjunto

        bloque.save()
        registrar_auditoria(
            request.user,
            'modificacion_bloque',
            f'Bloque {bloque.nombre}',
            anterior=anterior,
            nuevo={'nombre': bloque.nombre, 'descripcion': bloque.descripcion, 'activo': bloque.activo, 'conjunto': bloque.conjunto_id},
            asociacion=bloque.conjunto.asociacion,
            conjunto=bloque.conjunto,
        )
        messages.success(request, 'Bloque actualizado correctamente.')
    return redirect('bloques:listar_bloques')


@login_required
@user_passes_test(can_manage_bloques, login_url='/login/')
def eliminar_bloque(request, pk):
    bloque = get_object_or_404(scoped_bloques(request.user), pk=pk)
    if request.method == 'POST':
        bloque.activo = False
        bloque.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'desactivacion_bloque',
            f'Bloque {bloque.nombre}',
            nuevo={'activo': False},
            asociacion=bloque.conjunto.asociacion,
            conjunto=bloque.conjunto,
        )
        messages.success(request, 'Bloque desactivado correctamente.')
    return redirect('bloques:listar_bloques')
