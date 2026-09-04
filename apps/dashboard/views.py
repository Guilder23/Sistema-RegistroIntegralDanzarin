import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Asociacion, Conjunto, Auditoria
from apps.core.permissions import get_role, is_administrative
from apps.danzarines.models import Danzarin, Membresia
from apps.souvenirs.models import SouvenirEntrega
from apps.eventos.models import Evento


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def dashboard(request):
    role = get_role(request.user)
    profile = getattr(request.user, 'userprofile', None)

    # 1. Scoping inicial según el rol del usuario
    danzarines_qs = Danzarin.objects.all()
    membresias_qs = Membresia.objects.all()
    entregas_qs = SouvenirEntrega.objects.all()
    eventos_qs = Evento.objects.all()
    auditorias_qs = Auditoria.objects.all()

    asociaciones_filtro = Asociacion.objects.none()
    conjuntos_filtro = Conjunto.objects.none()

    asociacion_seleccionada_id = request.GET.get('asociacion_id', '').strip()
    conjunto_seleccionado_id = request.GET.get('conjunto_id', '').strip()

    if role == 'administrador_conjunto':
        # Ámbito estricto: Solo su conjunto asignado
        conjunto_id = profile.conjunto_id if profile else None
        asociacion_id = profile.asociacion_id if profile else None

        if conjunto_id:
            danzarines_qs = danzarines_qs.filter(membresias__conjunto_id=conjunto_id).distinct()
            membresias_qs = membresias_qs.filter(conjunto_id=conjunto_id)
            entregas_qs = entregas_qs.filter(danzarin__membresias__conjunto_id=conjunto_id).distinct()
            eventos_qs = eventos_qs.filter(Q(asociacion_id=asociacion_id) | Q(asociacion__isnull=True))
            auditorias_qs = auditorias_qs.filter(usuario_id=request.user.id)
            conjuntos_filtro = Conjunto.objects.filter(pk=conjunto_id)
            asociaciones_filtro = Asociacion.objects.filter(pk=asociacion_id) if asociacion_id else Asociacion.objects.none()
        else:
            danzarines_qs = danzarines_qs.none()
            membresias_qs = membresias_qs.none()
            entregas_qs = entregas_qs.none()
            auditorias_qs = auditorias_qs.none()

    elif role == 'administrador_asociacion':
        # Ámbito estricto: Solo su asociación y los conjuntos de su asociación
        asociacion_id = profile.asociacion_id if profile else None

        if asociacion_id:
            asociaciones_filtro = Asociacion.objects.filter(pk=asociacion_id)
            conjuntos_filtro = Conjunto.objects.filter(asociacion_id=asociacion_id, activo=True)

            # Filtro opcional por conjunto dentro de su asociación
            if conjunto_seleccionado_id and conjuntos_filtro.filter(pk=conjunto_seleccionado_id).exists():
                danzarines_qs = danzarines_qs.filter(membresias__conjunto_id=conjunto_seleccionado_id).distinct()
                membresias_qs = membresias_qs.filter(conjunto_id=conjunto_seleccionado_id)
                entregas_qs = entregas_qs.filter(danzarin__membresias__conjunto_id=conjunto_seleccionado_id).distinct()
            else:
                danzarines_qs = danzarines_qs.filter(membresias__asociacion_id=asociacion_id).distinct()
                membresias_qs = membresias_qs.filter(asociacion_id=asociacion_id)
                entregas_qs = entregas_qs.filter(danzarin__membresias__asociacion_id=asociacion_id).distinct()

            eventos_qs = eventos_qs.filter(asociacion_id=asociacion_id)
            auditorias_qs = auditorias_qs.filter(
                Q(usuario_id=request.user.id)
                | Q(usuario__userprofile__asociacion_id=asociacion_id)
                | Q(asociacion_id=asociacion_id)
            )
        else:
            danzarines_qs = danzarines_qs.none()
            membresias_qs = membresias_qs.none()
            entregas_qs = entregas_qs.none()
            auditorias_qs = auditorias_qs.none()

    else:
        # Superadministrador: Vista global con posibilidad de filtrar por asociación y conjunto
        asociaciones_filtro = Asociacion.objects.filter(activo=True).order_by('nombre')
        conjuntos_filtro = Conjunto.objects.filter(activo=True).select_related('asociacion').order_by('asociacion__nombre', 'nombre')

        if asociacion_seleccionada_id:
            danzarines_qs = danzarines_qs.filter(membresias__asociacion_id=asociacion_seleccionada_id).distinct()
            membresias_qs = membresias_qs.filter(asociacion_id=asociacion_seleccionada_id)
            entregas_qs = entregas_qs.filter(danzarin__membresias__asociacion_id=asociacion_seleccionada_id).distinct()
            eventos_qs = eventos_qs.filter(asociacion_id=asociacion_seleccionada_id)
            auditorias_qs = auditorias_qs.filter(
                Q(asociacion_id=asociacion_seleccionada_id) | Q(usuario__userprofile__asociacion_id=asociacion_seleccionada_id)
            )
            conjuntos_filtro = conjuntos_filtro.filter(asociacion_id=asociacion_seleccionada_id)

        if conjunto_seleccionado_id:
            danzarines_qs = danzarines_qs.filter(membresias__conjunto_id=conjunto_seleccionado_id).distinct()
            membresias_qs = membresias_qs.filter(conjunto_id=conjunto_seleccionado_id)
            entregas_qs = entregas_qs.filter(danzarin__membresias__conjunto_id=conjunto_seleccionado_id).distinct()

    # 2. Métricas y KPIs Principales
    total_danzarines = danzarines_qs.count()
    activos = danzarines_qs.filter(membresias__estado='activo').distinct().count()
    suspendidos = danzarines_qs.filter(membresias__estado='suspendido').distinct().count()
    castigados = danzarines_qs.filter(membresias__estado='castigado').distinct().count()
    bajas = danzarines_qs.filter(membresias__estado='baja').distinct().count()
    inactivos = total_danzarines - activos if total_danzarines >= activos else 0

    souvenirs_entregados = entregas_qs.count()
    souvenirs_pendientes = max(0, total_danzarines - souvenirs_entregados)

    pagos_al_dia = danzarines_qs.filter(membresias__estado_pago='al_dia').distinct().count()
    pagos_con_deuda = danzarines_qs.filter(membresias__estado_pago='con_deuda').distinct().count()

    total_eventos = eventos_qs.count()
    total_auditorias = auditorias_qs.count()

    # Porcentaje de danzarines activos y pagos al día
    tasa_activos_pct = round((activos / total_danzarines * 100), 1) if total_danzarines > 0 else 0
    tasa_al_dia_pct = round((pagos_al_dia / total_danzarines * 100), 1) if total_danzarines > 0 else 0
    tasa_souvenirs_pct = round((souvenirs_entregados / total_danzarines * 100), 1) if total_danzarines > 0 else 0

    # 3. Distribución por Sexo / Género
    por_sexo = {
        'varones': danzarines_qs.filter(sexo='m').count(),
        'mujeres': danzarines_qs.filter(sexo='f').count(),
        'otros': danzarines_qs.exclude(sexo__in=['m', 'f']).count(),
    }

    # 4. Distribución por Rangos de Edad
    current_year = timezone.now().year
    por_edad = {
        'menores': danzarines_qs.filter(fecha_nacimiento__year__gt=current_year - 18).count(),
        'jovenes': danzarines_qs.filter(
            fecha_nacimiento__year__lte=current_year - 18,
            fecha_nacimiento__year__gt=current_year - 30
        ).count(),
        'adultos': danzarines_qs.filter(
            fecha_nacimiento__year__lte=current_year - 30,
            fecha_nacimiento__year__gt=current_year - 60
        ).count(),
        'mayores': danzarines_qs.filter(fecha_nacimiento__year__lte=current_year - 60).count(),
    }

    # 5. Distribución por Asociaciones y Conjuntos
    distribucion_asociaciones = danzarines_qs.filter(membresias__estado='activo').values(
        'membresias__asociacion__nombre', 'membresias__conjunto__nombre'
    ).annotate(total=Count('id', distinct=True)).order_by(
        'membresias__asociacion__nombre', 'membresias__conjunto__nombre'
    )
    distribucion_lista = list(distribucion_asociaciones)

    # 7. Tendencia de Registros de Danzarines (Últimos 6 meses)
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

        cant_mes = danzarines_qs.filter(
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
        # Barras Horizontales (Horizontal Bar Chart): Distribución por Asociación y Conjunto
        'distribucion': {
            'labels': [
                f"{fila['membresias__asociacion__nombre'] or 'General'} / {fila['membresias__conjunto__nombre'] or 'General'}"
                for fila in distribucion_lista
            ] if distribucion_lista else ['Sin integrantes'],
            'data': [fila['total'] for fila in distribucion_lista] if distribucion_lista else [0],
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
                round(((por_edad['jovenes'] + por_edad['adultos']) / total_danzarines * 100), 1) if total_danzarines > 0 else 0,
                round((activos / (total_danzarines or 1)) * 100, 1),
            ],
        },
    }

    # Actividades recientes para el feed del dashboard
    actividades_recientes = auditorias_qs.order_by('-fecha_hora')[:6]

    return render(request, 'dashboard/dashboard.html', {
        'role': role,
        'user_profile': profile,
        'asociaciones_filtro': asociaciones_filtro,
        'conjuntos_filtro': conjuntos_filtro,
        'asociacion_id': asociacion_seleccionada_id,
        'conjunto_id': conjunto_seleccionado_id,
        'total_danzarines': total_danzarines,
        'danzarines_activos': activos,
        'danzarines_inactivos': inactivos,
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
