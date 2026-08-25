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
    from apps.socios.models import UserProfile
    try:
        return user.userprofile.rol
    except UserProfile.DoesNotExist:
        return 'miembro'


def is_administrative(user):
    return get_role(user) in {
        'superadministrador',
        'administrador_grupo',
        'administrador_subgrupo',
    }


def can_manage_events(user):
    return get_role(user) in {'superadministrador', 'administrador_grupo'}


def can_register_members(user):
    return get_role(user) in {'superadministrador', 'administrador_subgrupo'}


def can_manage_users(user):
    return get_role(user) == 'superadministrador'


def scope_filter(queryset, user, grupo_field='grupo', subgrupo_field='subgrupo'):
    """Limita un queryset al ámbito del usuario autenticado."""
    role = get_role(user)
    if role == 'superadministrador':
        return queryset
    from apps.socios.models import UserProfile
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return queryset.none()
    if role == 'administrador_grupo' and profile.grupo_id:
        return queryset.filter(**{f'{grupo_field}_id': profile.grupo_id})
    if role == 'administrador_subgrupo' and profile.subgrupo_id:
        return queryset.filter(**{f'{subgrupo_field}_id': profile.subgrupo_id})
    return queryset.none()


def scope_socios(queryset, user):
    role = get_role(user)
    if role == 'superadministrador':
        return queryset
    if role == 'miembro':
        return queryset.filter(user=user)
    return scope_filter(queryset, user, 'membresias__grupo', 'membresias__subgrupo').distinct()


def registrar_auditoria(usuario, accion, registro_afectado, anterior=None, nuevo=None):
    if get_role(usuario) == 'superadministrador':
        return
    from .models import Auditoria
    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        registro_afectado=registro_afectado,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
    )
