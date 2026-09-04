from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from xml.sax.saxutils import escape
from .permissions import can_manage_users


def get_home_redirect(user):
	from .permissions import is_administrative
	if is_administrative(user):
		return 'dashboard:dashboard'
	return 'socios:perfil_socio'


def inicio(request):
    if request.user.is_authenticated:
        return redirect(get_home_redirect(request.user))
    return render(request, 'core/inicio.html')


def faq(request):
    return render(request, 'core/faq.html')


def robots_txt(request):
	sitemap_url = f'{settings.PUBLIC_SITE_URL}{reverse("core:sitemap")}'
	content = '\n'.join([
		'User-agent: *',
		'Allow: /',
		'Disallow: /login/',
		'Disallow: /secret-admin/',
		'Disallow: /socios/',
		'Disallow: /reportes/',
		'Disallow: /dashboard/',
		'Sitemap: ' + sitemap_url,
		'',
	])
	return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
	public_urls = [
		f'{settings.PUBLIC_SITE_URL}{reverse("core:inicio")}',
		f'{settings.PUBLIC_SITE_URL}{reverse("core:faq")}',
	]
	url_entries = ''.join(
		f'<url><loc>{escape(url)}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>'
		for url, priority in ((public_urls[0], '1.0'), (public_urls[1], '0.7'))
	)
	content = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
		f'{url_entries}'
		'</urlset>'
	)
	return HttpResponse(content, content_type='application/xml')


def iniciar_sesion(request):
	if request.user.is_authenticated:
		return redirect(get_home_redirect(request.user))

	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '')

		login_error = None
		user = authenticate(request, username=username, password=password)
		if user is None:
			login_error = 'Usuario o contrasena incorrectos.'
		else:
			try:
				from apps.socios.models import Socio
				socio = Socio.objects.get(user=user)
				membresias = socio.membresias.all()
				if membresias.exists() and not membresias.filter(estado='activo').exists():
					login_error = 'Tu membresia no se encuentra activa. Comunicate con el administrador.'
			except Socio.DoesNotExist:
				pass

		if login_error:
			return render(request, 'core/inicio.html', {
				'show_login_modal': True,
				'login_username': username,
				'login_error': login_error,
			})

		login(request, user)
		next_url = request.GET.get('next') or request.POST.get('next')
		if next_url:
			return redirect(next_url)
		return redirect(get_home_redirect(user))

	return redirect(f"{reverse('core:inicio')}#modalLogin")


@login_required
def cerrar_sesion(request):
	logout(request)
	return redirect('core:inicio')


@login_required
@user_passes_test(can_manage_users, login_url='/login/')
def registrar_usuario(request):
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		email = request.POST.get('email', '').strip()
		password = request.POST.get('password', '')
		password2 = request.POST.get('password2', '')
		rol = request.POST.get('rol', 'miembro')
		roles_validos = {'superadministrador', 'administrador_asociacion', 'administrador_conjunto', 'miembro'}
		if rol not in roles_validos:
			rol = 'miembro'
		from apps.core.models import Asociacion, Conjunto
		asociacion = Asociacion.objects.filter(pk=request.POST.get('asociacion_id'), activo=True).first()
		conjunto = Conjunto.objects.filter(pk=request.POST.get('conjunto_id'), asociacion=asociacion, activo=True).first() if asociacion else None
		if rol == 'administrador_asociacion' and not asociacion:
			messages.error(request, 'El Administrador de Asociación debe tener una asociación asignada.')
			return redirect('core:registro')
		if rol == 'administrador_conjunto' and (not asociacion or not conjunto):
			messages.error(request, 'El Administrador de Conjunto debe tener asociación y conjunto asignados.')
			return redirect('core:registro')
		if rol == 'miembro' and (not asociacion or not conjunto):
			messages.error(request, 'El Miembro / Socio debe tener asociación y conjunto asignados.')
			return redirect('core:registro')

		if not username or not password:
			messages.error(request, 'Usuario y contrasena son obligatorios.')
			return redirect('core:registro')

		if password != password2:
			messages.error(request, 'Las contrasenas no coinciden.')
			return redirect('core:registro')

		if User.objects.filter(username=username).exists():
			messages.error(request, 'El nombre de usuario ya existe.')
			return redirect('core:registro')

		user = User.objects.create_user(
			username=username,
			first_name=first_name,
			last_name=last_name,
			email=email,
			password=password,
		)
		user.is_staff = rol != 'miembro'
		user.is_superuser = rol == 'superadministrador'
		user.save()
		from apps.socios.models import UserProfile
		UserProfile.objects.filter(user=user).update(rol=rol, asociacion=asociacion, conjunto=conjunto)
		if rol == 'miembro':
			from apps.socios.models import Socio, Membresia, generar_codigo_socio
			socio = Socio.objects.create(
				user=user,
				codigo_socio=generar_codigo_socio(),
				nombre=first_name or username,
				apellido_paterno=last_name,
				email=email,
			)
			Membresia.inscribir(socio, asociacion, conjunto, estado_pago='al_dia')

		messages.success(request, 'Usuario creado correctamente.')
		return redirect('core:registro')

	q = request.GET.get('q', '').strip()
	rol = request.GET.get('rol', '').strip()
	estado = request.GET.get('estado', '').strip()

	usuarios_qs = User.objects.order_by('-date_joined')
	if q:
		usuarios_qs = usuarios_qs.filter(
			Q(username__icontains=q)
			| Q(first_name__icontains=q)
			| Q(last_name__icontains=q)
			| Q(email__icontains=q)
		)

	if rol == 'admin':
		usuarios_qs = usuarios_qs.filter(is_staff=True)
	elif rol == 'usuario':
		usuarios_qs = usuarios_qs.filter(is_staff=False)

	if estado == 'activo':
		usuarios_qs = usuarios_qs.filter(is_active=True)
	elif estado == 'bloqueado':
		usuarios_qs = usuarios_qs.filter(is_active=False)

	paginator = Paginator(usuarios_qs, 10)
	page_number = request.GET.get('page')
	usuarios = paginator.get_page(page_number)

	return render(
		request,
		'auth/registro.html',
		{
			'usuarios': usuarios,
			'q': q,
			'rol': rol,
			'estado': estado,
		'asociaciones': __import__('apps.core.models', fromlist=['Asociacion']).Asociacion.objects.filter(activo=True),
		'conjuntos': __import__('apps.core.models', fromlist=['Conjunto']).Conjunto.objects.filter(activo=True).select_related('asociacion'),
		},
	)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def editar_usuario(request, user_id):
	objetivo = get_object_or_404(User, id=user_id)

	if request.method == 'POST':
		if objetivo.is_superuser and not request.user.is_superuser:
			messages.error(request, 'No tienes permiso para editar este usuario.')
			return redirect('core:registro')

		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip()
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		rol = request.POST.get('rol', 'miembro')
		from apps.core.models import Asociacion, Conjunto
		asociacion = Asociacion.objects.filter(pk=request.POST.get('asociacion_id'), activo=True).first()
		conjunto = Conjunto.objects.filter(pk=request.POST.get('conjunto_id'), asociacion=asociacion, activo=True).first() if asociacion else None
		if rol not in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto', 'miembro'}:
			rol = 'miembro'
		if rol == 'administrador_asociacion' and not asociacion or rol == 'administrador_conjunto' and (not asociacion or not conjunto):
			messages.error(request, 'El rol seleccionado requiere un ámbito válido.')
			return redirect('core:registro')

		if not username:
			messages.error(request, 'El usuario es obligatorio.')
			return redirect('core:registro')

		if User.objects.exclude(id=objetivo.id).filter(username=username).exists():
			messages.error(request, 'Ese nombre de usuario ya existe.')
			return redirect('core:registro')

		objetivo.username = username
		objetivo.email = email
		objetivo.first_name = first_name
		objetivo.last_name = last_name
		objetivo.is_staff = rol != 'miembro'
		objetivo.is_superuser = rol == 'superadministrador'

		password = request.POST.get('password', '')
		password2 = request.POST.get('password2', '')
		if password or password2:
			if password != password2:
				messages.error(request, 'Las contrasenas no coinciden.')
				return redirect('core:registro')
			objetivo.set_password(password)

		objetivo.save()
		from apps.socios.models import UserProfile
		UserProfile.objects.filter(user=objetivo).update(rol=rol, asociacion=asociacion, conjunto=conjunto)
		messages.success(request, 'Usuario actualizado correctamente.')

	return redirect('core:registro')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def toggle_bloqueo_usuario(request, user_id):
	objetivo = get_object_or_404(User, id=user_id)

	if request.method == 'POST':
		if objetivo == request.user:
			messages.error(request, 'No puedes bloquear tu propio usuario.')
			return redirect('core:registro')

		if objetivo.is_superuser and not request.user.is_superuser:
			messages.error(request, 'No tienes permiso para bloquear este usuario.')
			return redirect('core:registro')

		objetivo.is_active = not objetivo.is_active
		objetivo.save(update_fields=['is_active'])
		messages.success(
			request,
			f"Usuario {'bloqueado' if not objetivo.is_active else 'desbloqueado'} correctamente.",
		)

	return redirect('core:registro')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def eliminar_usuario(request, user_id):
	objetivo = get_object_or_404(User, id=user_id)

	if request.method == 'POST':
		if objetivo == request.user:
			messages.error(request, 'No puedes eliminar tu propio usuario.')
			return redirect('core:registro')

		if objetivo.is_superuser and not request.user.is_superuser:
			messages.error(request, 'No tienes permiso para eliminar este usuario.')
			return redirect('core:registro')

		objetivo.delete()
		messages.success(request, 'Usuario eliminado correctamente.')

	return redirect('core:registro')
