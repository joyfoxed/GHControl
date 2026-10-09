"""Decorators de autorização do módulo equipamentos (RBAC)."""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

MENSAGEM_STAFF = (
    'Acesso restrito: apenas técnicos e administradores podem modificar '
    'EPIs e EPCs. Alunos têm acesso somente leitura.'
)


def requer_staff(view_func):
    """
    Exige is_staff (ou superuser). Usuários comuns são redirecionados
    com mensagem amigável — não apenas 403 genérico.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('estoque:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, MENSAGEM_STAFF)
            return redirect('equipamentos:dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped


# Alias explícito para views de escrita (documentação do requisito).
staff_required = requer_staff
