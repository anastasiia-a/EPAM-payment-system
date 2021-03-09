"""payment_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, re_path, include

from wallets.views import operations, documentation, get_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wallets/', include('wallets.urls')),
    path('generate_token/', get_token),
    re_path('operations/(?P<wallet_id>[0-9]+)/'
            '(?P<operation>[a-z]*)/?$', operations),
    re_path('$', documentation),
]
