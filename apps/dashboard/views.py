from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear
from django.utils import timezone
from apps.socios.models import Socio
from apps.souvenirs.models import SouvenirEntrega
from apps.core.permissions import scope_socios, is_administrative


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def dashboard(request):
    socios = scope_socios(Socio.objects.all(), request.user)
    total_socios = socios.count()
    activos = socios.filter(membresias__estado='activo').distinct().count()
    inactivos = socios.exclude(membresias__estado='activo').distinct().count()
    souvenirs_entregados = SouvenirEntrega.objects.count()
    souvenirs_pendientes = max(0, total_socios - souvenirs_entregados)
    current_year = timezone.now().year
    por_sexo = {
        'varones': socios.filter(sexo='m').count(),
        'mujeres': socios.filter(sexo='f').count(),
    }
    por_edad = {
        'menores': socios.filter(fecha_nacimiento__year__gt=current_year - 18).count(),
        'adultos': socios.filter(fecha_nacimiento__year__lte=current_year - 18, fecha_nacimiento__year__gt=current_year - 60).count(),
        'mayores': socios.filter(fecha_nacimiento__year__lte=current_year - 60).count(),
    }
    estados = {
        estado: socios.filter(membresias__estado=estado).distinct().count()
        for estado in ('activo', 'suspendido', 'castigado', 'baja')
    }
    pagos = {
        'al_dia': socios.filter(membresias__estado_pago='al_dia').distinct().count(),
        'con_deuda': socios.filter(membresias__estado_pago='con_deuda').distinct().count(),
    }
    distribucion = socios.filter(membresias__estado='activo').values(
        'membresias__grupo__nombre', 'membresias__subgrupo__nombre'
    ).annotate(total=Count('id', distinct=True)).order_by(
        'membresias__grupo__nombre', 'membresias__subgrupo__nombre'
    )

    return render(request, 'dashboard/dashboard.html', {
        'total_socios': total_socios,
        'socios_activos': activos,
        'socios_inactivos': inactivos,
        'souvenirs_entregados': souvenirs_entregados,
        'souvenirs_pendientes': souvenirs_pendientes,
        'por_sexo': por_sexo,
        'por_edad': por_edad,
        'estados': estados,
        'pagos': pagos,
        'distribucion': distribucion,
    })
