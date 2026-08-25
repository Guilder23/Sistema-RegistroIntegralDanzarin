from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.socios.models import Membresia
from apps.core.permissions import get_role, scope_filter


def can_manage_members(user):
    return get_role(user) in {'superadministrador', 'administrador_grupo', 'administrador_subgrupo'}


@login_required
@user_passes_test(can_manage_members, login_url='/login/')
def listar_membresias(request):
    membresias = Membresia.objects.select_related('socio', 'grupo', 'subgrupo')
    if get_role(request.user) != 'superadministrador':
        profile = request.user.userprofile
        membresias = membresias.filter(grupo_id=profile.grupo_id)
        if get_role(request.user) == 'administrador_subgrupo':
            membresias = membresias.filter(subgrupo_id=profile.subgrupo_id)
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
        if membresia.grupo_id != profile.grupo_id or (get_role(request.user) == 'administrador_subgrupo' and membresia.subgrupo_id != profile.subgrupo_id):
            return redirect('membresias:listar_membresias')
    if request.method == 'POST':
        membresia.estado = request.POST.get('estado', membresia.estado)
        membresia.estado_pago = request.POST.get('estado_pago', membresia.estado_pago)
        membresia.observacion = request.POST.get('observacion', membresia.observacion).strip()
        membresia.save()
        messages.success(request, 'Membresía actualizada correctamente.')
    return redirect('membresias:listar_membresias')
