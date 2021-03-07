from django.urls import re_path, path

from wallets.views import deposits, withdrawals, crud_for_the_wallet, \
    see_wallets_or_create


urlpatterns = [
    re_path('^(?P<wallet_id>[0-9]+)/$', crud_for_the_wallet),
    re_path('^(?P<wallet_receiver>[0-9]+)/deposits/$', deposits),
    re_path('^(?P<wallet_sender>[0-9]+)/withdrawals/'
            '(?P<wallet_receiver>[0-9]+)/$', withdrawals),
    re_path('$', see_wallets_or_create),
]
