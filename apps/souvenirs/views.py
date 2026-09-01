from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from apps.eventos.models import Evento
from apps.socios.models import Socio
from .models import SouvenirEntrega, Souvenir
from apps.core.permissions import scope_filter, get_role, is_administrative, registrar_auditoria


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def listar_entregas(request):
    entregas = SouvenirEntrega.objects.select_related('socio', 'entregado_por', 'evento')
    if get_role(request.user) != 'superadministrador':
        entregas = entregas.filter(socio__membresias__asociacion_id=request.user.userprofile.asociacion_id)
        if get_role(request.user) == 'administrador_conjunto':
            entregas = entregas.filter(socio__membresias__conjunto_id=request.user.userprofile.conjunto_id)
    entregas = entregas.distinct().order_by('-fecha_entrega')
    paginator = Paginator(entregas, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'souvenirs/entregas/entregas.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def registrar_entrega(request):
    if request.method == 'POST':
        socio_id = request.POST.get('socio_id')
        evento_id = request.POST.get('evento_id')
        souvenir_id = request.POST.get('souvenir_id')
        observacion = request.POST.get('observacion', '').strip()

        socio = Socio.objects.filter(id=socio_id)
        if get_role(request.user) != 'superadministrador':
            socio = socio.filter(membresias__asociacion_id=request.user.userprofile.asociacion_id)
            if get_role(request.user) == 'administrador_conjunto':
                socio = socio.filter(membresias__conjunto_id=request.user.userprofile.conjunto_id)
        socio = socio.distinct().first()
        if not socio:
            messages.error(request, 'Selecciona un socio válido.')
            return redirect('souvenirs:registrar_entrega')

        evento = Evento.objects.filter(id=evento_id, activo=True).first()
        if not evento:
            messages.error(request, 'Selecciona un evento válido.')
            return redirect('souvenirs:registrar_entrega')

        if SouvenirEntrega.objects.filter(socio=socio, evento=evento).exists():
            messages.warning(request, 'Este socio ya registró una entrega para el evento seleccionado.')
            return redirect('souvenirs:listar_entregas')

        souvenir = None
        if souvenir_id:
            souvenir = Souvenir.objects.filter(id=souvenir_id, activo=True).first()

        SouvenirEntrega.objects.create(
            socio=socio,
            evento=evento,
            souvenir=souvenir,
            entregado_por=request.user,
            observacion=observacion,
        )

        if souvenir and souvenir.stock and souvenir.stock > 0:
            souvenir.stock = max(0, souvenir.stock - 1)
            souvenir.save()

        socio.recibio_souvenir = True
        socio.save()
        
        # Obtener asociación y conjunto del socio para la auditoría
        membresia = socio.membresias.filter(estado='activo').first()
        registrar_auditoria(
            request.user,
            'entrega_souvenir',
            f'Entrega a {socio} ({evento.nombre})',
            nuevo={'socio': str(socio), 'evento': evento.nombre, 'souvenir': souvenir.nombre if souvenir else 'Sin souvenir específico'},
            asociacion=membresia.asociacion if membresia else None,
            conjunto=membresia.conjunto if membresia else None,
        )
        messages.success(request, 'Entrega de souvenir registrada.')
        return redirect('souvenirs:listar_entregas')

    socios = Socio.objects.filter(membresias__estado='activo')
    if get_role(request.user) != 'superadministrador':
        socios = socios.filter(membresias__asociacion_id=request.user.userprofile.asociacion_id)
        if get_role(request.user) == 'administrador_conjunto':
            socios = socios.filter(membresias__conjunto_id=request.user.userprofile.conjunto_id)
    socios = socios.distinct().order_by('apellido', 'nombre')
    eventos = Evento.objects.filter(activo=True).order_by('-fecha_evento')
    souvenirs = Souvenir.objects.filter(activo=True).order_by('-creado')
    return render(request, 'souvenirs/entregas/registrar_entrega.html', {'socios': socios, 'eventos': eventos, 'souvenirs': souvenirs})


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def listar_souvenirs(request):
    q = request.GET.get('q', '').strip()
    activo = request.GET.get('activo', '').strip()
    evento_id = request.GET.get('evento_id', '').strip()
    objetos = Souvenir.objects.select_related('evento').order_by('-creado')

    if q:
        objetos = objetos.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(evento__nombre__icontains=q)
        )

    if evento_id:
        objetos = objetos.filter(evento_id=evento_id)

    if activo == 'si':
        objetos = objetos.filter(activo=True)
    elif activo == 'no':
        objetos = objetos.filter(activo=False)

    eventos = Evento.objects.filter(activo=True).order_by('-fecha_evento')
    paginator = Paginator(objetos, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'souvenirs/souvenirs.html', {
        'page_obj': page_obj,
        'q': q,
        'activo': activo,
        'eventos': eventos,
        'evento_id': evento_id,
    })


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def crear_souvenir(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        evento_id = request.POST.get('evento_id')
        descripcion = request.POST.get('descripcion', '').strip()
        stock = int(request.POST.get('stock') or 0)
        imagen = request.FILES.get('imagen')

        if not nombre:
            messages.error(request, 'Nombre requerido.')
            return redirect('souvenirs:listar_souvenirs')

        evento = None
        if evento_id:
            evento = Evento.objects.filter(id=evento_id, activo=True).first()

        souvenir = Souvenir.objects.create(nombre=nombre, evento=evento, descripcion=descripcion, stock=stock, imagen=imagen)
        registrar_auditoria(
            request.user,
            'creacion_souvenir',
            f'Souvenir {souvenir.nombre}',
            nuevo={'nombre': souvenir.nombre, 'stock': souvenir.stock, 'evento': evento.nombre if evento else None},
            asociacion=evento.asociacion if evento else None,
        )
        messages.success(request, 'Souvenir creado.')
        return redirect('souvenirs:listar_souvenirs')
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def editar_souvenir(request, pk):
    s = get_object_or_404(Souvenir, pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': s.nombre, 'stock': s.stock}
        s.nombre = request.POST.get('nombre', s.nombre).strip()
        evento_id = request.POST.get('evento_id')
        s.descripcion = request.POST.get('descripcion', s.descripcion).strip()
        s.stock = int(request.POST.get('stock') or s.stock)
        if request.FILES.get('imagen'):
            s.imagen = request.FILES.get('imagen')
        if evento_id:
            s.evento = Evento.objects.filter(id=evento_id, activo=True).first()
        else:
            s.evento = None
        s.save()
        registrar_auditoria(
            request.user,
            'modificacion_souvenir',
            f'Souvenir {s.nombre}',
            anterior=anterior,
            nuevo={'nombre': s.nombre, 'stock': s.stock},
            asociacion=s.evento.asociacion if s.evento else None,
        )
        messages.success(request, 'Souvenir actualizado.')
        return redirect('souvenirs:listar_souvenirs')
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def ver_souvenir(request, pk):
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def eliminar_souvenir(request, pk):
    s = get_object_or_404(Souvenir, pk=pk)
    if request.method == 'POST':
        if s.entregas.exists():
            messages.error(request, 'No se puede eliminar un souvenir asignado a un socio. Puedes cambiar su estado a inactivo.')
            return redirect('souvenirs:listar_souvenirs')
        nombre = s.nombre
        asociacion = s.evento.asociacion if s.evento else None
        s.delete()
        registrar_auditoria(
            request.user,
            'eliminacion_souvenir',
            f'Souvenir {nombre}',
            asociacion=asociacion,
        )
        messages.success(request, 'Souvenir eliminado.')
        return redirect('souvenirs:listar_souvenirs')
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def cambiar_estado_souvenir(request, pk):
    souvenir = get_object_or_404(Souvenir, pk=pk)
    if request.method == 'POST':
        souvenir.activo = not souvenir.activo
        souvenir.save(update_fields=['activo'])
        estado = 'activado' if souvenir.activo else 'desactivado'
        registrar_auditoria(
            request.user,
            'cambio_estado_souvenir',
            f'Souvenir {souvenir.nombre} ({estado})',
            nuevo={'activo': souvenir.activo},
            asociacion=souvenir.evento.asociacion if souvenir.evento else None,
        )
        messages.success(request, f'Souvenir {estado}.')
    return redirect('souvenirs:listar_souvenirs')

