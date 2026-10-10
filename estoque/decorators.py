"""Decorators de autorização do app estoque."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
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


def requer_superuser(view_func):
    """
    Restringe a view a superusuários (logs de auditoria / área sensível).
    Técnicos (is_staff) sem is_superuser e alunos são bloqueados.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('estoque:login')
        if not request.user.is_superuser:
            messages.error(
                request,
                'Acesso restrito: apenas superusuários podem visualizar '
                'os logs de auditoria do sistema.',
            )
            return redirect('estoque:portal')
        return view_func(request, *args, **kwargs)

    return _wrapped


# Alternativa nativa (redireciona ao login se falhar).
requer_superuser_nativo = user_passes_test(
    lambda u: u.is_active and u.is_superuser,
    login_url='estoque:login',
)
