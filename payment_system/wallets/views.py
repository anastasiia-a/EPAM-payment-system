import json
from decimal import Decimal, ROUND_FLOOR

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from wallets.models import Wallet
from wallets.serializer import WalletSerializer


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


@csrf_exempt
@require_http_methods(["POST"])
def deposits(request, wallet_sender):
    wallet_id = int(wallet_sender)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        wallet = Wallet.objects.get(id=wallet_id)
    except ValueError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Wallet.DoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)


@csrf_exempt
@require_http_methods(["POST"])
def withdrawals(request, wallet_sender, wallet_receiver):
    wallet_sender = int(wallet_sender)
    wallet_receiver = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)

        wallet_sender = Wallet.objects.get(id=wallet_sender)
        wallet_receiver = Wallet.objects.get(id=wallet_receiver)
    except ValueError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Wallet.DoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)
