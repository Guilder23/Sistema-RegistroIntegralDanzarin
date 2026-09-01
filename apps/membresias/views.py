from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.socios.models import Membresia
from apps.core.permissions import get_role, scope_filter, registrar_auditoria


def can_manage_members(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto'}


@login_required
@user_passes_test(can_manage_members, login_url='/login/')
def listar_membresias(request):
    membresias = Membresia.objects.select_related('socio', 'asociacion', 'conjunto')
    if get_role(request.user) != 'superadministrador':
        profile = request.user.userprofile
        membresias = membresias.filter(asociacion_id=profile.asociacion_id)
        if get_role(request.user) == 'administrador_conjunto':
            membresias = membresias.filter(conjunto_id=profile.conjunto_id)
    q = request.GET.get('q', '').strip()
    if q:
        membresias = membresias.filter(socio__nombre__icontains=q) | membresias.filter(socio__apellido__icontains=q)
    return render(request, 'membresias/membresias.html', {'membresias': membresias, 'q': q})


@login_required
@user_passes_test(can_manage_members, login_url='/login/')
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
            f'Membresía {membresia.pk} / Socio {membresia.socio_id}',
            {'estado': estado_anterior, 'estado_pago': pago_anterior},
            {'estado': membresia.estado, 'estado_pago': membresia.estado_pago},
        )
        messages.success(request, 'Membresía actualizada correctamente.')
    return redirect('membresias:listar_membresias')
