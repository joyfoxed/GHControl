"""
URL configuration for ghcontrol_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('estoque.urls')),
]

# Em desenvolvimento (DEBUG=True), serve arquivos estáticos de TODAS as fontes
# configuradas (estoque/static/, STATICFILES_DIRS e STATIC_ROOT) via finders.
# Nota: static(..., document_root=STATIC_ROOT) sozinho só expõe a pasta
# staticfiles/ — arquivos novos em estoque/static/ retornam 404 até o collectstatic.
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
