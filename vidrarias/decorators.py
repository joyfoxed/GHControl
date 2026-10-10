"""Decorators de autorização do módulo vidrarias (RBAC)."""

from functools import wraps

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required as django_staff_required
from django.shortcuts import redirect

MENSAGEM_STAFF = (
    'Acesso restrito: apenas técnicos e administradores podem modificar '
    'vidrarias. Alunos têm acesso somente leitura.'
)


def requer_staff(view_func):
    """
    Proteção de escrita equivalente a @staff_member_required:
    exige is_staff e redireciona alunos ao dashboard com mensagem.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('estoque:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, MENSAGEM_STAFF)
            return redirect('vidrarias:dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped


# Alias explícito solicitado no requisito de segurança.
staff_member_required = requer_staff
# Mantém referência ao decorator nativo do Django, se necessário.
django_staff_member_required = django_staff_required
