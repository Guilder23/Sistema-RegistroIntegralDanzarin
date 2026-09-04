from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, Http404

from .models import Evento
from apps.core.models import Asociacion, Conjunto
from apps.core.permissions import can_manage_events, get_role, scope_filter, registrar_auditoria


def opciones_ambito_evento(user):
    if get_role(user) == 'superadministrador':
        return (
            Asociacion.objects.filter(activo=True),
            Conjunto.objects.filter(activo=True).select_related('asociacion'),
        )

    asociacion_id = getattr(getattr(user, 'userprofile', None), 'asociacion_id', None)
    return (
        Asociacion.objects.filter(pk=asociacion_id, activo=True),
        Conjunto.objects.filter(asociacion_id=asociacion_id, activo=True).select_related('asociacion'),
    )


def obtener_ambito_evento(request):
    """Obtiene un ámbito válido y garantiza que conjunto pertenece a asociación."""
    asociacion_id = request.POST.get('asociacion_id')
    conjunto_id = request.POST.get('conjunto_id')
    asociacion, conjunto = None, None

    if get_role(request.user) == 'administrador_asociacion':
        asociacion = getattr(request.user.userprofile, 'asociacion', None)
    elif asociacion_id:
        asociacion = Asociacion.objects.filter(pk=asociacion_id, activo=True).first()

    if not asociacion:
        return None, None

    if request.POST.get('tipo_ambito') == 'conjunto':
        conjunto = Conjunto.objects.filter(
            pk=conjunto_id,
            asociacion=asociacion,
            activo=True,
        ).first()
        if not conjunto:
            return None, None

    return asociacion, conjunto


@login_required
@user_passes_test(lambda u: get_role(u) in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto'}, login_url='/login/')
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
    asociaciones, conjuntos = opciones_ambito_evento(request.user)
    return render(request, 'eventos/eventos.html', {
        'page_obj': page_obj,
        'q': q,
        'activo': activo,
        'asociaciones': asociaciones,
        'conjuntos': conjuntos,
    })


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

        asociacion, conjunto = obtener_ambito_evento(request)
        if not asociacion:
            messages.error(request, 'Selecciona una asociación y un conjunto válidos para el evento.')
            return redirect('eventos:listar_eventos')

        evento = Evento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            fecha_evento=fecha_evento,
            lugar=lugar,
            activo=activo,
            asociacion=asociacion,
            conjunto=conjunto,
            creado_por=request.user,
        )
        registrar_auditoria(
            request.user,
            'creacion_evento',
            f'Evento {evento.nombre}',
            nuevo={'nombre': evento.nombre, 'fecha': str(evento.fecha_evento), 'lugar': evento.lugar},
            asociacion=asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Evento creado correctamente.')
        return redirect('eventos:listar_eventos')

    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(can_manage_events, login_url='/login/')
def editar_evento(request, pk):
    evento = get_object_or_404(scope_filter(Evento.objects.all(), request.user), pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': evento.nombre, 'fecha': str(evento.fecha_evento), 'lugar': evento.lugar}
        evento.nombre = request.POST.get('nombre', evento.nombre).strip()
        evento.descripcion = request.POST.get('descripcion', evento.descripcion).strip()
        fecha_evento = request.POST.get('fecha_evento')
        evento.lugar = request.POST.get('lugar', evento.lugar).strip()
        evento.activo = request.POST.get('activo') == 'on'

        asociacion, conjunto = obtener_ambito_evento(request)
        if not asociacion:
            messages.error(request, 'Selecciona una asociación y un conjunto válidos para el evento.')
            return redirect('eventos:listar_eventos')
        evento.asociacion = asociacion
        evento.conjunto = conjunto

        if fecha_evento:
            evento.fecha_evento = fecha_evento
        evento.save()
        registrar_auditoria(
            request.user,
            'modificacion_evento',
            f'Evento {evento.nombre}',
            anterior=anterior,
            nuevo={'nombre': evento.nombre, 'fecha': str(evento.fecha_evento), 'lugar': evento.lugar},
            asociacion=evento.asociacion,
            conjunto=evento.conjunto,
        )
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
        nombre = evento.nombre
        asociacion = evento.asociacion
        evento.delete()
        registrar_auditoria(
            request.user,
            'eliminacion_evento',
            f'Evento {nombre}',
            asociacion=asociacion,
        )
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
        registrar_auditoria(
            request.user,
            'cambio_estado_evento',
            f'Evento {evento.nombre} ({evento.estado})',
            nuevo={'estado': evento.estado, 'activo': evento.activo},
            asociacion=evento.asociacion,
        )
        messages.success(request, f'Evento {evento.get_estado_display().lower()}.')

    return redirect('eventos:listar_eventos')


@login_required
@user_passes_test(lambda u: get_role(u) in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto'}, login_url='/login/')
def ver_evento(request, pk):
    return redirect('eventos:listar_eventos')


@login_required
def descargar_certificado(request, pk):
    from .models import Certificado

    certificado = get_object_or_404(Certificado, pk=pk)
    role = get_role(request.user)
    if role == 'miembro' and certificado.danzarin.user_id != request.user.id:
        raise Http404
    if role not in {'superadministrador', 'miembro'}:
        certificado = get_object_or_404(
            scope_filter(Certificado.objects.all(), request.user, 'evento__asociacion', 'evento__conjunto'),
            pk=pk,
        )
    return FileResponse(certificado.archivo.open('rb'), as_attachment=True, filename=f'certificado_{pk}.pdf')
