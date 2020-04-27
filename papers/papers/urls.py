"""papers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from . import views


handler404 = views.handler404
handler403 = views.handler403
handler500 = views.handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('slaves.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('management/', include('big_brother.urls')),
    path('fronttesting/', include('fronttesting.urls')),
    path('pass/', include('gestapo.urls'))
]
