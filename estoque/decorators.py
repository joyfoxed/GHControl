"""Decorators de autorização do app estoque."""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .permissions import (
    MENSAGEM_SEM_PERMISSAO,
    usuario_pode_movimentar_estoque,
)


def requer_permissao_movimentacao(view_func):
    """
    Bloqueia GET e POST de views que alteram estoque.

    Usuários sem permissão são redirecionados ao dashboard com mensagem amigável.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not usuario_pode_movimentar_estoque(request.user):
            messages.error(request, MENSAGEM_SEM_PERMISSAO)
            return redirect('estoque:dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped
