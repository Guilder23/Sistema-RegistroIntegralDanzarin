from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.contrib.staticfiles import finders
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO

from apps.eventos.models import Evento
from apps.socios.models import Socio
from apps.core.models import Asociacion, Conjunto
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
        asociacion_id = request.POST.get('asociacion_id')
        conjunto_id = request.POST.get('conjunto_id')
        observacion = request.POST.get('observacion', '').strip()

        role = get_role(request.user)
        if role == 'administrador_conjunto':
            asociacion_id = request.user.userprofile.asociacion_id
            conjunto_id = request.user.userprofile.conjunto_id
        elif role == 'administrador_asociacion':
            asociacion_id = request.user.userprofile.asociacion_id

        asociacion = Asociacion.objects.filter(pk=asociacion_id, activo=True).first()
        conjunto = Conjunto.objects.filter(pk=conjunto_id, asociacion=asociacion, activo=True).first() if asociacion and conjunto_id else None
        if not asociacion or not conjunto:
            messages.error(request, 'Selecciona una asociación y conjunto válidos.')
            return redirect('souvenirs:registrar_entrega')

        socio = Socio.objects.filter(id=socio_id)
        socio = socio.filter(membresias__asociacion=asociacion, membresias__conjunto=conjunto, membresias__estado='activo')
        socio = socio.distinct().first()
        if not socio:
            messages.error(request, 'Selecciona un socio válido.')
            return redirect('souvenirs:registrar_entrega')

        evento = evento_valido(evento_id, asociacion, conjunto)
        if not evento:
            messages.error(request, 'Selecciona un evento válido.')
            return redirect('souvenirs:registrar_entrega')

        if SouvenirEntrega.objects.filter(socio=socio, evento=evento).exists():
            messages.warning(request, 'Este socio ya registró una entrega para el evento seleccionado.')
            return redirect('souvenirs:listar_entregas')

        souvenir = souvenirs_scope(request.user).filter(id=souvenir_id, activo=True, evento=evento, asociacion=asociacion).filter(Q(conjunto=conjunto) | Q(conjunto__isnull=True)).first()
        if not souvenir:
            messages.error(request, 'Selecciona un souvenir perteneciente al evento y ámbito seleccionados.')
            return redirect('souvenirs:registrar_entrega')

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

    role = get_role(request.user)
    asociaciones, conjuntos, eventos = opciones_souvenirs(request.user)
    socios = Socio.objects.filter(membresias__estado='activo').prefetch_related('membresias').distinct().order_by('apellido', 'nombre')
    if role == 'administrador_asociacion':
        socios = socios.filter(membresias__asociacion_id=request.user.userprofile.asociacion_id)
    elif role == 'administrador_conjunto':
        socios = socios.filter(membresias__conjunto_id=request.user.userprofile.conjunto_id)
    socios_data = []
    for socio in socios:
        for membresia in socio.membresias.all():
            if membresia.estado == 'activo':
                socios_data.append({
                    'value': str(socio.id),
                    'label': str(socio),
                    'asociacionId': str(membresia.asociacion_id),
                    'conjuntoId': str(membresia.conjunto_id),
                })
    souvenirs = souvenirs_scope(request.user).filter(activo=True).order_by('-creado')
    return render(request, 'souvenirs/entregas/registrar_entrega.html', {
        'socios': socios, 'socios_data': socios_data, 'eventos': eventos,
        'souvenirs': souvenirs, 'asociaciones': asociaciones,
        'conjuntos': conjuntos, 'role': role,
    })


@login_required
def descargar_certificado_entrega(request, pk):
    entrega = get_object_or_404(
        SouvenirEntrega.objects.select_related('socio__user', 'evento', 'souvenir'),
        pk=pk,
    )
    if entrega.socio.user_id != request.user.id or not entrega.souvenir:
        raise Http404

    plantilla = finders.find('img/PlantillaCertificado.png')
    if not plantilla:
        raise Http404('No se encontró la plantilla del certificado.')

    with Image.open(plantilla) as imagen:
        imagen_width, imagen_height = imagen.size
    page_width = 842
    page_height = page_width * imagen_height / imagen_width
    buffer = BytesIO()
    documento = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    documento.drawImage(ImageReader(plantilla), 0, 0, width=page_width, height=page_height)

    nombre = str(entrega.socio)
    evento = entrega.evento.nombre if entrega.evento else 'la actividad registrada'
    fecha = entrega.fecha_entrega.strftime('%d/%m/%Y')
    texto = f'Se reconoce a {nombre} por su participación en {evento}.'
    documento.setFillColorRGB(0.04, 0.12, 0.23)
    documento.setFont('Helvetica-Bold', 24)
    documento.drawCentredString(page_width / 2, page_height * 0.60, nombre)
    documento.setFont('Helvetica', 14)
    documento.drawCentredString(page_width / 2, page_height * 0.53, texto[:110])
    documento.setFont('Helvetica', 12)
    documento.drawCentredString(page_width / 2, page_height * 0.47, f'Souvenir entregado: {entrega.souvenir.nombre}')
    documento.drawCentredString(page_width / 2, page_height * 0.42, f'Fecha de entrega: {fecha}')
    documento.save()
    buffer.seek(0)

    respuesta = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="certificado_{entrega.socio.codigo_socio or entrega.socio_id}.pdf"'
    return respuesta


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def listar_souvenirs(request):
    q = request.GET.get('q', '').strip()
    activo = request.GET.get('activo', '').strip()
    evento_id = request.GET.get('evento_id', '').strip()
    role = get_role(request.user)
    objetos = Souvenir.objects.select_related('evento', 'asociacion', 'conjunto').order_by('-creado')
    if role == 'administrador_asociacion':
        objetos = objetos.filter(asociacion_id=request.user.userprofile.asociacion_id)
    elif role == 'administrador_conjunto':
        objetos = objetos.filter(conjunto_id=request.user.userprofile.conjunto_id)

    if q:
        objetos = objetos.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(evento__nombre__icontains=q)
        )

    if evento_id:
        objetos = objetos.filter(evento_id=evento_id)
    asociacion_id = request.GET.get('asociacion_id', '').strip()
    conjunto_id = request.GET.get('conjunto_id', '').strip()
    if asociacion_id:
        objetos = objetos.filter(asociacion_id=asociacion_id)
    if conjunto_id:
        objetos = objetos.filter(conjunto_id=conjunto_id)

    if activo == 'si':
        objetos = objetos.filter(activo=True)
    elif activo == 'no':
        objetos = objetos.filter(activo=False)

    asociaciones, conjuntos, eventos = opciones_souvenirs(request.user)
    paginator = Paginator(objetos, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'souvenirs/souvenirs.html', {
        'page_obj': page_obj,
        'q': q,
        'activo': activo,
        'eventos': eventos,
        'evento_id': evento_id,
        'asociacion_id': asociacion_id,
        'conjunto_id': conjunto_id,
        'asociaciones': asociaciones,
        'conjuntos': conjuntos,
        'role': role,
    })


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def crear_souvenir(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        evento_id = request.POST.get('evento_id')
        asociacion, conjunto = ambito_souvenir(request)
        descripcion = request.POST.get('descripcion', '').strip()
        stock = int(request.POST.get('stock') or 0)
        imagen = request.FILES.get('imagen')

        if not nombre:
            messages.error(request, 'Nombre requerido.')
            return redirect('souvenirs:listar_souvenirs')

        evento = None
        if evento_id:
            evento = evento_valido(evento_id, asociacion, conjunto)
            if not evento:
                messages.error(request, 'El evento no pertenece al ámbito seleccionado.')
                return redirect('souvenirs:listar_souvenirs')

        if not asociacion:
            messages.error(request, 'Selecciona una asociación válida para el souvenir.')
            return redirect('souvenirs:listar_souvenirs')

        souvenir = Souvenir.objects.create(nombre=nombre, asociacion=asociacion, conjunto=conjunto, evento=evento, descripcion=descripcion, stock=stock, imagen=imagen, creado_por=request.user)
        registrar_auditoria(
            request.user,
            'creacion_souvenir',
            f'Souvenir {souvenir.nombre}',
            nuevo={'nombre': souvenir.nombre, 'stock': souvenir.stock, 'evento': evento.nombre if evento else None},
            asociacion=asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Souvenir creado.')
        return redirect('souvenirs:listar_souvenirs')
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def editar_souvenir(request, pk):
    s = get_object_or_404(souvenirs_scope(request.user), pk=pk)
    if request.method == 'POST':
        anterior = {'nombre': s.nombre, 'stock': s.stock}
        s.nombre = request.POST.get('nombre', s.nombre).strip()
        evento_id = request.POST.get('evento_id')
        asociacion, conjunto = ambito_souvenir(request, existing=s)
        s.descripcion = request.POST.get('descripcion', s.descripcion).strip()
        s.stock = int(request.POST.get('stock') or s.stock)
        if request.FILES.get('imagen'):
            s.imagen = request.FILES.get('imagen')
        if evento_id:
            s.evento = evento_valido(evento_id, asociacion, conjunto)
            if not s.evento:
                messages.error(request, 'El evento no pertenece al ámbito seleccionado.')
                return redirect('souvenirs:listar_souvenirs')
        else:
            s.evento = None
        if not asociacion:
            messages.error(request, 'Selecciona una asociación válida para el souvenir.')
            return redirect('souvenirs:listar_souvenirs')
        s.asociacion = asociacion
        s.conjunto = conjunto
        s.save()
        registrar_auditoria(
            request.user,
            'modificacion_souvenir',
            f'Souvenir {s.nombre}',
            anterior=anterior,
            nuevo={'nombre': s.nombre, 'stock': s.stock},
            asociacion=s.asociacion,
            conjunto=s.conjunto,
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
    s = get_object_or_404(souvenirs_scope(request.user), pk=pk)
    if request.method == 'POST':
        if s.entregas.exists():
            messages.error(request, 'No se puede eliminar un souvenir asignado a un socio. Puedes cambiar su estado a inactivo.')
            return redirect('souvenirs:listar_souvenirs')
        nombre = s.nombre
        asociacion = s.asociacion
        conjunto = s.conjunto
        s.delete()
        registrar_auditoria(
            request.user,
            'eliminacion_souvenir',
            f'Souvenir {nombre}',
            asociacion=asociacion,
            conjunto=conjunto,
        )
        messages.success(request, 'Souvenir eliminado.')
        return redirect('souvenirs:listar_souvenirs')
    return redirect('souvenirs:listar_souvenirs')


@login_required
@user_passes_test(is_administrative, login_url='/login/')
def cambiar_estado_souvenir(request, pk):
    souvenir = get_object_or_404(souvenirs_scope(request.user), pk=pk)
    if request.method == 'POST':
        souvenir.activo = not souvenir.activo
        souvenir.save(update_fields=['activo'])
        estado = 'activado' if souvenir.activo else 'desactivado'
        registrar_auditoria(
            request.user,
            'cambio_estado_souvenir',
            f'Souvenir {souvenir.nombre} ({estado})',
            nuevo={'activo': souvenir.activo},
            asociacion=souvenir.asociacion,
            conjunto=souvenir.conjunto,
        )
        messages.success(request, f'Souvenir {estado}.')
    return redirect('souvenirs:listar_souvenirs')


def souvenirs_scope(user):
    role = get_role(user)
    queryset = Souvenir.objects.all()
    if role == 'administrador_asociacion':
        return queryset.filter(asociacion_id=user.userprofile.asociacion_id)
    if role == 'administrador_conjunto':
        return queryset.filter(conjunto_id=user.userprofile.conjunto_id)
    return queryset


def opciones_souvenirs(user):
    role = get_role(user)
    asociaciones = Asociacion.objects.filter(activo=True)
    conjuntos = Conjunto.objects.filter(activo=True).select_related('asociacion')
    eventos = Evento.objects.filter(activo=True).select_related('asociacion', 'conjunto')
    if role == 'administrador_asociacion':
        asociaciones = asociaciones.filter(pk=user.userprofile.asociacion_id)
        conjuntos = conjuntos.filter(asociacion_id=user.userprofile.asociacion_id)
        eventos = eventos.filter(asociacion_id=user.userprofile.asociacion_id)
    elif role == 'administrador_conjunto':
        asociaciones = asociaciones.filter(pk=user.userprofile.asociacion_id)
        conjuntos = conjuntos.filter(pk=user.userprofile.conjunto_id)
        eventos = eventos.filter(asociacion_id=user.userprofile.asociacion_id).filter(Q(conjunto__isnull=True) | Q(conjunto_id=user.userprofile.conjunto_id))
    return asociaciones, conjuntos, eventos.order_by('-fecha_evento')


def ambito_souvenir(request, existing=None):
    role = get_role(request.user)
    if role == 'administrador_conjunto':
        return request.user.userprofile.asociacion, request.user.userprofile.conjunto
    if role == 'administrador_asociacion':
        asociacion = request.user.userprofile.asociacion
        conjunto_id = request.POST.get('conjunto_id')
        conjunto = Conjunto.objects.filter(pk=conjunto_id, asociacion=asociacion, activo=True).first() if conjunto_id else None
        return asociacion, conjunto
    asociacion = Asociacion.objects.filter(pk=request.POST.get('asociacion_id'), activo=True).first()
    conjunto = None
    if request.POST.get('tipo_ambito') == 'conjunto':
        conjunto = Conjunto.objects.filter(pk=request.POST.get('conjunto_id'), asociacion=asociacion, activo=True).first() if asociacion and request.POST.get('conjunto_id') else None
    return asociacion, conjunto


def evento_valido(evento_id, asociacion, conjunto):
    if not asociacion:
        return None
    eventos = Evento.objects.filter(pk=evento_id, activo=True, asociacion=asociacion)
    if conjunto:
        eventos = eventos.filter(Q(conjunto__isnull=True) | Q(conjunto=conjunto))
    else:
        eventos = eventos.filter(conjunto__isnull=True)
    return eventos.first()

