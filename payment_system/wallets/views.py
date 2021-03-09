import json
from decimal import Decimal, ROUND_FLOOR, InvalidOperation

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.authtoken.models import Token

from wallets.decorators import decorator_for_authorization
from wallets.models import Wallet, Operation


exceptions = (
    ValueError,
    KeyError,
    AttributeError,
    IntegrityError,
    InvalidOperation,
    Wallet.DoesNotExist,
)


@decorator_for_authorization
@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["GET", "POST"])
def see_wallets_or_create(request: WSGIRequest) -> JsonResponse:
    """
    If HTTP method - GET:
    returns information about all wallets.

    If HTTP method - POST:
    creates the new wallet.
    """
    if request.method == "GET":
        wallet_list = Wallet.objects.all()
        paginator = Paginator(wallet_list, 25)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        result = page_obj.object_list.values('id', 'name', 'client_firstname',
                                             'client_surname')
        return JsonResponse(list(result), safe=False)

    if request.method == "POST":
        data = json.loads(request.body)
        wallet_pk = Wallet.objects.all().last().pk
        if not (data.get('client_firstname') and data.get('client_surname')):
            return JsonResponse(['Enter the correct data'], safe=False,
                                status=status.HTTP_400_BAD_REQUEST)

        fields = {
            'name': f'wallet {wallet_pk + 1}',
            'client_firstname': data.get('client_firstname'),
            'client_surname': data.get('client_surname'),
        }
        try:
            Wallet.objects.create(**fields)
            return JsonResponse(['The wallet created'], safe=False,
                                status=status.HTTP_201_CREATED)
        except exceptions:
            return JsonResponse(['The wallet can not be created'], safe=False,
                                status=status.HTTP_400_BAD_REQUEST)


@decorator_for_authorization
@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def crud_for_the_wallet(request: WSGIRequest, wallet_id: str)\
        -> JsonResponse:
    """
    If HTTP method - GET:
    Returns all data about the selected wallet.

    If HTTP method - DELETE:
    Deletes the selected wallet.

    If HTTP method - POST:
    Updates the selected wallet.
    """
    wallet_id = int(wallet_id)
    wallet = Wallet.objects.filter(id=wallet_id)

    if wallet and request.method == 'GET':
        return JsonResponse(list(wallet.values()), safe=False)

    if wallet and request.method == 'DELETE':
        Wallet.objects.get(pk=wallet_id).delete()
        return JsonResponse([f'Wallet with id={wallet_id} deleted'], safe=False)

    if wallet and request.method == 'POST':
        w = Wallet.objects.get(pk=wallet_id)
        data = json.loads(request.body)
        if not (data.get('client_firstname') and data.get('client_surname')):
            return JsonResponse(['Enter the correct data'], safe=False,
                                status=status.HTTP_400_BAD_REQUEST)

        fields = {
            'client_firstname': data.get('client_firstname', w.client_firstname),
            'client_surname': data.get('client_surname', w.client_surname),
        }
        try:
            wallet.update(**fields)
        except exceptions:
            return JsonResponse(['The wallet can not be updated.'], safe=False,
                                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse([f'Wallet with id={wallet_id} updated'], safe=False)

    return JsonResponse([f'Wallet with id={wallet_id} does not exist'],
                        safe=False, status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
def transfer_money(sender: int, receiver: int, amount: Decimal) -> None:
    """
    Transfers money from the sender's wallet to the receiver's wallet
    if the sender's wallet balance is greater than or equal
    to the amount of money entered.
    """
    Wallet.objects.filter(pk=sender).update(balance=F('balance') - amount)
    if Wallet.objects.get(pk=sender).balance < Decimal("0.00"):
        raise ValueError

    Wallet.objects.filter(pk=receiver).update(balance=F('balance') + amount)
    Operation.objects.create(name='deposit', wallet=Wallet.objects.get(pk=receiver),
                             amount=amount)
    Operation.objects.create(name='withdrawal', wallet=Wallet.objects.get(pk=sender),
                             amount=amount)


@decorator_for_authorization
@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["POST"])
def deposits(request: WSGIRequest, wallet_receiver: str) -> JsonResponse:
    """
    Called when requesting to transfer money to
    the customer's wallet.

    Returns status 200-OK if it can be done
    otherwise returns status 400-BAD REQUEST.
    """
    wallet_id = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        if amount > Decimal("0.00"):
            with transaction.atomic():
                Wallet.objects.filter(id=wallet_id).update(balance=F('balance') + amount)
                Operation.objects.create(name='deposit', amount=amount,
                                         wallet=Wallet.objects.get(id=wallet_id))
                return JsonResponse({}, status=status.HTTP_200_OK)

    except exceptions:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@transaction.non_atomic_requests
@decorator_for_authorization
@csrf_exempt
@require_http_methods(["POST"])
def withdrawals(request: WSGIRequest, wallet_sender: str,
                wallet_receiver: str) -> JsonResponse:
    """
    Called when requesting to transfer money to
    the customer's wallet from another wallet.

    Returns status 200-OK if it can be done
    otherwise returns status 400-BAD REQUEST.
    """
    wallet_sender = int(wallet_sender)
    wallet_receiver = int(wallet_receiver)
    try:
        data = json.loads(request.body)
        amount = Decimal(data['amount'])
        amount = amount.quantize(Decimal("1.00"), ROUND_FLOOR)
        if amount > Decimal("0.00"):
            transfer_money(wallet_sender, wallet_receiver, amount)
            return JsonResponse({}, status=status.HTTP_200_OK)

    except exceptions:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@transaction.non_atomic_requests
@decorator_for_authorization
@require_http_methods(["GET"])
def operations(request: WSGIRequest, wallet_id: str,
               operation: str) -> JsonResponse:
    """
    Returns operations (deposit/withdrawal/all operations)
    on the desired wallet in JSON format.
    """
    wallet_id = int(wallet_id)
    if not Wallet.objects.filter(id=wallet_id):
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    operation_cases = (
        '',
        'deposit',
        'withdrawal',
    )
    if operation not in operation_cases:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    operations_qs = Operation.objects.filter(wallet=wallet_id)
    if operation:
        operations_qs = operations_qs.filter(name=operation)

    filter_ = request.GET.get('filter')
    if filter_ in ('date', '-date'):
        operations_qs = operations_qs.order_by(filter_)
    elif filter_:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    paginator = Paginator(operations_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    result = page_obj.object_list.values()
    return JsonResponse(list(result), safe=False)


def documentation(request: WSGIRequest) -> HttpResponse:
    """Returns documentation html page"""
    return render(request, "index.html")


@transaction.non_atomic_requests
@csrf_exempt
@require_http_methods(["POST"])
def get_token(request: WSGIRequest) -> JsonResponse:
    """
    Returns the user's token
    if the user was successfully authorized.

    If the user is authorized for the first time,
    a new token is created for the user.
    If the user has been authorized before,
    the existing token is returned.
    """
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    user = User.objects.filter(username=username)
    if user and check_password(password, user.first().password):
        user = user.first()
        token = Token.objects.filter(user=user).first()
        token = Token.objects.create(user=user) if not token else token

        return JsonResponse({'Token': f'{token}'})

    return JsonResponse(['Invalid username or password'], safe=False,
                        status=status.HTTP_401_UNAUTHORIZED)
