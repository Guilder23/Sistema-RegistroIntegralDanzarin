from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from apps.core.models import Grupo
from apps.core.permissions import get_role, registrar_auditoria


def is_superadmin(user):
    return get_role(user) == 'superadministrador'


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def listar_grupos(request):
    q = request.GET.get('q', '').strip()
    grupos = Grupo.objects.all()
    if q:
        grupos = grupos.filter(nombre__icontains=q)
    return render(request, 'grupos/grupos.html', {'grupos': grupos, 'q': q})


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def crear_grupo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        if nombre and not Grupo.objects.filter(nombre__iexact=nombre).exists():
            grupo = Grupo.objects.create(nombre=nombre, activo=activo)
            registrar_auditoria(
                request.user,
                'creacion_grupo',
                f'Grupo {grupo.nombre}',
                nuevo={'nombre': grupo.nombre, 'activo': grupo.activo},
                grupo=grupo,
            )
            messages.success(request, 'Grupo creado correctamente.')
        else:
            messages.error(request, 'El nombre es obligatorio y debe ser único.')
    return redirect('grupos:listar_grupos')


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def editar_grupo(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': grupo.nombre, 'activo': grupo.activo}
        grupo.nombre = request.POST.get('nombre', grupo.nombre).strip()
        grupo.activo = request.POST.get('activo') == 'on'
        grupo.save()
        registrar_auditoria(
            request.user,
            'modificacion_grupo',
            f'Grupo {grupo.nombre}',
            anterior=anterior,
            nuevo={'nombre': grupo.nombre, 'activo': grupo.activo},
            grupo=grupo,
        )
        messages.success(request, 'Grupo actualizado correctamente.')
    return redirect('grupos:listar_grupos')


@login_required
@user_passes_test(is_superadmin, login_url='/login/')
def eliminar_grupo(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        grupo.activo = False
        grupo.save(update_fields=['activo'])
        registrar_auditoria(
            request.user,
            'desactivacion_grupo',
            f'Grupo {grupo.nombre}',
            nuevo={'activo': False},
            grupo=grupo,
        )
        messages.success(request, 'Grupo desactivado correctamente.')
    return redirect('grupos:listar_grupos')

