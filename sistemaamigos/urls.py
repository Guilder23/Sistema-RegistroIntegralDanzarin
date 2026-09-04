"""
URL configuration for sistemaamigos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include(('apps.core.urls', 'core'), namespace='core')),
    path('danzarines/', include(('apps.danzarines.urls', 'danzarines'), namespace='danzarines')),
    path('reportes/', include(('apps.reportes.urls', 'reportes'), namespace='reportes')),
    path('souvenirs/', include(('apps.souvenirs.urls', 'souvenirs'), namespace='souvenirs')),
    path('eventos/', include(('apps.eventos.urls', 'eventos'), namespace='eventos')),
    path('dashboard/', include(('apps.dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('asociaciones/', include(('apps.asociaciones.urls', 'asociaciones'), namespace='asociaciones')),
    path('conjuntos/', include(('apps.conjuntos.urls', 'conjuntos'), namespace='conjuntos')),
    path('bloques/', include(('apps.bloques.urls', 'bloques'), namespace='bloques')),
    path('membresias/', include(('apps.membresias.urls', 'membresias'), namespace='membresias')),
    path('auditoria/', include(('apps.auditoria.urls', 'auditoria'), namespace='auditoria')),
    path('secret-admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
