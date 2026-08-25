import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Grupo, Subgrupo, Auditoria
from apps.core.permissions import get_role, is_administrative
from apps.socios.models import Socio, Membresia
from apps.souvenirs.models import SouvenirEntrega
from apps.eventos.models import Evento


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def dashboard(request):
    role = get_role(request.user)
    profile = getattr(request.user, 'userprofile', None)

    # 1. Scoping inicial según el rol del usuario
    socios_qs = Socio.objects.all()
    membresias_qs = Membresia.objects.all()
    entregas_qs = SouvenirEntrega.objects.all()
    eventos_qs = Evento.objects.all()
    auditorias_qs = Auditoria.objects.all()

    grupos_filtro = Grupo.objects.none()
    subgrupos_filtro = Subgrupo.objects.none()

    grupo_seleccionado_id = request.GET.get('grupo_id', '').strip()
    subgrupo_seleccionado_id = request.GET.get('subgrupo_id', '').strip()

    if role == 'administrador_subgrupo':
        # Ámbito estricto: Solo su subgrupo asignado
        subgrupo_id = profile.subgrupo_id if profile else None
        grupo_id = profile.grupo_id if profile else None

        if subgrupo_id:
            socios_qs = socios_qs.filter(membresias__subgrupo_id=subgrupo_id).distinct()
            membresias_qs = membresias_qs.filter(subgrupo_id=subgrupo_id)
            entregas_qs = entregas_qs.filter(socio__membresias__subgrupo_id=subgrupo_id).distinct()
            eventos_qs = eventos_qs.filter(Q(grupo_id=grupo_id) | Q(grupo__isnull=True))
            auditorias_qs = auditorias_qs.filter(usuario_id=request.user.id)
            subgrupos_filtro = Subgrupo.objects.filter(pk=subgrupo_id)
            grupos_filtro = Grupo.objects.filter(pk=grupo_id) if grupo_id else Grupo.objects.none()
        else:
            socios_qs = socios_qs.none()
            membresias_qs = membresias_qs.none()
            entregas_qs = entregas_qs.none()
            auditorias_qs = auditorias_qs.none()

    elif role == 'administrador_grupo':
        # Ámbito estricto: Solo su grupo y los subgrupos de su grupo
        grupo_id = profile.grupo_id if profile else None

        if grupo_id:
            grupos_filtro = Grupo.objects.filter(pk=grupo_id)
            subgrupos_filtro = Subgrupo.objects.filter(grupo_id=grupo_id, activo=True)

            # Filtro opcional por subgrupo dentro de su grupo
            if subgrupo_seleccionado_id and subgrupos_filtro.filter(pk=subgrupo_seleccionado_id).exists():
                socios_qs = socios_qs.filter(membresias__subgrupo_id=subgrupo_seleccionado_id).distinct()
                membresias_qs = membresias_qs.filter(subgrupo_id=subgrupo_seleccionado_id)
                entregas_qs = entregas_qs.filter(socio__membresias__subgrupo_id=subgrupo_seleccionado_id).distinct()
            else:
                socios_qs = socios_qs.filter(membresias__grupo_id=grupo_id).distinct()
                membresias_qs = membresias_qs.filter(grupo_id=grupo_id)
                entregas_qs = entregas_qs.filter(socio__membresias__grupo_id=grupo_id).distinct()

            eventos_qs = eventos_qs.filter(grupo_id=grupo_id)
            auditorias_qs = auditorias_qs.filter(
                Q(usuario_id=request.user.id)
                | Q(usuario__userprofile__grupo_id=grupo_id)
                | Q(grupo_id=grupo_id)
            )
        else:
            socios_qs = socios_qs.none()
            membresias_qs = membresias_qs.none()
            entregas_qs = entregas_qs.none()
            auditorias_qs = auditorias_qs.none()

    else:
        # Superadministrador: Vista global con posibilidad de filtrar por grupo y subgrupo
        grupos_filtro = Grupo.objects.filter(activo=True).order_by('nombre')
        subgrupos_filtro = Subgrupo.objects.filter(activo=True).select_related('grupo').order_by('grupo__nombre', 'nombre')

        if grupo_seleccionado_id:
            socios_qs = socios_qs.filter(membresias__grupo_id=grupo_seleccionado_id).distinct()
            membresias_qs = membresias_qs.filter(grupo_id=grupo_seleccionado_id)
            entregas_qs = entregas_qs.filter(socio__membresias__grupo_id=grupo_seleccionado_id).distinct()
            eventos_qs = eventos_qs.filter(grupo_id=grupo_seleccionado_id)
            auditorias_qs = auditorias_qs.filter(
                Q(grupo_id=grupo_seleccionado_id) | Q(usuario__userprofile__grupo_id=grupo_seleccionado_id)
            )
            subgrupos_filtro = subgrupos_filtro.filter(grupo_id=grupo_seleccionado_id)

        if subgrupo_seleccionado_id:
            socios_qs = socios_qs.filter(membresias__subgrupo_id=subgrupo_seleccionado_id).distinct()
            membresias_qs = membresias_qs.filter(subgrupo_id=subgrupo_seleccionado_id)
            entregas_qs = entregas_qs.filter(socio__membresias__subgrupo_id=subgrupo_seleccionado_id).distinct()

    # 2. Métricas y KPIs Principales
    total_socios = socios_qs.count()
    activos = socios_qs.filter(membresias__estado='activo').distinct().count()
    suspendidos = socios_qs.filter(membresias__estado='suspendido').distinct().count()
    castigados = socios_qs.filter(membresias__estado='castigado').distinct().count()
    bajas = socios_qs.filter(membresias__estado='baja').distinct().count()
    inactivos = total_socios - activos if total_socios >= activos else 0

    souvenirs_entregados = entregas_qs.count()
    souvenirs_pendientes = max(0, total_socios - souvenirs_entregados)

    pagos_al_dia = socios_qs.filter(membresias__estado_pago='al_dia').distinct().count()
    pagos_con_deuda = socios_qs.filter(membresias__estado_pago='con_deuda').distinct().count()

    total_eventos = eventos_qs.count()
    total_auditorias = auditorias_qs.count()

    # Porcentaje de socios activos y pagos al día
    tasa_activos_pct = round((activos / total_socios * 100), 1) if total_socios > 0 else 0
    tasa_al_dia_pct = round((pagos_al_dia / total_socios * 100), 1) if total_socios > 0 else 0
    tasa_souvenirs_pct = round((souvenirs_entregados / total_socios * 100), 1) if total_socios > 0 else 0

    # 3. Distribución por Sexo / Género
    por_sexo = {
        'varones': socios_qs.filter(sexo='m').count(),
        'mujeres': socios_qs.filter(sexo='f').count(),
        'otros': socios_qs.exclude(sexo__in=['m', 'f']).count(),
    }

    # 4. Distribución por Rangos de Edad
    current_year = timezone.now().year
    por_edad = {
        'menores': socios_qs.filter(fecha_nacimiento__year__gt=current_year - 18).count(),
        'jovenes': socios_qs.filter(
            fecha_nacimiento__year__lte=current_year - 18,
            fecha_nacimiento__year__gt=current_year - 30
        ).count(),
        'adultos': socios_qs.filter(
            fecha_nacimiento__year__lte=current_year - 30,
            fecha_nacimiento__year__gt=current_year - 60
        ).count(),
        'mayores': socios_qs.filter(fecha_nacimiento__year__lte=current_year - 60).count(),
    }

    # 5. Distribución por Modalidades / Categorías
    modalidades_data = socios_qs.values('modalidad').annotate(
        total=Count('id', distinct=True)
    ).order_by('-total')[:8]
    modalidades_labels = [m['modalidad'] if m['modalidad'] else 'General' for m in modalidades_data]
    modalidades_counts = [m['total'] for m in modalidades_data]

    # 6. Distribución por Grupos y Subgrupos
    distribucion_grupos = socios_qs.filter(membresias__estado='activo').values(
        'membresias__grupo__nombre', 'membresias__subgrupo__nombre'
    ).annotate(total=Count('id', distinct=True)).order_by(
        'membresias__grupo__nombre', 'membresias__subgrupo__nombre'
    )
    distribucion_lista = list(distribucion_grupos)

    # 7. Tendencia de Registros de Socios (Últimos 6 meses)
    hoy = timezone.now().date()
    meses_labels = []
    meses_counts = []
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    for i in range(5, -1, -1):
        # Calcular fecha del mes correspondiente
        primer_dia_mes = (hoy.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(year=primer_dia_mes.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - timedelta(days=1)

        nombre_mes = f"{meses_nombres[primer_dia_mes.month - 1]} {primer_dia_mes.year}"
        meses_labels.append(nombre_mes)

        cant_mes = socios_qs.filter(
            fecha_ingreso__gte=primer_dia_mes,
            fecha_ingreso__lte=ultimo_dia_mes
        ).count()
        meses_counts.append(cant_mes)

    # 8. Estructura de Datos para Chart.js
    graficos = {
        # Pastel (Pie Chart): Estado de Pagos
        'pagos': {
            'labels': ['Al día', 'Con deuda'],
            'data': [pagos_al_dia, pagos_con_deuda],
        },
        # Pastel (Pie Chart): Entregas de Souvenirs
        'souvenirs': {
            'labels': ['Entregados', 'Pendientes'],
            'data': [souvenirs_entregados, souvenirs_pendientes],
        },
        # Rosquilla (Doughnut Chart): Género / Sexo
        'sexo': {
            'labels': ['Varones', 'Mujeres', 'Otros / No especificado'],
            'data': [por_sexo['varones'], por_sexo['mujeres'], por_sexo['otros']],
        },
        # Barras Verticales (Bar Chart): Estados de Membresía
        'estados': {
            'labels': ['Activos', 'Suspendidos', 'Castigados', 'Dados de baja'],
            'data': [activos, suspendidos, castigados, bajas],
        },
        # Barras Verticales (Bar Chart): Rangos de Edad
        'edades': {
            'labels': ['Menores (<18)', 'Jóvenes (18-29)', 'Adultos (30-59)', 'Mayores (60+)'],
            'data': [por_edad['menores'], por_edad['jovenes'], por_edad['adultos'], por_edad['mayores']],
        },
        # Barras Horizontales (Horizontal Bar Chart): Distribución por Grupo y Subgrupo
        'distribucion': {
            'labels': [
                f"{fila['membresias__grupo__nombre'] or 'General'} / {fila['membresias__subgrupo__nombre'] or 'General'}"
                for fila in distribucion_lista
            ] if distribucion_lista else ['Sin integrantes'],
            'data': [fila['total'] for fila in distribucion_lista] if distribucion_lista else [0],
        },
        # Área Polar (Polar Area Chart): Modalidades
        'modalidades': {
            'labels': modalidades_labels if modalidades_labels else ['General'],
            'data': modalidades_counts if modalidades_counts else [0],
        },
        # Línea con Relleno Gradiente (Line Chart): Tendencia de Inscripciones
        'tendencia': {
            'labels': meses_labels,
            'data': meses_counts,
        },
        # Radar Chart: Indicadores Clave de Salud Operativa
        'radar': {
            'labels': ['Actividad (%)', 'Al día (%)', 'Souvenirs (%)', 'Jóvenes/Adultos (%)', 'Membresías Activas (%)'],
            'data': [
                tasa_activos_pct,
                tasa_al_dia_pct,
                tasa_souvenirs_pct,
                round(((por_edad['jovenes'] + por_edad['adultos']) / total_socios * 100), 1) if total_socios > 0 else 0,
                round((activos / (total_socios or 1)) * 100, 1),
            ],
        },
    }

    # Actividades recientes para el feed del dashboard
    actividades_recientes = auditorias_qs.order_by('-fecha_hora')[:6]

    return render(request, 'dashboard/dashboard.html', {
        'role': role,
        'user_profile': profile,
        'grupos_filtro': grupos_filtro,
        'subgrupos_filtro': subgrupos_filtro,
        'grupo_id': grupo_seleccionado_id,
        'subgrupo_id': subgrupo_seleccionado_id,
        'total_socios': total_socios,
        'socios_activos': activos,
        'socios_inactivos': inactivos,
        'suspendidos': suspendidos,
        'castigados': castigados,
        'bajas': bajas,
        'souvenirs_entregados': souvenirs_entregados,
        'souvenirs_pendientes': souvenirs_pendientes,
        'pagos_al_dia': pagos_al_dia,
        'pagos_con_deuda': pagos_con_deuda,
        'total_eventos': total_eventos,
        'total_auditorias': total_auditorias,
        'tasa_activos_pct': tasa_activos_pct,
        'tasa_al_dia_pct': tasa_al_dia_pct,
        'tasa_souvenirs_pct': tasa_souvenirs_pct,
        'por_sexo': por_sexo,
        'por_edad': por_edad,
        'distribucion': distribucion_lista,
        'actividades_recientes': actividades_recientes,
        'graficos': graficos,
    })
