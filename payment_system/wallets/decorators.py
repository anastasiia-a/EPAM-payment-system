from django.http import HttpResponse
from rest_framework import status
from rest_framework.authtoken.models import Token


def decorator_for_authorization(func):
    """
    Checks the token entered by the user.
    If it does not exist in the database,
    the 401-UNAUTHORIZED status is returned.
    """
    def wrapper_checking_token(*args, **kwargs):
        request = args[0]
        meta = request.META.get('HTTP_AUTHORIZATION', '').split()
        token = meta[-1] if meta else None
        if not (token and Token.objects.filter(key=token)):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

        return func(*args, **kwargs)

    return wrapper_checking_token
