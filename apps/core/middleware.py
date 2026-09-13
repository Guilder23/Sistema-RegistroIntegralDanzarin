from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class RequireAuthenticationMiddleware:
    """Blocks application pages for anonymous users before view dispatch."""

    public_paths = {
        '/',
        '/login/',
        '/robots.txt',
        '/sitemap.xml',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        is_static = path.startswith(settings.STATIC_URL)
        is_admin = path == '/secret-admin' or path.startswith('/secret-admin/')
        is_public_certificate = path.startswith('/danzarines/certificado/')

        if (
            not request.user.is_authenticated
            and path not in self.public_paths
            and not is_static
            and not is_admin
            and not is_public_certificate
        ):
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

        response = self.get_response(request)
        if not is_static:
            response.headers.setdefault('X-Content-Type-Options', 'nosniff')
            response.headers.setdefault('Referrer-Policy', 'same-origin')
            response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        return response
