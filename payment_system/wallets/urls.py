from django.urls import re_path
from rest_framework.routers import SimpleRouter

from wallets.views import WalletViewSet, deposits, withdrawals, see_the_wallet

router = SimpleRouter()
router.register(r'', WalletViewSet)

urlpatterns = [
    re_path('(?P<wallet_id>[0-9]+)/$', see_the_wallet),
    re_path('(?P<wallet_receiver>[0-9]+)/deposits/$', deposits),
    re_path('(?P<wallet_sender>[0-9]+)/withdrawals/'
            '(?P<wallet_receiver>[0-9]+)/$', withdrawals),
]

urlpatterns += router.urls
