from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
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

    return render(request, 'dashboard/dashboard.html', {
        'total_socios': total_socios,
        'socios_activos': activos,
        'socios_inactivos': inactivos,
        'souvenirs_entregados': souvenirs_entregados,
        'souvenirs_pendientes': souvenirs_pendientes,
    })
