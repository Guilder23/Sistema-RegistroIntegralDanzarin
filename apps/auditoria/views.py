from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Auditoria, Asociacion, Conjunto
from apps.core.permissions import get_role, is_administrative


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def listar_auditoria(request):
    role = get_role(request.user)
    profile = getattr(request.user, 'userprofile', None)

    registros = Auditoria.objects.select_related(
        'usuario',
        'usuario__userprofile',
        'usuario__userprofile__asociacion',
        'usuario__userprofile__conjunto',
        'asociacion',
        'conjunto',
    ).all()

    asociaciones = Asociacion.objects.none()
    conjuntos = Conjunto.objects.none()
    usuarios_disponibles = User.objects.none()

    # 1. Aplicar ámbito base según el rol del administrador
    if role == 'administrador_conjunto':
        # El de conjuntos solo debe ver de él
        registros = registros.filter(usuario_id=request.user.id)
        conjuntos = Conjunto.objects.filter(pk=profile.conjunto_id) if (profile and profile.conjunto_id) else Conjunto.objects.none()
        asociaciones = Asociacion.objects.filter(pk=profile.asociacion_id) if (profile and profile.asociacion_id) else Asociacion.objects.none()

    elif role == 'administrador_asociacion':
        # El admin de asociaciones debe ver de él sus cambios y de sus conjuntos
        asociacion_id = profile.asociacion_id if profile else None
        if asociacion_id:
            registros = registros.filter(
                ~Q(usuario__is_superuser=True),
                ~Q(usuario__userprofile__rol='superadministrador'),
            ).filter(
                Q(usuario_id=request.user.id)
                | Q(usuario__userprofile__asociacion_id=asociacion_id)
                | Q(asociacion_id=asociacion_id)
                | Q(conjunto__asociacion_id=asociacion_id)
            )
            asociaciones = Asociacion.objects.filter(pk=asociacion_id)
            conjuntos = Conjunto.objects.filter(asociacion_id=asociacion_id, activo=True)
            usuarios_disponibles = User.objects.filter(
                Q(id=request.user.id)
                | Q(userprofile__asociacion_id=asociacion_id)
            ).distinct().order_by('first_name', 'username')
        else:
            registros = registros.filter(usuario_id=request.user.id)

    else:
        # Superadministrador: Ve historial de él, de asociaciones y de conjuntos
        asociaciones = Asociacion.objects.filter(activo=True).order_by('nombre')
        conjuntos = Conjunto.objects.filter(activo=True).select_related('asociacion').order_by('asociacion__nombre', 'nombre')
        usuarios_disponibles = User.objects.filter(is_staff=True).order_by('username')

    registros_base = registros

    # 2. Filtro por origen / nivel de administrador
    origen = request.GET.get('origen', 'todos').strip()
    if origen == 'mis_cambios':
        registros = registros.filter(usuario_id=request.user.id)
    elif origen == 'conjuntos':
        # Cambios generados por conjuntos o administradores de conjunto
        if role == 'administrador_asociacion' and profile and profile.asociacion_id:
            registros = registros.filter(
                (Q(usuario__userprofile__rol='administrador_conjunto') | Q(conjunto__isnull=False))
                & ~Q(usuario_id=request.user.id)
            )
        else:
            registros = registros.filter(
                Q(usuario__userprofile__rol='administrador_conjunto') | Q(conjunto__isnull=False)
            )
    elif origen == 'admin_asociacion':
        registros = registros.filter(usuario__userprofile__rol='administrador_asociacion')
    elif origen == 'superadmin':
        registros = registros.filter(
            Q(usuario__is_superuser=True) | Q(usuario__userprofile__rol='superadministrador')
        )

    # 3. Filtro por asociación específica (para Superadministrador)
    asociacion_id = request.GET.get('asociacion_id', '').strip()
    if asociacion_id and role == 'superadministrador':
        registros = registros.filter(
            Q(asociacion_id=asociacion_id) | Q(usuario__userprofile__asociacion_id=asociacion_id)
        )
        conjuntos = conjuntos.filter(asociacion_id=asociacion_id)

    # 4. Filtro por conjunto específico (para Superadmin y Admin de Asociación)
    conjunto_id = request.GET.get('conjunto_id', '').strip()
    if conjunto_id and role in {'superadministrador', 'administrador_asociacion'}:
        registros = registros.filter(
            Q(conjunto_id=conjunto_id) | Q(usuario__userprofile__conjunto_id=conjunto_id)
        )

    # 5. Filtro por usuario específico
    usuario_id = request.GET.get('usuario_id', '').strip()
    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)

    # 6. Filtro por texto de búsqueda
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(accion__icontains=q)
            | Q(registro_afectado__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(usuario__first_name__icontains=q)
            | Q(usuario__last_name__icontains=q)
            | Q(asociacion__nombre__icontains=q)
            | Q(conjunto__nombre__icontains=q)
        )

    # 7. Filtro por tipo de acción
    accion = request.GET.get('accion', '').strip()
    if accion:
        registros = registros.filter(accion=accion)

    # 8. Filtro por rango de fechas
    fecha_desde = request.GET.get('desde', '').strip()
    fecha_hasta = request.GET.get('hasta', '').strip()
    if fecha_desde:
        registros = registros.filter(fecha_hora__date__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha_hora__date__lte=fecha_hasta)

    # Lista de acciones distintas para el dropdown de acciones (acotado al ámbito del usuario)
    acciones_disponibles = registros_base.values_list('accion', flat=True).distinct().order_by('accion')


    # Métricas para el panel superior
    total_registros = registros.count()
    hoy = timezone.now().date()
    registros_hoy = registros.filter(fecha_hora__date=hoy).count()

    # Paginación
    registros = registros.order_by('-fecha_hora', '-pk')
    paginator = Paginator(registros, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'auditoria/auditoria.html', {
        'page_obj': page_obj,
        'registros': page_obj.object_list,
        'role': role,
        'user_profile': profile,
        'asociaciones': asociaciones,
        'conjuntos': conjuntos,
        'usuarios_disponibles': usuarios_disponibles,
        'acciones_disponibles': acciones_disponibles,
        'total_registros': total_registros,
        'registros_hoy': registros_hoy,
        'q': q,
        'origen': origen,
        'accion': accion,
        'asociacion_id': asociacion_id,
        'conjunto_id': conjunto_id,
        'usuario_id': usuario_id,
        'desde': fecha_desde,
        'hasta': fecha_hasta,
    })

