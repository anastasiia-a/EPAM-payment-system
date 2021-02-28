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
from django.urls import path, re_path
from rest_framework.routers import SimpleRouter

from wallets.views import WalletViewSet, deposits, withdrawals

router = SimpleRouter()

router.register(r'wallets', WalletViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('wallets/(?P<wallet_sender>[0-9]+)/deposits/$', deposits),
    re_path('wallets/(?P<wallet_sender>[0-9]+)/withdrawals/(?P<wallet_receiver>[0-9]+)/$', withdrawals)
]

urlpatterns += router.urls
