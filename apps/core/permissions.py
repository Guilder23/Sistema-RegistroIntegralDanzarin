def can_manage_inventory(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff:
        return True
    return user.groups.filter(name='operador').exists()


def get_role(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    if getattr(user, 'is_superuser', False):
        return 'superadministrador'
    from apps.danzarines.models import UserProfile
    try:
        return user.userprofile.rol
    except UserProfile.DoesNotExist:
        return 'miembro'


def is_administrative(user):
    return get_role(user) in {
        'superadministrador',
        'administrador_asociacion',
        'administrador_conjunto',
    }


def can_manage_events(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion'}


def can_register_members(user):
    return get_role(user) in {'superadministrador', 'administrador_asociacion', 'administrador_conjunto'}
def can_manage_member_states(user):
    return get_role(user) in {'superadministrador', 'administrador_conjunto'}


def can_manage_users(user):
    return get_role(user) == 'superadministrador'


def scope_filter(queryset, user, asociacion_field='asociacion', conjunto_field='conjunto'):
    """Limita un queryset al ámbito del usuario autenticado."""
    role = get_role(user)
    if role == 'superadministrador':
        return queryset
    from apps.danzarines.models import UserProfile
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return queryset.none()
    if role == 'administrador_asociacion' and profile.asociacion_id:
        return queryset.filter(**{f'{asociacion_field}_id': profile.asociacion_id})
    if role == 'administrador_conjunto' and profile.conjunto_id:
        return queryset.filter(**{f'{conjunto_field}_id': profile.conjunto_id})
    return queryset.none()


def scope_danzarines(queryset, user):
    role = get_role(user)
    if role == 'superadministrador':
        return queryset
    if role == 'miembro':
        return queryset.filter(user=user)
    return scope_filter(queryset, user, 'membresias__asociacion', 'membresias__conjunto').distinct()


def registrar_auditoria(usuario, accion, registro_afectado, anterior=None, nuevo=None, asociacion=None, conjunto=None):
    from .models import Auditoria
    from apps.danzarines.models import UserProfile

    auditoria_asociacion = asociacion
    auditoria_conjunto = conjunto

    if usuario and getattr(usuario, 'is_authenticated', False):
        try:
            profile = getattr(usuario, 'userprofile', None)
            if profile:
                if not auditoria_asociacion and profile.asociacion:
                    auditoria_asociacion = profile.asociacion
                if not auditoria_conjunto and profile.conjunto:
                    auditoria_conjunto = profile.conjunto
        except Exception:
            pass

    Auditoria.objects.create(
        usuario=usuario if (usuario and getattr(usuario, 'is_authenticated', False)) else None,
        accion=accion,
        registro_afectado=registro_afectado,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
        asociacion=auditoria_asociacion,
        conjunto=auditoria_conjunto,
    )

