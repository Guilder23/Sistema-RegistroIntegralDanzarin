from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from apps.danzarines.models import Membresia
from apps.core.models import Asociacion, Conjunto
from apps.core.permissions import get_role, scope_filter, registrar_auditoria, can_manage_member_states


def can_manage_members(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto'}


@login_required
@user_passes_test(can_manage_members, login_url='/login/')
def listar_membresias(request):
    role = get_role(request.user)
    membresias = Membresia.objects.select_related('danzarin', 'asociacion', 'conjunto')
    if role != 'superadministrador':
        profile = request.user.userprofile
        membresias = membresias.filter(asociacion_id=profile.asociacion_id)
        if role == 'administrador_conjunto':
            membresias = membresias.filter(conjunto_id=profile.conjunto_id)
    q = request.GET.get('q', '').strip()
    asociacion_id = request.GET.get('asociacion_id', '').strip()
    conjunto_id = request.GET.get('conjunto_id', '').strip()
    estado = request.GET.get('estado', '').strip()
    estado_pago = request.GET.get('estado_pago', '').strip()
    if q:
        membresias = membresias.filter(Q(danzarin__nombre__icontains=q) | Q(danzarin__apellido__icontains=q) | Q(danzarin__apellido_paterno__icontains=q) | Q(danzarin__apellido_materno__icontains=q) | Q(danzarin__carnet_ci__icontains=q))
    if asociacion_id:
        membresias = membresias.filter(asociacion_id=asociacion_id)
    if conjunto_id:
        membresias = membresias.filter(conjunto_id=conjunto_id)
    if estado:
        membresias = membresias.filter(estado=estado)
    if estado_pago:
        membresias = membresias.filter(estado_pago=estado_pago)
    asociaciones = Asociacion.objects.filter(activo=True)
    conjuntos = Conjunto.objects.filter(activo=True).select_related('asociacion')
    if role == 'administrador_asociacion':
        asociaciones = asociaciones.filter(pk=request.user.userprofile.asociacion_id)
        conjuntos = conjuntos.filter(asociacion_id=request.user.userprofile.asociacion_id)
    elif role == 'administrador_conjunto':
        asociaciones = asociaciones.filter(pk=request.user.userprofile.asociacion_id)
        conjuntos = conjuntos.filter(pk=request.user.userprofile.conjunto_id)
    return render(request, 'membresias/membresias.html', {
        'membresias': membresias,
        'q': q,
        'can_edit': can_manage_member_states(request.user),
        'asociaciones': asociaciones,
        'conjuntos': conjuntos,
        'asociacion_id': asociacion_id,
        'conjunto_id': conjunto_id,
        'estado': estado,
        'estado_pago': estado_pago,
    })


@login_required
@user_passes_test(can_manage_member_states, login_url='/login/')
def cambiar_membresia(request, pk):
    membresia = get_object_or_404(Membresia, pk=pk)
    if get_role(request.user) != 'superadministrador':
        profile = request.user.userprofile
        if membresia.asociacion_id != profile.asociacion_id or (get_role(request.user) == 'administrador_conjunto' and membresia.conjunto_id != profile.conjunto_id):
            return redirect('membresias:listar_membresias')
    if request.method == 'POST':
        estado_anterior = membresia.estado
        pago_anterior = membresia.estado_pago
        membresia.estado = request.POST.get('estado', membresia.estado)
        membresia.estado_pago = request.POST.get('estado_pago', membresia.estado_pago)
        membresia.observacion = request.POST.get('observacion', membresia.observacion).strip()
        membresia.save()
        registrar_auditoria(
            request.user,
            'modificacion_membresia',
            f'Membresía {membresia.pk} / Danzarin {membresia.danzarin_id}',
            {'estado': estado_anterior, 'estado_pago': pago_anterior},
            {'estado': membresia.estado, 'estado_pago': membresia.estado_pago},
        )
        messages.success(request, 'Membresía actualizada correctamente.')
    return redirect('membresias:listar_membresias')
