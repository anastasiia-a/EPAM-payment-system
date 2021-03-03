import json
from decimal import Decimal, ROUND_FLOOR

from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from wallets.models import Wallet, Operation
from wallets.serializer import WalletSerializer


@transaction.non_atomic_requests
class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


@transaction.atomic
def transfer_money(sender: str, receiver: str, amount: Decimal) -> None:
    """Transfers money from the sender's wallet to the receiver's wallet
    if the sender's wallet balance is greater than or equal to the amount of
    money entered."""
    wallet_receiver = Wallet.objects.filter(pk=receiver)
    wallet_sender = Wallet.objects.filter(pk=sender)
    if wallet_sender.annotate(money=F('balance')).filter(money__gte=amount):
        wallet_sender.update(balance=F('balance') - amount)
        wallet_receiver.update(balance=F('balance') + amount)
    else:
        raise ValueError

    Operation.objects.create(name='deposit', wallet=wallet_receiver, amount=amount)
    Operation.objects.create(name='withdrawal', wallet=wallet_sender, amount=amount)


@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["POST"])
def deposits(request, wallet_receiver: str) -> HttpResponse:
    """Called when requesting to transfer money to
    the customer's wallet.
    Returns status 200-OK if it can be done
    otherwise returns status 400-BAD REQUEST."""
    wallet_id = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        if amount > Decimal("0.00"):
            Wallet.objects.filter(pk=wallet_id).update(balance=F('balance') + amount)
            Operation.objects.create(name='deposit', wallet=Wallet.objects.get(pk=wallet_id),
                                     amount=amount)

    except (ValueError, KeyError, Wallet.DoesNotExist, AttributeError):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)


@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["POST"])
def withdrawals(request, wallet_sender: str,
                wallet_receiver: str) -> HttpResponse:
    """Called when requesting to transfer money to
    the customer's wallet from another wallet.
    Returns status 200-OK if it can be done
    otherwise returns status 400-BAD REQUEST."""
    wallet_sender = int(wallet_sender)
    wallet_receiver = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        if amount > Decimal("0.00"):
            transfer_money(wallet_sender, wallet_receiver, amount)
    except (ValueError, KeyError, Wallet.DoesNotExist, AttributeError):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_200_OK)


@transaction.non_atomic_requests
@require_http_methods(["GET"])
def operations(request, wallet_id: str, operation: str):
    """Returns operations (deposit/withdrawal/all operations)
    on the desired wallet in JSON format."""
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


def documentation(request):
    return render(request, "index.html")
