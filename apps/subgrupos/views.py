from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.core.models import Grupo, Subgrupo
from apps.core.permissions import get_role, registrar_auditoria


def can_manage_subgroups(user):
    return get_role(user) in {'superadministrador', 'administrador_grupo'}


def scoped_subgroups(user):
    if get_role(user) == 'superadministrador':
        return Subgrupo.objects.select_related('grupo').all()
    return Subgrupo.objects.filter(grupo_id=user.userprofile.grupo_id).select_related('grupo')


@login_required
@user_passes_test(can_manage_subgroups, login_url='/login/')
def listar_subgrupos(request):
    q = request.GET.get('q', '').strip()
    subgrupos = scoped_subgroups(request.user)
    if q:
        subgrupos = subgrupos.filter(nombre__icontains=q)
    grupos = Grupo.objects.filter(activo=True) if get_role(request.user) == 'superadministrador' else Grupo.objects.filter(pk=request.user.userprofile.grupo_id)
    return render(request, 'subgrupos/subgrupos.html', {'subgrupos': subgrupos, 'grupos': grupos, 'q': q})


@login_required
@user_passes_test(can_manage_subgroups, login_url='/login/')
def crear_subgrupo(request):
    if request.method == 'POST':
        grupo_id = request.POST.get('grupo_id')
        if get_role(request.user) != 'superadministrador':
            grupo_id = request.user.userprofile.grupo_id
        grupo = Grupo.objects.filter(pk=grupo_id, activo=True).first()
        nombre = request.POST.get('nombre', '').strip()
        if grupo and nombre:
            subgrupo, created = Subgrupo.objects.get_or_create(grupo=grupo, nombre=nombre, defaults={'activo': True})
            if created:
                registrar_auditoria(
                    request.user,
                    'creacion_subgrupo',
                    f'Subgrupo {subgrupo.nombre} ({grupo.nombre})',
                    nuevo={'nombre': subgrupo.nombre, 'grupo': grupo.nombre},
                    grupo=grupo,
                    subgrupo=subgrupo,
                )
                messages.success(request, 'Subgrupo creado correctamente.')
            else:
                messages.info(request, 'El subgrupo ya existe.')
        else:
            messages.error(request, 'Grupo y nombre son obligatorios.')
    return redirect('subgrupos:listar_subgrupos')


@login_required
@user_passes_test(can_manage_subgroups, login_url='/login/')
def editar_subgrupo(request, pk):
    subgrupo = get_object_or_404(scoped_subgroups(request.user), pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': subgrupo.nombre, 'activo': subgrupo.activo}
        subgrupo.nombre = request.POST.get('nombre', subgrupo.nombre).strip()
        subgrupo.activo = request.POST.get('activo') == 'on'
        subgrupo.save()
        registrar_auditoria(
            request.user,
            'modificacion_subgrupo',
            f'Subgrupo {subgrupo.nombre}',
            anterior=anterior,
            nuevo={'nombre': subgrupo.nombre, 'activo': subgrupo.activo},
            grupo=subgrupo.grupo,
            subgrupo=subgrupo,
        )
        messages.success(request, 'Subgrupo actualizado correctamente.')
    return redirect('subgrupos:listar_subgrupos')


@login_required
@user_passes_test(can_manage_subgroups, login_url='/login/')
def eliminar_subgrupo(request, pk):
    subgrupo = get_object_or_404(scoped_subgroups(request.user), pk=pk)
    if request.method == 'POST':
        subgrupo.activo = False
        subgrupo.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'desactivacion_subgrupo',
            f'Subgrupo {subgrupo.nombre}',
            nuevo={'activo': False},
            grupo=subgrupo.grupo,
            subgrupo=subgrupo,
        )
        messages.success(request, 'Subgrupo desactivado correctamente.')
    return redirect('subgrupos:listar_subgrupos')

