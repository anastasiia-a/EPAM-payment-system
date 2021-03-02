import json
from decimal import Decimal, ROUND_FLOOR

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from wallets.models import Wallet, Operation
from wallets.serializer import WalletSerializer


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


@csrf_exempt
@require_http_methods(["POST"])
def deposits(request, wallet_sender: str) -> HttpResponse:
    """Called when requesting to transfer money to
    the customer's wallet"""
    wallet_id = int(wallet_sender)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        wallet = Wallet.objects.get(id=wallet_id)
    except (ValueError, KeyError, Wallet.DoesNotExist):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)


@csrf_exempt
@require_http_methods(["POST"])
def withdrawals(request, wallet_sender: str,
                wallet_receiver: str) -> HttpResponse:
    """Called when requesting to transfer money to
    the customer's wallet from another wallet."""
    wallet_sender = int(wallet_sender)
    wallet_receiver = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        wallet_sender = Wallet.objects.get(id=wallet_sender)
        wallet_receiver = Wallet.objects.get(id=wallet_receiver)
    except (ValueError, KeyError, Wallet.DoesNotExist):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)


@require_http_methods(["GET"])
def operations(request, wallet_id: str, operation: str):
    """Returns operations (deposit/withdrawal/all operations)
    on the desired wallet."""
    operation_cases = (
        '',
        'deposit',
        'withdrawal',
    )
    if operation not in operation_cases:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    wallet_id = int(wallet_id)
    operations_qs = Operation.objects.filter(wallet=wallet_id)
    if operation:
        operations_qs = operations_qs.filter(name=operation)

    filter_ = request.GET.get('filter', None)
    if filter_ in ('date', '-date'):
        operations_qs = operations_qs.order_by(filter_)
    elif filter_:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    operations_list = list(operations_qs.values())
    return JsonResponse(operations_list, safe=False)
