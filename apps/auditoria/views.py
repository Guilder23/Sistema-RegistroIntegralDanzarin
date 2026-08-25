from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Auditoria, Grupo, Subgrupo
from apps.core.permissions import get_role, is_administrative


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def listar_auditoria(request):
    role = get_role(request.user)
    profile = getattr(request.user, 'userprofile', None)

    registros = Auditoria.objects.select_related(
        'usuario',
        'usuario__userprofile',
        'usuario__userprofile__grupo',
        'usuario__userprofile__subgrupo',
        'grupo',
        'subgrupo',
    ).all()

    grupos = Grupo.objects.none()
    subgrupos = Subgrupo.objects.none()
    usuarios_disponibles = User.objects.none()

    # 1. Aplicar ámbito base según el rol del administrador
    if role == 'administrador_subgrupo':
        # El de subgrupos solo debe ver de él
        registros = registros.filter(usuario_id=request.user.id)
        subgrupos = Subgrupo.objects.filter(pk=profile.subgrupo_id) if (profile and profile.subgrupo_id) else Subgrupo.objects.none()
        grupos = Grupo.objects.filter(pk=profile.grupo_id) if (profile and profile.grupo_id) else Grupo.objects.none()

    elif role == 'administrador_grupo':
        # El admin de grupos debe ver de él sus cambios y de sus subgrupos
        grupo_id = profile.grupo_id if profile else None
        if grupo_id:
            registros = registros.filter(
                Q(usuario_id=request.user.id)
                | Q(usuario__userprofile__grupo_id=grupo_id)
                | Q(grupo_id=grupo_id)
            )
            grupos = Grupo.objects.filter(pk=grupo_id)
            subgrupos = Subgrupo.objects.filter(grupo_id=grupo_id, activo=True)
            usuarios_disponibles = User.objects.filter(
                Q(id=request.user.id)
                | Q(userprofile__grupo_id=grupo_id)
            ).distinct().order_by('first_name', 'username')
        else:
            registros = registros.filter(usuario_id=request.user.id)

    else:
        # Superadministrador: Ve historial de él, de grupos y de subgrupos
        grupos = Grupo.objects.filter(activo=True).order_by('nombre')
        subgrupos = Subgrupo.objects.filter(activo=True).select_related('grupo').order_by('grupo__nombre', 'nombre')
        usuarios_disponibles = User.objects.filter(is_staff=True).order_by('username')

    registros_base = registros

    # 2. Filtro por origen / nivel de administrador
    origen = request.GET.get('origen', 'todos').strip()
    if origen == 'mis_cambios':
        registros = registros.filter(usuario_id=request.user.id)
    elif origen == 'subgrupos':
        # Cambios generados por subgrupos o administradores de subgrupo
        if role == 'administrador_grupo' and profile and profile.grupo_id:
            registros = registros.filter(
                (Q(usuario__userprofile__rol='administrador_subgrupo') | Q(subgrupo__isnull=False))
                & ~Q(usuario_id=request.user.id)
            )
        else:
            registros = registros.filter(
                Q(usuario__userprofile__rol='administrador_subgrupo') | Q(subgrupo__isnull=False)
            )
    elif origen == 'admin_grupo':
        registros = registros.filter(usuario__userprofile__rol='administrador_grupo')
    elif origen == 'superadmin':
        registros = registros.filter(
            Q(usuario__is_superuser=True) | Q(usuario__userprofile__rol='superadministrador')
        )

    # 3. Filtro por grupo específico (para Superadministrador)
    grupo_id = request.GET.get('grupo_id', '').strip()
    if grupo_id and role == 'superadministrador':
        registros = registros.filter(
            Q(grupo_id=grupo_id) | Q(usuario__userprofile__grupo_id=grupo_id)
        )
        subgrupos = subgrupos.filter(grupo_id=grupo_id)

    # 4. Filtro por subgrupo específico (para Superadmin y Admin de Grupo)
    subgrupo_id = request.GET.get('subgrupo_id', '').strip()
    if subgrupo_id and role in {'superadministrador', 'administrador_grupo'}:
        registros = registros.filter(
            Q(subgrupo_id=subgrupo_id) | Q(usuario__userprofile__subgrupo_id=subgrupo_id)
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
            | Q(grupo__nombre__icontains=q)
            | Q(subgrupo__nombre__icontains=q)
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
    paginator = Paginator(registros, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'auditoria/auditoria.html', {
        'page_obj': page_obj,
        'registros': page_obj.object_list,
        'role': role,
        'user_profile': profile,
        'grupos': grupos,
        'subgrupos': subgrupos,
        'usuarios_disponibles': usuarios_disponibles,
        'acciones_disponibles': acciones_disponibles,
        'total_registros': total_registros,
        'registros_hoy': registros_hoy,
        'q': q,
        'origen': origen,
        'accion': accion,
        'grupo_id': grupo_id,
        'subgrupo_id': subgrupo_id,
        'usuario_id': usuario_id,
        'desde': fecha_desde,
        'hasta': fecha_hasta,
    })

