from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, Http404

from .models import Evento
from apps.core.permissions import can_manage_events, get_role, scope_filter


@login_required
@user_passes_test(lambda u: get_role(u) in {'superadministrador', 'administrador_grupo', 'administrador_subgrupo'}, login_url='/login/')
def listar_eventos(request):
    q = request.GET.get('q', '').strip()
    activo = request.GET.get('activo', '').strip()
    eventos = scope_filter(Evento.objects.order_by('-fecha_evento'), request.user)

    if q:
        eventos = eventos.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(lugar__icontains=q)
        )

    if activo == 'si':
        eventos = eventos.filter(activo=True)
    elif activo == 'no':
        eventos = eventos.filter(activo=False)

    paginator = Paginator(eventos, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'eventos/eventos.html', {'page_obj': page_obj, 'q': q, 'activo': activo})


@login_required
@user_passes_test(can_manage_events, login_url='/login/')
def crear_evento(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        fecha_evento = request.POST.get('fecha_evento')
        lugar = request.POST.get('lugar', '').strip()
        activo = request.POST.get('activo') == 'on'

        if not nombre or not fecha_evento:
            messages.error(request, 'Nombre y fecha de evento son obligatorios.')
            return redirect('eventos:listar_eventos')

        grupo = None
        if get_role(request.user) == 'administrador_grupo':
            grupo = request.user.userprofile.grupo
        elif request.POST.get('grupo_id'):
            from apps.core.models import Grupo
            grupo = Grupo.objects.filter(pk=request.POST['grupo_id']).first()
        if not grupo:
            messages.error(request, 'Selecciona un grupo para el evento.')
            return redirect('eventos:listar_eventos')

        Evento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            fecha_evento=fecha_evento,
            lugar=lugar,
            activo=activo,
            grupo=grupo,
        )
        messages.success(request, 'Evento creado correctamente.')
        return redirect('eventos:listar_eventos')

    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(can_manage_events, login_url='/login/')
def editar_evento(request, pk):
    evento = get_object_or_404(scope_filter(Evento.objects.all(), request.user), pk=pk)
    if request.method == 'POST':
        evento.nombre = request.POST.get('nombre', evento.nombre).strip()
        evento.descripcion = request.POST.get('descripcion', evento.descripcion).strip()
        fecha_evento = request.POST.get('fecha_evento')
        evento.lugar = request.POST.get('lugar', evento.lugar).strip()
        evento.activo = request.POST.get('activo') == 'on'

        if fecha_evento:
            evento.fecha_evento = fecha_evento
        evento.save()
        messages.success(request, 'Evento actualizado correctamente.')
        return redirect('eventos:listar_eventos')

    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(can_manage_events, login_url='/login/')
def eliminar_evento(request, pk):
    evento = get_object_or_404(scope_filter(Evento.objects.all(), request.user), pk=pk)
    if request.method == 'POST':
        if evento.souvenirs.exists():
            messages.error(request, 'No se puede eliminar un evento que tiene souvenirs asignados. Puedes cambiar su estado a inactivo.')
            return redirect('eventos:listar_eventos')
        evento.delete()
        messages.success(request, 'Evento eliminado correctamente.')
    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(can_manage_events, login_url='/login/')
def cambiar_estado_evento(request, pk):
    evento = get_object_or_404(scope_filter(Evento.objects.all(), request.user), pk=pk)
    if request.method == 'POST':
        evento.estado = 'finalizado' if evento.estado == 'programado' else 'programado'
        evento.activo = evento.estado == 'programado'
        evento.save()
        messages.success(request, f'Evento {evento.get_estado_display().lower()}.')
    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(lambda u: get_role(u) in {'superadministrador', 'administrador_grupo', 'administrador_subgrupo'}, login_url='/login/')
def ver_evento(request, pk):
    return redirect('eventos:listar_eventos')


@login_required
def descargar_certificado(request, pk):
    from .models import Certificado

    certificado = get_object_or_404(Certificado, pk=pk)
    role = get_role(request.user)
    if role == 'miembro' and certificado.socio.user_id != request.user.id:
        raise Http404
    if role not in {'superadministrador', 'miembro'}:
        certificado = get_object_or_404(
            scope_filter(Certificado.objects.all(), request.user, 'evento__grupo', 'evento__subgrupo'),
            pk=pk,
        )
    return FileResponse(certificado.archivo.open('rb'), as_attachment=True, filename=f'certificado_{pk}.pdf')
