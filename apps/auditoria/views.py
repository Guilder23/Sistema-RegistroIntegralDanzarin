from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from apps.core.models import Auditoria
from apps.core.permissions import get_role


@login_required
@user_passes_test(lambda user: get_role(user) == 'superadministrador', login_url='/login/')
def listar_auditoria(request):
    registros = Auditoria.objects.select_related('usuario').all()
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(accion__icontains=q) | registros.filter(registro_afectado__icontains=q)
    return render(request, 'auditoria/auditoria.html', {'registros': registros, 'q': q})
